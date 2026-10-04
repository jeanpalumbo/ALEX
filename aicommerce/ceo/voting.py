"""Technical Vote — an extra governance layer for important decisions.

Jean's ask: before a high-stakes decision reaches him, run a real vote among
the specialists it actually concerns, PLUS an independent technical read
from a stronger model (Opus) via the real Anthropic API, and attach all of
it as evidence. This does NOT replace human approval or let anything
execute by majority vote — it only makes the evidence Jean sees richer
before he decides. The ApprovalQueue is still the only gate that lets an
action actually run.

Each persona's vote goes through `Orchestrator.run_cycle` exactly like any
other delegated "think" task — same budget scope, same permission check,
same audit trail, same event publishing. The Opus call is separate (it
isn't a registered agent) and is metered against its own `opus_review`
budget scope directly.

Each voter is asked to open their response with `VOTE: FOR`, `VOTE: AGAINST`,
or `VOTE: ABSTAIN` so the tally is parsed from a real, explicit statement —
not guessed from sentiment in free text.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from aicommerce.ceo.llm import LLMNotConfigured
from aicommerce.ceo.model_router import ModelRouter
from aicommerce.ceo.orchestrator import Orchestrator
from aicommerce.control_plane.budget import BudgetExceededError

_VOTE_PATTERN = re.compile(r"VOTE:\s*(FOR|AGAINST|ABSTAIN)", re.IGNORECASE)

_VOTE_PROMPT_TEMPLATE = """A decision needs your professional vote, not just a comment. Open your \
response with exactly one line "VOTE: FOR", "VOTE: AGAINST", or "VOTE: ABSTAIN", then explain why in \
your own voice. Vote AGAINST if the evidence doesn't support it, even if you'd personally like it to \
go through -- that's the point of asking you.

PROPOSAL: {proposal}
"""

_OPUS_PROMPT_TEMPLATE = """You are being consulted as an independent senior technical reviewer for a \
real decision at a small AI-run ecommerce company. You have no stake in the outcome and no loyalty to \
whoever proposed this -- give the most rigorous technical/risk read you can, including real failure \
modes and what evidence is still missing. Open your response with exactly one line "VOTE: FOR", \
"VOTE: AGAINST", or "VOTE: ABSTAIN", then your reasoning.

