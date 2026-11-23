"""
Tests for Policy Engine & Compiler (Section 7.6 & Section 13).
"""

from __future__ import annotations

import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.llm_client import HeuristicLLMClient
from app.memory.policy_engine import PolicyEngine
from app.schemas import GroundingLabel, MemoryCandidate, MemoryType, PolicyAction, Speaker


def test_policy_compilation_and_evaluation():
    engine = PolicyEngine(HeuristicLLMClient())
    rule = engine.compile_rule("u_001", "Do not remember assistant assumptions. Ask me before changing project goals.")

    assert rule.user_id == "u_001"
    assert rule.compiled_policy.name is not None

    cand = MemoryCandidate(
        id="mc_009",
        user_id="u_001",
        memory_text="User wants project to use RAG.",
        memory_type=MemoryType.GOAL,
        source_turn_ids=["t_005"],
        source_speaker=Speaker.USER,
        extraction_confidence=0.9,
    )

    action = engine.evaluate_policies(cand, GroundingLabel.SUPPORTED, [rule])
    assert action in (PolicyAction.ALLOW_STORE, PolicyAction.REQUIRE_CONFIRMATION)
    print("[PASS] Policy engine test passed.")


if __name__ == "__main__":
    test_policy_compilation_and_evaluation()
