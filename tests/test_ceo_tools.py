from datetime import timedelta

from aicommerce.agents.stubs import EchoAgent
from aicommerce.brain.store import CompanyBrain
from aicommerce.ceo.orchestrator import Orchestrator
from aicommerce.ceo.state import CEOState
from aicommerce.ceo.tools import CEOTools
from aicommerce.control_plane.approvals import ApprovalQueue
from aicommerce.control_plane.budget import BudgetGuard
from aicommerce.control_plane.events import EventBus
from aicommerce.control_plane.permissions import PermissionManager, Role
from aicommerce.control_plane.preflight import PreflightResult, ReadinessPreflight
from aicommerce.control_plane.registry import AgentRegistry, AgentSpec
from aicommerce.control_plane.scheduler import Scheduler


def build(events=None, scheduler=None, preflight_provider=None):
    registry = AgentRegistry()
    permissions = PermissionManager()
    budget = BudgetGuard()
    approvals = ApprovalQueue()
    brain = CompanyBrain(":memory:")

    registry.register(AgentSpec(name="research", mission="research"), EchoAgent("research"))
    permissions.define_role(Role(name="r", allowed_actions=frozenset({"do_research", "do_launch"})))
    permissions.assign_role("research", "r")
    budget.set_budget("research", 50.0)

    orchestrator = Orchestrator(registry, permissions, budget, approvals, brain, events=events)
    tools = CEOTools(orchestrator, CEOState(), scheduler=scheduler, preflight_provider=preflight_provider)
    return tools, orchestrator


def test_get_company_state_reflects_real_registry_and_budget():
    tools, orchestrator = build()
    state = tools.dispatch("get_company_state", {})
    assert "research" in state["agents"]
    assert any(b["scope"] == "research" for b in state["budgets"])
    assert state["pending_approvals"] == 0


def test_record_and_query_memory_round_trip():
    tools, _ = build()
    tools.dispatch("record_memory", {"kind": "semantic", "content": "core product is X", "confidence": "fact"})
    result = tools.dispatch("query_memory", {"kind": "semantic"})
    assert any(r["content"] == "core product is X" for r in result["records"])


def test_record_memory_rejects_institutional_kind_via_schema_but_not_dispatch():
    # dispatch itself doesn't enforce the schema (the LLM tool schema does),
    # but MemoryKind("institutional") must still be a valid kind for direct writes
    # made by trusted code paths, not the CEO's own tool call.
    tools, _ = build()
    result = tools.dispatch("record_memory", {"kind": "institutional", "content": "x", "confidence": "fact"})
    assert "recorded_id" in result


def test_set_objective_updates_state_and_brain():
    tools, orchestrator = build()
    tools.dispatch("set_objective", {"objective": "grow revenue 10%"})
    assert tools.state.objective == "grow revenue 10%"
    records = orchestrator.brain.query(tags=["objective"])
    assert any("grow revenue 10%" in r.content for r in records)


def test_propose_action_low_risk_executes_immediately():
    tools, orchestrator = build()
    result = tools.dispatch(
        "propose_action",
        {"agent_name": "research", "action": "do_research", "risk": "low", "reversible": True, "cost": 0},
    )
    assert result["status"] == "executed"
    assert result["success"] is True


def test_propose_action_high_risk_requires_approval():
    tools, orchestrator = build()
    result = tools.dispatch(
        "propose_action",
        {"agent_name": "research", "action": "do_launch", "risk": "high", "reversible": False, "cost": 10},
    )
    assert result["status"] == "pending_approval"
    assert "approval_request_id" in result
    assert len(orchestrator.approvals.pending()) == 1


def test_propose_action_denied_for_unpermitted_action():
    tools, orchestrator = build()
    result = tools.dispatch(
        "propose_action",
        {"agent_name": "research", "action": "delete_everything", "risk": "low"},
    )
    assert result["status"] == "denied"


def test_dispatch_unknown_tool_returns_error_not_exception():
    tools, _ = build()
    result = tools.dispatch("not_a_real_tool", {})
    assert "error" in result


def test_get_preflight_without_provider_returns_explicit_error():
    tools, _ = build()
    result = tools.dispatch("get_preflight", {})
    assert "error" in result


def test_get_preflight_with_provider_reflects_real_report():
    pf = ReadinessPreflight()
    pf.add_check("thing", lambda: False, on_fail=PreflightResult.DEGRADED, reason="thing is off")
    tools, _ = build(preflight_provider=pf.run)

    result = tools.dispatch("get_preflight", {})
    assert result["result"] == "degraded"
    assert "thing" in result["failed_checks"]
    assert "thing is off" in result["reasons"]


def test_get_scheduler_status_without_scheduler_returns_explicit_error():
    tools, _ = build()
    result = tools.dispatch("get_scheduler_status", {})
    assert "error" in result


