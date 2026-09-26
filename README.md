# AI Commerce Operating System

An AI Commerce Operating System: an ecommerce company whose daily work is executed
by a coordinated organization of AI agents, governed by explicit policies, budgets,
permissions, evidence and human approvals.

See [`AI_COMMERCE_MASTER_CONTEXT.md`](./AI_COMMERCE_MASTER_CONTEXT.md) and
[`AI_COMMERCE_OS_MASTER_PLAN.md`](./AI_COMMERCE_OS_MASTER_PLAN.md) for the full
vision, principles and milestone plan. This README tracks **actual, verified
implementation status** — read `aicommerce/` and run `pytest` to check it yourself.

**Note on the master plan doc's Section 1:** it states "solo existe este
documento — no hay repo, carpeta ni implementación". That was true when it was
written, in a session that had lost this one. Jean confirmed on recovering this
conversation that this repo (with a working CEO Console, real model, 79 tests)
is the current, correct state — this README supersedes that doc's baseline
claim. The rest of that doc (constitution, architecture, milestone checklist,
definition of done) still applies and is the checklist used below.

## What you can do right now

Open the **CEO Console** in a browser and have a real conversation with the AI CEO —
it uses a real Anthropic model, with real tool-calling into the real Company
Brain / Control Plane / Orchestrator. Nothing here is a mock chatbot.

```bash
python run_ceo_console.py
# open http://127.0.0.1:8420/
```

You can:
- Chat with the CEO. It answers using `get_company_state`, `query_memory`,
  `list_agents`, `get_pending_approvals`, `propose_action`, `record_memory`,
  `set_objective` — real tool calls against the live system, visible in the
  "🔧" line under each of its replies.
- Set the current objective (also settable by asking the CEO directly).
- See pending approvals and **APPROVE / REJECT** them from the console — the
  decision is executed (or discarded) for real through the Orchestrator and
  logged to Company Brain.
- Watch budgets (daily / shopify / ceo_llm), registered agents, and the last
  ~50 Company Brain entries (decisions, episodes, etc.), refreshed every 5s.

## Status (Reality-First) — verified by running the code, not by reading old status text

