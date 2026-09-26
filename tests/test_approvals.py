from datetime import datetime, timedelta, timezone

import pytest

from aicommerce.control_plane.approvals import ApprovalQueue, ApprovalRequest, ApprovalStatus


def make_request(**overrides) -> ApprovalRequest:
    defaults = dict(
        action="launch_campaign",
        agent="ads_agent",
        reason="new product launch",
        evidence="market research doc v3",
        impact="spend $500 over 7 days",
        cost=500.0,
        risk="high",
        reversible=False,
        proposal="launch on Meta and Google",
    )
    defaults.update(overrides)
    return ApprovalRequest(**defaults)


def test_submitted_request_is_pending():
    queue = ApprovalQueue()
    req = queue.submit(make_request())
    assert req.status == ApprovalStatus.PENDING
    assert req in queue.pending()


def test_approve_transitions_and_records_decider():
    queue = ApprovalQueue()
    req = queue.submit(make_request())
    decided = queue.decide(req.id, approve=True, decided_by="jean", note="looks good")

    assert decided.status == ApprovalStatus.APPROVED
    assert decided.decided_by == "jean"
    assert decided.decision_note == "looks good"
    assert req not in queue.pending()


def test_reject_transitions():
    queue = ApprovalQueue()
    req = queue.submit(make_request())
    decided = queue.decide(req.id, approve=False, decided_by="jean")
    assert decided.status == ApprovalStatus.REJECTED


def test_cannot_decide_twice():
    queue = ApprovalQueue()
    req = queue.submit(make_request())
    queue.decide(req.id, approve=True, decided_by="jean")
    with pytest.raises(ValueError):
        queue.decide(req.id, approve=True, decided_by="jean")


def test_overdue_pending_request_expires():
    queue = ApprovalQueue()
    past_deadline = datetime.now(timezone.utc) - timedelta(days=1)
    req = queue.submit(make_request(deadline=past_deadline))

    assert req not in queue.pending()
    assert queue.get(req.id).status == ApprovalStatus.EXPIRED


def test_mark_executed_requires_prior_approval():
    queue = ApprovalQueue()
    req = queue.submit(make_request())
    with pytest.raises(ValueError):
        queue.mark_executed(req.id, success=True)

    queue.decide(req.id, approve=True, decided_by="jean")
    executed = queue.mark_executed(req.id, success=True)
    assert executed.status == ApprovalStatus.EXECUTED
