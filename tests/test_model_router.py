from aicommerce.ceo.llm import LLMResponse
from aicommerce.ceo.model_router import ModelRouter, estimate_cost
from aicommerce.control_plane.events import EventBus


class FakeModel:
    configured = True
    model = "fake-model-1"

    def __init__(self, response=None, error=None):
        self._response = response
        self._error = error

    def call(self, system, messages, tools=None, max_tokens=1024):
        if self._error:
            raise self._error
        return self._response


def make_response(input_tokens=100, output_tokens=50):
    return LLMResponse(
        text="hello",
        tool_calls=[],
        stop_reason="end_turn",
        raw_content=[{"type": "text", "text": "hello"}],
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


def test_estimate_cost_is_zero_for_zero_tokens():
    assert estimate_cost(0, 0) == 0.0


def test_estimate_cost_scales_with_tokens():
    small = estimate_cost(1000, 0)
    big = estimate_cost(2000, 0)
    assert big == small * 2
    assert small > 0


def test_successful_call_publishes_model_call_event_with_metrics():
    events = EventBus()
    router = ModelRouter(FakeModel(response=make_response(200, 100)), events=events)

    routed = router.call("system", [{"role": "user", "content": "hi"}], task="ceo_chat")

    assert routed.model == "fake-model-1"
    assert routed.estimated_cost > 0
    logged = events.history("model.call")
    assert len(logged) == 1
    assert logged[0].payload["input_tokens"] == 200
    assert logged[0].payload["output_tokens"] == 100
    assert logged[0].payload["task"] == "ceo_chat"
    assert "correlation_id" in logged[0].payload


def test_failed_call_publishes_call_failed_event_and_reraises():
    events = EventBus()
    router = ModelRouter(FakeModel(error=RuntimeError("upstream 500")), events=events)

    import pytest

    with pytest.raises(RuntimeError):
        router.call("system", [], task="ceo_chat")

    logged = events.history("model.call_failed")
    assert len(logged) == 1
    assert "upstream 500" in logged[0].payload["error"]
    assert events.history("model.call") == []


def test_correlation_id_is_shared_when_passed_explicitly():
    events = EventBus()
    router = ModelRouter(FakeModel(response=make_response()), events=events)

    router.call("system", [], task="ceo_chat", correlation_id="fixed-id")
    router.call("system", [], task="ceo_chat", correlation_id="fixed-id")

    logged = events.history("model.call")
    assert logged[0].payload["correlation_id"] == "fixed-id"
    assert logged[1].payload["correlation_id"] == "fixed-id"


def test_router_works_without_an_event_bus():
    router = ModelRouter(FakeModel(response=make_response()), events=None)
    routed = router.call("system", [])
    assert routed.response.text == "hello"