| Component | Status | Evidence |
|---|---|---|
| Company Brain (SQLite, 6 memory kinds, supersede) | **OPERATIVO** | `aicommerce/brain/`, thread-safe (fixed 2026-09-26 — sqlite connections were crashing under FastAPI's threadpool), 5 tests |
| AgentRegistry / PermissionManager (RBAC, deny-by-default) / BudgetGuard (enforced) / ApprovalQueue / EventBus / ReadinessPreflight | **OPERATIVO** | `aicommerce/control_plane/`, 28 tests |
| Scheduler | **PARCIAL** | polling-based (`run_due()` must be called; nothing calls it automatically yet — see Next step). In-process only, no persistence across restarts. |
| AI CEO Orchestrator (OBSERVE→UNDERSTAND→DECIDE→ACT→MEASURE→LEARN) | **OPERATIVO** | `aicommerce/ceo/orchestrator.py` — every action goes through permissions → budget → agent → QA, and high-risk/irreversible actions stop at `PENDING_APPROVAL` until a human decides. 8 tests. |
| CEO chat (real Anthropic model, real tool-use loop) | **OPERATIVO** | `aicommerce/ceo/service.py` + `llm.py` + `tools.py`. Verified live: asked "analiza el estado actual y dime las 3 prioridades" → it called 10 real tools, correctly reported Shopify as unconfigured (it tried `read_shop`/`read_products`/`read_orders` and got real failures), tagged claims FACT/HYPOTHESIS, and proposed a real `create_product` action that correctly stopped at human approval. |
| CEO Console (web UI) | **OPERATIVO** | `aicommerce/webapp/` — FastAPI + vanilla JS, single page, no mocked panels. Chat, objective, approvals (with working Approve/Reject), budget, agents, memory all read/write the live backend. |
| Shopify Agent — reads | **PARCIAL / BLOQUEADO (falta credencial)** | Real Admin REST client implemented (`aicommerce/agents/shopify_agent.py`), covered by 5 tests with a mocked HTTP layer. **Blocked in this environment**: no `SHOPIFY_STORE`/`SHOPIFY_TOKEN` exist anywhere on this machine (checked `.env` files across the whole user profile) and the Shopify MCP connector available in *this Claude Code session* reported "connection invalidated" when queried — it is not usable by the standalone web server anyway (that MCP is scoped to interactive Claude sessions, not to an independent Python process). **Needs from you**: a Shopify Admin API access token (Admin → Apps → Develop apps) in `.env`. |
| Shopify Agent — writes (create/update/delete product, set price, set inventory) | **DESIGNED, gated correctly, blocked on credentials** | Code exists and is wired so writes can *only* be reached via `Orchestrator.run_cycle`, which enforces permission + budget + QA + (always, since writes are risk=high/irreversible) human approval. Verified live: proposing `create_product` produced a real pending approval; approving it correctly attempted the real Shopify call and failed cleanly with "SHOPIFY_STORE/SHOPIFY_TOKEN not set" — no crash, no bypass. |
| Autonomous scheduler-driven CEO ticks | **DISEÑADO, apagado por defecto** | Wired in `aicommerce/bootstrap.py` behind `AUTONOMOUS_LLM_TICKS=false`. Turning it on makes the CEO call the paid model on a timer, reserving/spending from the `ceo_llm` budget each time — deliberately not the default, since master context principle 13/28 says never silently route to a paid model. |
| Other specialized agents (Research, Ads, SEO, CRM, Finance, ...) | **NO EMPEZADO** | only `shopify` and the `qa`/`echo` stub agents exist. |
| Evolution Engine, production autonomy (Milestones 9-10) | **NO EMPEZADO** | as before — no shadow-mode grading, no self-proposed agent changes. |
| PROFILE (offline/sandbox/live) | **OPERATIVO** | `config.PROFILE`, default `offline`. In `offline`, `ShopifyAgent` refuses every real HTTP call — even with valid credentials — before it refuses for missing credentials. Verified: `PROFILE=offline` + real-looking creds still returns "PROFILE=offline: no real external calls are permitted". `sandbox`/`live` lift the gate (credentials still separately required). 2 tests. |
| Kill switch | **OPERATIVO** | `Orchestrator.engage_kill_switch()`/`disengage_kill_switch()`, checked first in `run_cycle` before permissions/budget/agent — while engaged, every proposed action (read or write) is denied and logged. Console has a **STOP**/**REANUDAR** button calling `POST /api/killswitch`. Verified live: engaged it, asked the CEO to read Shopify orders, it correctly reported the denial and did not attempt the call; disengaged and normal operation resumed. Chat/memory queries still work while engaged (they don't go through `run_cycle`). 4 tests. |
| Approval expiration (payload binding) | **PARCIAL** | Every approval now gets `deadline = now + APPROVAL_TTL_SECONDS` (default 1800s) and an expired pending request is excluded from `pending()`/cannot be decided. Approval is implicitly bound to the exact `params`/`budget_scope` snapshot taken at proposal time (stored in `ApprovalRequest.metadata`, not re-derived at decide time) — there is no API path to alter params before approving (proven by `test_eval_scenarios.py`, which asserts the decide endpoint's schema has no params/cost/action field). Not yet implemented: an explicit content hash for defense-in-depth beyond what's needed today. |
| CEO Console auth / CSRF | **PARCIAL** | Every `/api/*` call requires an `X-Console-Token` header matching a random token generated on first run and persisted to `.env`; the token is embedded server-side into the rendered page (never sent elsewhere) and the index page itself needs no token. This is a lightweight session/CSRF mitigation appropriate for a **loopback-only** tool (binds to 127.0.0.1 by default) — it is *not* real multi-user auth and must not be exposed beyond localhost as-is. |
| Scheduler + EventBus persistence, auto-run loop (Milestone 7) | **OPERATIVO** | `Scheduler`/`EventBus` optionally persist to SQLite (`data/scheduler.db`, `data/events.db`); a job's `last_run` survives a restart so it isn't re-fired immediately (verified with a test that simulates exactly that). A daemon thread started from the FastAPI `lifespan` calls `run_due()` every 30s automatically — verified live: watched `heartbeat`'s `last_run` go from `null` to a real timestamp with no manual trigger. One job's exception no longer blocks the rest of that tick, and a failed job is retried next tick rather than skipped. |
| Backup / restore (Milestone 7) | **OPERATIVO** | `aicommerce/backup.py`, exposed as `POST /api/backup` (create), `GET /api/backup` (list), `POST /api/backup/restore` (destructive, requires `confirm: true`). Plain file copies under `data/backups/<timestamp>/`. Verified live via curl: created a real backup of the running instance's data dir. |
| Audit/event stream (Milestone 2/7) | **OPERATIVO** | `Orchestrator` now publishes to the `EventBus` at every terminal outcome (`action.executed/denied/failed/qa_rejected/pending_approval`) and on kill-switch transitions — durable, queryable (`GET /api/events`, paginated `EventBus.query_persisted`), and shown live in the Console's **Activity/events** panel. Previously the bus existed but nothing published real events to it. |
| ModelRouter (Milestone 4) | **PARCIAL (un solo proveedor)** | `aicommerce/ceo/model_router.py` separates "which model / at what cost" from the CEO's chat loop, per the master plan's explicit ask. Every real model call now records provider/model/task/latency/input+output tokens/estimated cost/correlation id as a `model.call` event, and `CEOService` spends that estimate from the `ceo_llm` budget for real (verified live: two real calls landed as `model.call` events with real token counts, and `ceo_llm`'s `spent` moved from $0 to match). There is exactly one configured provider (Anthropic) — this does **not** fabricate a second provider or a fallback chain; that remains DISEÑADO until a second approved credential exists. |
| Evaluation suite (Milestone 9) | **PARCIAL** | `tests/test_eval_scenarios.py` runs 7 adversarial/edge scenarios against the real orchestrator/tools/API (not descriptions): prompt injection in agent content and in a CEO-written memory record stays inert data; double-approval can't double-spend; an empty objective is recorded not dropped; contradictory memory facts both survive (supersede is opt-in); a reserved budget is released, not leaked, on agent failure. Not yet built: shadow-mode grading against real historical decisions, drift thresholds, adversarial fuzzing beyond these fixed scenarios. |

**106 tests, all passing** (`python -m pytest`), no external network calls in the test
suite (Shopify HTTP calls are mocked; the LLM is a fake/scripted model in CEO tests;
the console auth tests use FastAPI's in-process `TestClient`).

## What I need from you to unblock Shopify

Add to `ai-commerce-os/.env` (copy from `.env.example`):
```
SHOPIFY_STORE=tu-tienda.myshopify.com
SHOPIFY_TOKEN=shpat_...   # Admin API access token: Shopify Admin -> Settings -> Apps -> Develop apps -> Create app -> Admin API access token, scopes read/write_products, read/write_orders, read/write_inventory, read_customers
```
Restart the server (`python run_ceo_console.py`) and the preflight badge will go
from DEGRADED to READY, and the CEO's `read_*` tool calls will return real data
instead of the clean "not configured" error they return today.

## Running

```bash
python -m pytest              # 106 tests
python run_ceo_console.py     # starts the CEO Console on http://127.0.0.1:8420
```

Copy `.env.example` to `.env` first if you haven't (an `ANTHROPIC_API_KEY` is
already present, copied from your existing `~/.env` on 2026-09-26 — never
committed to git). `CONSOLE_TOKEN` is generated automatically on first run and
written back to `.env` — you don't need to set it yourself. `PROFILE` defaults
to `offline`, so no agent makes real external calls until you set it to
`sandbox` or `live`.

## Stopping / kill switch

- **Stop the process**: close the terminal running `run_ceo_console.py`, or
  find the PID listening on the configured port and kill it — there's no
  separate "stop everything" script yet.
- **Stop new actions without stopping the process**: click **STOP** in the
  console header (or `POST /api/killswitch {"engaged": true, "reason": "..."}`).
  This blocks every new proposed action immediately; chat and memory browsing
  keep working so you can see what's going on. Click **REANUDAR** (or
  `engaged: false`) to resume.

## Talking to the CEO

Type into the chat box at the top-left. Good first messages:
- "Analiza el estado actual de la empresa y dime cuáles son las tres prioridades operativas siguientes."
- "Ejecuta la primera prioridad." (it will tell you what it can do automatically vs. what needs your approval or a missing credential)
- "¿Qué has aprendido hasta ahora?" (it will call `query_memory`)

## Approving / rejecting actions

Any action the CEO proposes with `risk in {high, critical}` or `reversible=False`
stops at **Pending Approvals** in the right panel, showing what it wants to do, why,
the requesting agent, estimated cost, risk and reversibility. Click **APPROVE** to
actually run it (through the same permission/budget/QA path) or **REJECT** to
discard it. Both are logged to Company Brain via the decision it already recorded
when escalating.

## Layout

```
aicommerce/
  config.py         Reads .env — no hardcoded secrets; PROFILE, CONSOLE_TOKEN, APPROVAL_TTL_SECONDS
  backup.py          backup_data_dir / restore_data_dir / list_backups
  bootstrap.py       Wires the one live System instance (brain, control plane, agents, CEO)
  brain/             Company Brain: persistent, provider-agnostic memory (SQLite, thread-safe)
  control_plane/     Agent registry, permissions, budget guard, approvals, events (persisted), scheduler (persisted), preflight
  agents/            Agent base class, stub agents, real ShopifyAgent (profile-gated)
  ceo/               state, llm (Anthropic wrapper), model_router (telemetry/cost), tools (LLM<->system bridge), service (chat loop), orchestrator (kill switch, event publishing)
  webapp/            FastAPI server (console-token auth, scheduler auto-run thread) + static/index.html (CEO Console)
tests/               106 tests covering every module above, including the CEO chat loop, Shopify agent (mocked HTTP), kill switch, backup/restore, and an adversarial evaluation suite
run_ceo_console.py   Entry point: starts the web server
```
