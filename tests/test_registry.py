import pytest

from aicommerce.control_plane.registry import AgentRegistry, AgentSpec


def test_register_and_lookup():
    registry = AgentRegistry()
    spec = AgentSpec(name="research", mission="find markets", tools=("web_search",))
    registry.register(spec, instance=object())

    assert registry.get_spec("research") is spec
    assert registry.get_instance("research") is not None
    assert [s.name for s in registry.list_agents()] == ["research"]


def test_duplicate_registration_rejected():
    registry = AgentRegistry()
    spec = AgentSpec(name="research", mission="find markets")
    registry.register(spec, instance=object())
    with pytest.raises(ValueError):
        registry.register(spec, instance=object())


def test_find_by_tool():
    registry = AgentRegistry()
    registry.register(AgentSpec(name="research", mission="m", tools=("web_search",)), object())
    registry.register(AgentSpec(name="seo", mission="m", tools=("web_search", "sitemap")), object())
    registry.register(AgentSpec(name="finance", mission="m", tools=("ledger",)), object())

    found = {s.name for s in registry.find_by_tool("web_search")}
    assert found == {"research", "seo"}


def test_unregister():
    registry = AgentRegistry()
    registry.register(AgentSpec(name="research", mission="m"), object())
    registry.unregister("research")
    assert registry.get_spec("research") is None
    assert registry.get_instance("research") is None
