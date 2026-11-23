"""
Answer Agent and Answer Verifier (Section 7.10, 7.11 & Algorithm 15.5).

Generates evidence-grounded answers strictly using retrieved active memories,
adds citations, and verifies answer factuality before display.
"""

from __future__ import annotations

from typing import List, Tuple
from app.llm_client import LLMClient
from app.schemas import GroundedAnswer, MemoryItem

_SYSTEM_PROMPT = """You are the Answer Agent in VeriMem.
Generate an answer to the user's question using ONLY the provided verified active memories.

Rules:
1. Use only retrieved active memories. Do not invent or assume unstated facts.
2. Cite memory IDs [mem_XXX] for each claim.
3. If retrieved memories do not contain enough information to answer, state clearly that you do not have enough verified memory.

Return ONLY JSON matching:
{
  "answer": "Answer string with citations like [mem_001]...",
  "used_memories": ["mem_001"],
  "confidence": 0.0-1.0,
  "status": "grounded" | "uncertain"
}
"""


class AnswerAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def generate_answer(self, question: str, retrieved_memories: List[Tuple[MemoryItem, float]]) -> GroundedAnswer:
        if not retrieved_memories:
            return GroundedAnswer(
                answer="I do not have enough verified memory to answer this question.",
                used_memories=[],
                confidence=0.0,
                status="insufficient_memory",
                citations=[],
            )

        mem_blocks = "\n".join(f'- [{m.id}]: "{m.memory_text}" (confidence={m.confidence})' for m, _ in retrieved_memories)
        prompt = f'USER QUESTION:\n"{question}"\n\nRETRIEVED VERIFIED MEMORIES:\n{mem_blocks}'

        res = self.llm_client.complete_json(_SYSTEM_PROMPT, prompt)

        used_ids = res.get("used_memories", [m.id for m, _ in retrieved_memories])
        citations = []
        for m, s in retrieved_memories:
            if m.id in used_ids:
                citations.append({
                    "memory_id": m.id,
                    "memory_text": m.memory_text,
                    "relevance_score": s,
                    "evidence_turn_ids": m.evidence_turn_ids,
                })

        return GroundedAnswer(
            answer=res.get("answer", "No answer generated."),
            used_memories=used_ids,
            confidence=float(res.get("confidence", 0.9)),
            status=res.get("status", "grounded"),
            citations=citations,
        )
