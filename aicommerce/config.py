"""Central config. Reads from environment / `.env` — never hardcodes secrets.

`.env` is gitignored (see .gitignore). `.env.example` documents every variable
this project reads, with empty/placeholder values.
"""
from __future__ import annotations

import os
import secrets
from pathlib import Path

from dotenv import load_dotenv, set_key

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(ENV_PATH)

# === Profile — offline (default) / sandbox / live ===
# Master-plan requirement: the system starts offline/mock by default. In
# "offline", ShopifyAgent refuses real HTTP calls even if credentials happen
# to be present — this is a distinct, harder gate than "not configured".
PROFILE = os.getenv("PROFILE", "offline").lower()
if PROFILE not in ("offline", "sandbox", "live"):
    PROFILE = "offline"

# === Local console auth (session + CSRF mitigation for the loopback UI) ===
# A random token is generated on first run and persisted to .env so it
# survives restarts. It is embedded server-side into the rendered page (never
# sent to any third party) and required as a header on every /api/* call —
# a cross-origin page cannot read it or attach a custom header without
# triggering a CORS preflight that this server does not answer.
CONSOLE_TOKEN = os.getenv("CONSOLE_TOKEN", "")
if not CONSOLE_TOKEN:
    CONSOLE_TOKEN = secrets.token_urlsafe(32)
    if ENV_PATH.exists():
        set_key(str(ENV_PATH), "CONSOLE_TOKEN", CONSOLE_TOKEN)

# === AI CEO model ===
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CEO_MODEL = os.getenv("CEO_MODEL", "claude-sonnet-5")

# === Opus technical review (optional) — an independent, stronger-model ===
# === second opinion for important decisions, via a real Anthropic call. ===
# === Uses ANTHROPIC_API_KEY (same key as the CEO's own model) unless     ===
# === OPUS_MODEL is left empty, in which case voting runs without Opus.   ===
OPUS_MODEL = os.getenv("OPUS_MODEL", "claude-opus-5-5")
OPUS_REVIEW_BUDGET_LIMIT = float(os.getenv("OPUS_REVIEW_BUDGET_LIMIT", "5.0"))
# Opus's vote in a technical vote counts for this many "votes" in the
# weighted tally (default 2x one persona's) -- Jean's explicit call that
# Opus's read should carry more weight than any single persona's, since
# it's consulted specifically as the independent technical authority for
# decisive moments, not for routine day-to-day work.
OPUS_VOTE_WEIGHT = int(os.getenv("OPUS_VOTE_WEIGHT", "2"))

# === Free-tier background model (optional) — for low-stakes autonomous ===
# === persona check-ins ONLY, never for real interactive reasoning.      ===
# Leave OPENROUTER_API_KEY empty to disable; autonomous check-ins then
# report blocked (not silently billed to the paid model).
# Default is a specific free model, not the "openrouter/free" auto-router
# alias -- verified live on 2026-10-04 that the alias can route a request
# to a content-safety classifier model instead of an actual chat model
# (got back a literal "User Safety: safe" instead of real reasoning).
# qwen/qwen3.8-27b:free was verified live to give real, coherent answers.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "qwen/qwen3.8-27b:free")

# === Local Ollama model (optional) — zero-cost, runs on Jean's own GPU,  ===
# === no account/API key, no shared-pool rate limits. Requires Ollama    ===
# === installed and running locally with OLLAMA_MODEL already pulled    ===
# === (`ollama pull <model>`) -- this code never installs Ollama, starts ===
# === the service, or pulls models for you. qwen2.5:7b was picked as the ===
# === default because it fits comfortably in 6GB of VRAM quantized; a    ===
# === ~27B model does NOT fit a 6GB card and will be extremely slow/OOM. ===
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

# === Shopify (optional — ShopifyAgent runs in DEGRADED/BLOCKED mode without it) ===
SHOPIFY_STORE = os.getenv("SHOPIFY_STORE", "")
SHOPIFY_TOKEN = os.getenv("SHOPIFY_TOKEN", "")
SHOPIFY_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2024-10")

