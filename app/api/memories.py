"""
Active Memories API (Section 14.3).
"""

from __future__ import annotations

from typing import Dict, Any, Optional
from fastapi import APIRouter
from app.memory.store import MemoryStore

router = APIRouter(prefix="/users", tags=["Memories"])
store = MemoryStore()


@router.get("/{user_id}/memories")
def get_user_memories(user_id: str, status: Optional[str] = "active") -> Dict[str, Any]:
    memories = store.get_user_memories(user_id, status=status)
    return {
        "user_id": user_id,
        "count": len(memories),
        "memories": [
            {
                "id": m.id,
                "memory_text": m.memory_text,
                "type": m.memory_type.value,
                "confidence": m.confidence,
                "status": m.status.value,
                "version": m.version,
                "evidence_turn_ids": m.evidence_turn_ids,
                "created_at": m.created_at.isoformat(),
            }
            for m in memories
        ],
    }
