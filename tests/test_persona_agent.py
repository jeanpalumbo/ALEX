from aicommerce.agents.persona import RESEARCH_PERSONA, Persona, PersonaAgent
from aicommerce.brain.store import CompanyBrain
from aicommerce.ceo.llm import LLMResponse
from aicommerce.ceo.model_router import ModelRouter


class FakeModel:
    configured = True
    model = "fake-model"

    def __init__(self, text="a response", input_tokens=100, output_tokens=50):
        self.text = text
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.calls = []

    def call(self, system, messages, tools=None, max_tokens=1024):
        self.calls.append({"system": system, "messages": messages})
        return LLMResponse(
            text=self.text, tool_calls=[], stop_reason="end_turn", raw_content=[],
            input_tokens=self.input_tokens, output_tokens=self.output_tokens,
        )


def test_persona_system_prompt_contains_every_identity_field():
    prompt = RESEARCH_PERSONA.system_prompt()
    assert RESEARCH_PERSONA.name in prompt
    assert RESEARCH_PERSONA.role in prompt
    assert RESEARCH_PERSONA.mission in prompt
    assert RESEARCH_PERSONA.personality in prompt
    assert RESEARCH_PERSONA.career_motivation in prompt
    for item in RESEARCH_PERSONA.expertise:
        assert item in prompt


def test_persona_agent_reasons_via_real_router_and_returns_text():
    model = FakeModel(text="HYPOTHESIS: thermal mugs might sell, but I have no data yet.")
    router = ModelRouter(model)
    brain = CompanyBrain(":memory:")
    agent = PersonaAgent(RESEARCH_PERSONA, router, brain)

    result = agent.execute({"action": "think", "params": {"prompt": "Should we sell thermal mugs?"}})

    assert result.success is True
    assert "thermal mugs" in result.output
    assert model.calls[0]["system"] == RESEARCH_PERSONA.system_prompt()


def test_persona_agent_records_its_own_tagged_memory():
    model = FakeModel(text="some finding")
    router = ModelRouter(model)
    brain = CompanyBrain(":memory:")
    agent = PersonaAgent(RESEARCH_PERSONA, router, brain)

    agent.execute({"action": "think", "params": {"prompt": "research X"}})

    from aicommerce.brain.models import MemoryKind

    records = brain.query(kind=MemoryKind.EPISODIC, tags=["elena_voss"])
    assert len(records) == 1
    assert "some finding" in records[0].content


def test_persona_agent_uses_its_own_past_memory_as_context():
    model = FakeModel(text="second finding")
    router = ModelRouter(model)
    brain = CompanyBrain(":memory:")
    agent = PersonaAgent(RESEARCH_PERSONA, router, brain)

    agent.execute({"action": "think", "params": {"prompt": "first task"}})
    agent.execute({"action": "think", "params": {"prompt": "second task"}})

    second_call_messages = model.calls[1]["messages"]
    assert "first task" in second_call_messages[0]["content"]  # prior memory fed back in


def test_persona_agent_rejects_unsupported_actions():
    agent = PersonaAgent(RESEARCH_PERSONA, ModelRouter(FakeModel()), CompanyBrain(":memory:"))
    result = agent.execute({"action": "delete_everything", "params": {}})
    assert result.success is False
    assert "only supports action='think'" in result.error


def test_persona_agent_requires_a_prompt():
    agent = PersonaAgent(RESEARCH_PERSONA, ModelRouter(FakeModel()), CompanyBrain(":memory:"))
    result = agent.execute({"action": "think", "params": {}})
    assert result.success is False
    assert "prompt is required" in result.error


def test_persona_agent_reports_unconfigured_model_cleanly():
    class Unconfigured:
        configured = False
        model = "x"

        def call(self, *a, **k):
            raise AssertionError("should never be called")

    agent = PersonaAgent(RESEARCH_PERSONA, ModelRouter(Unconfigured()), CompanyBrain(":memory:"))
    result = agent.execute({"action": "think", "params": {"prompt": "x"}})
    assert result.success is False
    assert "not configured" in result.error


def test_persona_agent_reports_real_cost_on_the_result():
    model = FakeModel(input_tokens=1000, output_tokens=1000)
    router = ModelRouter(model)
    agent = PersonaAgent(RESEARCH_PERSONA, router, CompanyBrain(":memory:"))

    result = agent.execute({"action": "think", "params": {"prompt": "x"}})
    assert result.cost > 0


def test_custom_persona_is_not_tied_to_research():
    persona = Persona(
        name="Test Person",
        role="Tester",
        mission="m",
        personality="p",
        career_motivation="c",
        expertise=("testing",),
        operating_principles="o",
    )
    assert "Test Person" in persona.system_prompt()