PROPOSAL: {proposal}
"""


@dataclass
class Vote:
    voter: str
    stance: str  # "for" | "against" | "abstain" | "error"
    reasoning: str
    cost: float = 0.0
    weight: int = 1  # Opus's vote counts for more -- see TechnicalVote.weighted_tally


@dataclass
class TechnicalVote:
    proposal: str
    votes: list[Vote]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def tally(self) -> dict[str, int]:
        """Raw, one-vote-each count — never hidden, even though the weighted
        tally below is what actually has more say in a close call."""
        counts = {"for": 0, "against": 0, "abstain": 0, "error": 0}
        for v in self.votes:
            counts[v.stance] = counts.get(v.stance, 0) + 1
        return counts

    @property
    def weighted_tally(self) -> dict[str, int]:
        """Opus's vote is weighted (default 2x a persona's) per Jean's explicit \
        instruction: day-to-day work runs on the free/open models; Opus is the \
        independent technical authority consulted specifically for decisive \
        votes, and its read carries more weight than any one persona's — but \
        never silently: both tallies are always reported side by side."""
        counts = {"for": 0, "against": 0, "abstain": 0, "error": 0}
        for v in self.votes:
            counts[v.stance] = counts.get(v.stance, 0) + v.weight
        return counts

    @property
    def total_cost(self) -> float:
        return sum(v.cost for v in self.votes)

    def to_dict(self) -> dict:
        return {
            "proposal": self.proposal,
            "created_at": self.created_at.isoformat(),
            "tally": self.tally,
            "weighted_tally": self.weighted_tally,
            "total_cost": round(self.total_cost, 6),
            "votes": [
                {"voter": v.voter, "stance": v.stance, "reasoning": v.reasoning, "weight": v.weight}
                for v in self.votes
            ],
        }

    def summary_text(self) -> str:
        lines = [
            f"Technical vote on: {self.proposal}",
            f"Tally (one vote each): {self.tally}",
            f"Weighted tally (Opus counts for more): {self.weighted_tally}",
        ]
        for v in self.votes:
            weight_note = f" (weight={v.weight})" if v.weight != 1 else ""
            lines.append(f"- {v.voter}{weight_note}: {v.stance.upper()} — {v.reasoning}")
        return "\n".join(lines)


def _parse_stance(text: str) -> tuple[str, str]:
    match = _VOTE_PATTERN.search(text)
    if not match:
        return "abstain", text.strip() or "(no explicit vote line found in response)"
    stance = match.group(1).lower()
    reasoning = _VOTE_PATTERN.sub("", text, count=1).strip()
    return stance, reasoning


def _persona_vote(orchestrator: Orchestrator, agent_name: str, proposal: str) -> Vote:
    spec = orchestrator.registry.get_spec(agent_name)
    voter_label = spec.limits.get("persona", agent_name) if spec else agent_name

    outcome = orchestrator.run_cycle(
        objective=f"technical vote: {proposal}",
        agent_name=agent_name,
        action="think",
        budget_scope=agent_name,
        cost=0.0,
        risk="low",
        reversible=True,
        params={"prompt": _VOTE_PROMPT_TEMPLATE.format(proposal=proposal)},
    )
    if outcome.status.value != "executed" or outcome.agent_result is None or not outcome.agent_result.success:
        reason = outcome.detail or (outcome.agent_result.error if outcome.agent_result else "no result")
        return Vote(voter=voter_label, stance="error", reasoning=reason, cost=0.0)

    stance, reasoning = _parse_stance(outcome.agent_result.output)
    return Vote(voter=voter_label, stance=stance, reasoning=reasoning, cost=outcome.agent_result.cost)


def _opus_vote(opus_router: ModelRouter, budget, proposal: str, weight: int) -> Vote:
    try:
        routed = opus_router.call(
            "You are a rigorous, independent senior technical reviewer. Be direct about risk.",
            [{"role": "user", "content": _OPUS_PROMPT_TEMPLATE.format(proposal=proposal)}],
            task="technical_vote:opus",
        )
    except LLMNotConfigured as exc:
        return Vote(voter="Opus (independent review)", stance="error", reasoning=str(exc), cost=0.0, weight=weight)
    except Exception as exc:  # noqa: BLE001
        return Vote(
            voter="Opus (independent review)", stance="error", reasoning=f"model error: {exc}", cost=0.0,
            weight=weight,
        )

    try:
        budget.spend("opus_review", routed.estimated_cost)
    except (KeyError, BudgetExceededError):
        pass  # the call already happened; don't pretend it didn't just because metering failed

    stance, reasoning = _parse_stance(routed.response.text)
    return Vote(
        voter="Opus (independent review)", stance=stance, reasoning=reasoning, cost=routed.estimated_cost,
        weight=weight,
    )


def run_technical_vote(
    proposal: str,
    orchestrator: Orchestrator,
    voter_agent_names: list[str],
    opus_router: Optional[ModelRouter] = None,
    opus_weight: int = 2,
) -> TechnicalVote:
    """Runs every named agent's real vote through the Orchestrator (same
    budget/permission/audit path as any delegated task) plus, if
    `opus_router` is given, an independent Opus review charged to its own
    `opus_review` budget scope. A failed/unconfigured voter is recorded as
    an "error" vote with the real reason, never silently skipped.

    `opus_weight` (default 2): per Jean's explicit instruction, Opus is
    consulted specifically for decisive votes and its technical read counts
    for more than a single persona's in `weighted_tally` — but the raw
    one-each `tally` is always reported alongside it, never hidden."""
    votes = [_persona_vote(orchestrator, name, proposal) for name in voter_agent_names]
    if opus_router is not None:
        votes.append(_opus_vote(opus_router, orchestrator.budget, proposal, weight=opus_weight))
    return TechnicalVote(proposal=proposal, votes=votes)
