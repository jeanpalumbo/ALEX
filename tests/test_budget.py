import pytest

from aicommerce.control_plane.budget import BudgetExceededError, BudgetGuard


def test_spend_within_budget_succeeds():
    guard = BudgetGuard()
    guard.set_budget("daily", 100.0)
    guard.spend("daily", 40.0)

    status = guard.status("daily")
    assert status["spent"] == 40.0
    assert status["available"] == 60.0


def test_spend_beyond_budget_raises_and_never_applies():
    guard = BudgetGuard()
    guard.set_budget("daily", 50.0)

    with pytest.raises(BudgetExceededError):
        guard.spend("daily", 51.0)

    # the rejected spend must not have been silently applied
    assert guard.status("daily")["spent"] == 0.0


def test_reserve_then_spend_from_reservation():
    guard = BudgetGuard()
    guard.set_budget("campaign:launch", 200.0)
    guard.reserve("campaign:launch", 80.0)

    status = guard.status("campaign:launch")
    assert status["reserved"] == 80.0
    assert status["available"] == 120.0

    guard.spend("campaign:launch", 80.0, from_reservation=True)
    status = guard.status("campaign:launch")
    assert status["reserved"] == 0.0
    assert status["spent"] == 80.0
    assert status["available"] == 120.0


def test_reserve_beyond_available_raises():
    guard = BudgetGuard()
    guard.set_budget("daily", 100.0)
    guard.reserve("daily", 60.0)

    with pytest.raises(BudgetExceededError):
        guard.reserve("daily", 41.0)


def test_release_reservation_frees_budget():
    guard = BudgetGuard()
    guard.set_budget("daily", 100.0)
    guard.reserve("daily", 60.0)
    guard.release_reservation("daily", 60.0)

    assert guard.status("daily")["available"] == 100.0


def test_history_tracks_actual_spend_only():
    guard = BudgetGuard()
    guard.set_budget("daily", 100.0)
    guard.spend("daily", 10.0)
    guard.spend("daily", 5.0)

    assert guard.history("daily") == [
        {"scope": "daily", "amount": 10.0},
        {"scope": "daily", "amount": 5.0},
    ]
