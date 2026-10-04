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

    mock_openai.assert_called_once()
    kw = mock_openai.call_args.kwargs
    assert kw["base_url"] == "http://localhost:11434/v1"
    assert kw["api_key"] == "ollama"
    assert kw["max_retries"] == 0 and kw["timeout"] > 0
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


def test_config_exposes_ollama_api_key_and_model_constructs_without_env():
    from aicommerce import config
    from aicommerce.ceo.llm import OllamaModel

    assert isinstance(config.OLLAMA_API_KEY, str)
    assert OllamaModel().configured is True


def _ok_client():
    choice = MagicMock(finish_reason="stop")
    choice.message.content = "ok"
    choice.message.tool_calls = None
    client = MagicMock()
    client.chat.completions.create.return_value = MagicMock(choices=[choice], usage=None)
    return client


def test_daily_call_cap_raises_then_fallback_takes_over(monkeypatch):
    import pytest
    from aicommerce import config
    from aicommerce.ceo.llm import FallbackModel, OllamaLimitReached

    monkeypatch.setattr(config, "OLLAMA_MAX_CALLS_PER_DAY", 2)
    ollama = OllamaModel(base_url="http://x/v1", model="m")
    with patch("openai.OpenAI", return_value=_ok_client()) as mock_openai:
        ollama.call("s", [{"role": "user", "content": "1"}])
        ollama.call("s", [{"role": "user", "content": "2"}])
        with pytest.raises(OllamaLimitReached):
            ollama.call("s", [{"role": "user", "content": "3"}])
    assert mock_openai.return_value.chat.completions.create.call_count == 2

    backup = MagicMock(configured=True, model="backup", free=True)
    backup.call.return_value = "from-backup"
    chain = FallbackModel(ollama, backup)
    assert chain.call("s", []) == "from-backup"
    assert chain.last_model == "backup"


def test_no_cap_by_default(monkeypatch):
    from aicommerce import config

    monkeypatch.setattr(config, "OLLAMA_MAX_CALLS_PER_DAY", 0)
    ollama = OllamaModel(base_url="http://x/v1", model="m")
    with patch("openai.OpenAI", return_value=_ok_client()):
        for _ in range(5):
            ollama.call("s", [{"role": "user", "content": "x"}])
