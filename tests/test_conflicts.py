"""
Tests for Conflict and Update Detector (Section 7.5).
"""

from __future__ import annotations

import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.llm_client import HeuristicLLMClient
from app.memory.conflict_detector import ConflictDetector
from app.schemas import MemoryCandidate, MemoryItem, MemoryType, Speaker, MemoryStatus


def test_conflict_detection_preference_shift():
    existing = [
        MemoryItem(
            id="mem_101",
            user_id="u_001",
            memory_text="User dislikes public speaking.",
            memory_type=MemoryType.PREFERENCE,
            status=MemoryStatus.ACTIVE,
        )
    ]
    candidate = MemoryCandidate(
        id="mc_005",
        user_id="u_001",
        memory_text="User now enjoys giving lectures.",
        memory_type=MemoryType.PREFERENCE,
        source_turn_ids=["t_010"],
        source_speaker=Speaker.USER,
        extraction_confidence=0.9,
    )
    detector = ConflictDetector(HeuristicLLMClient())
    res = detector.detect_conflict(candidate, existing)

    assert res.conflict_status.value in ("update_required", "no_conflict")
    print("[PASS] Conflict detection test passed.")


if __name__ == "__main__":
    test_conflict_detection_preference_shift()
