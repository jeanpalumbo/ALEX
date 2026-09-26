"""Scheduler — recurring jobs (daily business review, SEO crawl, etc.).

PARTIAL: this is a polling-based, in-process scheduler with no persistence
across restarts and no real wall-clock timer thread. Something has to call
`run_due()` periodically (e.g. a loop, a cron-triggered process). A real
deployment would back this with an actual cron/queue; this is enough to unit
test the job-selection logic deterministically via an injectable clock.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional


@dataclass
class Job:
    name: str
    interval: timedelta
    func: Callable[[], None]
    last_run: Optional[datetime] = None

    def due(self, now: datetime) -> bool:
        return self.last_run is None or (now - self.last_run) >= self.interval


class Scheduler:
    def __init__(self, clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc)) -> None:
        self._clock = clock
        self._jobs: dict[str, Job] = {}

    def add_job(self, name: str, interval: timedelta, func: Callable[[], None]) -> None:
        if name in self._jobs:
            raise ValueError(f"job '{name}' already scheduled")
        self._jobs[name] = Job(name=name, interval=interval, func=func)

    def remove_job(self, name: str) -> None:
        self._jobs.pop(name, None)

    def run_due(self) -> list[str]:
        """Run every job whose interval has elapsed. Returns names of jobs run."""
        now = self._clock()
        ran = []
        for job in self._jobs.values():
            if job.due(now):
                job.func()
                job.last_run = now
                ran.append(job.name)
        return ran

    def jobs(self) -> list[Job]:
        return list(self._jobs.values())
