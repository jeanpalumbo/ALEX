"""CEO Console — FastAPI backend.

Every endpoint reads/writes the real, live `System` (see `aicommerce.bootstrap`).
There is no mock data path: if Shopify or the LLM isn't configured, the
endpoints say so explicitly (BLOCKED/DEGRADED), they don't fabricate output.

Local auth / CSRF note: this app is meant to bind to 127.0.0.1 only. Every
`/api/*` call must carry the `X-Console-Token` header matching
`config.CONSOLE_TOKEN` (a random value generated on first run and persisted
to `.env`). The token is embedded server-side into the rendered `index.html`
and read from there by the page's own JS — a third-party page cannot read it
(different origin) and cannot attach a custom header cross-origin without a
CORS preflight, which this server never answers (no CORS middleware is
installed). This is a lightweight session/CSRF mitigation appropriate for a
single-user loopback tool, not a substitute for real auth if this is ever
exposed beyond localhost — don't do that.
"""
from __future__ import annotations

import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from aicommerce import backup, config
from aicommerce.bootstrap import get_system
from aicommerce.brain.models import MemoryKind
from aicommerce.reports import generate_status_report

_scheduler_stop = threading.Event()


def _record_job_error(system, job_name: str, exc: Exception) -> None:
    from aicommerce.brain.models import Confidence, MemoryKind, MemoryRecord

    system.brain.record(
        MemoryRecord(
            kind=MemoryKind.EPISODIC,
            content=f"Scheduler job '{job_name}' raised {type(exc).__name__}: {exc}. "
            "last_run was not advanced; it will be retried next tick.",
            source="scheduler",
            confidence=Confidence.FACT,
            tags=("scheduler_error", job_name),
        )
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Milestone 7: the Scheduler needs something calling `run_due()`
    periodically. Previously nothing did — it only ran when a test or a
    manual `POST /api/scheduler/run` called it. Now the server itself drives
    it every 30s in a daemon thread for as long as the process is up."""
    system = get_system()

    def loop() -> None:
        while not _scheduler_stop.wait(30):
            system.scheduler.run_due(on_error=lambda name, exc: _record_job_error(system, name, exc))

    thread = threading.Thread(target=loop, name="scheduler-loop", daemon=True)
    thread.start()
    try:
        yield
    finally:
        _scheduler_stop.set()


app = FastAPI(title="AI Commerce OS — CEO Console", lifespan=lifespan)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def require_console_token(x_console_token: Optional[str] = Header(None)) -> None:
    if not x_console_token or x_console_token != config.CONSOLE_TOKEN:
        raise HTTPException(status_code=401, detail="missing or invalid X-Console-Token header")


api = APIRouter(prefix="/api", dependencies=[Depends(require_console_token)])


@app.get("/")
def index() -> HTMLResponse:
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    html = html.replace("__CONSOLE_TOKEN__", config.CONSOLE_TOKEN)
    return HTMLResponse(html)


# ----------------------------------------------------------------------
# State / preflight
# ----------------------------------------------------------------------
@api.get("/state")
def get_state() -> dict:
    system = get_system()
    report = system.preflight.run()
    return {
        "ceo_state": system.ceo.state.to_dict(),
        "llm_configured": system.ceo.llm_configured,
        "profile": config.PROFILE,
        "kill_switch_engaged": system.orchestrator.kill_switch_engaged,
        "kill_switch_reason": system.orchestrator.kill_switch_reason,
        "preflight": {
            "result": report.result.value,
            "failed_checks": report.failed_checks,
            "reasons": report.reasons,
        },
        "pending_approvals": len(system.approvals.pending()),
        "agent_count": len(system.registry.list_agents()),
    }


# ----------------------------------------------------------------------
# Kill switch
# ----------------------------------------------------------------------
class KillSwitchRequest(BaseModel):
    engaged: bool
    reason: str = ""
    by: str = "jean"


@api.post("/killswitch")
def set_kill_switch(body: KillSwitchRequest) -> dict:
    system = get_system()
    if body.engaged:
        system.orchestrator.engage_kill_switch(body.reason or "no reason given", by=body.by)
    else:
        system.orchestrator.disengage_kill_switch(by=body.by)
    return {
        "kill_switch_engaged": system.orchestrator.kill_switch_engaged,
        "kill_switch_reason": system.orchestrator.kill_switch_reason,
    }


# ----------------------------------------------------------------------
# Chat
# ----------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str


@api.post("/chat")
def post_chat(body: ChatRequest) -> dict:
    system = get_system()
    turn = system.ceo.chat(body.message)
    return {
        "role": turn.role,
        "content": turn.content,
        "tool_activity": turn.tool_activity,
        "timestamp": turn.timestamp.isoformat(),
    }


@api.get("/chat/history")
def get_chat_history() -> dict:
    system = get_system()
    return {
        "history": [
            {
                "role": t.role,
                "content": t.content,
                "tool_activity": t.tool_activity,
                "timestamp": t.timestamp.isoformat(),
            }
            for t in system.ceo.history
        ]
    }


class ObjectiveRequest(BaseModel):
    objective: str


@api.post("/objective")
def post_objective(body: ObjectiveRequest) -> dict:
    system = get_system()
    return system.ceo.tools.dispatch("set_objective", {"objective": body.objective})


# ----------------------------------------------------------------------
# Agents / budget
# ----------------------------------------------------------------------
@api.get("/agents")
def get_agents() -> dict:
    system = get_system()
    return {
        "agents": [
            {
                "name": s.name,
                "mission": s.mission,
                "authority": list(s.authority),
                "tools": list(s.tools),
                "limits": s.limits,
                "kpis": list(s.kpis),
            }
            for s in system.registry.list_agents()
        ]
    }


@api.get("/budget")
def get_budget() -> dict:
    system = get_system()
    return {"budgets": system.budget.all_status()}


# ----------------------------------------------------------------------
# Approvals
# ----------------------------------------------------------------------
@api.get("/approvals")
def get_approvals() -> dict:
    system = get_system()
    return {
        "pending": [
            {
                "id": r.id,
                "action": r.action,
                "agent": r.agent,
                "reason": r.reason,
                "evidence": r.evidence,
                "impact": r.impact,
                "cost": r.cost,
                "risk": r.risk,
                "reversible": r.reversible,
                "proposal": r.proposal,
                "created_at": r.created_at.isoformat(),
                "deadline": r.deadline.isoformat() if r.deadline else None,
            }
            for r in system.approvals.pending()
        ]
    }


class ApprovalDecision(BaseModel):
    approve: bool
    decided_by: str = "jean"
    note: str = ""


@api.post("/approvals/{request_id}/decide")
def decide_approval(request_id: str, body: ApprovalDecision) -> dict:
    system = get_system()
    try:
        if body.approve:
            outcome = system.orchestrator.approve_and_execute(
                request_id,
                decided_by=body.decided_by,
                objective=system.ceo.state.objective or "human-approved action",
                note=body.note,
            )
            return {"status": outcome.status.value, "detail": outcome.detail}
        else:
            request = system.orchestrator.reject(request_id, decided_by=body.decided_by, note=body.note)
            return {"status": request.status.value}
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ----------------------------------------------------------------------
# Company Brain
# ----------------------------------------------------------------------
@api.get("/brain")
def get_brain(kind: Optional[str] = None, tag: Optional[str] = None, limit: int = 50) -> dict:
    system = get_system()
    records = system.brain.query(
        kind=MemoryKind(kind) if kind else None,
        tags=[tag] if tag else None,
        limit=limit,
    )
    return {
        "records": [
            {
                "id": r.id,
                "kind": r.kind.value,
                "content": r.content,
                "source": r.source,
                "confidence": r.confidence.value,
                "tags": list(r.tags),
                "timestamp": r.timestamp.isoformat(),
            }
            for r in records
        ]
    }


# ----------------------------------------------------------------------
# Events / scheduler
# ----------------------------------------------------------------------
@api.get("/events")
def get_events(type: Optional[str] = None, limit: int = 50) -> dict:
    system = get_system()
    events = system.events.history(type)[-limit:]
    return {
        "events": [{"type": e.type, "payload": e.payload, "timestamp": e.timestamp.isoformat()} for e in events]
    }


@api.get("/scheduler")
def get_scheduler() -> dict:
    system = get_system()
    return {
        "jobs": [
            {
                "name": j.name,
                "interval_seconds": j.interval.total_seconds(),
                "last_run": j.last_run.isoformat() if j.last_run else None,
            }
            for j in system.scheduler.jobs()
        ]
    }


@api.post("/scheduler/run")
def run_scheduler() -> dict:
    system = get_system()
    ran = system.scheduler.run_due()
    return {"ran": ran}


# ----------------------------------------------------------------------
# Backup / restore
# ----------------------------------------------------------------------
@api.post("/backup")
def create_backup() -> dict:
    dest = backup.backup_data_dir(config.DATA_DIR)
    return {"backup": dest.name, "path": str(dest)}


@api.get("/backup")
def list_backups() -> dict:
    return {"backups": [p.name for p in backup.list_backups(config.DATA_DIR)]}


class RestoreRequest(BaseModel):
    backup: str
    confirm: bool = False


@api.post("/backup/restore")
def restore_backup(body: RestoreRequest) -> dict:
    if not body.confirm:
        raise HTTPException(
            status_code=400,
            detail="restore overwrites the live database files — resend with confirm: true",
        )
    backup_dir = config.DATA_DIR / "backups" / body.backup
    try:
        restored = backup.restore_data_dir(backup_dir, config.DATA_DIR)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"restored": restored, "note": "restart the server for the restored data to take effect"}


# ----------------------------------------------------------------------
# Reports (master plan Fase 3)
# ----------------------------------------------------------------------
@api.get("/reports/status")
def get_status_report(period: str = "daily") -> dict:
    system = get_system()
    report = generate_status_report(
        system.orchestrator, system.ceo.state, system.preflight.run(), registry=system.registry, period=period
    )
    return report.to_dict()


app.include_router(api)
