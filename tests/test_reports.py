from aicommerce.agents.stubs import EchoAgent
from aicommerce.brain.store import CompanyBrain
from aicommerce.ceo.orchestrator import Orchestrator
from aicommerce.ceo.state import CEOState
from aicommerce.control_plane.approvals import ApprovalQueue
from aicommerce.control_plane.budget import BudgetGuard
from aicommerce.control_plane.events import EventBus
from aicommerce.control_plane.permissions import PermissionManager, Role
from aicommerce.control_plane.preflight import PreflightResult, ReadinessPreflight
from aicommerce.control_plane.registry import AgentRegistry, AgentSpec
from aicommerce.reports import generate_status_report


def build():
    registry = AgentRegistry()
    permissions = PermissionManager()
    budget = BudgetGuard()
    approvals = ApprovalQueue()
    brain = CompanyBrain(":memory:")
    events = EventBus()

    registry.register(AgentSpec(name="research", mission="m"), EchoAgent("research"))
    permissions.define_role(Role(name="r", allowed_actions=frozenset({"do_research", "do_launch"})))
    permissions.assign_role("research", "r")
    budget.set_budget("research", 50.0)

    orchestrator = Orchestrator(registry, permissions, budget, approvals, brain, events=events)
    state = CEOState()
    return orchestrator, state, registry


def build_preflight(ready: bool = True):
    pf = ReadinessPreflight()
    if not ready:
        pf.add_check("thing", lambda: False, on_fail=PreflightResult.DEGRADED, reason="thing is broken")
    return pf


def test_report_reflects_real_executed_and_blocked_actions():
    orchestrator, state, registry = build()
    orchestrator.run_cycle(objective="test", agent_name="research", action="do_research", budget_scope="research")
    orchestrator.run_cycle(objective="test", agent_name="research", action="not_allowed", budget_scope="research")

    report = generate_status_report(orchestrator, state, build_preflight().run(), registry=registry)

    assert len(report.actions_executed) == 1
    assert len(report.actions_blocked) == 1
    assert report.preflight_result == "ready"


def test_report_lists_pending_approvals_as_decisions_requiring_owner():
    orchestrator, state, registry = build()
    outcome = orchestrator.run_cycle(
        objective="risky move", agent_name="research", action="do_launch",
        budget_scope="research", risk="high", cost=5.0,
    )

    report = generate_status_report(orchestrator, state, build_preflight().run(), registry=registry)

    assert len(report.pending_approvals) == 1
    assert report.pending_approvals[0]["id"] == outcome.approval_request_id
    assert report.decisions_requiring_owner == report.pending_approvals
    assert any("waiting on human approval" in r for r in report.risks)


def test_report_surfaces_preflight_problems_and_risks():
    orchestrator, state, registry = build()
    report = generate_status_report(orchestrator, state, build_preflight(ready=False).run(), registry=registry)

    assert report.preflight_result == "degraded"
    assert "thing is broken" in report.problems
    assert any("not ready" in r for r in report.risks)


def test_report_surfaces_kill_switch_as_a_problem():
    orchestrator, state, registry = build()
    orchestrator.engage_kill_switch("incident", by="jean")

    report = generate_status_report(orchestrator, state, build_preflight().run(), registry=registry)

    assert any("Kill switch engaged" in p for p in report.problems)


def test_report_never_fabricates_task_status_fields():
    """The master directive explicitly forbids inventing completion status
    without evidence -- confirm the report dict has no such fabricated key."""
    orchestrator, state, registry = build()
    report = generate_status_report(orchestrator, state, build_preflight().run(), registry=registry)
    d = report.to_dict()
    for forbidden in ("status", "task_status", "completion"):
        assert forbidden not in d


def test_to_dict_is_json_serializable():
    import json

    orchestrator, state, registry = build()
    report = generate_status_report(orchestrator, state, build_preflight().run(), registry=registry)
    json.dumps(report.to_dict())  # must not raise
