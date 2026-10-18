from shared.llm import estimate_cost


def test_estimate_cost_uses_per_million_prices():
    assert estimate_cost("claude-sonnet-5-5", 1_000_000, 0) == 2.0
    assert estimate_cost("claude-sonnet-5-5", 0, 1_000_000) == 10.0
