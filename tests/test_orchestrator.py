import pytest

from aicommerce.agents.stubs import EchoAgent
from aicommerce.brain.models import MemoryKind
from aicommerce.brain.store import CompanyBrain
from aicommerce.ceo.orchestrator import Orchestrator, TaskStatus
from aicommerce.control_plane.approvals import ApprovalQueue
from aicommerce.control_plane.budget import BudgetGuard
from aicommerce.control_plane.permissions import PermissionManager, Role
from aicommerce.control_plane.registry import AgentRegistry, AgentSpec


def build_orchestrator():
    registry = AgentRegistry()
    permissions = PermissionManager()
    budget = BudgetGuard()
    approvals = ApprovalQueue()
    brain = CompanyBrain(":memory:")

    agent = EchoAgent(name="research", cost_per_task=5.0)
    registry.register(AgentSpec(name="research", mission="research markets"), agent)

    permissions.define_role(Role(name="research_role", allowed_actions=frozenset({"research_market"})))
    permissions.assign_role("research", "research_role")

    budget.set_budget("research", 100.0)

    orchestrator = Orchestrator(registry, permissions, budget, approvals, brain)
    return orchestrator, registry, permissions, budget, approvals, brain


def test_low_risk_task_executes_immediately_and_spends_budget():
    orchestrator, *_, budget, _, brain = build_orchestrator()

    outcome = orchestrator.run_cycle(
        objective="find 3 trending kitchen gadgets",
        agent_name="research",
        action="research_market",
        budget_scope="research",
        cost=5.0,
        risk="low",
    )

    assert outcome.status == TaskStatus.EXECUTED
    assert outcome.agent_result.success is True
    assert budget.status("research")["spent"] == 5.0

    episodes = brain.query(kind=MemoryKind.EPISODIC)
    assert any("Executed" in e.content for e in episodes)


def test_unregistered_agent_is_denied():
    orchestrator, *_ = build_orchestrator()

    outcome = orchestrator.run_cycle(
        objective="do something",
        agent_name="ghost",
        action="anything",
        budget_scope="research",
    )

    assert outcome.status == TaskStatus.DENIED


def test_action_without_permission_is_denied():
    orchestrator, *_ = build_orchestrator()

    outcome = orchestrator.run_cycle(
        objective="delete all customer data",
        agent_name="research",
        action="delete_customers",  # not in research_role
        budget_scope="research",
    )

    assert outcome.status == TaskStatus.DENIED


def test_budget_exceeded_fails_without_executing_agent():
    orchestrator, registry, *_ , budget, _, brain = build_orchestrator()

    outcome = orchestrator.run_cycle(
        objective="expensive research",
        agent_name="research",
        action="research_market",
        budget_scope="research",
        cost=500.0,  # exceeds the $100 budget
        risk="low",
    )

    assert outcome.status == TaskStatus.FAILED
    assert budget.status("research")["spent"] == 0.0


def test_high_risk_task_requires_approval_and_does_not_execute_yet():
    orchestrator, *_ = build_orchestrator()

    outcome = orchestrator.run_cycle(
        objective="launch a paid ad campaign",
        agent_name="research",
        action="research_market",
        budget_scope="research",
        cost=5.0,
        risk="high",
    )

    assert outcome.status == TaskStatus.PENDING_APPROVAL
    assert outcome.approval_request_id is not None


def test_approving_a_pending_request_executes_it():
    orchestrator, *_ = build_orchestrator()

    outcome = orchestrator.run_cycle(
        objective="launch a paid ad campaign",
        agent_name="research",
        action="research_market",
        budget_scope="research",
        cost=5.0,
        risk="high",
    )
    assert outcome.status == TaskStatus.PENDING_APPROVAL

    final = orchestrator.approve_and_execute(
        outcome.approval_request_id,
        decided_by="jean",
        objective="launch a paid ad campaign",
        budget_scope="research",
    )

    assert final.status == TaskStatus.EXECUTED


def test_irreversible_low_risk_action_still_requires_approval():
    orchestrator, *_ = build_orchestrator()

    outcome = orchestrator.run_cycle(
        objective="permanently delete a product listing",
        agent_name="research",
        action="research_market",
        budget_scope="research",
        cost=0.0,
        risk="low",
        reversible=False,
    )

    assert outcome.status == TaskStatus.PENDING_APPROVAL


def test_qa_rejection_releases_reserved_budget():
    registry = AgentRegistry()
    permissions = PermissionManager()
    budget = BudgetGuard()
    approvals = ApprovalQueue()
    brain = CompanyBrain(":memory:")

    class BrokenAgent(EchoAgent):
        def execute(self, task):
            from aicommerce.agents.base import AgentResult
            return AgentResult(success=True, output="did something", evidence="")  # no evidence -> QA rejects

    agent = BrokenAgent(name="research", cost_per_task=10.0)
    registry.register(AgentSpec(name="research", mission="m"), agent)
    permissions.define_role(Role(name="r", allowed_actions=frozenset({"research_market"})))
    permissions.assign_role("research", "r")
    budget.set_budget("research", 100.0)

    orchestrator = Orchestrator(registry, permissions, budget, approvals, brain)
    outcome = orchestrator.run_cycle(
        objective="test",
        agent_name="research",
        action="research_market",
        budget_scope="research",
        cost=10.0,
        risk="low",
    )

    assert outcome.status == TaskStatus.QA_REJECTED
    assert budget.status("research")["spent"] == 0.0
    assert budget.status("research")["reserved"] == 0.0
