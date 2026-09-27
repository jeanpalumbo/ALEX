# Runbook — AI Commerce OS / CEO Console

Master plan Milestone 10 asks for this explicitly. Every command below was
actually run against this repo on 2026-09-27 to write this document — it is
not a description of what should work.

## Start

```bash
cd C:\Users\Jean\ai-commerce-os
python run_ceo_console.py
```

Open `http://127.0.0.1:8420/`. First boot with no `.env`: copy
`.env.example` to `.env` first — `ANTHROPIC_API_KEY` must be set for chat to
work; `CONSOLE_TOKEN` is generated automatically and written back to `.env`.

**How to tell it actually started, not just that the process exists:**
```bash
curl -s -H "X-Console-Token: $(python -c "from aicommerce import config; print(config.CONSOLE_TOKEN)")" http://127.0.0.1:8420/api/state
```
A JSON body with `"preflight"` in it means it's up. Connection refused means
it isn't — check `server.log` (if you redirected stdout there) for a
traceback, most commonly a port already in use or a missing dependency.

## Stop

```bash
# find the PID bound to the console port (default 8420), then:
netstat -ano | grep ":8420" | grep LISTEN     # Windows/Git Bash
taskkill //F //PID <pid>
```
There is no separate stop script — killing the process is the only way to
fully stop it. Killing it does **not** lose data: Company Brain, the event
log and the scheduler's job state are all in `data/*.db` on disk.

## Kill switch (stop new actions without stopping the process)

Use this instead of killing the process when you want the system to stay
observable (chat, memory, budget, events) but refuse to take any new action:

```bash
curl -s -H "X-Console-Token: $TOKEN" -H "Content-Type: application/json" \
  -X POST http://127.0.0.1:8420/api/killswitch \
  -d '{"engaged": true, "reason": "why you're stopping it", "by": "jean"}'
```
Or click **STOP** in the console header. Every `propose_action` call and
every `Orchestrator.run_cycle` call is refused while engaged — verified by
`tests/test_kill_switch_and_profile.py` and live in this session (engaged
it, asked the CEO to read Shopify orders over chat, it reported the denial
instead of attempting the call). Disengage the same way with
`"engaged": false`.

## Backup

```bash
curl -s -H "X-Console-Token: $TOKEN" -X POST http://127.0.0.1:8420/api/backup
```
Copies `data/brain.db`, `data/events.db`, `data/scheduler.db` into
`data/backups/<UTC-timestamp>/`. List existing backups:
```bash
curl -s -H "X-Console-Token: $TOKEN" http://127.0.0.1:8420/api/backup
```

## Restore

**Destructive** — overwrites the live DB files. Stop the server first (a
running process holds open SQLite connections to the files being replaced):
```bash
# 1. stop the server (see "Stop" above)
# 2. copy the backup files back by hand, OR start the server and call:
curl -s -H "X-Console-Token: $TOKEN" -H "Content-Type: application/json" \
  -X POST http://127.0.0.1:8420/api/backup/restore \
  -d '{"backup": "<folder-name-from-the-list-above>", "confirm": true}'
# 3. restart the server so it reopens the restored files
```

## Rotating secrets

**`CONSOLE_TOKEN`** (the header every `/api/*` call needs): delete the line
from `.env` and restart — `aicommerce/config.py` generates a fresh one and
writes it back on the next import. Every open browser tab needs a hard
reload afterward (it re-embeds the new token server-side into `index.html`
on each page load).

**`ANTHROPIC_API_KEY`**: edit `.env` directly, restart the server. Never
commit `.env` — it's gitignored; verify with `git status` that it doesn't
show up before any commit.

## Incidents

1. Engage the kill switch first if an agent might be about to do something
   wrong — it's non-destructive and instant.
2. Check `GET /api/events?limit=50` and `GET /api/brain?limit=50` for what
   actually happened, in order, with timestamps — this is the audit trail,
   not a guess.
3. If the process itself is unhealthy (hung, crash-looping), kill it, take
   note of `server.log`, then restart. Company Brain/events/scheduler state
   survive because they're on disk, not in memory only.
4. If a write action against a real external system (once Shopify
   credentials exist) may have partially applied, do **not** immediately
   retry — read the current external state first and reconcile by hand
   before proposing the same action again. Nothing in this codebase
   auto-retries an uncertain external effect.
5. Back up (`POST /api/backup`) before any recovery action that touches the
   DB files directly.

## Updating the code

```bash
cd C:\Users\Jean\ai-commerce-os
python -m pytest -q          # must be green before touching the running server
# stop the server, pull/apply changes, restart
```
There's no hot-reload in production mode; `run_ceo_console.py` starts
uvicorn without `reload=True` on purpose (predictable restarts, no surprise
mid-request reloads).

## Known limitations (read before relying on this in an incident)

- Auth is a single shared token appropriate for one person on loopback
  (127.0.0.1) only. Do not bind `CEO_CONSOLE_HOST` to `0.0.0.0` or expose
  this port to a network with more than one person on it.
- Restoring a backup while the server is running against the same files is
  unsafe (SQLite file replaced under an open connection) — always restart
  after a restore.
- The kill switch is persisted (`data/kill_switch.db`) — if you engage it
  and then kill the process as part of an incident, it comes back up still
  engaged on the next start. Verified live on 2026-09-27: engaged it,
  killed the real process, restarted, `GET /api/state` still showed
  `kill_switch_engaged: true` with the original reason. You must disengage
  it explicitly (`{"engaged": false}`) once the incident is resolved.
