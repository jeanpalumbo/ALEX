"""Tests for FallbackModel -- real resilience for the free-tier background
path (e.g. local Ollama down -> OpenRouter; OpenRouter rate-limited -> local
Ollama), without ModelRouter/PersonaAgent needing to know a chain exists."""
from aicommerce.ceo.llm import FallbackModel, LLMNotConfigured, LLMResponse


class _FakeModel:
    def __init__(self, configured=True, raises=None, response_text="ok", free=True):
        self.configured = configured
        self.raises = raises
        self.response_text = response_text
        self.free = free
        self.model = "fake-model"
        self.calls = 0

    def call(self, system, messages, tools=None, max_tokens=4096):
        self.calls += 1
        if self.raises:
            raise self.raises
        return LLMResponse(text=self.response_text, tool_calls=[], stop_reason="end_turn", raw_content=[])


def test_fallback_requires_at_least_one_model():
    import pytest

    with pytest.raises(ValueError):
        FallbackModel()


def test_fallback_uses_first_configured_model():
    primary = _FakeModel(response_text="from primary")
    secondary = _FakeModel(response_text="from secondary")
    fb = FallbackModel(primary, secondary)

    result = fb.call("sys", [{"role": "user", "content": "hi"}])

    assert result.text == "from primary"
    assert primary.calls == 1
    assert secondary.calls == 0


def test_fallback_skips_unconfigured_model():
    primary = _FakeModel(configured=False)
    secondary = _FakeModel(response_text="from secondary")
    fb = FallbackModel(primary, secondary)

    result = fb.call("sys", [{"role": "user", "content": "hi"}])

    assert result.text == "from secondary"
    assert primary.calls == 0


def test_fallback_falls_through_on_call_exception():
    primary = _FakeModel(raises=RuntimeError("connection refused"))
    secondary = _FakeModel(response_text="from secondary")
    fb = FallbackModel(primary, secondary)

    result = fb.call("sys", [{"role": "user", "content": "hi"}])

    assert result.text == "from secondary"
    assert primary.calls == 1


def test_fallback_raises_when_nothing_configured():
    primary = _FakeModel(configured=False)
    secondary = _FakeModel(configured=False)
    fb = FallbackModel(primary, secondary)

    import pytest

    with pytest.raises(LLMNotConfigured):
        fb.call("sys", [{"role": "user", "content": "hi"}])


def test_fallback_configured_true_if_any_model_configured():
    fb = FallbackModel(_FakeModel(configured=False), _FakeModel(configured=True))
    assert fb.configured is True


def test_fallback_configured_false_if_none_configured():
    fb = FallbackModel(_FakeModel(configured=False), _FakeModel(configured=False))
    assert fb.configured is False


def test_fallback_exposes_which_model_actually_answered_as_free():
    primary = _FakeModel(raises=RuntimeError("down"), free=True)
    secondary = _FakeModel(response_text="ok", free=False)
    fb = FallbackModel(primary, secondary)

    fb.call("sys", [{"role": "user", "content": "hi"}])

    assert fb.free is False  # reflects secondary (the one that actually answered)
