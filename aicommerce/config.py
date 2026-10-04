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
