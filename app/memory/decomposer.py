"""
Atomic Fact Decomposer (Section 7.4).

Splits complex multi-claim memory candidates into minimal, independently checkable atomic facts.
"""

from __future__ import annotations

import uuid
from typing import List
from app.llm_client import LLMClient
from app.schemas import AtomicFact, MemoryCandidate

_SYSTEM_PROMPT = """You split a candidate memory statement into atomic facts.

Rules:
- Each atomic fact must be a single, minimal, independently checkable claim.
- Do not add information that isn't in the original statement.
- Do not merge multiple claims into one atomic fact.
- If the statement is already atomic, return it unchanged as the only fact.
- For each atomic fact, extract a (subject, predicate, object) triple if possible.

Return ONLY JSON matching:
{
  "atomic_facts": [
    {"text": "...", "subject": "..." or null, "predicate": "..." or null, "object": "..." or null}
  ]
}
"""


class AtomicFactDecomposer:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def decompose(self, candidate: MemoryCandidate) -> List[AtomicFact]:
        prompt = f'Candidate memory statement:\n"{candidate.memory_text}"'
        res = self.llm_client.complete_json(_SYSTEM_PROMPT, prompt)

        facts = []
        for item in res.get("atomic_facts", []):
            text = (item.get("text") or "").strip()
            if not text:
                continue
            facts.append(
                AtomicFact(
                    fact_id=f"fact_{uuid.uuid4().hex[:8]}",
                    candidate_id=candidate.id,
                    text=text,
                    subject=item.get("subject"),
                    predicate=item.get("predicate"),
                    object=item.get("object"),
                )
            )

        if not facts:
            facts.append(
                AtomicFact(
                    fact_id=f"fact_{uuid.uuid4().hex[:8]}",
                    candidate_id=candidate.id,
                    text=candidate.memory_text,
                )
            )

        return facts
