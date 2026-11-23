"""
Conflict and Update Detector (Section 7.5 & Algorithm 15.3).

Compares new candidate memories with active stored memories to classify conflicts & temporal updates.
"""

from __future__ import annotations

from typing import List, Optional
from app.llm_client import LLMClient
from app.schemas import (
    ConflictResult,
    ConflictStatus,
    ConflictType,
    MemoryCandidate,
    MemoryItem,
)

_SYSTEM_PROMPT = """You are the Conflict and Update Detector in VeriMem.
Compare a new candidate memory against existing active memories.

Conflict Types:
- "value_conflict": Direct contradiction (e.g. "likes X" vs "dislikes X")
- "temporal_update": Fact changed over time (e.g. "unemployed" -> "got job")
- "preference_shift": Shift in user preference (e.g. "disliked public speaking" -> "enjoys lectures now")
- "identity_conflict": Conflicting name, location, age, occupation
- "relationship_conflict": Conflicting relationship details
- "goal_conflict": New project/personal goal replacing old goal
- "no_conflict": No contradiction found

Status options:
- "no_conflict"
- "update_required"
- "temporal_both"
- "require_confirmation"

Return ONLY JSON matching:
{
  "conflict_status": "no_conflict"|"update_required"|"temporal_both"|"require_confirmation",
  "conflict_type": "value_conflict"|"temporal_update"|"preference_shift"|"identity_conflict"|"relationship_conflict"|"goal_conflict"|"no_conflict",
  "related_memory_ids": ["..."],
  "reason": "...",
  "recommended_action": "store_new"|"retire_old_and_store_new"|"keep_both_temporal"|"ask_user"
}
"""


class ConflictDetector:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def detect_conflict(
        self, candidate: MemoryCandidate, existing_memories: List[MemoryItem]
    ) -> ConflictResult:
        if not existing_memories:
            return ConflictResult(
                candidate_id=candidate.id,
                conflict_status=ConflictStatus.NO_CONFLICT,
                conflict_type=ConflictType.NO_CONFLICT,
                reason="No prior active memories exist for comparison.",
                recommended_action="store_new",
            )

        active_mem_block = "\n".join(
            f'- mem_id={m.id} [{m.memory_type.value}]: "{m.memory_text}"'
            for m in existing_memories
        )

        prompt = (
            f'NEW CANDIDATE MEMORY [{candidate.memory_type.value}]:\n"{candidate.memory_text}"\n\n'
            f"EXISTING ACTIVE MEMORIES:\n{active_mem_block}"
        )

        res = self.llm_client.complete_json(_SYSTEM_PROMPT, prompt)

        try:
            status = ConflictStatus(res.get("conflict_status", "no_conflict"))
        except ValueError:
            status = ConflictStatus.NO_CONFLICT

        try:
            c_type = ConflictType(res.get("conflict_type", "no_conflict"))
        except ValueError:
            c_type = ConflictType.NO_CONFLICT

        return ConflictResult(
            candidate_id=candidate.id,
            conflict_status=status,
            related_memory_ids=res.get("related_memory_ids", []),
            conflict_type=c_type,
            reason=res.get("reason"),
            recommended_action=res.get("recommended_action", "store_new"),
        )
