"""CEO Console — FastAPI backend.

Every endpoint reads/writes the real, live `System` (see `aicommerce.bootstrap`).
There is no mock data path: if Shopify or the LLM isn't configured, the
endpoints say so explicitly (BLOCKED/DEGRADED), they don't fabricate output.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from aicommerce.bootstrap import get_system
from aicommerce.brain.models import MemoryKind

app = FastAPI(title="AI Commerce OS — CEO Console")

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


# ----------------------------------------------------------------------
# State / preflight
# ----------------------------------------------------------------------
@app.get("/api/state")
def get_state() -> dict:
    system = get_system()
    report = system.preflight.run()
    return {
        "ceo_state": system.ceo.state.to_dict(),
        "llm_configured": system.ceo.llm_configured,
        "preflight": {
            "result": report.result.value,
            "failed_checks": report.failed_checks,
            "reasons": report.reasons,
        },
        "pending_approvals": len(system.approvals.pending()),
        "agent_count": len(system.registry.list_agents()),
    }


# ----------------------------------------------------------------------
# Chat
# ----------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str


@app.post("/api/chat")
def post_chat(body: ChatRequest) -> dict:
    system = get_system()
    turn = system.ceo.chat(body.message)
    return {
        "role": turn.role,
        "content": turn.content,
        "tool_activity": turn.tool_activity,
        "timestamp": turn.timestamp.isoformat(),
    }


@app.get("/api/chat/history")
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


@app.post("/api/objective")
def post_objective(body: ObjectiveRequest) -> dict:
    system = get_system()
    return system.ceo.tools.dispatch("set_objective", {"objective": body.objective})


# ----------------------------------------------------------------------
# Agents / budget
# ----------------------------------------------------------------------
@app.get("/api/agents")
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


@app.get("/api/budget")
def get_budget() -> dict:
    system = get_system()
    return {"budgets": system.budget.all_status()}


# ----------------------------------------------------------------------
# Approvals
# ----------------------------------------------------------------------
@app.get("/api/approvals")
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
            }
            for r in system.approvals.pending()
        ]
    }


class ApprovalDecision(BaseModel):
    approve: bool
    decided_by: str = "jean"
    note: str = ""


@app.post("/api/approvals/{request_id}/decide")
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
@app.get("/api/brain")
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
@app.get("/api/events")
def get_events(type: Optional[str] = None, limit: int = 50) -> dict:
    system = get_system()
    events = system.events.history(type)[-limit:]
    return {
        "events": [{"type": e.type, "payload": e.payload, "timestamp": e.timestamp.isoformat()} for e in events]
    }


@app.get("/api/scheduler")
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


@app.post("/api/scheduler/run")
def run_scheduler() -> dict:
    system = get_system()
    ran = system.scheduler.run_due()
    return {"ran": ran}
