"""
Memory Candidate Extractor (Section 7.2).

Extracts potential user memory candidates from conversation turns.
The extractor is allowed to propose memories, but is NEVER allowed to store them directly.
"""

from __future__ import annotations

import uuid
from typing import List
from app.llm_client import LLMClient
from app.schemas import MemoryCandidate, MemoryType, Speaker, Turn

_SYSTEM_PROMPT = """You are the Memory Candidate Extractor for VeriMem.
Extract potential long-term user memories from dialogue turns.

Classify memory_type as one of:
- "persona": Stable user facts (e.g. location, occupation)
- "preference": Likes, dislikes, habits
- "event": Time-bound event or plan
- "relationship": People, entities, and connection details
- "goal": Future intention or goal
- "constraint": Rules or explicit boundaries

Return ONLY JSON matching:
{
  "candidates": [
    {
      "memory_text": "...",
      "memory_type": "persona"|"preference"|"event"|"relationship"|"goal"|"constraint",
      "extraction_confidence": 0.0-1.0
    }
  ]
}
"""


import re

def is_question_text(text: str) -> bool:
    if not text:
        return False
    t = text.lower().strip()
    if t.endswith("?"):
        return True
    pattern = r'\b(what|where|who|whom|whose|how|why|which|when|do i|did i|should i|can i|could i|would i|is my|are my|am i|what do|what is|what are|what was|what were|what did|which do|which one|do you know|tell me|so now what|coffee or tea|prefer coffee or tea|do i prefer)\b'
    if bool(re.search(pattern, t)):
        return True
    if any(k in t for k in ["asked", "asking", "inquiring", "wondering", "question", "user presented dialogue information."]):
        return True
    return False


class MemoryCandidateExtractor:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def extract(self, turns: List[Turn]) -> List[MemoryCandidate]:
        if not turns:
            return []

        # If turn text itself is a question/query, do not extract memory candidates
        if any(is_question_text(t.text) for t in turns if t.speaker == Speaker.USER):
            return []

        user_id = turns[0].user_id
        turns_block = "\n".join(f'turn_id={t.id} [{t.speaker.value}]: "{t.text}"' for t in turns)
        prompt = f"Dialogue Turns:\n{turns_block}"

        response = self.llm_client.complete_json(_SYSTEM_PROMPT, prompt)
        candidates = []

        for item in response.get("candidates", []):
            text = item.get("memory_text", "").strip()
            if not text:
                continue

            clean_t = text.replace("User mentioned:", "").replace("User asked:", "").strip()
            if is_question_text(clean_t):
                continue

            # Default source speaker and turns
            source_turn_ids = [t.id for t in turns]
            source_speaker = turns[0].speaker if turns else Speaker.USER

            try:
                m_type = MemoryType(item.get("memory_type", "persona"))
            except ValueError:
                m_type = MemoryType.PERSONA

            conf = float(item.get("extraction_confidence", 0.8))

            candidates.append(
                MemoryCandidate(
                    id=f"mc_{uuid.uuid4().hex[:8]}",
                    user_id=user_id,
                    memory_text=text,
                    memory_type=m_type,
                    source_turn_ids=source_turn_ids,
                    source_speaker=source_speaker,
                    extraction_confidence=round(conf, 2),
                )
            )

        return candidates
