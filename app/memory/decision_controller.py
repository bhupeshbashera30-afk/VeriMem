"""
Memory Decision Controller (Section 7.7 & Algorithm 15.4).

Makes the final write/update decision for each candidate memory based on
grounding, conflict detection, and active user policies.
"""

from __future__ import annotations

from typing import Optional
from app.schemas import (
    ConflictResult,
    ConflictStatus,
    DecisionType,
    GroundingLabel,
    GroundingResult,
    MemoryCandidate,
    MemoryDecision,
    PolicyAction,
)


class MemoryDecisionController:
    def decide(
        self,
        candidate: MemoryCandidate,
        grounding: GroundingResult,
        conflict: ConflictResult,
        policy_action: PolicyAction,
    ) -> MemoryDecision:
        label = grounding.grounding_label

        # 1. Reject unsupported or unconfirmed assistant-originated memories
        if label == GroundingLabel.ASSISTANT_ORIGINATED:
            return MemoryDecision(
                candidate_id=candidate.id,
                decision=DecisionType.REJECT_ASSISTANT_ORIGINATED,
                reason="Rejected: Memory came solely from assistant assertion without user confirmation.",
                confidence=grounding.grounding_confidence,
            )

        if label in (GroundingLabel.UNSUPPORTED, GroundingLabel.CONTRADICTED):
            return MemoryDecision(
                candidate_id=candidate.id,
                decision=DecisionType.REJECT_UNSUPPORTED,
                reason=f"Rejected: Memory is {label.value} by dialogue evidence.",
                confidence=grounding.grounding_confidence,
            )

        # 2. Check user policy overrides
        if policy_action == PolicyAction.REJECT:
            return MemoryDecision(
                candidate_id=candidate.id,
                decision=DecisionType.REJECT_UNSUPPORTED,
                reason="Rejected: Blocked by active natural-language user policy.",
                confidence=grounding.grounding_confidence,
            )

        if policy_action == PolicyAction.REQUIRE_CONFIRMATION:
            return MemoryDecision(
                candidate_id=candidate.id,
                decision=DecisionType.ASK_CONFIRMATION,
                reason="Pending Confirmation: Policy requires explicit user confirmation before committing.",
                confidence=grounding.grounding_confidence,
            )

        # 3. Check conflict decisions
        if conflict.conflict_status in (ConflictStatus.UPDATE_REQUIRED, ConflictStatus.REQUIRE_CONFIRMATION):
            if conflict.recommended_action == "ask_user":
                return MemoryDecision(
                    candidate_id=candidate.id,
                    decision=DecisionType.ASK_CONFIRMATION,
                    reason=f"Pending Confirmation: {conflict.reason}",
                    confidence=grounding.grounding_confidence,
                    parent_memory_id=conflict.related_memory_ids[0] if conflict.related_memory_ids else None,
                    retired_memory_ids=conflict.related_memory_ids,
                )

            if conflict.recommended_action in ("retire_old_and_store_new", "store_new"):
                parent_id = conflict.related_memory_ids[0] if conflict.related_memory_ids else None
                return MemoryDecision(
                    candidate_id=candidate.id,
                    decision=DecisionType.UPDATE_REPLACE,
                    reason=f"Update Replace: {conflict.reason}",
                    confidence=grounding.grounding_confidence,
                    parent_memory_id=parent_id,
                    retired_memory_ids=conflict.related_memory_ids,
                )

        if conflict.conflict_status == ConflictStatus.TEMPORAL_BOTH:
            return MemoryDecision(
                candidate_id=candidate.id,
                decision=DecisionType.UPDATE_TEMPORAL,
                reason="Temporal Update: Maintained timeline of past and present facts.",
                confidence=grounding.grounding_confidence,
            )

        # 4. Store decision based on grounding confidence & label
        if label == GroundingLabel.PARTIALLY_SUPPORTED or policy_action == PolicyAction.MARK_UNCERTAIN:
            return MemoryDecision(
                candidate_id=candidate.id,
                decision=DecisionType.STORE_UNCERTAIN,
                reason="Store Uncertain: Fact is partially supported or marked uncertain by policy.",
                confidence=grounding.grounding_confidence,
            )

        return MemoryDecision(
            candidate_id=candidate.id,
            decision=DecisionType.STORE_ACTIVE,
            reason="Store Active: Memory is directly grounded in user evidence and allowed by policy.",
            confidence=grounding.grounding_confidence,
        )
