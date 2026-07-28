"""Persistent job scheduler built on APScheduler + SQLite.

Scheduled jobs run a natural-language command through the agent and push the
result to a notifier (e.g. a Telegram chat). Jobs survive restarts because the
job store is a SQLite file.
"""
import asyncio
from typing import Callable

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from config import settings

_scheduler: AsyncIOScheduler | None = None
# notifier(target: str, text: str) -> Awaitable | None
_notifier: Callable[[str, str], object] | None = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        jobstores = {
            "default": SQLAlchemyJobStore(url=f"sqlite:///{settings.DB_PATH}")
        }
        _scheduler = AsyncIOScheduler(jobstores=jobstores)
    return _scheduler


def set_notifier(fn: Callable[[str, str], object]) -> None:
    global _notifier
    _notifier = fn


def start() -> None:
    sched = get_scheduler()
    if not sched.running:
        sched.start()


async def run_scheduled(command: str, target: str) -> None:
    """Top-level (importable) callable executed by APScheduler."""
    from core.agent import Agent
    from core.logger import StatusReporter
    from core.plugin_loader import load_plugins

    reporter = StatusReporter()
    agent = Agent(load_plugins())
    result = await agent.run(command, reporter, session=f"sched:{target}")
    if _notifier is not None:
        maybe = _notifier(target, f"⏰ Scheduled task done:\n{result}")
        if asyncio.iscoroutine(maybe):
            await maybe


def add_job(command: str, target: str, *, cron: str = "", interval_seconds: int = 0,
            run_at: str = "") -> str:
    """Create a job. Provide exactly one of cron / interval_seconds / run_at.

    - cron: 5-field crontab, e.g. "0 9 * * *" (every day 09:00)
    - interval_seconds: repeat every N seconds
    - run_at: ISO datetime for a one-off run, e.g. "2026-07-06T18:30:00"
    """
    sched = get_scheduler()
    if cron:
        trigger = CronTrigger.from_crontab(cron)
    elif interval_seconds:
        trigger = IntervalTrigger(seconds=interval_seconds)
    elif run_at:
        trigger = DateTrigger(run_date=run_at)
    else:
        raise ValueError("Provide cron, interval_seconds, or run_at.")
    job = sched.add_job(
        run_scheduled, trigger=trigger, args=[command, target], replace_existing=False
    )
    return job.id


def list_jobs() -> list[dict]:
    jobs = get_scheduler().get_jobs()
    return [
        {
            "id": j.id,
            "next_run": str(j.next_run_time),
            "command": j.args[0] if j.args else "",
            "target": j.args[1] if len(j.args) > 1 else "",
        }
        for j in jobs
    ]


def remove_job(job_id: str) -> bool:
    try:
        get_scheduler().remove_job(job_id)
        return True
    except Exception:  # noqa: BLE001
        return False
