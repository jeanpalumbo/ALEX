"""CEO Status Report — master plan Fase 3.

This module assembles a status report from real, currently-available data
sources (BudgetGuard, AgentRegistry, ApprovalQueue, EventBus, Company Brain,
ReadinessPreflight). It deliberately does NOT invent per-task status values
(COMPLETED/IN_PROGRESS/BLOCKED/PLANNED/FAILED/NOT_STARTED) for work items,
because there is no task/objective-tracking system yet (that's Fase 7) --
doing so here would be exactly the kind of fabricated status the master
directive prohibits ("nunca afirmar una acción sin evidencia real"). What it
reports is real: executed/denied/failed actions (from the EventBus), pending
approvals, budget, decisions, and preflight state, windowed by period.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional

PERIOD_WINDOWS = {
    "daily": timedelta(hours=24),
    "eod": timedelta(hours=24),  # "since this time yesterday" -- no daily-cutoff scheduler yet
    "executive": timedelta(days=7),
}


@dataclass
class StatusReport:
    generated_at: datetime
    period: str
    window_start: datetime
    preflight_result: str
    preflight_reasons: list[str]
    objective: Optional[str]
    current_task: Optional[str]
    actions_executed: list[dict]
    actions_blocked: list[dict]
    pending_approvals: list[dict]
    budgets: list[dict]
    agents: list[str]
    recent_decisions: list[dict]
    experiments: list[dict]
    problems: list[str]
    risks: list[str]
    decisions_requiring_owner: list[dict]

    def to_dict(self) -> dict:
        return {
            "generated_at": self.generated_at.isoformat(),
            "period": self.period,
            "window_start": self.window_start.isoformat(),
            "estado": self.preflight_result,
            "objetivo": self.objective,
            "tarea_actual": self.current_task,
            "acciones_ejecutadas": self.actions_executed,
            "acciones_bloqueadas": self.actions_blocked,
            "pendientes_de_jean": self.pending_approvals,
            "presupuesto": self.budgets,
            "agentes": self.agents,
            "decisiones_recientes": self.recent_decisions,
            "experimentos": self.experiments,
            "problemas": self.problems,
            "riesgos": self.risks,
            "decisiones_que_requieren_owner": self.decisions_requiring_owner,
        }


def generate_status_report(orchestrator, ceo_state, preflight_report, registry=None, period: str = "daily") -> StatusReport:
    """Build a report from explicit control-plane pieces rather than a
    duck-typed "system" object, so both `aicommerce.bootstrap.System` (the
    web server) and `CEOTools` (which only holds an orchestrator + state,
    not the whole System) can call this the same way."""
    if period not in PERIOD_WINDOWS:
        period = "daily"
    now = datetime.now(timezone.utc)
    window_start = now - PERIOD_WINDOWS[period]

    registry = registry or orchestrator.registry
    all_events = orchestrator.events.history(limit=500) if orchestrator.events else []
    windowed_events = [e for e in all_events if e.timestamp >= window_start]

    executed = [
        {"type": e.type, "payload": e.payload, "timestamp": e.timestamp.isoformat()}
        for e in windowed_events if e.type == "action.executed"
    ]
    blocked = [
        {"type": e.type, "payload": e.payload, "timestamp": e.timestamp.isoformat()}
        for e in windowed_events if e.type in ("action.denied", "action.failed", "action.qa_rejected")
    ]

    pending = [
        {
            "id": r.id, "action": r.action, "agent": r.agent, "reason": r.reason,
            "cost": r.cost, "risk": r.risk, "reversible": r.reversible,
        }
        for r in orchestrator.approvals.pending()
    ]

    from aicommerce.brain.models import MemoryKind

    decisions = [
        {"content": r.content, "confidence": r.confidence.value, "timestamp": r.timestamp.isoformat()}
        for r in orchestrator.brain.query(kind=MemoryKind.DECISION, limit=100)
        if r.timestamp >= window_start
    ]
    experiments = [
        {"content": r.content, "confidence": r.confidence.value, "timestamp": r.timestamp.isoformat()}
        for r in orchestrator.brain.query(kind=MemoryKind.EXPERIMENT, limit=50)
        if r.timestamp >= window_start
    ]

    problems: list[str] = []
    if ceo_state.last_error:
        problems.append(f"CEO last_error: {ceo_state.last_error}")
    if preflight_report.result != "ready":
        problems.extend(preflight_report.reasons)
    if orchestrator.kill_switch_engaged:
        problems.append(f"Kill switch engaged: {orchestrator.kill_switch_reason}")
    for e in blocked[-10:]:
        problems.append(f"{e['type']}: {e['payload']}")

    risks: list[str] = []
    if preflight_report.result != "ready":
        risks.append(f"Preflight is {preflight_report.result}, not ready.")
    if pending:
        risks.append(f"{len(pending)} action(s) waiting on human approval.")

    return StatusReport(
        generated_at=now,
        period=period,
        window_start=window_start,
        preflight_result=preflight_report.result.value,
        preflight_reasons=preflight_report.reasons,
        objective=ceo_state.objective,
        current_task=ceo_state.current_task,
        actions_executed=executed,
        actions_blocked=blocked,
        pending_approvals=pending,
        budgets=orchestrator.budget.all_status(),
        agents=[s.name for s in registry.list_agents()],
        recent_decisions=decisions,
        experiments=experiments,
        problems=problems,
        risks=risks,
        decisions_requiring_owner=pending,
    )
