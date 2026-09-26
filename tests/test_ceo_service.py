from aicommerce.agents.stubs import EchoAgent
from aicommerce.brain.store import CompanyBrain
from aicommerce.ceo.llm import LLMResponse, ToolCall
from aicommerce.ceo.orchestrator import Orchestrator
from aicommerce.ceo.service import CEOService
from aicommerce.control_plane.approvals import ApprovalQueue
from aicommerce.control_plane.budget import BudgetGuard
from aicommerce.control_plane.permissions import PermissionManager, Role
from aicommerce.control_plane.registry import AgentRegistry, AgentSpec


def build_orchestrator():
    registry = AgentRegistry()
    permissions = PermissionManager()
    budget = BudgetGuard()
    approvals = ApprovalQueue()
    brain = CompanyBrain(":memory:")

    registry.register(AgentSpec(name="research", mission="research"), EchoAgent("research"))
    permissions.define_role(Role(name="r", allowed_actions=frozenset({"do_research"})))
    permissions.assign_role("research", "r")
    budget.set_budget("research", 50.0)

    return Orchestrator(registry, permissions, budget, approvals, brain)


class UnconfiguredModel:
    configured = False

    def call(self, *a, **k):
        raise AssertionError("call() should never be invoked when not configured")


class ScriptedModel:
    """Replays a fixed sequence of LLMResponse objects, one per `call()`."""

    configured = True

    def __init__(self, responses: list[LLMResponse]) -> None:
        self._responses = list(responses)
        self.calls = 0

    def call(self, system, messages, tools=None, max_tokens=1024):
        response = self._responses[self.calls]
        self.calls += 1
        return response


class RaisingModel:
    configured = True

    def call(self, *a, **k):
        raise RuntimeError("simulated network failure")


def test_chat_without_llm_configured_returns_unknown_without_calling_model():
    service = CEOService(build_orchestrator(), model=UnconfiguredModel())
    turn = service.chat("what is our budget?")
    assert turn.content.startswith("UNKNOWN:")
    assert turn.role == "assistant"


def test_chat_runs_tool_then_returns_final_text():
    tool_response = LLMResponse(
        text="",
        tool_calls=[ToolCall(id="call_1", name="get_company_state", input={})],
        stop_reason="tool_use",
        raw_content=[{"type": "tool_use", "id": "call_1", "name": "get_company_state", "input": {}}],
    )
    final_response = LLMResponse(
        text="FACT: you have 1 agent registered and 0 pending approvals.",
        tool_calls=[],
        stop_reason="end_turn",
        raw_content=[{"type": "text", "text": "FACT: you have 1 agent registered and 0 pending approvals."}],
    )
    model = ScriptedModel([tool_response, final_response])
    service = CEOService(build_orchestrator(), model=model)

    turn = service.chat("what's our status?")

    assert model.calls == 2
    assert "FACT:" in turn.content
    assert turn.tool_activity[0]["tool"] == "get_company_state"
    assert turn.tool_activity[0]["result"]["agents"] == ["research"]


def test_chat_records_episodic_memory_of_the_conversation():
    final_response = LLMResponse(text="hello", tool_calls=[], stop_reason="end_turn", raw_content=[{"type": "text", "text": "hello"}])
    orchestrator = build_orchestrator()
    service = CEOService(orchestrator, model=ScriptedModel([final_response]))

    service.chat("hi")

    from aicommerce.brain.models import MemoryKind
    episodes = orchestrator.brain.query(kind=MemoryKind.EPISODIC, tags=["chat"])
    assert len(episodes) == 1
    assert "hi" in episodes[0].content


def test_chat_survives_model_exception():
    service = CEOService(build_orchestrator(), model=RaisingModel())
    turn = service.chat("hello")
    assert "UNKNOWN" in turn.content
    assert service.state.last_error is not None


def test_chat_history_accumulates_across_turns():
    final_response = LLMResponse(text="ok", tool_calls=[], stop_reason="end_turn", raw_content=[{"type": "text", "text": "ok"}])
    service = CEOService(build_orchestrator(), model=ScriptedModel([final_response, final_response]))

    service.chat("first")
    service.chat("second")

    assert [t.content for t in service.history if t.role == "user"] == ["first", "second"]


def test_chat_spends_from_the_ceo_llm_budget_when_one_is_configured():
    orchestrator = build_orchestrator()
    orchestrator.budget.set_budget("ceo_llm", 1.0)
    response = LLMResponse(
        text="ok", tool_calls=[], stop_reason="end_turn",
        raw_content=[{"type": "text", "text": "ok"}], input_tokens=1000, output_tokens=500,
    )
    service = CEOService(orchestrator, model=ScriptedModel([response]))

    service.chat("hi")

    status = orchestrator.budget.status("ceo_llm")
    assert status["spent"] > 0


def test_chat_without_a_ceo_llm_budget_configured_does_not_error():
    # build_orchestrator() never calls set_budget("ceo_llm", ...) -- must be
    # a silent no-op, not a crash, since not every deployment tracks it.
    response = LLMResponse(text="ok", tool_calls=[], stop_reason="end_turn", raw_content=[{"type": "text", "text": "ok"}])
    service = CEOService(build_orchestrator(), model=ScriptedModel([response]))

    turn = service.chat("hi")
    assert turn.content == "ok"
