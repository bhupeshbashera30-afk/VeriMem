"""
Tests for Grounded Answer Agent and Retriever (Section 7.9 & 7.10).
"""

from __future__ import annotations

import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.agents.answer_agent import AnswerAgent
from app.llm_client import HeuristicLLMClient
from app.memory.retriever import HybridRetriever
from app.schemas import MemoryItem, MemoryStatus, MemoryType


def test_grounded_qa():
    memories = [
        MemoryItem(
            id="mem_001",
            user_id="u_001",
            memory_text="User is making a major project on hallucination-aware memory.",
            memory_type=MemoryType.GOAL,
            status=MemoryStatus.ACTIVE,
            confidence=0.95,
        ),
        MemoryItem(
            id="mem_002",
            user_id="u_001",
            memory_text="User wants project to include natural language programming.",
            memory_type=MemoryType.CONSTRAINT,
            status=MemoryStatus.ACTIVE,
            confidence=0.92,
        ),
    ]

    retriever = HybridRetriever()
    retrieved = retriever.retrieve("What is my project about?", memories, top_k=2)

    assert len(retrieved) >= 1
    llm = HeuristicLLMClient()
    agent = AnswerAgent(llm)
    ans = agent.generate_answer("What is my project about?", retrieved)

    assert ans.confidence > 0.0
    assert len(ans.used_memories) > 0
    print("[PASS] Grounded QA test passed.")


if __name__ == "__main__":
    test_grounded_qa()
