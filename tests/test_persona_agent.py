from aicommerce.agents.persona import FINANCE_PERSONA, RESEARCH_PERSONA, Persona, PersonaAgent
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


def test_persona_agent_receives_institutional_rules_as_context():
    from aicommerce.brain.models import Confidence, MemoryKind, MemoryRecord

    model = FakeModel(text="ok")
    router = ModelRouter(model)
    brain = CompanyBrain(":memory:")
    brain.record(MemoryRecord(
        kind=MemoryKind.INSTITUTIONAL,
        content="Never approve a spend without free validation first.",
        source="jean",
        confidence=Confidence.FACT,
    ))
    agent = PersonaAgent(RESEARCH_PERSONA, router, brain)

    agent.execute({"action": "think", "params": {"prompt": "should we spend on ads?"}})

    sent_content = model.calls[0]["messages"][0]["content"]
    assert "Never approve a spend without free validation first." in sent_content
    assert "Company rules/methodology you must follow" in sent_content


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


def test_every_persona_has_a_self_correction_style():
    """Jean's explicit ask: every employee needs real self-correction built
    in, not just a generic one. Each should be distinguishable."""
    from aicommerce.agents.persona import CEO_PERSONA, ENGINEERING_PERSONA, FINANCE_PERSONA, STORE_OPS_PERSONA

    personas = [CEO_PERSONA, RESEARCH_PERSONA, STORE_OPS_PERSONA, ENGINEERING_PERSONA, FINANCE_PERSONA]
    styles = {p.self_correction_style for p in personas}
    assert len(styles) == len(personas)  # all distinct, not copy-pasted
    for p in personas:
        assert p.self_correction_style in p.system_prompt()


def test_all_five_core_personas_have_distinct_full_identities():
    from aicommerce.agents.persona import CEO_PERSONA, ENGINEERING_PERSONA, FINANCE_PERSONA, STORE_OPS_PERSONA

    personas = [CEO_PERSONA, RESEARCH_PERSONA, STORE_OPS_PERSONA, ENGINEERING_PERSONA, FINANCE_PERSONA]
    names = {p.name for p in personas}
    assert len(names) == 5  # no duplicate identities
    for p in personas:
        for field_value in (p.mission, p.personality, p.career_motivation, p.operating_principles):
            assert len(field_value) > 50  # real depth, not a placeholder stub


def test_finance_persona_votes_against_spend_without_free_validation_first():
    finance_model = FakeModel(
        text="VOTE: AGAINST\nWe haven't tried the free version of this yet. Automatic no at this stage."
    )
    agent = PersonaAgent(FINANCE_PERSONA, ModelRouter(finance_model), CompanyBrain(":memory:"))

    result = agent.execute({"action": "think", "params": {"prompt": "Should we spend $200 on ads?"}})

    assert result.success is True
    assert "free version" in result.output


def test_store_ops_and_engineering_lead_personas_reason_distinctly(monkeypatch):
    from aicommerce.agents.persona import ENGINEERING_PERSONA, STORE_OPS_PERSONA

    marcus_model = FakeModel(text="Marcus says: not without proven fulfillment capacity.")
    priya_model = FakeModel(text="Priya says: this diff is too broad, split it.")

    marcus = PersonaAgent(STORE_OPS_PERSONA, ModelRouter(marcus_model), CompanyBrain(":memory:"))
    priya = PersonaAgent(ENGINEERING_PERSONA, ModelRouter(priya_model), CompanyBrain(":memory:"))

    r1 = marcus.execute({"action": "think", "params": {"prompt": "should we list this product?"}})
    r2 = priya.execute({"action": "think", "params": {"prompt": "is this change safe to merge?"}})

    assert "fulfillment" in r1.output
    assert "split it" in r2.output
    assert marcus_model.calls[0]["system"] != priya_model.calls[0]["system"]  # genuinely different identities


def test_think_background_without_a_background_router_fails_cleanly():
    agent = PersonaAgent(RESEARCH_PERSONA, ModelRouter(FakeModel()), CompanyBrain(":memory:"))
    result = agent.execute({"action": "think_background", "params": {"prompt": "anything new?"}})
    assert result.success is False
    assert "no background/free-tier model configured" in result.error


def test_think_background_uses_the_free_router_not_the_paid_one():
    paid_model = FakeModel(text="PAID response")
    free_model = FakeModel(text="FREE response")
    agent = PersonaAgent(
        RESEARCH_PERSONA, ModelRouter(paid_model), CompanyBrain(":memory:"),
        background_router=ModelRouter(free_model),
    )

    result = agent.execute({"action": "think_background", "params": {"prompt": "anything new?"}})

    assert result.success is True
    assert result.output == "FREE response"
    assert len(paid_model.calls) == 0
    assert len(free_model.calls) == 1


def test_think_background_records_memory_tagged_differently_from_think():
    free_model = FakeModel(text="nothing new")
    brain = CompanyBrain(":memory:")
    agent = PersonaAgent(
        RESEARCH_PERSONA, ModelRouter(FakeModel()), brain, background_router=ModelRouter(free_model)
    )

    agent.execute({"action": "think_background", "params": {"prompt": "check in"}})

    from aicommerce.brain.models import MemoryKind

    records = brain.query(kind=MemoryKind.EPISODIC, tags=["elena_voss"])
    assert len(records) == 1
    assert "persona_autonomous_task" in records[0].tags
    assert "persona_task" not in records[0].tags
