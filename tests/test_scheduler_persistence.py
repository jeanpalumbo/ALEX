from datetime import datetime, timedelta, timezone

from aicommerce.control_plane.scheduler import Scheduler


class FakeClock:
    def __init__(self, start: datetime) -> None:
        self.now = start

    def advance(self, delta: timedelta) -> None:
        self.now += delta

    def __call__(self) -> datetime:
        return self.now


def test_last_run_survives_a_new_scheduler_instance_against_the_same_db(tmp_path):
    db_path = tmp_path / "scheduler.db"
    clock = FakeClock(datetime(2026, 1, 1, tzinfo=timezone.utc))

    s1 = Scheduler(clock=clock, db_path=db_path)
    calls = []
    s1.add_job("heartbeat", timedelta(hours=1), lambda: calls.append("ran"))
    s1.run_due()
    assert calls == ["ran"]

    # Simulate a process restart 5 minutes later: a fresh Scheduler pointed at
    # the same db must remember it already ran, and NOT fire again yet.
    clock.advance(timedelta(minutes=5))
    s2 = Scheduler(clock=clock, db_path=db_path)
    calls2 = []
    s2.add_job("heartbeat", timedelta(hours=1), lambda: calls2.append("ran"))
    ran = s2.run_due()

    assert ran == []
    assert calls2 == []


def test_job_fires_again_after_restart_once_interval_has_truly_elapsed(tmp_path):
    db_path = tmp_path / "scheduler.db"
    clock = FakeClock(datetime(2026, 1, 1, tzinfo=timezone.utc))

    s1 = Scheduler(clock=clock, db_path=db_path)
    s1.add_job("heartbeat", timedelta(hours=1), lambda: None)
    s1.run_due()

    clock.advance(timedelta(hours=2))
    s2 = Scheduler(clock=clock, db_path=db_path)
    calls = []
    s2.add_job("heartbeat", timedelta(hours=1), lambda: calls.append("ran"))
    ran = s2.run_due()

    assert ran == ["heartbeat"]
    assert calls == ["ran"]


def test_run_due_one_failing_job_does_not_block_the_others():
    clock = FakeClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
    scheduler = Scheduler(clock=clock)

    def boom():
        raise RuntimeError("simulated failure")

    good_calls = []
    scheduler.add_job("bad", timedelta(hours=1), boom)
    scheduler.add_job("good", timedelta(hours=1), lambda: good_calls.append("ran"))

    errors = []
    ran = scheduler.run_due(on_error=lambda name, exc: errors.append((name, str(exc))))

    assert ran == ["good"]
    assert good_calls == ["ran"]
    assert errors == [("bad", "simulated failure")]


def test_failed_job_is_retried_next_tick_not_skipped_for_a_full_interval():
    clock = FakeClock(datetime(2026, 1, 1, tzinfo=timezone.utc))
    scheduler = Scheduler(clock=clock)

    attempts = []

    def flaky():
        attempts.append(1)
        if len(attempts) == 1:
            raise RuntimeError("first attempt fails")

    scheduler.add_job("flaky", timedelta(hours=1), flaky)

    ran1 = scheduler.run_due(on_error=lambda *a: None)
    assert ran1 == []
    assert len(attempts) == 1

    clock.advance(timedelta(seconds=1))  # well within the interval
    ran2 = scheduler.run_due(on_error=lambda *a: None)
    assert ran2 == ["flaky"]
    assert len(attempts) == 2
