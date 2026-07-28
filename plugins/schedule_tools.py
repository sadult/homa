"""Scheduling tools: run any natural-language command later or on a schedule."""
from core import scheduler
from tools.registry import Tool, ToolRegistry


async def add_schedule(command: str, target: str = "default", cron: str = "",
                       interval_seconds: int = 0, run_at: str = ""):
    try:
        job_id = scheduler.add_job(command, target, cron=cron,
                                   interval_seconds=interval_seconds, run_at=run_at)
    except ValueError as exc:
        return {"error": str(exc)}
    return {"job_id": job_id}


async def list_schedules():
    return {"jobs": scheduler.list_jobs()}


async def remove_schedule(job_id: str):
    return {"removed": scheduler.remove_job(job_id)}


def register(r: ToolRegistry) -> None:
    C = "schedule"
    r.register(Tool("schedule.add",
        "Schedule a command. Use exactly one of: cron (\"0 9 * * *\"), interval_seconds, or run_at (ISO datetime). target is the chat/session to notify.",
        {"type": "object", "properties": {"command": {"type": "string"}, "target": {"type": "string"},
         "cron": {"type": "string"}, "interval_seconds": {"type": "integer"}, "run_at": {"type": "string"}},
         "required": ["command"]}, add_schedule, category=C))
    r.register(Tool("schedule.list", "List all scheduled jobs.",
        {"type": "object", "properties": {}}, list_schedules, category=C))
    r.register(Tool("schedule.remove", "Remove a scheduled job by id.",
        {"type": "object", "properties": {"job_id": {"type": "string"}}, "required": ["job_id"]},
        remove_schedule, category=C))