def test_get_scheduler_status_with_real_scheduler():
    scheduler = Scheduler()
    scheduler.add_job("heartbeat", timedelta(minutes=15), lambda: None)
    tools, _ = build(scheduler=scheduler)

    result = tools.dispatch("get_scheduler_status", {})
    assert result["jobs"][0]["name"] == "heartbeat"
    assert result["jobs"][0]["interval_seconds"] == 900.0
    assert result["jobs"][0]["last_run"] is None


def test_get_recent_events_reflects_real_orchestrator_activity():
    events = EventBus()
    tools, orchestrator = build(events=events)

    tools.dispatch("propose_action", {"agent_name": "research", "action": "do_research", "risk": "low"})

    result = tools.dispatch("get_recent_events", {})
    types = [e["type"] for e in result["events"]]
    assert "action.executed" in types


def test_get_recent_events_filters_by_type():
    events = EventBus()
    tools, orchestrator = build(events=events)
    tools.dispatch("propose_action", {"agent_name": "research", "action": "do_research", "risk": "low"})
    tools.dispatch("propose_action", {"agent_name": "research", "action": "delete_everything", "risk": "low"})

    result = tools.dispatch("get_recent_events", {"event_type": "action.denied"})
    assert len(result["events"]) == 1
    assert result["events"][0]["type"] == "action.denied"


def test_generate_status_report_tool_without_preflight_provider_errors():
    tools, _ = build()
    result = tools.dispatch("generate_status_report", {})
    assert "error" in result


def test_generate_status_report_tool_reflects_real_state():
    from aicommerce.control_plane.preflight import ReadinessPreflight

    pf = ReadinessPreflight()
    tools, orchestrator = build(events=EventBus(), preflight_provider=pf.run)

    tools.dispatch("propose_action", {"agent_name": "research", "action": "do_research", "risk": "low"})
    result = tools.dispatch("generate_status_report", {"period": "daily"})

    assert result["estado"] == "ready"
    assert len(result["acciones_ejecutadas"]) == 1


def test_finance_is_a_default_voter_for_technical_votes():
    tools, _ = build()
    assert "finance" in tools.voter_agent_names


def test_record_content_brief_writes_a_structured_pending_brief():
    tools, orchestrator = build()

    result = tools.dispatch(
        "record_content_brief",
        {
            "asset_type": "landing_page",
            "product": "thermal mug",
            "key_message": "keeps drinks hot for 12 hours",
            "target_audience": "office workers",
            "approval_reference": "approval-123",
        },
    )

    assert result["status"] == "pending_execution"
    assert result["asset_type"] == "landing_page"

    from aicommerce.brain.models import MemoryKind

    records = orchestrator.brain.query(kind=MemoryKind.DECISION, tags=["content_brief"])
    assert len(records) == 1
    assert records[0].metadata["product"] == "thermal mug"
    assert records[0].metadata["status"] == "pending_execution"
    assert "approval-123" in records[0].content


def test_record_content_brief_without_optional_fields_still_works():
    tools, orchestrator = build()
    result = tools.dispatch(
        "record_content_brief",
        {"asset_type": "flyer", "product": "mug", "key_message": "stays hot"},
    )
    assert result["status"] == "pending_execution"
    assert result["target_audience"] == ""


def test_create_task_without_taskboard_wired_returns_error_not_crash():
    tools, _ = build()  # build() doesn't pass tasks= -- tools.tasks is None
    result = tools.dispatch("create_task", {"objective": "obj", "title": "t", "owner": "research"})
    assert "error" in result


def test_create_update_and_list_task_round_trip_through_dispatch():
    from aicommerce.brain.tasks import TaskBoard

    tools, _ = build()
    tools.tasks = TaskBoard()

    created = tools.dispatch(
        "create_task", {"objective": "validate product X", "title": "run demand research", "owner": "research"}
    )
    assert created["status"] == "pending"
    task_id = created["id"]

    updated = tools.dispatch(
        "update_task_status", {"task_id": task_id, "status": "in_progress", "notes": "started"}
    )
    assert updated["status"] == "in_progress"
    assert updated["notes"] == "started"

    listed = tools.dispatch("list_tasks", {"objective": "validate product X"})
    assert len(listed["tasks"]) == 1
    assert listed["tasks"][0]["id"] == task_id


def test_update_task_status_on_done_task_returns_error_not_crash():
    from aicommerce.brain.tasks import TaskBoard

    tools, _ = build()
    tools.tasks = TaskBoard()
    created = tools.dispatch("create_task", {"objective": "obj", "title": "t", "owner": "research"})
    tools.dispatch("update_task_status", {"task_id": created["id"], "status": "done"})

    result = tools.dispatch("update_task_status", {"task_id": created["id"], "status": "in_progress"})
    assert "error" in result
