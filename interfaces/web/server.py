"""FastAPI web interface + REST API for HOMA, with live step streaming."""
import asyncio
import json
import os

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import settings
from core import memory
from core.agent import Agent
from core.logger import StatusReporter
from core.plugin_loader import load_plugins

app = FastAPI(title="HOMA", version="1.1")
_registry = load_plugins()
_STATIC = os.path.join(os.path.dirname(__file__), "static")


class CommandIn(BaseModel):
    command: str
    session: str = "web"
    auto_confirm: bool = False


class SessionIn(BaseModel):
    session: str = "web"


def _auth(token: str | None) -> None:
    # Accept either a raw token or an "Bearer <token>" header.
    if token and token.startswith("Bearer "):
        token = token[7:]
    if token != settings.WEB_AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/")
async def index():
    return FileResponse(os.path.join(_STATIC, "index.html"))


@app.get("/api/tools")
async def tools(authorization: str | None = Header(default=None)):
    _auth(authorization)
    return {"categories": _registry.categories(), "count": len(_registry.all())}


@app.post("/api/forget")
async def forget(body: SessionIn, authorization: str | None = Header(default=None)):
    """Clear the conversation history for a session (the web chat's memory)."""
    _auth(authorization)
    return {"cleared": memory.clear_history(body.session)}


@app.post("/api/command")
async def command(body: CommandIn, authorization: str | None = Header(default=None)):
    _auth(authorization)

    async def confirm(_name, _args):
        return body.auto_confirm

    agent = Agent(_registry, confirm_cb=confirm)
    reporter = StatusReporter()
    result = await agent.run(body.command, reporter, session=body.session)
    return {"result": result, "steps": reporter.steps}


@app.post("/api/stream")
async def stream(body: CommandIn, authorization: str | None = Header(default=None)):
    """Server-Sent Events: emits {type:'step'} entries live, then {type:'final'}.
    This is what makes the UI feel fast — you see each action as it happens."""
    _auth(authorization)
    queue: asyncio.Queue = asyncio.Queue()

    def on_log(entry):
        queue.put_nowait({"type": "step", **entry})

    reporter = StatusReporter(on_log=on_log)

    async def confirm(_name, _args):
        return body.auto_confirm

    async def worker():
        try:
            agent = Agent(_registry, confirm_cb=confirm)
            result = await agent.run(body.command, reporter, session=body.session)
            await queue.put({"type": "final", "result": result})
        except Exception as exc:  # noqa: BLE001
            await queue.put({"type": "final", "result": f"⚠️ Error: {exc}"})
        finally:
            await queue.put(None)

    async def gen():
        task = asyncio.create_task(worker())
        try:
            while True:
                item = await queue.get()
                if item is None:
                    break
                yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
        finally:
            task.cancel()

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})


app.mount("/static", StaticFiles(directory=_STATIC), name="static")
