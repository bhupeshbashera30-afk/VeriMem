"""
Hybrid Memory Store (Section 7.8 & Section 10).

SQLite-backed relational database manager for conversations, turns, candidate memories,
verified active memories, evidence links, conflicts, policies, and audit logs.
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.config import DB_PATH
from app.schemas import (
    AuditLog,
    CompiledPolicy,
    DecisionType,
    EvidenceSpan,
    GroundingResult,
    MemoryCandidate,
    MemoryDecision,
    MemoryItem,
    MemoryStatus,
    MemoryType,
    PolicyAction,
    PolicyRule,
    Speaker,
    Turn,
)


class MemoryStore:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DB_PATH
        self._shared_conn: Optional[sqlite3.Connection] = None
        dir_name = os.path.dirname(self.db_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        if self.db_path == ":memory:":
            self._shared_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._shared_conn.row_factory = sqlite3.Row
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if self._shared_conn:
            return self._shared_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                metadata TEXT
            );""")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS turns (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                speaker TEXT NOT NULL,
                text TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );""")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_candidates (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                memory_text TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                source_turn_ids TEXT NOT NULL,
                source_speaker TEXT NOT NULL,
                extraction_confidence REAL NOT NULL,
                created_at TEXT NOT NULL
            );""")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                memory_text TEXT NOT NULL,
                atomic_subject TEXT,
                atomic_predicate TEXT,
                atomic_object TEXT,
                memory_type TEXT NOT NULL,
                status TEXT NOT NULL,
                confidence REAL NOT NULL,
                importance REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                valid_from TEXT,
                valid_until TEXT,
                version INTEGER NOT NULL,
                parent_memory_id TEXT
            );""")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_evidence (
                id TEXT PRIMARY KEY,
                memory_id TEXT NOT NULL,
                turn_id TEXT NOT NULL,
                evidence_text TEXT NOT NULL,
                support_type TEXT NOT NULL
            );""")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_policies (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                natural_language_rule TEXT NOT NULL,
                compiled_policy_json TEXT NOT NULL,
                priority INTEGER NOT NULL,
                active INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );""")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                input_ref TEXT NOT NULL,
                decision TEXT NOT NULL,
                reason TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_at TEXT NOT NULL
            );""")
            conn.commit()

    # --- Conversation & Turns ------------------------------------------------
    def save_turn(self, turn: Turn) -> None:
        with self._get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO turns (id, conversation_id, user_id, speaker, text, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (turn.id, turn.conversation_id, turn.user_id, turn.speaker.value, turn.text, turn.timestamp.isoformat()),
            )
            conn.commit()

    def get_turns_for_session(self, session_id: str) -> List[Turn]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM turns WHERE conversation_id = ? ORDER BY timestamp ASC", (session_id,)).fetchall()
            return [
                Turn(
                    id=r["id"],
                    conversation_id=r["conversation_id"],
                    user_id=r["user_id"],
                    speaker=Speaker(r["speaker"]),
                    text=r["text"],
                    timestamp=datetime.fromisoformat(r["timestamp"]),
                )
                for r in rows
            ]

    # --- Candidates ----------------------------------------------------------
    def save_candidate(self, candidate: MemoryCandidate) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO memory_candidates 
                (id, user_id, memory_text, memory_type, source_turn_ids, source_speaker, extraction_confidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    candidate.id,
                    candidate.user_id,
                    candidate.memory_text,
                    candidate.memory_type.value,
                    json.dumps(candidate.source_turn_ids),
                    candidate.source_speaker.value,
                    candidate.extraction_confidence,
                    candidate.created_at.isoformat(),
                ),
            )
            conn.commit()

    # --- Memories ------------------------------------------------------------
    def commit_memory_decision(
        self,
        candidate: MemoryCandidate,
        grounding: GroundingResult,
        decision: MemoryDecision,
    ) -> Optional[MemoryItem]:
        now_str = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            cursor = conn.cursor()

            # Handle replace/update
            if decision.decision == DecisionType.UPDATE_REPLACE:
                to_retire = set()
                if decision.parent_memory_id:
                    to_retire.add(decision.parent_memory_id)
                if hasattr(decision, "retired_memory_ids") and decision.retired_memory_ids:
                    to_retire.update(decision.retired_memory_ids)
                for rid in to_retire:
                    cursor.execute(
                        "UPDATE memories SET status = ?, updated_at = ? WHERE id = ?",
                        (MemoryStatus.RETIRED.value, now_str, rid),
                    )

            # Map decision to memory status
            status_map = {
                DecisionType.STORE_ACTIVE: MemoryStatus.ACTIVE,
                DecisionType.STORE_UNCERTAIN: MemoryStatus.UNCERTAIN,
                DecisionType.UPDATE_REPLACE: MemoryStatus.ACTIVE,
                DecisionType.UPDATE_TEMPORAL: MemoryStatus.ACTIVE,
                DecisionType.ASK_CONFIRMATION: MemoryStatus.PENDING_CONFIRMATION,
                DecisionType.REJECT_UNSUPPORTED: MemoryStatus.REJECTED,
                DecisionType.REJECT_ASSISTANT_ORIGINATED: MemoryStatus.REJECTED,
            }
            m_status = status_map.get(decision.decision, MemoryStatus.REJECTED)

            mem_id = f"mem_{uuid.uuid4().hex[:8]}"
            memory_item = MemoryItem(
                id=mem_id,
                user_id=candidate.user_id,
                memory_text=candidate.memory_text,
                memory_type=candidate.memory_type,
                status=m_status,
                confidence=decision.confidence,
                parent_memory_id=decision.parent_memory_id,
                evidence_turn_ids=[span.turn_id for span in grounding.evidence_spans],
            )

            cursor.execute(
                """INSERT INTO memories 
                (id, user_id, memory_text, atomic_subject, atomic_predicate, atomic_object, memory_type, status, confidence, importance, created_at, updated_at, version, parent_memory_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    memory_item.id,
                    memory_item.user_id,
                    memory_item.memory_text,
                    memory_item.atomic_subject,
                    memory_item.atomic_predicate,
                    memory_item.atomic_object,
                    memory_item.memory_type.value,
                    memory_item.status.value,
                    memory_item.confidence,
                    memory_item.importance,
                    now_str,
                    now_str,
                    memory_item.version,
                    memory_item.parent_memory_id,
                ),
            )

            # Save evidence links
            for span in grounding.evidence_spans:
                cursor.execute(
                    "INSERT INTO memory_evidence (id, memory_id, turn_id, evidence_text, support_type) VALUES (?, ?, ?, ?, ?)",
                    (f"ev_{uuid.uuid4().hex[:8]}", mem_id, span.turn_id, span.text, span.support_type.value),
                )

            # Log audit entry
            cursor.execute(
                "INSERT INTO audit_logs (id, user_id, operation, input_ref, decision, reason, confidence, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    f"log_{uuid.uuid4().hex[:8]}",
                    candidate.user_id,
                    "process_memory",
                    candidate.id,
                    decision.decision.value,
                    decision.reason,
                    decision.confidence,
                    now_str,
                ),
            )
            conn.commit()
            return memory_item

    def get_user_memories(self, user_id: str, status: Optional[str] = None) -> List[MemoryItem]:
        with self._get_conn() as conn:
            if status:
                rows = conn.execute("SELECT * FROM memories WHERE user_id = ? AND status = ? ORDER BY created_at DESC", (user_id, status)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM memories WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()

            memories = []
            for r in rows:
                ev_rows = conn.execute("SELECT turn_id FROM memory_evidence WHERE memory_id = ?", (r["id"],)).fetchall()
                turn_ids = [e["turn_id"] for e in ev_rows]
                memories.append(
                    MemoryItem(
                        id=r["id"],
                        user_id=r["user_id"],
                        memory_text=r["memory_text"],
                        memory_type=MemoryType(r["memory_type"]),
                        status=MemoryStatus(r["status"]),
                        confidence=r["confidence"],
                        importance=r["importance"],
                        created_at=datetime.fromisoformat(r["created_at"]),
                        updated_at=datetime.fromisoformat(r["updated_at"]),
                        version=r["version"],
                        parent_memory_id=r["parent_memory_id"],
                        evidence_turn_ids=turn_ids,
                    )
                )
            return memories

    # --- Policies ------------------------------------------------------------
    def save_policy(self, rule: PolicyRule) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO memory_policies 
                (id, user_id, natural_language_rule, compiled_policy_json, priority, active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    rule.id,
                    rule.user_id,
                    rule.natural_language_rule,
                    rule.compiled_policy.model_dump_json(),
                    rule.compiled_policy.priority,
                    1 if rule.active else 0,
                    rule.created_at.isoformat(),
                ),
            )
            conn.commit()

    def get_user_policies(self, user_id: str) -> List[PolicyRule]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM memory_policies WHERE user_id = ? AND active = 1 ORDER BY priority DESC", (user_id,)).fetchall()
            if not rows and user_id == "user_default":
                # Default project policies
                defaults = [
                    ("pol_01", "Reject assistant-originated assumptions without explicit user evidence.", PolicyAction.REJECT, 20, {"source_speaker": "assistant"}, [MemoryType.PERSONA, MemoryType.PREFERENCE, MemoryType.GOAL]),
                    ("pol_02", "Require explicit user confirmation before storing sensitive financial/health records.", PolicyAction.REQUIRE_CONFIRMATION, 15, {}, [MemoryType.CONSTRAINT]),
                    ("pol_03", "Automatically retire old preference memories when a preference update occurs.", PolicyAction.ALLOW_STORE, 10, {}, [MemoryType.PREFERENCE]),
                ]
                for p_id, rule_txt, action, prio, cond, scopes in defaults:
                    cp = CompiledPolicy(
                        policy_id=p_id,
                        name="Project Policy",
                        description=rule_txt,
                        priority=prio,
                        action=action,
                        condition=cond,
                        scope=scopes
                    )
                    pr = PolicyRule(id=p_id, user_id=user_id, natural_language_rule=rule_txt, compiled_policy=cp)
                    self.save_policy(pr)
                rows = conn.execute("SELECT * FROM memory_policies WHERE user_id = ? AND active = 1 ORDER BY priority DESC", (user_id,)).fetchall()

            rules = []
            for r in rows:
                c_json = json.loads(r["compiled_policy_json"])
                rules.append(
                    PolicyRule(
                        id=r["id"],
                        user_id=r["user_id"],
                        natural_language_rule=r["natural_language_rule"],
                        compiled_policy=c_json,
                        active=bool(r["active"]),
                        created_at=datetime.fromisoformat(r["created_at"]),
                    )
                )
            return rules

    # --- Audit Logs ----------------------------------------------------------
    def get_audit_logs(self, user_id: str) -> List[AuditLog]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM audit_logs WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
            return [
                AuditLog(
                    id=r["id"],
                    user_id=r["user_id"],
                    operation=r["operation"],
                    input_ref=r["input_ref"],
                    decision=r["decision"],
                    reason=r["reason"],
                    confidence=r["confidence"],
                    created_at=datetime.fromisoformat(r["created_at"]),
                )
                for r in rows
            ]
