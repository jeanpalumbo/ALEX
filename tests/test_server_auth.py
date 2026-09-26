"""The console API must reject requests without the correct console token.
Uses FastAPI's TestClient (httpx) — no real network, no server process."""
from fastapi.testclient import TestClient


def build_client():
    from aicommerce.webapp.server import app

    return TestClient(app)


def test_api_call_without_token_is_rejected():
    client = build_client()
    response = client.get("/api/state")
    assert response.status_code == 401


def test_api_call_with_wrong_token_is_rejected():
    client = build_client()
    response = client.get("/api/state", headers={"X-Console-Token": "wrong-token"})
    assert response.status_code == 401


def test_api_call_with_correct_token_succeeds():
    from aicommerce import config

    client = build_client()
    response = client.get("/api/state", headers={"X-Console-Token": config.CONSOLE_TOKEN})
    assert response.status_code == 200
    assert "preflight" in response.json()


def test_index_page_does_not_require_token_and_embeds_it():
    from aicommerce import config

    client = build_client()
    response = client.get("/")
    assert response.status_code == 200
    assert config.CONSOLE_TOKEN in response.text
    assert "__CONSOLE_TOKEN__" not in response.text
