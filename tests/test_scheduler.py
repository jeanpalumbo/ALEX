from datetime import datetime, timedelta, timezone

import pytest

from aicommerce.control_plane.scheduler import Scheduler


class FakeClock:
    def __init__(self, start: datetime) -> None:
        self.now = start

    def advance(self, delta: timedelta) -> None:
        self.now += delta

    def __call__(self) -> datetime:
        return self.now


def test_job_runs_first_time_immediately():
    clock = FakeClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
    scheduler = Scheduler(clock=clock)
    calls = []
    scheduler.add_job("daily_review", timedelta(days=1), lambda: calls.append("ran"))

    ran = scheduler.run_due()
    assert ran == ["daily_review"]
    assert calls == ["ran"]


def test_job_does_not_rerun_before_interval_elapses():
    clock = FakeClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
    scheduler = Scheduler(clock=clock)
    calls = []
    scheduler.add_job("daily_review", timedelta(days=1), lambda: calls.append("ran"))

    scheduler.run_due()
    clock.advance(timedelta(hours=1))
    ran = scheduler.run_due()

    assert ran == []
    assert calls == ["ran"]


def test_job_reruns_after_interval_elapses():
    clock = FakeClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
    scheduler = Scheduler(clock=clock)
    calls = []
    scheduler.add_job("daily_review", timedelta(days=1), lambda: calls.append("ran"))

    scheduler.run_due()
    clock.advance(timedelta(days=1, minutes=1))
    ran = scheduler.run_due()

    assert ran == ["daily_review"]
    assert calls == ["ran", "ran"]


def test_duplicate_job_name_rejected():
    scheduler = Scheduler()
    scheduler.add_job("job1", timedelta(hours=1), lambda: None)
    with pytest.raises(ValueError):
        scheduler.add_job("job1", timedelta(hours=1), lambda: None)


def test_remove_job():
    clock = FakeClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
    scheduler = Scheduler(clock=clock)
    calls = []
    scheduler.add_job("job1", timedelta(hours=1), lambda: calls.append("ran"))
    scheduler.remove_job("job1")

    assert scheduler.run_due() == []
    assert calls == []
