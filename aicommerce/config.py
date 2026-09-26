"""Central config. Reads from environment / `.env` — never hardcodes secrets.

`.env` is gitignored (see .gitignore). `.env.example` documents every variable
this project reads, with empty/placeholder values.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

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
