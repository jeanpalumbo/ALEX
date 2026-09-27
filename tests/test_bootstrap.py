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
