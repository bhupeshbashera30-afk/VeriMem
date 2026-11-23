"""
Audit Agent (Section 12 - Agentic Design).

Explains memory decision audit logs, rejections, updates, and policy enforcement in human-readable terms.
"""

from __future__ import annotations

from typing import List, Dict, Any
from app.schemas import AuditLog


class AuditAgent:
    def explain_log(self, log: AuditLog) -> Dict[str, Any]:
        explanation = {
            "log_id": log.id,
            "operation": log.operation,
            "decision": log.decision,
            "confidence": log.confidence,
            "timestamp": log.created_at.isoformat(),
            "plain_explanation": f"Operation '{log.operation}' on candidate {log.input_ref} resulted in decision [{log.decision}]. Rationale: {log.reason}",
        }
        return explanation

    def summarize_audit_trail(self, logs: List[AuditLog]) -> Dict[str, Any]:
        total = len(logs)
        decisions = {}
        for l in logs:
            decisions[l.decision] = decisions.get(l.decision, 0) + 1

        return {
            "total_decisions": total,
            "decision_breakdown": decisions,
            "recent_logs": [self.explain_log(l) for l in logs[:10]],
        }
