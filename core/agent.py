import asyncio
import json

from config import settings
from core import llm, memory
from core.logger import StatusReporter
from tools.registry import ToolRegistry

SYSTEM_PROMPT = """You are HOMA, an autonomous assistant ("agent") running on the
user's own laptop. You carry out natural-language commands by calling tools.
You can drive a real web browser, inspect the system, read files, check mail,
remember facts, and schedule future tasks.

HOW TO WORK (important):
- Be decisive and PERSISTENT. Keep calling tools, step by step, until the task
  is actually finished. Do NOT stop halfway and ask what to do next unless you
  are truly blocked (e.g. missing credentials).
- When several independent reads are useful (e.g. read two pages, check disk and
  list a folder), request them together in ONE step so they run in parallel.
- Before interacting with a page (click / type / fill), first call
  `browser.inspect` or `browser.extract_form` to learn the REAL selectors.
  Never invent selectors.
- "Open a site and answer the questions": call `browser.extract_form` to get the
  questions with their options + selectors, decide each answer yourself, fill
  them with `browser.fill_form`, then click next/submit.
- If the user already has their own browser open, use `browser.connect_existing`.
- Use `memory.remember` for durable preferences, `memory.recall`/`memory.search`
  to reuse them.
- Dangerous actions (shell, file writes, sending mail) require confirmation; if
  denied, explain what is blocked and how to enable it.

FINISH by replying in the user's language (Persian or English) with a short,
concrete summary: what you did and the result.
"""


def _tool_msg(tool_call_id: str, result) -> dict:
    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "content": json.dumps(result, ensure_ascii=False, default=str),
    }


class Agent:
    def __init__(self, registry: ToolRegistry, confirm_cb=None):
        self.registry = registry
        # confirm_cb: async fn(tool_name, args) -> bool
        self.confirm_cb = confirm_cb

    async def _run_one(self, tc, reporter: StatusReporter) -> dict:
        name = tc.function.name
        try:
            args = json.loads(tc.function.arguments or "{}")
        except json.JSONDecodeError:
            args = {}
        reporter.log(f"{name}({', '.join(f'{k}={v}' for k, v in args.items())[:120]})")

        tool = self.registry.get(name)
        if tool is None:
            return _tool_msg(tc.id, {"error": f"unknown tool {name}"})

        if tool.dangerous and settings.REQUIRE_CONFIRMATION:
            approved = await self.confirm_cb(name, args) if self.confirm_cb else False
            if not approved:
                reporter.log(f"{name} was not confirmed", "error")
                return _tool_msg(tc.id, {"error": "not confirmed by user"})

        try:
            result = await tool.handler(**args)
            reporter.log(f"✓ {name}", "ok")
        except Exception as exc:  # noqa: BLE001
            result = {"error": str(exc)}
            reporter.log(f"error in {name}: {exc}", "error")
        return _tool_msg(tc.id, result)

    async def run(self, user_command: str, reporter: StatusReporter,
                  session: str = "default") -> str:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages += memory.get_history(session)
        messages.append({"role": "user", "content": user_command})
        memory.add_message(session, "user", user_command)

        tools = self.registry.openai_schema()
        reporter.log(f"command: {user_command}")

        for _step in range(settings.MAX_STEPS):
            msg = await asyncio.to_thread(llm.chat, messages, tools)
            messages.append(msg.model_dump(exclude_none=True))

            if not msg.tool_calls:
                final = msg.content or "Done."
                memory.add_message(session, "assistant", final)
                reporter.log("done", "ok")
                return final

            # Run every tool call in this step; read-only ones run concurrently,
            # while dangerous ones (needing confirmation) run one at a time.
            safe = [tc for tc in msg.tool_calls
                    if not (self.registry.get(tc.function.name)
                            and self.registry.get(tc.function.name).dangerous)]
            risky = [tc for tc in msg.tool_calls if tc not in safe]

            results = []
            if safe:
                results += await asyncio.gather(
                    *(self._run_one(tc, reporter) for tc in safe))
            for tc in risky:
                results.append(await self._run_one(tc, reporter))

            # Preserve original tool_call order for the API.
            by_id = {r["tool_call_id"]: r for r in results}
            for tc in msg.tool_calls:
                messages.append(by_id[tc.id])

        memory.add_message(session, "assistant", "(max steps reached)")
        reporter.log("max steps reached", "error")
        return "Reached the step limit; the task may be unfinished."
