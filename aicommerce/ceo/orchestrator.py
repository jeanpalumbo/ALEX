"""AI CEO orchestrator.

Runs the core loop from master context section 6:
  OBSERVE -> UNDERSTAND -> DECIDE -> ACT -> MEASURE -> LEARN -> IMPROVE

The CEO here is bounded by the constitution: it is not an unrestricted owner.
Every task goes through permissions, budget and (when risk/reversibility
warrants it) human approval before an agent's action counts as executed.
High-risk or irreversible actions never execute themselves — they stop at
PENDING_APPROVAL and wait for `approve_and_execute`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from aicommerce.agents.base import Agent, AgentResult
from aicommerce.agents.stubs import QAAgent
from aicommerce.brain.models import Confidence, MemoryKind, MemoryRecord
from aicommerce.brain.store import CompanyBrain
from aicommerce.control_plane.approvals import ApprovalQueue, ApprovalRequest, ApprovalStatus
from aicommerce.control_plane.budget import BudgetExceededError, BudgetGuard
from aicommerce.control_plane.events import EventBus
from aicommerce.control_plane.permissions import PermissionDeniedError, PermissionManager
from aicommerce.control_plane.registry import AgentRegistry


class TaskStatus(str, Enum):
    EXECUTED = "executed"
    FAILED = "failed"
    DENIED = "denied"
    PENDING_APPROVAL = "pending_approval"
    QA_REJECTED = "qa_rejected"


@dataclass
class TaskOutcome:
    status: TaskStatus
    agent_result: Optional[AgentResult] = None
    approval_request_id: Optional[str] = None
    detail: str = ""


REQUIRES_APPROVAL_RISKS = {"high", "critical"}


class Orchestrator:
    def __init__(
        self,
        registry: AgentRegistry,
        permissions: PermissionManager,
        budget: BudgetGuard,
        approvals: ApprovalQueue,
        brain: CompanyBrain,
        qa_agent: Optional[QAAgent] = None,
        approval_ttl_seconds: int = 1800,
        events: Optional[EventBus] = None,
    ) -> None:
        self.registry = registry
        self.permissions = permissions
        self.budget = budget
        self.approvals = approvals
        self.brain = brain
        self.qa_agent = qa_agent or QAAgent()
        self.approval_ttl_seconds = approval_ttl_seconds
        self.events = events
        # Kill switch: while engaged, run_cycle refuses every new action
        # (read or write) before touching permissions/budget/agents. Chat and
        # memory queries still work since they don't go through run_cycle.
        self.kill_switch_engaged = False
        self.kill_switch_reason = ""

    def _publish(self, event_type: str, payload: dict) -> None:
        if self.events is not None:
            self.events.publish(event_type, payload)

    # ------------------------------------------------------------------
    # Core loop
    # ------------------------------------------------------------------
    def run_cycle(
        self,
        *,
        objective: str,
        agent_name: str,
        action: str,
        budget_scope: str,
        cost: float = 0.0,
        risk: str = "low",
        reversible: bool = True,
        tool: Optional[str] = None,
        params: Optional[dict] = None,
    ) -> TaskOutcome:
        """DECIDE + ACT (+ escalate) for a single delegated task.

        Records a `decision` memory either way, so every important call is
        traceable to evidence, per section 27.
        """
        if self.kill_switch_engaged:
            return self._deny(
                objective, agent_name, action, f"kill switch engaged: {self.kill_switch_reason or 'no reason given'}"
            )

        # UNDERSTAND: is this agent even known to the control plane?
        if self.registry.get_instance(agent_name) is None:
            return self._deny(objective, agent_name, action, "agent not registered")

        # DECIDE: permission check (least privilege, deny-by-default)
        try:
            self.permissions.require_action(agent_name, action)
            if tool:
                self.permissions.require_tool(agent_name, tool)
        except PermissionDeniedError as exc:
            return self._deny(objective, agent_name, action, str(exc))

        # DECIDE: does this need a human? (section 12 — high-risk/irreversible)
        if risk in REQUIRES_APPROVAL_RISKS or not reversible:
            from datetime import datetime, timedelta, timezone

            request = self.approvals.submit(
                ApprovalRequest(
                    action=action,
                    agent=agent_name,
                    reason=objective,
                    evidence=f"requested by orchestrator for objective: {objective}",
                    impact=f"risk={risk}, reversible={reversible}",
                    cost=cost,
                    risk=risk,
                    reversible=reversible,
                    proposal=f"run '{action}' via agent '{agent_name}'",
                    deadline=datetime.now(timezone.utc) + timedelta(seconds=self.approval_ttl_seconds),
                )
            )
            request.metadata = {"params": params or {}, "budget_scope": budget_scope}
            self._publish(
                "action.pending_approval",
                {"agent": agent_name, "action": action, "risk": risk, "approval_request_id": request.id},
            )
            self.brain.record(
                MemoryRecord(
                    kind=MemoryKind.DECISION,
                    content=f"Escalated '{action}' ({objective}) to human approval: risk={risk}, reversible={reversible}",
                    source="orchestrator",
                    confidence=Confidence.FACT,
                    tags=("approval", agent_name),
                )
            )
            return TaskOutcome(
                status=TaskStatus.PENDING_APPROVAL,
                approval_request_id=request.id,
                detail="requires human approval before execution",
            )

        return self._execute(objective, agent_name, action, budget_scope, cost, params)

    def approve_and_execute(
        self,
        request_id: str,
        *,
        decided_by: str,
        objective: str,
        budget_scope: Optional[str] = None,
        note: str = "",
    ) -> TaskOutcome:
        """Human approves a pending request; only then does the agent run.

        `budget_scope` and the original call's `params` are read back from the
        request itself (recorded at submission time) when not passed here
        explicitly, so the caller does not need to remember them across the
        approval round-trip.
        """
        request = self.approvals.decide(request_id, approve=True, decided_by=decided_by, note=note)
        stored = request.metadata or {}
        outcome = self._execute(
            objective,
            request.agent,
            request.action,
            budget_scope or stored.get("budget_scope", "default"),
            request.cost,
            stored.get("params"),
        )
        self.approvals.mark_executed(request_id, success=outcome.status == TaskStatus.EXECUTED)
        return outcome

    def reject(self, request_id: str, *, decided_by: str, note: str = "") -> ApprovalRequest:
        return self.approvals.decide(request_id, approve=False, decided_by=decided_by, note=note)

    # ------------------------------------------------------------------
    # Kill switch
    # ------------------------------------------------------------------
    def engage_kill_switch(self, reason: str, by: str = "human") -> None:
        self.kill_switch_engaged = True
        self.kill_switch_reason = reason
        self._publish("kill_switch.engaged", {"reason": reason, "by": by})
        self.brain.record(
            MemoryRecord(
                kind=MemoryKind.DECISION,
                content=f"Kill switch ENGAGED by {by}: {reason}. No new actions will be accepted.",
                source=by,
                confidence=Confidence.FACT,
                tags=("kill_switch",),
            )
        )

    def disengage_kill_switch(self, by: str = "human") -> None:
        self.kill_switch_engaged = False
        self._publish("kill_switch.disengaged", {"by": by})
        self.brain.record(
            MemoryRecord(
                kind=MemoryKind.DECISION,
                content=f"Kill switch DISENGAGED by {by}. New actions may be accepted again.",
                source=by,
                confidence=Confidence.FACT,
                tags=("kill_switch",),
            )
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _execute(
        self,
        objective: str,
        agent_name: str,
        action: str,
        budget_scope: str,
        cost: float,
        params: Optional[dict] = None,
    ) -> TaskOutcome:
        agent: Agent = self.registry.get_instance(agent_name)

        try:
            if cost > 0:
                self.budget.reserve(budget_scope, cost)
        except BudgetExceededError as exc:
            self._publish("action.failed", {"agent": agent_name, "action": action, "reason": "budget_exceeded"})
            self.brain.record(
                MemoryRecord(
                    kind=MemoryKind.DECISION,
                    content=f"Blocked '{action}' ({objective}) — budget exceeded: {exc}",
                    source="orchestrator",
                    confidence=Confidence.FACT,
                    tags=("budget", agent_name),
                )
            )
            return TaskOutcome(status=TaskStatus.FAILED, detail=str(exc))

        # ACT
        result = agent.execute({"objective": objective, "action": action, "params": params or {}})

        if not result.success:
            if cost > 0:
                self.budget.release_reservation(budget_scope, cost)
            self.brain.record(
                MemoryRecord(
                    kind=MemoryKind.EPISODIC,
                    content=f"Agent '{agent_name}' failed action '{action}': {result.error}",
                    source=agent_name,
                    confidence=Confidence.FACT,
                    tags=("agent_failed", agent_name),
                )
            )
            self._publish("action.failed", {"agent": agent_name, "action": action, "reason": result.error})
            return TaskOutcome(status=TaskStatus.FAILED, agent_result=result, detail=result.error)

        # QA gate — nothing downstream trusts raw agent output, even on success
        qa_result = self.qa_agent.review(result)
        if not qa_result.success:
            if cost > 0:
                self.budget.release_reservation(budget_scope, cost)
            self.brain.record(
                MemoryRecord(
                    kind=MemoryKind.EPISODIC,
                    content=f"QA rejected result of '{action}' by {agent_name}: {qa_result.error}",
                    source="qa_agent",
                    confidence=Confidence.FACT,
                    tags=("qa_rejected", agent_name),
                )
            )
            self._publish("action.qa_rejected", {"agent": agent_name, "action": action, "reason": qa_result.error})
            return TaskOutcome(status=TaskStatus.QA_REJECTED, agent_result=result, detail=qa_result.error)

        # MEASURE + LEARN
        if cost > 0:
            self.budget.spend(budget_scope, cost, from_reservation=True)

        self.brain.record(
            MemoryRecord(
                kind=MemoryKind.EPISODIC,
                content=f"Executed '{action}' via {agent_name} for objective: {objective}. Output: {result.output}",
                source=agent_name,
                confidence=Confidence.FACT,
                tags=("executed", agent_name),
                metadata={"cost": cost},
            )
        )
        self._publish("action.executed", {"agent": agent_name, "action": action, "cost": cost})
        return TaskOutcome(status=TaskStatus.EXECUTED, agent_result=result)

    def _deny(self, objective: str, agent_name: str, action: str, reason: str) -> TaskOutcome:
        self._publish("action.denied", {"agent": agent_name, "action": action, "reason": reason})
        self.brain.record(
            MemoryRecord(
                kind=MemoryKind.DECISION,
                content=f"Denied '{action}' ({objective}) for agent '{agent_name}': {reason}",
                source="orchestrator",
                confidence=Confidence.FACT,
                tags=("denied", agent_name),
            )
        )
        return TaskOutcome(status=TaskStatus.DENIED, detail=reason)
