"""Smoke tests for wiring the whole system together. No network calls are
made here — CEOModel just checks whether a key string is present, and the
Shopify agent isn't invoked unless a test calls it."""
import importlib

from aicommerce.bootstrap import System


def test_system_constructs_and_registers_shopify_agent(tmp_path, monkeypatch):
    from aicommerce import config

    monkeypatch.setattr(config, "BRAIN_DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)

    system = System()

    assert system.registry.get_instance("shopify") is not None
    assert system.permissions.can_act("shopify", "read_products") is True
    assert system.permissions.can_act("shopify", "create_product") is True  # permitted, but still gated by risk/approval
    assert "daily" in system.budget.scopes()
    assert "shopify" in system.budget.scopes()
    assert "ceo_llm" in system.budget.scopes()


def test_preflight_reports_degraded_when_shopify_not_configured(tmp_path, monkeypatch):
    from aicommerce import config

    monkeypatch.setattr(config, "BRAIN_DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "SHOPIFY_STORE", "")
    monkeypatch.setattr(config, "SHOPIFY_TOKEN", "")

    system = System()
    report = system.preflight.run()

    assert "shopify_configured" in report.failed_checks


def test_shopify_write_action_via_orchestrator_requires_approval(tmp_path, monkeypatch):
    from aicommerce import config

    monkeypatch.setattr(config, "BRAIN_DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)

    system = System()
    outcome = system.orchestrator.run_cycle(
        objective="add a new product",
        agent_name="shopify",
        action="create_product",
        budget_scope="shopify",
        cost=0.0,
        risk="high",
        reversible=False,
        params={"product_data": {"title": "Test"}},
    )

    assert outcome.status.value == "pending_approval"
    assert len(system.approvals.pending()) == 1


def test_shopify_write_cannot_bypass_approval_by_claiming_low_risk(tmp_path, monkeypatch):
    """Code-level backstop: even if the caller (e.g. a manipulated CEO tool
    call) claims risk='low', reversible=True for a Shopify write action, the
    Orchestrator must still force it to PENDING_APPROVAL because the write
    action itself is in ShopifyAgent's high_risk_actions."""
    from aicommerce import config

    monkeypatch.setattr(config, "BRAIN_DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)

    system = System()
    outcome = system.orchestrator.run_cycle(
        objective="sneaky low-risk claim",
        agent_name="shopify",
        action="delete_product",
        budget_scope="shopify",
        cost=0.0,
        risk="low",       # lying about risk
        reversible=True,  # lying about reversibility
        params={"product_id": 1},
    )

    assert outcome.status.value == "pending_approval"
    assert len(system.approvals.pending()) == 1
    assert system.approvals.pending()[0].risk == "critical"


def test_engineering_agent_registered_with_merge_locked_behind_approval(tmp_path, monkeypatch):
    from aicommerce import config

    monkeypatch.setattr(config, "BRAIN_DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)

    system = System()
    assert system.registry.get_instance("engineering") is not None
    assert system.permissions.can_act("engineering", "read_file") is True
    assert system.permissions.can_act("engineering", "write_file") is True
    assert system.permissions.can_act("engineering", "merge_to_master") is True  # permitted, but still gated

    outcome = system.orchestrator.run_cycle(
        objective="ship a fix",
        agent_name="engineering",
        action="merge_to_master",
        budget_scope="engineering",
        risk="low",       # claiming low risk
        reversible=True,  # claiming reversible
        params={"branch": "ceo-sandbox/whatever"},
    )
    assert outcome.status.value == "pending_approval"
    assert system.approvals.pending()[0].risk == "critical"


def test_engineering_read_action_executes_immediately_without_approval(tmp_path, monkeypatch):
    from aicommerce import config

    monkeypatch.setattr(config, "BRAIN_DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)

    system = System()
    outcome = system.orchestrator.run_cycle(
        objective="inspect repo",
        agent_name="engineering",
        action="current_branch",
        budget_scope="engineering",
        risk="low",
    )
    assert outcome.status.value == "executed"


def test_research_persona_agent_registered_with_own_budget(tmp_path, monkeypatch):
    from aicommerce import config

    monkeypatch.setattr(config, "BRAIN_DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)

    system = System()
    assert system.registry.get_instance("research") is not None
    assert system.registry.get_spec("research").mission  # non-empty, real persona mission
    assert "research" in system.budget.scopes()
    assert system.permissions.can_act("research", "think") is True
    assert system.permissions.can_act("research", "delete_everything") is False


def test_all_persona_agents_registered_with_their_own_budgets(tmp_path, monkeypatch):
    """Jean's explicit ask: every employee configured the same way -- not
    just Elena. Confirms Marcus (store_ops) and Priya (engineering_lead)
    are wired up exactly like Elena (research)."""
    from aicommerce import config

    monkeypatch.setattr(config, "BRAIN_DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)

    system = System()
    for name in ("research", "store_ops", "engineering_lead", "finance"):
        assert system.registry.get_instance(name) is not None, f"{name} not registered"
        assert system.registry.get_spec(name).mission
        assert name in system.budget.scopes()
        assert system.permissions.can_act(name, "think") is True

    # each persona agent has its own ModelRouter/CEOModel instance, not a
    # shared one -- confirms they're independent actors, not aliases
    assert system.research_agent.router is not system.store_ops_agent.router
    assert system.store_ops_agent.router is not system.engineering_lead_agent.router
    assert system.finance_agent.router is not system.research_agent.router


def test_ceo_has_its_own_named_identity(tmp_path, monkeypatch):
    from aicommerce import config

    monkeypatch.setattr(config, "BRAIN_DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)

    system = System()
    from aicommerce.ceo.service import SYSTEM_PROMPT

    assert "Alex Rivera" in SYSTEM_PROMPT
    assert "pending_approval" in SYSTEM_PROMPT  # operational specifics still present on top


def test_opus_router_wired_with_its_own_budget(tmp_path, monkeypatch):
    from aicommerce import config

    monkeypatch.setattr(config, "BRAIN_DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)

    system = System()
    assert system.opus_router is not None
    assert system.opus_router.model.model == config.OPUS_MODEL
    assert "opus_review" in system.budget.scopes()
    assert system.ceo.tools.opus_router is system.opus_router


def test_persona_autonomy_disabled_by_default(tmp_path, monkeypatch):
    from aicommerce import config

    monkeypatch.setattr(config, "BRAIN_DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "AUTONOMOUS_PERSONA_TICKS", False)

    system = System()
    job_names = {j.name for j in system.scheduler.jobs()}
    assert "autonomous_research_tick" not in job_names
    assert "autonomous_store_ops_tick" not in job_names
    assert "autonomous_engineering_lead_tick" not in job_names


def test_persona_autonomy_when_enabled_registers_one_job_per_persona_with_separate_budgets(tmp_path, monkeypatch):
    from aicommerce import config

    monkeypatch.setattr(config, "BRAIN_DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "AUTONOMOUS_PERSONA_TICKS", True)
    monkeypatch.setattr(config, "AUTONOMOUS_PERSONA_TICK_INTERVAL_SECONDS", 999999)

    system = System()
    job_names = {j.name for j in system.scheduler.jobs()}
    assert {"autonomous_research_tick", "autonomous_store_ops_tick", "autonomous_engineering_lead_tick"} <= job_names


def test_persona_autonomous_tick_actually_goes_through_the_orchestrator(tmp_path, monkeypatch):
    """Not a mock of the scheduling -- runs the real job function and checks
    the real budget/brain effects, same as a CEO-delegated 'think' call."""
    from aicommerce import config
    from aicommerce.ceo.llm import LLMResponse

    monkeypatch.setattr(config, "BRAIN_DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "AUTONOMOUS_PERSONA_TICKS", True)
    monkeypatch.setattr(config, "AUTONOMOUS_PERSONA_TICK_INTERVAL_SECONDS", 999999)
    monkeypatch.setattr(config, "AUTONOMOUS_PERSONA_TICK_ESTIMATED_COST", 0.01)

    system = System()

    fake_response = LLMResponse(
        text="Nothing new since last check-in.", tool_calls=[], stop_reason="end_turn", raw_content=[],
        input_tokens=10, output_tokens=5,
    )
    # Autonomous ticks now go through the FREE background router, not the
    # paid one -- mock that one instead, and expect $0 actually charged.
    monkeypatch.setattr(system.research_agent.background_router.model, "call", lambda *a, **k: fake_response)
    monkeypatch.setattr(
        type(system.research_agent.background_router.model), "configured", property(lambda self: True)
    )

    ran = system.scheduler.run_due()
    assert "autonomous_research_tick" in ran

    assert system.budget.status("research")["spent"] == 0.0  # genuinely free -- nothing charged
    from aicommerce.brain.models import MemoryKind

    records = system.brain.query(kind=MemoryKind.EPISODIC, tags=["elena_voss"])
    assert any("Nothing new since last check-in" in r.content for r in records)
    assert any("persona_autonomous_task" in r.tags for r in records)
