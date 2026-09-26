"""Base class for specialized agents (Research, Product, Brand, ... — master
context section 7). Real capability (calling Shopify, ad platforms, etc.) is
added by subclasses; none of that exists yet, so only stub agents ship here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:
    success: bool
    output: Any = None
    cost: float = 0.0
    evidence: str = ""
    error: str = ""
    metadata: dict = field(default_factory=dict)


class Agent:
    """Subclasses implement `execute`. `name` must match the name the agent is
    registered under in the AgentRegistry."""

    name: str = "unnamed-agent"

    def execute(self, task: dict) -> AgentResult:
        raise NotImplementedError