# === Autonomy ===
# Off by default: an autonomous tick that calls the LLM costs real money every
# time it fires. Turning this on is an explicit, informed choice, not a default.
AUTONOMOUS_LLM_TICKS = os.getenv("AUTONOMOUS_LLM_TICKS", "false").lower() == "true"
AUTONOMOUS_TICK_INTERVAL_SECONDS = int(os.getenv("AUTONOMOUS_TICK_INTERVAL_SECONDS", "3600"))
AUTONOMOUS_TICK_ESTIMATED_COST = float(os.getenv("AUTONOMOUS_TICK_ESTIMATED_COST", "0.05"))

# Same idea, one level down: each persona (research/store_ops/engineering_lead)
# can check in on its own schedule instead of only acting when the CEO
# explicitly delegates to it. Off by default for the same reason -- every
# tick is a real, separately-budgeted model call per persona.
AUTONOMOUS_PERSONA_TICKS = os.getenv("AUTONOMOUS_PERSONA_TICKS", "false").lower() == "true"
AUTONOMOUS_PERSONA_TICK_INTERVAL_SECONDS = int(os.getenv("AUTONOMOUS_PERSONA_TICK_INTERVAL_SECONDS", "14400"))  # 4h
AUTONOMOUS_PERSONA_TICK_ESTIMATED_COST = float(os.getenv("AUTONOMOUS_PERSONA_TICK_ESTIMATED_COST", "0.05"))

# === Web server ===
HOST = os.getenv("CEO_CONSOLE_HOST", "127.0.0.1")
PORT = int(os.getenv("CEO_CONSOLE_PORT", "8420"))

# === Data ===
DATA_DIR = ROOT_DIR / "data"
BRAIN_DB_PATH = DATA_DIR / "brain.db"

# === Budgets (initial limits; adjustable later via the API) ===
DAILY_BUDGET_LIMIT = float(os.getenv("DAILY_BUDGET_LIMIT", "20.0"))
SHOPIFY_BUDGET_LIMIT = float(os.getenv("SHOPIFY_BUDGET_LIMIT", "10.0"))
CEO_LLM_BUDGET_LIMIT = float(os.getenv("CEO_LLM_BUDGET_LIMIT", "5.0"))
ENGINEERING_BUDGET_LIMIT = float(os.getenv("ENGINEERING_BUDGET_LIMIT", "0.0"))  # cost=0 for local git/tests today
RESEARCH_BUDGET_LIMIT = float(os.getenv("RESEARCH_BUDGET_LIMIT", "5.0"))  # persona agents call the real model
STORE_OPS_BUDGET_LIMIT = float(os.getenv("STORE_OPS_BUDGET_LIMIT", "5.0"))
ENGINEERING_LEAD_BUDGET_LIMIT = float(os.getenv("ENGINEERING_LEAD_BUDGET_LIMIT", "5.0"))
FINANCE_BUDGET_LIMIT = float(os.getenv("FINANCE_BUDGET_LIMIT", "5.0"))
MARKETING_BUDGET_LIMIT = float(os.getenv("MARKETING_BUDGET_LIMIT", "5.0"))
DESIGN_BUDGET_LIMIT = float(os.getenv("DESIGN_BUDGET_LIMIT", "5.0"))
RND_BUDGET_LIMIT = float(os.getenv("RND_BUDGET_LIMIT", "5.0"))

# === Telegram bridge — talk to the CEO from anywhere, no shared network needed ===
# Leave TELEGRAM_BOT_TOKEN empty to disable the bridge entirely (default).
# TELEGRAM_ALLOWED_CHAT_ID starts empty; the bridge tells the first sender
# their chat_id in "bootstrap mode" without forwarding anything to the CEO
# until you set this and restart.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ALLOWED_CHAT_ID = os.getenv("TELEGRAM_ALLOWED_CHAT_ID", "")

# === Approvals ===
# Every approval request gets a deadline (now + this many seconds) unless the
# caller sets one explicitly. An expired pending request can no longer be
# approved — it must be re-proposed, so a stale approval can't be executed
# against a payload/context that has since moved on.
APPROVAL_TTL_SECONDS = int(os.getenv("APPROVAL_TTL_SECONDS", "1800"))
