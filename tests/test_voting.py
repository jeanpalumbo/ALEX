from aicommerce.agents.persona import RESEARCH_PERSONA, STORE_OPS_PERSONA, PersonaAgent
from aicommerce.brain.store import CompanyBrain
from aicommerce.ceo.llm import LLMResponse
from aicommerce.ceo.model_router import ModelRouter
from aicommerce.ceo.orchestrator import Orchestrator
from aicommerce.ceo.voting import TechnicalVote, Vote, run_technical_vote
from aicommerce.control_plane.approvals import ApprovalQueue
from aicommerce.control_plane.budget import BudgetGuard
from aicommerce.control_plane.permissions import PermissionManager, Role
from aicommerce.control_plane.registry import AgentRegistry, AgentSpec


class FakeModel:
    configured = True
    model = "fake-model"

    def __init__(self, text):
        self.text = text
        self.calls = 0

    def call(self, system, messages, tools=None, max_tokens=1024):
        self.calls += 1
        return LLMResponse(
            text=self.text, tool_calls=[], stop_reason="end_turn", raw_content=[],
            input_tokens=50, output_tokens=20,
        )


def build_voting_orchestrator():
    registry = AgentRegistry()
    permissions = PermissionManager()
    budget = BudgetGuard()
    approvals = ApprovalQueue()
    brain = CompanyBrain(":memory:")

    for name, persona, text in [
        ("research", RESEARCH_PERSONA, "VOTE: FOR\nThe data supports this."),
        ("store_ops", STORE_OPS_PERSONA, "VOTE: AGAINST\nFulfillment isn't proven yet."),
    ]:
        agent = PersonaAgent(persona, ModelRouter(FakeModel(text)), brain)
        registry.register(
            AgentSpec(name=name, mission="m", authority=("think",), limits={"persona": persona.name}),
            agent,
        )
        permissions.define_role(Role(name=f"{name}_role", allowed_actions=frozenset({"think"})))
        permissions.assign_role(name, f"{name}_role")
        budget.set_budget(name, 10.0)

    budget.set_budget("opus_review", 10.0)
    orchestrator = Orchestrator(registry, permissions, budget, approvals, brain)
    return orchestrator


def test_vote_tally_counts_each_stance():
    vote = TechnicalVote(
        proposal="p",
        votes=[
            Vote(voter="A", stance="for", reasoning="r"),
            Vote(voter="B", stance="against", reasoning="r"),
            Vote(voter="C", stance="for", reasoning="r"),
        ],
    )
    assert vote.tally == {"for": 2, "against": 1, "abstain": 0, "error": 0}


def test_run_technical_vote_collects_real_votes_from_each_persona():
    orchestrator = build_voting_orchestrator()

    vote = run_technical_vote("Should we launch product X?", orchestrator, ["research", "store_ops"])

    assert len(vote.votes) == 2
    by_voter = {v.voter: v for v in vote.votes}
    assert by_voter["Elena Voss"].stance == "for"
    assert by_voter["Marcus Chen"].stance == "against"
    assert vote.tally == {"for": 1, "against": 1, "abstain": 0, "error": 0}


def test_run_technical_vote_includes_opus_when_router_given():
    orchestrator = build_voting_orchestrator()
    opus_router = ModelRouter(FakeModel("VOTE: ABSTAIN\nNot enough data for a technical call."))

    vote = run_technical_vote("proposal", orchestrator, ["research"], opus_router=opus_router)

    assert len(vote.votes) == 2
    opus_vote = [v for v in vote.votes if v.voter == "Opus (independent review)"][0]
    assert opus_vote.stance == "abstain"


def test_run_technical_vote_without_opus_router_omits_it():
    orchestrator = build_voting_orchestrator()
    vote = run_technical_vote("proposal", orchestrator, ["research"], opus_router=None)
    assert len(vote.votes) == 1


def test_opus_unconfigured_records_an_error_vote_not_a_crash():
    from aicommerce.ceo.llm import CEOModel

    orchestrator = build_voting_orchestrator()
    unconfigured_opus = ModelRouter(CEOModel(api_key=""))

    vote = run_technical_vote("proposal", orchestrator, [], opus_router=unconfigured_opus)

    assert len(vote.votes) == 1
    assert vote.votes[0].stance == "error"
    assert "ANTHROPIC_API_KEY" in vote.votes[0].reasoning


def test_vote_without_an_explicit_vote_line_is_recorded_as_abstain():
    registry = AgentRegistry()
    permissions = PermissionManager()
    budget = BudgetGuard()
    approvals = ApprovalQueue()
    brain = CompanyBrain(":memory:")

    agent = PersonaAgent(RESEARCH_PERSONA, ModelRouter(FakeModel("I have thoughts but no clear vote.")), brain)
    registry.register(AgentSpec(name="research", mission="m", authority=("think",)), agent)
    permissions.define_role(Role(name="r", allowed_actions=frozenset({"think"})))
    permissions.assign_role("research", "r")
    budget.set_budget("research", 10.0)
    orchestrator = Orchestrator(registry, permissions, budget, approvals, brain)

    vote = run_technical_vote("proposal", orchestrator, ["research"])
    assert vote.votes[0].stance == "abstain"


def test_vote_for_an_unregistered_agent_is_recorded_as_error_not_a_crash():
    orchestrator = build_voting_orchestrator()
    vote = run_technical_vote("proposal", orchestrator, ["nonexistent_agent"])
    assert len(vote.votes) == 1
    assert vote.votes[0].stance == "error"


def test_vote_charges_real_persona_cost_to_their_own_budget_scope():
    orchestrator = build_voting_orchestrator()
    run_technical_vote("proposal", orchestrator, ["research"])
    assert orchestrator.budget.status("research")["spent"] > 0


def test_summary_text_includes_every_vote():
    vote = TechnicalVote(proposal="Launch X?", votes=[Vote(voter="A", stance="for", reasoning="good data")])
    text = vote.summary_text()
    assert "Launch X?" in text
    assert "A: FOR" in text
    assert "good data" in text


def test_opus_vote_has_configured_weight_and_counts_more_in_weighted_tally():
    orchestrator = build_voting_orchestrator()
    opus_router = ModelRouter(FakeModel("VOTE: FOR\nLooks sound technically."))

    # fixture: research votes FOR, store_ops votes AGAINST; opus (weight=3) votes FOR too
    vote = run_technical_vote(
        "proposal", orchestrator, ["research", "store_ops"], opus_router=opus_router, opus_weight=3
    )

    opus_vote = [v for v in vote.votes if "Opus" in v.voter][0]
    assert opus_vote.weight == 3
    assert vote.tally["for"] == 2  # research + opus, one vote each
    assert vote.tally["against"] == 1  # store_ops
    assert vote.weighted_tally["for"] == 4  # research(1) + opus(3)
    assert vote.weighted_tally["against"] == 1  # store_ops(1)


def test_default_opus_weight_is_two_when_not_specified():
    orchestrator = build_voting_orchestrator()
    opus_router = ModelRouter(FakeModel("VOTE: FOR\nok"))

    vote = run_technical_vote("proposal", orchestrator, [], opus_router=opus_router)

    assert vote.votes[0].weight == 2


def test_weighted_tally_matches_raw_tally_when_no_opus():
    orchestrator = build_voting_orchestrator()
    vote = run_technical_vote("proposal", orchestrator, ["research", "store_ops"])
    assert vote.weighted_tally == vote.tally


def test_to_dict_is_json_serializable():
    import json

    orchestrator = build_voting_orchestrator()
    vote = run_technical_vote("proposal", orchestrator, ["research", "store_ops"])
    json.dumps(vote.to_dict())
