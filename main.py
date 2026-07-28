"""HOMA entry point.

Usage:
  python main.py telegram   # run the Telegram bot
  python main.py web        # run the web UI + REST API
  python main.py both       # run both together (default)
  python main.py cli "..."  # run a single command from the terminal
  python main.py check      # test the connection to 9Router and list model ids
"""
import asyncio
import sys

import uvicorn

from config import settings
from core import scheduler
from core.agent import Agent
from core.logger import StatusReporter, setup_logging
from core.plugin_loader import load_plugins


async def run_cli(command: str) -> None:
    agent = Agent(load_plugins(), confirm_cb=lambda n, a: asyncio.sleep(0, result=True))
    reporter = StatusReporter()
    result = await agent.run(command, reporter)
    print("\n" + result + "\n\n---\n" + reporter.summary())


async def run_telegram() -> None:
    from interfaces.telegram_bot import build_application
    scheduler.start()
    app = build_application()
    await app.initialize()
    await app.start()
    # drop_pending_updates=True stops the bot from replaying old messages that
    # piled up while it was offline/crashed (the cause of the "loops old
    # commands" behavior).
    await app.updater.start_polling(drop_pending_updates=True)
    print("🕊 HOMA Telegram bot running. Ctrl+C to stop.")
    await asyncio.Event().wait()


def run_web() -> None:
    scheduler.start()
    uvicorn.run("interfaces.web.server:app", host=settings.WEB_HOST,
                port=settings.WEB_PORT, log_level="info")


async def run_both() -> None:
    from interfaces.telegram_bot import build_application
    scheduler.start()
    app = build_application()
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    config = uvicorn.Config("interfaces.web.server:app", host=settings.WEB_HOST,
                            port=settings.WEB_PORT, log_level="info")
    server = uvicorn.Server(config)
    print("🕊 HOMA running (Telegram + Web).")
    await server.serve()


def run_check() -> None:
    """Diagnose connectivity to the model endpoint and list available models."""
    import os

    import httpx

    base = settings.NINEROUTER_BASE_URL.rstrip("/")
    print(f"Endpoint : {base}")
    print(f"Model    : {settings.MODEL}")
    for var in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
                "http_proxy", "https_proxy", "all_proxy"):
        if os.environ.get(var):
            print(f"note     : {var} is set — localhost traffic bypasses it on purpose")
            break
    try:
        r = httpx.get(
            f"{base}/models",
            headers={"Authorization": f"Bearer {settings.NINEROUTER_API_KEY}"},
            timeout=10,
            trust_env=False,
        )
    except Exception as exc:
        print(f"\nFAILED — cannot connect: {exc!r}\n")
        print("Hints:")
        print("  1. Is 9Router actually running? Open its dashboard in your browser.")
        print("  2. NINEROUTER_BASE_URL in .env must be the LOCAL endpoint shown in")
        print("     the 9Router dashboard, e.g. http://localhost:<port>/v1")
        print("  3. If a VPN/proxy app intercepts ALL traffic, exclude localhost/127.0.0.1.")
        sys.exit(1)
    if r.status_code == 401:
        print("\nFAILED — endpoint reachable but the API key was rejected (HTTP 401).")
        print("Copy the key from the 9Router dashboard into NINEROUTER_API_KEY in .env.")
        sys.exit(1)
    if r.status_code != 200:
        print(f"\nFAILED — endpoint answered HTTP {r.status_code}: {r.text[:300]}")
        sys.exit(1)
    ids = [m.get("id", "?") for m in r.json().get("data", [])]
    print(f"\nOK — connected. {len(ids)} models available:")
    for mid in ids:
        marker = "   <-- current MODEL" if mid == settings.MODEL else ""
        print(f"  - {mid}{marker}")
    if ids and settings.MODEL not in ids:
        print(f"\nWARNING: MODEL='{settings.MODEL}' is not in the list above.")
        print("Copy one of the exact ids into MODEL in .env.")


def main() -> None:
    setup_logging()
    mode = sys.argv[1] if len(sys.argv) > 1 else "both"
    if mode == "cli":
        asyncio.run(run_cli(" ".join(sys.argv[2:]) or "say hello"))
    elif mode == "telegram":
        asyncio.run(run_telegram())
    elif mode == "web":
        run_web()
    elif mode == "check":
        run_check()
    else:
        asyncio.run(run_both())


if __name__ == "__main__":
    main()
