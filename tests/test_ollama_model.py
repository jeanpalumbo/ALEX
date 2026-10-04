"""Tests for OllamaModel -- the local, zero-cost drop-in for CEOModel that
talks to Ollama's OpenAI-compatible endpoint. Reuses the same converter
functions already verified for OpenRouterModel. No real network/GPU calls
here (mocked client) -- live verification happens once Jean's Ollama
install finishes and a model is actually pulled."""
from unittest.mock import MagicMock, patch

from aicommerce.ceo.llm import OllamaModel


def test_ollama_model_configured_when_base_url_and_model_set():
    model = OllamaModel(base_url="http://localhost:11434/v1", model="qwen2.5:7b")
    assert model.configured is True


def test_ollama_model_not_configured_without_base_url(monkeypatch):
    from aicommerce import config

    monkeypatch.setattr(config, "OLLAMA_BASE_URL", "")
    model = OllamaModel(base_url="", model="qwen2.5:7b")
    assert model.configured is False


def test_ollama_model_is_marked_free():
    assert OllamaModel.free is True


def test_ollama_model_call_hits_local_base_url_with_no_real_api_key():
    model = OllamaModel(base_url="http://localhost:11434/v1", model="qwen2.5:7b")
    fake_choice = MagicMock(finish_reason="stop")
    fake_choice.message.content = "hola"
    fake_choice.message.tool_calls = None
    fake_response = MagicMock(choices=[fake_choice], usage=None)

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = fake_response
    with patch("openai.OpenAI", return_value=fake_client) as mock_openai:
        result = model.call("system prompt", [{"role": "user", "content": "hi"}])

    mock_openai.assert_called_once_with(base_url="http://localhost:11434/v1", api_key="ollama")
    assert result.text == "hola"
    call_kwargs = fake_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "qwen2.5:7b"


def test_ollama_model_call_with_tools_converts_to_openai_function_schema():
    model = OllamaModel(base_url="http://localhost:11434/v1", model="qwen2.5:7b")
    fake_choice = MagicMock(finish_reason="stop")
    fake_choice.message.content = "ok"
    fake_choice.message.tool_calls = None
    fake_response = MagicMock(choices=[fake_choice], usage=None)

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = fake_response
    with patch("openai.OpenAI", return_value=fake_client):
        model.call(
            "sys",
            [{"role": "user", "content": "hi"}],
            tools=[{"name": "t", "description": "d", "input_schema": {}}],
        )

    call_kwargs = fake_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["tools"][0]["function"]["name"] == "t"
