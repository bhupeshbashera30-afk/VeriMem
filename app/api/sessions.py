"""
Session Ingestion & Memory Processing API (Section 14.1 & 14.2).
"""

from __future__ import annotations

import uuid
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL, ENABLE_OFFLINE_HEURISTICS
from app.llm_client import AnthropicLLMClient, HeuristicLLMClient
from app.memory.conflict_detector import ConflictDetector
from app.memory.decision_controller import MemoryDecisionController
from app.memory.decomposer import AtomicFactDecomposer
from app.memory.extractor import MemoryCandidateExtractor
from app.memory.policy_engine import PolicyEngine
from app.memory.store import MemoryStore
from app.memory.verifier import EvidenceGroundingVerifier
from app.schemas import Speaker, Turn

router = APIRouter(prefix="/sessions", tags=["Sessions"])
store = MemoryStore()


def get_llm():
    if ANTHROPIC_API_KEY and not ENABLE_OFFLINE_HEURISTICS:
        return AnthropicLLMClient(model=ANTHROPIC_MODEL)
    return HeuristicLLMClient()


class AddTurnRequest(BaseModel):
    user_id: str
    speaker: str
    text: str


@router.post("/{session_id}/turns")
def add_turn(session_id: str, req: AddTurnRequest) -> Dict[str, Any]:
    try:
        spk = Speaker(req.speaker)
    except ValueError:
        spk = Speaker.USER

    turn_id = f"t_{uuid.uuid4().hex[:8]}"
    turn = Turn(
        id=turn_id,
        conversation_id=session_id,
        user_id=req.user_id,
        speaker=spk,
        text=req.text,
    )
    store.save_turn(turn)
    return {"turn_id": turn_id, "memory_processing_status": "queued"}


@router.post("/{session_id}/process-memory")
def process_session_memory(session_id: str) -> Dict[str, Any]:
    turns = store.get_turns_for_session(session_id)
    if not turns:
        raise HTTPException(status_code=404, detail="No turns found for this session")

    user_id = turns[0].user_id
    llm = get_llm()

    extractor = MemoryCandidateExtractor(llm)
    decomposer = AtomicFactDecomposer(llm)
    verifier = EvidenceGroundingVerifier(llm)
    conflict_detector = ConflictDetector(llm)
    policy_engine = PolicyEngine(llm)
    decision_controller = MemoryDecisionController()

    candidates = extractor.extract(turns)

    stored_count = 0
    updated_count = 0
    rejected_count = 0
    confirmation_count = 0

    existing_memories = store.get_user_memories(user_id, status="active")
    user_policies = store.get_user_policies(user_id)

    for cand in candidates:
        store.save_candidate(cand)

        # 1. Decompose facts
        facts = decomposer.decompose(cand)

        # 2. Verify evidence grounding
        grounding = verifier.verify(cand, facts, turns)

        # 3. Detect conflicts
        conflict = conflict_detector.detect_conflict(cand, existing_memories)

        # 4. Evaluate policies
        policy_action = policy_engine.evaluate_policies(cand, grounding.grounding_label, user_policies)

        # 5. Make final decision
        decision = decision_controller.decide(cand, grounding, conflict, policy_action)

        # 6. Commit write
        mem_item = store.commit_memory_decision(cand, grounding, decision)

        if decision.decision in ("STORE_ACTIVE", "STORE_UNCERTAIN"):
            stored_count += 1
        elif decision.decision in ("UPDATE_REPLACE", "UPDATE_TEMPORAL"):
            updated_count += 1
        elif decision.decision == "ASK_CONFIRMATION":
            confirmation_count += 1
        else:
            rejected_count += 1

    return {
        "session_id": session_id,
        "candidates": len(candidates),
        "stored": stored_count,
        "updated": updated_count,
        "rejected": rejected_count,
        "needs_confirmation": confirmation_count,
    }
