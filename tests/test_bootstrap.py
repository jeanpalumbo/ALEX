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
