from unittest.mock import MagicMock, patch

from aicommerce.agents.shopify_agent import ShopifyAgent


def test_unconfigured_agent_reports_clear_error():
    agent = ShopifyAgent(store="", token="")
    assert agent.configured is False

    result = agent.execute({"action": "read_products", "params": {}})
    assert result.success is False
    assert "SHOPIFY_STORE" in result.error


def test_configured_agent_reads_products():
    agent = ShopifyAgent(store="test-shop.myshopify.com", token="shpat_fake")

    fake_response = MagicMock()
    fake_response.json.return_value = {"products": [{"id": 1, "title": "Widget"}]}
    fake_response.raise_for_status.return_value = None

    with patch("aicommerce.agents.shopify_agent.requests.get", return_value=fake_response) as mock_get:
        result = agent.execute({"action": "read_products", "params": {"limit": 10}})

    assert result.success is True
    assert result.output == [{"id": 1, "title": "Widget"}]
    assert result.evidence
    mock_get.assert_called_once()
    assert "products.json" in mock_get.call_args[0][0]


def test_write_action_calls_post_with_expected_payload():
    agent = ShopifyAgent(store="test-shop.myshopify.com", token="shpat_fake")

    fake_response = MagicMock()
    fake_response.json.return_value = {"product": {"id": 99, "title": "New Product"}}
    fake_response.raise_for_status.return_value = None

    with patch("aicommerce.agents.shopify_agent.requests.post", return_value=fake_response) as mock_post:
        result = agent.execute(
            {"action": "create_product", "params": {"product_data": {"title": "New Product"}}}
        )

    assert result.success is True
    assert result.output["id"] == 99
    mock_post.assert_called_once()
    assert mock_post.call_args[1]["json"] == {"product": {"title": "New Product"}}


def test_unknown_action_fails_cleanly():
    agent = ShopifyAgent(store="test-shop.myshopify.com", token="shpat_fake")
    result = agent.execute({"action": "nuke_the_store", "params": {}})
    assert result.success is False
    assert "unknown shopify action" in result.error


def test_http_error_surfaces_as_failed_result_not_exception():
    import requests

    agent = ShopifyAgent(store="test-shop.myshopify.com", token="shpat_fake")

    with patch("aicommerce.agents.shopify_agent.requests.get", side_effect=requests.HTTPError("429")):
        result = agent.execute({"action": "read_products", "params": {}})

    assert result.success is False
    assert "Shopify API error" in result.error
