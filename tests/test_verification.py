"""
Tests for Evidence Grounding Verification (Section 7.3 & Section 21 Demo).
"""

from __future__ import annotations

import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.llm_client import HeuristicLLMClient
from app.memory.decomposer import AtomicFactDecomposer
from app.memory.verifier import EvidenceGroundingVerifier
from app.schemas import GroundingLabel, MemoryCandidate, MemoryType, Speaker, Turn


def test_verification_user_supported_vs_assistant_originated():
    turns = [
        Turn(id="t_001", conversation_id="s_001", user_id="u_001", speaker=Speaker.USER, text="I am making a major project on hallucination-aware memory."),
        Turn(id="t_002", conversation_id="s_001", user_id="u_001", speaker=Speaker.ASSISTANT, text="Since you are a final-year computer science student, this fits your course."),
    ]
    turns_dict = {t.id: t for t in turns}
    llm = HeuristicLLMClient()
    decomposer = AtomicFactDecomposer(llm)
    verifier = EvidenceGroundingVerifier(llm)

    # 1. User candidate
    user_cand = MemoryCandidate(
        id="mc_001",
        user_id="u_001",
        memory_text="User is making a major project on hallucination-aware memory.",
        memory_type=MemoryType.GOAL,
        source_turn_ids=["t_001"],
        source_speaker=Speaker.USER,
        extraction_confidence=0.9,
    )
    user_facts = decomposer.decompose(user_cand)
    user_res = verifier.verify(user_cand, user_facts, turns)
    assert user_res.grounding_label in (GroundingLabel.SUPPORTED, GroundingLabel.PARTIALLY_SUPPORTED)

    # 2. Assistant unconfirmed candidate
    asst_cand = MemoryCandidate(
        id="mc_002",
        user_id="u_001",
        memory_text="User is a final-year computer science student.",
        memory_type=MemoryType.PERSONA,
        source_turn_ids=["t_002"],
        source_speaker=Speaker.ASSISTANT,
        extraction_confidence=0.7,
    )
    asst_facts = decomposer.decompose(asst_cand)
    asst_res = verifier.verify(asst_cand, asst_facts, [turns_dict["t_002"]])
    assert asst_res.grounding_label == GroundingLabel.ASSISTANT_ORIGINATED
    print("[PASS] Verification test passed.")


if __name__ == "__main__":
    test_verification_user_supported_vs_assistant_originated()
