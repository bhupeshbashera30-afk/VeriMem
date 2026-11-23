"""
Tests for Memory Candidate Extraction (Section 7.2).
"""

from __future__ import annotations

import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.llm_client import HeuristicLLMClient
from app.memory.extractor import MemoryCandidateExtractor
from app.schemas import Speaker, Turn


def test_extraction_from_user_turn():
    turns = [
        Turn(id="t_001", conversation_id="s_001", user_id="u_001", speaker=Speaker.USER, text="I want to build a major project on hallucination-aware memory."),
    ]
    extractor = MemoryCandidateExtractor(HeuristicLLMClient())
    candidates = extractor.extract(turns)

    assert len(candidates) >= 1
    assert candidates[0].user_id == "u_001"
    assert candidates[0].extraction_confidence > 0.0
    print("[PASS] Extraction test passed.")


if __name__ == "__main__":
    test_extraction_from_user_turn()
