"""Central Approval Queue — high-risk / irreversible / expensive actions wait
here for human sign-off before execution."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    EXECUTED = "executed"
    FAILED = "failed"


@dataclass
class ApprovalRequest:
    action: str
    agent: str
    reason: str
    evidence: str
    impact: str
    cost: float
    risk: str  # e.g. "low" | "medium" | "high"
    reversible: bool
    proposal: str
    deadline: Optional[datetime] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    decided_at: Optional[datetime] = None
    decided_by: Optional[str] = None
    decision_note: Optional[str] = None
    metadata: dict = field(default_factory=dict)


class ApprovalQueue:
    def __init__(self) -> None:
        self._requests: dict[str, ApprovalRequest] = {}

    def submit(self, request: ApprovalRequest) -> ApprovalRequest:
        self._requests[request.id] = request
        return request

    def get(self, request_id: str) -> ApprovalRequest:
        return self._requests[request_id]

    def pending(self) -> list[ApprovalRequest]:
        self._expire_overdue()
        return [r for r in self._requests.values() if r.status == ApprovalStatus.PENDING]

    def _expire_overdue(self) -> None:
        now = datetime.now(timezone.utc)
        for r in self._requests.values():
            if r.status == ApprovalStatus.PENDING and r.deadline and now > r.deadline:
                r.status = ApprovalStatus.EXPIRED

    def decide(self, request_id: str, approve: bool, decided_by: str, note: str = "") -> ApprovalRequest:
        request = self.get(request_id)
        self._expire_overdue()
        if request.status != ApprovalStatus.PENDING:
            raise ValueError(f"request {request_id} is not pending (status={request.status})")
        request.status = ApprovalStatus.APPROVED if approve else ApprovalStatus.REJECTED
        request.decided_at = datetime.now(timezone.utc)
        request.decided_by = decided_by
        request.decision_note = note
        return request

    def mark_executed(self, request_id: str, success: bool) -> ApprovalRequest:
        request = self.get(request_id)
        if request.status != ApprovalStatus.APPROVED:
            raise ValueError(f"request {request_id} was not approved (status={request.status})")
        request.status = ApprovalStatus.EXECUTED if success else ApprovalStatus.FAILED
        return request
