from datetime import datetime, timedelta, timezone

from aicommerce.agents.stubs import EchoAgent
from aicommerce.brain.store import CompanyBrain
from aicommerce.ceo.orchestrator import Orchestrator, TaskStatus
from aicommerce.control_plane.approvals import ApprovalQueue
from aicommerce.control_plane.budget import BudgetGuard
from aicommerce.control_plane.permissions import PermissionManager, Role
from aicommerce.control_plane.registry import AgentRegistry, AgentSpec


def build_orchestrator(approval_ttl_seconds=1800):
    registry = AgentRegistry()
    permissions = PermissionManager()
    budget = BudgetGuard()
    approvals = ApprovalQueue()
    brain = CompanyBrain(":memory:")

    registry.register(AgentSpec(name="research", mission="m"), EchoAgent("research"))
    permissions.define_role(Role(name="r", allowed_actions=frozenset({"do_research"})))
    permissions.assign_role("research", "r")
    budget.set_budget("research", 50.0)

    return Orchestrator(registry, permissions, budget, approvals, brain, approval_ttl_seconds=approval_ttl_seconds)


def test_kill_switch_blocks_new_low_risk_actions():
    orchestrator = build_orchestrator()
    orchestrator.engage_kill_switch("testing emergency stop", by="jean")

    outcome = orchestrator.run_cycle(
        objective="do something", agent_name="research", action="do_research", budget_scope="research"
    )

    assert outcome.status == TaskStatus.DENIED
    assert "kill switch" in outcome.detail


def test_kill_switch_blocks_high_risk_actions_before_approval_queue():
    orchestrator = build_orchestrator()
    orchestrator.engage_kill_switch("stop everything")

    outcome = orchestrator.run_cycle(
        objective="do something risky",
        agent_name="research",
        action="do_research",
        budget_scope="research",
        risk="high",
    )

    assert outcome.status == TaskStatus.DENIED
    assert len(orchestrator.approvals.pending()) == 0


def test_disengage_kill_switch_allows_actions_again():
    orchestrator = build_orchestrator()
    orchestrator.engage_kill_switch("temporary")
    orchestrator.disengage_kill_switch(by="jean")

    outcome = orchestrator.run_cycle(
        objective="do something", agent_name="research", action="do_research", budget_scope="research"
    )
    assert outcome.status == TaskStatus.EXECUTED


def test_kill_switch_transitions_are_recorded_in_brain():
    orchestrator = build_orchestrator()
    orchestrator.engage_kill_switch("audit test")
    orchestrator.disengage_kill_switch()

    from aicommerce.brain.models import MemoryKind

    records = orchestrator.brain.query(kind=MemoryKind.DECISION, tags=["kill_switch"])
    assert len(records) == 2
    assert "ENGAGED" in records[1].content  # most recent first
    assert "DISENGAGED" in records[0].content


def test_approval_request_gets_a_deadline_and_expires():
    orchestrator = build_orchestrator(approval_ttl_seconds=1)
    outcome = orchestrator.run_cycle(
        objective="risky", agent_name="research", action="do_research", budget_scope="research", risk="high"
    )
    request = orchestrator.approvals.get(outcome.approval_request_id)
    assert request.deadline is not None

    # force it into the past to simulate expiry without sleeping in a test
    request.deadline = datetime.now(timezone.utc) - timedelta(seconds=1)
    assert outcome.approval_request_id not in [r.id for r in orchestrator.approvals.pending()]


def test_profile_offline_blocks_shopify_even_with_credentials(monkeypatch):
    from aicommerce import config
    from aicommerce.agents.shopify_agent import ShopifyAgent

    monkeypatch.setattr(config, "PROFILE", "offline")
    agent = ShopifyAgent(store="shop.myshopify.com", token="shpat_real")

    assert agent.configured is True
    assert agent.operational is False

    result = agent.execute({"action": "read_products", "params": {}})
    assert result.success is False
    assert "PROFILE=offline" in result.error


def test_profile_sandbox_allows_shopify_calls_when_configured(monkeypatch):
    from unittest.mock import MagicMock, patch

    from aicommerce import config
    from aicommerce.agents.shopify_agent import ShopifyAgent

    monkeypatch.setattr(config, "PROFILE", "sandbox")
    agent = ShopifyAgent(store="shop.myshopify.com", token="shpat_real")
    assert agent.operational is True

    fake_response = MagicMock()
    fake_response.json.return_value = {"products": []}
    fake_response.raise_for_status.return_value = None
    with patch("aicommerce.agents.shopify_agent.requests.get", return_value=fake_response):
        result = agent.execute({"action": "read_products", "params": {}})
    assert result.success is True
