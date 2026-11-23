"""
Audit API (Section 14.6).
"""

from __future__ import annotations

from typing import Dict, Any
from fastapi import APIRouter
from app.agents.audit_agent import AuditAgent
from app.memory.store import MemoryStore

router = APIRouter(tags=["Audit"])
store = MemoryStore()
audit_agent = AuditAgent()


@router.get("/users/{user_id}/audit")
def get_user_audit_logs(user_id: str) -> Dict[str, Any]:
    logs = store.get_audit_logs(user_id)
    summary = audit_agent.summarize_audit_trail(logs)
    return {
        "user_id": user_id,
        "summary": summary,
        "logs": [l.model_dump() for l in logs],
    }
