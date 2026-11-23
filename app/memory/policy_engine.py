"""
Natural-Language Policy Engine (Section 7.6 & Section 13).

Converts user-written natural language memory instructions into executable policies
and evaluates memory candidates against compiled policy rules.
"""

from __future__ import annotations

import uuid
from typing import List, Optional
from app.llm_client import LLMClient
from app.schemas import (
    CompiledPolicy,
    GroundingLabel,
    MemoryCandidate,
    MemoryType,
    PolicyAction,
    PolicyRule,
)

_PARSER_SYSTEM_PROMPT = """You are the Natural Language Policy Parser for VeriMem.
Convert user natural language memory rules into executable policy JSON schemas.

Policy Action choices:
- "allow_store": Allow storing the memory
- "reject": Do not store memory
- "mark_uncertain": Store memory but do not use for final QA without confirmation
- "require_confirmation": Ask user before storing/updating
- "retire_old": Retire old memory version
- "keep_both_temporal": Maintain temporal timeline
- "redact_sensitive": Remove sensitive fields
- "expire_after": Set TTL/expiry

Return ONLY JSON matching:
{
  "name": "Short Policy Name",
  "description": "...",
  "scope": ["persona", "preference", "goal", "relationship", "event", "constraint"],
  "condition": {
    "source_speaker": "user" | "assistant" | null,
    "grounding_label": ["supported", "partially_supported"] | null
  },
  "action": "allow_store" | "reject" | "mark_uncertain" | "require_confirmation",
  "fallback": "reject",
  "priority": 10
}
"""


class PolicyEngine:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def compile_rule(self, user_id: str, natural_rule: str) -> PolicyRule:
        prompt = f'USER MEMORY RULE:\n"{natural_rule}"'
        res = self.llm_client.complete_json(_PARSER_SYSTEM_PROMPT, prompt)

        scopes = []
        for s in res.get("scope", ["persona", "preference", "goal"]):
            try:
                scopes.append(MemoryType(s))
            except ValueError:
                pass

        try:
            action = PolicyAction(res.get("action", "allow_store"))
        except ValueError:
            action = PolicyAction.ALLOW_STORE

        try:
            fallback = PolicyAction(res.get("fallback", "reject"))
        except ValueError:
            fallback = PolicyAction.REJECT

        compiled = CompiledPolicy(
            policy_id=f"pol_{uuid.uuid4().hex[:8]}",
            name=res.get("name", "User Policy"),
            description=res.get("description"),
            scope=scopes if scopes else [MemoryType.PERSONA, MemoryType.PREFERENCE, MemoryType.GOAL],
            condition=res.get("condition", {}),
            action=action,
            fallback=fallback,
            priority=int(res.get("priority", 10)),
            active=True,
        )

        return PolicyRule(
            id=compiled.policy_id,
            user_id=user_id,
            natural_language_rule=natural_rule,
            compiled_policy=compiled,
            active=True,
        )

    def evaluate_policies(
        self,
        candidate: MemoryCandidate,
        grounding_label: GroundingLabel,
        policies: List[PolicyRule],
    ) -> PolicyAction:
        active_policies = [p for p in policies if p.active and p.compiled_policy.active]
        active_policies.sort(key=lambda p: p.compiled_policy.priority, reverse=True)

        for p in active_policies:
            cp = p.compiled_policy
            if cp.scope and candidate.memory_type not in cp.scope:
                continue

            cond = cp.condition
            # Check source speaker condition
            req_speaker = cond.get("source_speaker")
            if req_speaker and candidate.source_speaker.value != req_speaker:
                continue

            # Check grounding label condition
            req_labels = cond.get("grounding_label")
            if req_labels and grounding_label.value not in req_labels:
                return cp.fallback

            if cp.action != PolicyAction.ALLOW_STORE:
                return cp.action

        return PolicyAction.ALLOW_STORE
