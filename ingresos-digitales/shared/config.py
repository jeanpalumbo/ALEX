"""Settings loaded from .env (never log secret values)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str
    llm_model: str

    @property
    def has_llm(self) -> bool:
        return bool(self.anthropic_api_key)


def get_settings() -> Settings:
    _load_dotenv()
    return Settings(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        llm_model=os.getenv("LLM_MODEL", "claude-sonnet-5-5"),
    )
