# AI Commerce Operating System

An AI Commerce Operating System: an ecommerce company whose daily work is executed
by a coordinated organization of AI agents, governed by explicit policies, budgets,
permissions, evidence and human approvals.

See [`AI_COMMERCE_MASTER_CONTEXT.md`](./AI_COMMERCE_MASTER_CONTEXT.md) for the full
vision, principles and roadmap. This README tracks **actual implementation status**,
verifiable by reading `aicommerce/` and running `pytest`.

## Status (Reality-First)

This project was bootstrapped on 2026-09-26. Nothing existed before this. Status below
uses the classification from the master context: IMPLEMENTED / PARTIAL / DESIGNED /
BLOCKED / DEPRECATED / UNKNOWN.

| Phase | Component | Status | Notes |
|---|---|---|---|
| 0 | Repo / tests / structure | IMPLEMENTED | this repo |
| 1 | Company Brain (persistent memory) | IMPLEMENTED | SQLite-backed, `aicommerce/brain/` |
| 2 | Agent Registry | IMPLEMENTED | in-memory, `aicommerce/control_plane/registry.py` |
| 2 | Permissions (RBAC/scopes) | IMPLEMENTED | `aicommerce/control_plane/permissions.py` |
| 2 | Budget Guard | IMPLEMENTED | enforces, not advisory; `aicommerce/control_plane/budget.py` |
| 2 | Approval Queue | IMPLEMENTED | `aicommerce/control_plane/approvals.py` |
| 2 | Readiness Preflight | IMPLEMENTED | `aicommerce/control_plane/preflight.py` |
| 3 | Event Bus | IMPLEMENTED | in-process pub/sub, `aicommerce/control_plane/events.py` |
| 3 | Scheduler | PARTIAL | polling-based, in-process only, no persistence across restarts |
| 4 | Shopify integration | DESIGNED | not implemented — no store/credentials configured yet |
| 5 | AI CEO orchestrator | PARTIAL | `aicommerce/ceo/orchestrator.py` runs the OBSERVE→...→IMPROVE loop against the registry/budget/approval/brain, but only stub agents exist |
| 6 | Specialized agents (Research, Product, Brand, ...) | PARTIAL | only `EchoAgent`-style stub agents exist for wiring/testing; no real research/ads/SEO capability yet |
| 7 | Evaluation | UNKNOWN | not started |
| 8 | Evolution Engine | UNKNOWN | not started |
| 9 | Production autonomous operation | UNKNOWN | not started |

Nothing here is connected to a real Shopify store, real ad accounts, or real money.
Everything is local, in-process, and safe to run repeatedly.

## Running

```bash
python -m pytest
```

## Layout

```
aicommerce/
  brain/            Company Brain: persistent, provider-agnostic memory (SQLite)
  control_plane/    Agent registry, permissions, budget guard, approvals, events, scheduler, preflight
  agents/           Agent base class + stub agents
  ceo/              AI CEO orchestrator (OBSERVE -> UNDERSTAND -> DECIDE -> ACT -> MEASURE -> LEARN -> IMPROVE)
tests/              pytest suite covering every module above
```
