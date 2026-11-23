"""
VeriMem Core Data Schemas.

Mirrors sections 7 and 10 of the VeriMem system design document.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Speaker(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class MemoryType(str, Enum):
    PERSONA = "persona"
    PREFERENCE = "preference"
    EVENT = "event"
    RELATIONSHIP = "relationship"
    GOAL = "goal"
    CONSTRAINT = "constraint"


class Turn(BaseModel):
    id: str
    conversation_id: str
    user_id: str
    speaker: Speaker
    text: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MemoryCandidate(BaseModel):
    id: str
    user_id: str
    memory_text: str
    memory_type: MemoryType
    source_turn_ids: List[str]
    source_speaker: Speaker
    extraction_confidence: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AtomicFact(BaseModel):
    fact_id: str
    candidate_id: str
    text: str
    subject: Optional[str] = None
    predicate: Optional[str] = None
    object: Optional[str] = None


class GroundingLabel(str, Enum):
    SUPPORTED = "supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    UNSUPPORTED = "unsupported"
    CONTRADICTED = "contradicted"
    ASSISTANT_ORIGINATED = "assistant_originated"


class SupportType(str, Enum):
    DIRECT = "direct"
    ENTAILED = "entailed"
    PARTIAL = "partial"


class EvidenceSpan(BaseModel):
    turn_id: str
    text: str
    support_type: SupportType = SupportType.DIRECT


class AtomicFactVerdict(BaseModel):
    fact_id: str
    text: str
    label: GroundingLabel
    evidence_spans: List[EvidenceSpan] = Field(default_factory=list)
    contradiction_reason: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class GroundingResult(BaseModel):
    candidate_id: str
    grounding_label: GroundingLabel
    evidence_spans: List[EvidenceSpan] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)
    grounding_confidence: float = Field(ge=0.0, le=1.0)
    atomic_verdicts: List[AtomicFactVerdict] = Field(default_factory=list)
    rationale: Optional[str] = None


class ConflictType(str, Enum):
    VALUE_CONFLICT = "value_conflict"
    TEMPORAL_UPDATE = "temporal_update"
    PREFERENCE_SHIFT = "preference_shift"
    IDENTITY_CONFLICT = "identity_conflict"
    RELATIONSHIP_CONFLICT = "relationship_conflict"
    GOAL_CONFLICT = "goal_conflict"
    NO_CONFLICT = "no_conflict"


class ConflictStatus(str, Enum):
    NO_CONFLICT = "no_conflict"
    UPDATE_REQUIRED = "update_required"
    TEMPORAL_BOTH = "temporal_both"
    REQUIRE_CONFIRMATION = "require_confirmation"


class ConflictResult(BaseModel):
    candidate_id: str
    conflict_status: ConflictStatus
    related_memory_ids: List[str] = Field(default_factory=list)
    conflict_type: ConflictType = ConflictType.NO_CONFLICT
    reason: Optional[str] = None
    recommended_action: str = "store_new"


class PolicyAction(str, Enum):
    ALLOW_STORE = "allow_store"
    REJECT = "reject"
    MARK_UNCERTAIN = "mark_uncertain"
    REQUIRE_CONFIRMATION = "require_confirmation"
    RETIRE_OLD = "retire_old"
    KEEP_BOTH_TEMPORAL = "keep_both_temporal"
    REDACT_SENSITIVE = "redact_sensitive"
    EXPIRE_AFTER = "expire_after"


class CompiledPolicy(BaseModel):
    policy_id: str
    name: str
    description: Optional[str] = None
    scope: List[MemoryType] = Field(default_factory=list)
    condition: Dict[str, Any] = Field(default_factory=dict)
    action: PolicyAction = PolicyAction.ALLOW_STORE
    fallback: PolicyAction = PolicyAction.REJECT
    priority: int = 10
    active: bool = True


class PolicyRule(BaseModel):
    id: str
    user_id: str
    natural_language_rule: str
    compiled_policy: CompiledPolicy
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionType(str, Enum):
    STORE_ACTIVE = "STORE_ACTIVE"
    STORE_UNCERTAIN = "STORE_UNCERTAIN"
    REJECT_UNSUPPORTED = "REJECT_UNSUPPORTED"
    REJECT_ASSISTANT_ORIGINATED = "REJECT_ASSISTANT_ORIGINATED"
    UPDATE_REPLACE = "UPDATE_REPLACE"
    UPDATE_TEMPORAL = "UPDATE_TEMPORAL"
    ASK_CONFIRMATION = "ASK_CONFIRMATION"


class MemoryDecision(BaseModel):
    candidate_id: str
    decision: DecisionType
    reason: str
    confidence: float
    parent_memory_id: Optional[str] = None
    retired_memory_ids: List[str] = Field(default_factory=list)


class MemoryStatus(str, Enum):
    ACTIVE = "active"
    UNCERTAIN = "uncertain"
    RETIRED = "retired"
    REJECTED = "rejected"
    PENDING_CONFIRMATION = "pending_confirmation"


class MemoryItem(BaseModel):
    id: str
    user_id: str
    memory_text: str
    memory_type: MemoryType
    status: MemoryStatus = MemoryStatus.ACTIVE
    confidence: float = 1.0
    importance: float = 1.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    version: int = 1
    parent_memory_id: Optional[str] = None
    evidence_turn_ids: List[str] = Field(default_factory=list)
    atomic_subject: Optional[str] = None
    atomic_predicate: Optional[str] = None
    atomic_object: Optional[str] = None


class AuditLog(BaseModel):
    id: str
    user_id: str
    operation: str
    input_ref: str
    decision: str
    reason: str
    confidence: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class QAQuery(BaseModel):
    question: str
    user_id: str


class GroundedAnswer(BaseModel):
    answer: str
    used_memories: List[str] = Field(default_factory=list)
    confidence: float
    status: str
    citations: List[Dict[str, Any]] = Field(default_factory=list)
