"""
Evidence Grounding Verifier (Section 7.3 & Algorithm 15.2).

Verifies whether memory candidates are grounded in user-provided dialogue evidence.
Enforces the safety-critical rule: unconfirmed assistant-originated claims are rejected.
"""

from __future__ import annotations

from typing import List, Dict, Optional
from app.llm_client import LLMClient
from app.schemas import (
    AtomicFact,
    AtomicFactVerdict,
    EvidenceSpan,
    GroundingLabel,
    GroundingResult,
    MemoryCandidate,
    Speaker,
    SupportType,
    Turn,
)

_SYSTEM_PROMPT = """You are the Evidence Grounding Verifier in a memory system for an AI agent.
Check whether atomic factual claims are supported by conversation evidence turns.

For EACH atomic fact, assign exactly one label:
- "supported": directly stated or unambiguously entailed by something the USER said.
- "partially_supported": part of the fact is stated, but part is inferred/extrapolated.
- "unsupported": no turn supports this fact.
- "contradicted": dialogue evidence directly conflicts with this fact.
- "assistant_originated": fact stated ONLY by assistant, never confirmed by user.

Return ONLY JSON matching:
{
  "verdicts": [
    {
      "fact_id": "...",
      "label": "supported"|"partially_supported"|"unsupported"|"contradicted"|"assistant_originated",
      "evidence_spans": [{"turn_id": "...", "text": "...", "support_type": "direct"|"entailed"|"partial"}],
      "contradiction_reason": "..." or null,
      "confidence": 0.0-1.0
    }
  ]
}
"""

_LABEL_SEVERITY = {
    GroundingLabel.CONTRADICTED: 4,
    GroundingLabel.ASSISTANT_ORIGINATED: 3,
    GroundingLabel.UNSUPPORTED: 2,
    GroundingLabel.PARTIALLY_SUPPORTED: 1,
    GroundingLabel.SUPPORTED: 0,
}


class EvidenceGroundingVerifier:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def verify(
        self,
        candidate: MemoryCandidate,
        atomic_facts: List[AtomicFact],
        source_turns: List[Turn],
    ) -> GroundingResult:
        if not atomic_facts:
            raise ValueError("verify() requires at least one atomic fact")

        # Deterministic rule: if only assistant turn cited, force assistant_originated
        has_user_turn = any(t.speaker == Speaker.USER for t in source_turns)
        if not has_user_turn or candidate.source_speaker == Speaker.ASSISTANT:
            # Check if any user turn confirms it
            if not has_user_turn:
                verdicts = [
                    AtomicFactVerdict(
                        fact_id=f.fact_id,
                        text=f.text,
                        label=GroundingLabel.ASSISTANT_ORIGINATED,
                        evidence_spans=[],
                        contradiction_reason=None,
                        confidence=0.95,
                    )
                    for f in atomic_facts
                ]
                return self._aggregate(candidate, verdicts)

        prompt_block = self._build_prompt(candidate, atomic_facts, source_turns)
        raw = self.llm_client.complete_json(_SYSTEM_PROMPT, prompt_block)
        verdicts = self._parse_verdicts(raw, atomic_facts)
        return self._aggregate(candidate, verdicts)

    def _build_prompt(self, candidate: MemoryCandidate, atomic_facts: List[AtomicFact], source_turns: List[Turn]) -> str:
        facts_block = "\n".join(f'- fact_id={f.fact_id}: "{f.text}"' for f in atomic_facts)
        turns_block = "\n".join(f'- turn_id={t.id} [{t.speaker.value}]: "{t.text}"' for t in source_turns)
        return (
            f"source_speaker: {candidate.source_speaker.value}\n\n"
            f"Atomic facts to verify:\n{facts_block}\n\n"
            f"Transcript turns:\n{turns_block}"
        )

    def _parse_verdicts(self, raw: dict, atomic_facts: List[AtomicFact]) -> List[AtomicFactVerdict]:
        facts_by_id = {f.fact_id: f for f in atomic_facts}
        verdicts: List[AtomicFactVerdict] = []
        seen = set()

        for item in raw.get("verdicts", []):
            fid = item.get("fact_id")
            fact = facts_by_id.get(fid)
            if not fact:
                continue
            seen.add(fid)

            spans = [
                EvidenceSpan(
                    turn_id=s["turn_id"],
                    text=s["text"],
                    support_type=SupportType(s.get("support_type", "direct")),
                )
                for s in item.get("evidence_spans", [])
                if s.get("turn_id") and s.get("text")
            ]

            try:
                g_label = GroundingLabel(item.get("label", "unsupported"))
            except ValueError:
                g_label = GroundingLabel.UNSUPPORTED

            verdicts.append(
                AtomicFactVerdict(
                    fact_id=fid,
                    text=fact.text,
                    label=g_label,
                    evidence_spans=spans,
                    contradiction_reason=item.get("contradiction_reason"),
                    confidence=float(item.get("confidence", 0.5)),
                )
            )

        for f in atomic_facts:
            if f.fact_id not in seen:
                verdicts.append(
                    AtomicFactVerdict(
                        fact_id=f.fact_id,
                        text=f.text,
                        label=GroundingLabel.UNSUPPORTED,
                        evidence_spans=[],
                        confidence=0.0,
                    )
                )

        return verdicts

    def _aggregate(self, candidate: MemoryCandidate, verdicts: List[AtomicFactVerdict]) -> GroundingResult:
        overall_label = max((v.label for v in verdicts), key=lambda l: _LABEL_SEVERITY[l])
        all_spans = [span for v in verdicts for span in v.evidence_spans]
        unsupported = [
            v.text for v in verdicts
            if v.label in (GroundingLabel.UNSUPPORTED, GroundingLabel.CONTRADICTED, GroundingLabel.ASSISTANT_ORIGINATED)
        ]
        conf = min(v.confidence for v in verdicts) if verdicts else 0.0

        return GroundingResult(
            candidate_id=candidate.id,
            grounding_label=overall_label,
            evidence_spans=all_spans,
            unsupported_claims=unsupported,
            grounding_confidence=round(conf, 2),
            atomic_verdicts=verdicts,
        )
