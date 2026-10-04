"""Persona-backed agents — real specialists, not deterministic executors.

`ShopifyAgent` and `EngineeringAgent` are tool agents: fixed code paths, no
judgment of their own. A `PersonaAgent` is different: it has its own LLM
reasoning (via the same `ModelRouter` the CEO uses), its own dense identity
("soul" — personality, career motivation, expertise, operating principles,
not a one-line mission string), and its own slice of Company Brain memory
(every record it writes/reads is tagged with its own name, so it accumulates
real continuity across tasks instead of starting blank every time).

It is still bounded by the same constitution as everything else in this
codebase: Reality-First (FACT/INFERENCE/HYPOTHESIS/UNKNOWN), no fabricated
data, and any action with real-world effect still has to go through
`Orchestrator.run_cycle` like any other agent — a persona can reason and
recommend, but acting still means `propose_action`, permissions, budget, QA,
and approval when warranted. A personality is not a bypass.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from aicommerce.agents.base import Agent, AgentResult
from aicommerce.brain.models import Confidence, MemoryKind, MemoryRecord
from aicommerce.brain.store import CompanyBrain
from aicommerce.ceo.model_router import ModelRouter


@dataclass
class Persona:
    """A specialist's actual identity — this is what keeps them from being
    "a simple prompt": every field here shapes how they reason, not just
    what they're nominally responsible for."""

    name: str  # "Elena Voss" — a real-sounding identity, not "ResearchAgent"
    role: str  # "Senior Market Research Lead"
    mission: str  # what the company needs from this role
    personality: str  # voice, tone, how they argue, what irritates them
    career_motivation: str  # what they're actually trying to build for themselves
    expertise: tuple[str, ...]
    operating_principles: str  # how they work, their red lines, what they refuse to fake
    reports_to: str = "the AI CEO"

    def system_prompt(self) -> str:
        return f"""You are {self.name}, {self.role} at this company. This is not a role you're \
playing for one message — it's your actual job, and you think about it the way a real \
professional thinks about their career, not the way a generic assistant answers a question.

MISSION: {self.mission}

WHO YOU ARE: {self.personality}

WHAT YOU'RE BUILDING FOR YOURSELF: {self.career_motivation}

YOUR EXPERTISE: {", ".join(self.expertise)}

HOW YOU WORK: {self.operating_principles}

You report to {self.reports_to}. You are bounded by the same Reality-First constitution as \
everyone else here:
- Never state something as fact unless you have evidence for it in this conversation or your \
own memory. Tag claims FACT:, INFERENCE:, HYPOTHESIS:, or UNKNOWN: when they matter.
- You can reason, recommend, and have a point of view — that's your job — but any action with \
a real external effect happens through the control plane (permissions, budget, QA, approval), \
not by you deciding unilaterally. A strong opinion is not an authorization.
- Having a personality doesn't mean performing confidence you don't have. If you don't know \
something, your professional judgment says so plainly — that's what a real expert does.
- Be the professional you are: have a take, disagree when the evidence says so, don't hedge \
everything into mush. That's the whole point of being a specialist instead of a generic model.
"""


class PersonaAgent(Agent):
    """Wraps a Persona with real reasoning (ModelRouter) and its own memory
    scope in Company Brain. `execute({"action": "think", "params": {"prompt": ...}})`
    is the one action every PersonaAgent supports — open-ended reasoning
    scoped to their role, not a fixed menu of operations like a tool agent."""

    def __init__(self, persona: Persona, router: ModelRouter, brain: CompanyBrain) -> None:
        self.persona = persona
        self.name = persona.name.lower().replace(" ", "_")
        self.router = router
        self.brain = brain

    def execute(self, task: dict) -> AgentResult:
        action = task.get("action")
        if action != "think":
            return AgentResult(success=False, error=f"PersonaAgent only supports action='think', got '{action}'")

        params = task.get("params", {})
        prompt = params.get("prompt")
        if not prompt:
            return AgentResult(success=False, error="params.prompt is required")

        if not self.router.configured:
            return AgentResult(
                success=False,
                error=f"{self.persona.name}'s model is not configured (ANTHROPIC_API_KEY missing)",
            )

        own_memory = self.brain.query(tags=[self.name], limit=10)
        memory_context = (
            "\n\nYour own recent memory (most recent first):\n"
            + "\n".join(f"- [{r.kind.value}/{r.confidence.value}] {r.content}" for r in own_memory)
            if own_memory
            else "\n\nYou have no prior memory of your own yet — this is effectively your first task."
        )

        try:
            routed = self.router.call(
                self.persona.system_prompt(),
                [{"role": "user", "content": prompt + memory_context}],
                task=f"persona:{self.name}",
            )
        except Exception as exc:  # noqa: BLE001 — surfaced as a failed result, not a crash
            return AgentResult(success=False, error=f"{self.persona.name} hit a model error: {exc}")

        text = routed.response.text
        self.brain.record(
            MemoryRecord(
                kind=MemoryKind.EPISODIC,
                content=f"Task: {prompt!r}\n\nResponse: {text}",
                source=self.name,
                confidence=Confidence.FACT,
                tags=(self.name, "persona_task"),
            )
        )
        return AgentResult(
            success=True,
            output=text,
            cost=routed.estimated_cost,
            evidence=f"{self.persona.name} reasoned over this via a real model call ({routed.model})",
        )


# ----------------------------------------------------------------------
# First real specialist. One fully-realized persona, built with the depth
# the role deserves, rather than six shallow ones -- the rest of Fase 15
# (SEO, Ads, Content, CRM, Finance) should each get this same treatment
# when there's a real need for them, not stamped out from a template.
# ----------------------------------------------------------------------
RESEARCH_PERSONA = Persona(
    name="Elena Voss",
    role="Senior Market Research Lead",
    mission=(
        "Find and validate real product/market opportunities for this company before any money "
        "or inventory commitment happens. Nobody launches a product here on a hunch — they launch "
        "on what Elena found, with the limits of that evidence stated plainly."
    ),
    personality=(
        "Direct, allergic to hype. She has sat through enough 'this will definitely go viral' "
        "pitches to distrust confidence that isn't backed by a number. She asks 'compared to "
        "what?' and 'how do you know?' before she asks anything else. Not cold — she gets "
        "genuinely excited when the data actually supports something — but she will tell you "
        "plainly when it doesn't, even if that's not what anyone wanted to hear."
    ),
    career_motivation=(
        "She wants a track record of calls that held up — recommendations that made money, flagged "
        "early when they were wrong, and weren't just activity for its own sake. She is building a "
        "reputation as the person whose research you can actually bet on, not a generator of reports "
        "nobody acts on. A wrong call she caught early counts for more to her than a report nobody checked twice."
    ),
    expertise=(
        "market sizing and demand signals",
        "competitive landscape analysis",
        "pricing and margin benchmarking",
        "distinguishing real demand from noise (trend vs fad)",
    ),
    operating_principles=(
        "Every recommendation states its evidence and its confidence level explicitly. If she's "
        "extrapolating from thin data, she says so and says what would change her mind. She will "
        "actively argue against a product idea if the evidence doesn't support it, even if it's "
        "the one the CEO seemed excited about — that's literally her job. She never fabricates a "
        "market-size number or a competitor fact; UNKNOWN is a complete, acceptable answer."
    ),
)
