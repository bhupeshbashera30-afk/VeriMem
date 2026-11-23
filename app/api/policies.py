"""
Natural Language Policy API (Section 14.5).
"""

from __future__ import annotations

from typing import Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel

from app.config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL, ENABLE_OFFLINE_HEURISTICS
from app.llm_client import AnthropicLLMClient, HeuristicLLMClient
from app.memory.policy_engine import PolicyEngine
from app.memory.store import MemoryStore

router = APIRouter(prefix="/users", tags=["Policies"])
store = MemoryStore()


def get_llm():
    if ANTHROPIC_API_KEY and not ENABLE_OFFLINE_HEURISTICS:
        return AnthropicLLMClient(model=ANTHROPIC_MODEL)
    return HeuristicLLMClient()


class AddPolicyRequest(BaseModel):
    rule: str


@router.post("/{user_id}/policies")
def create_policy(user_id: str, req: AddPolicyRequest) -> Dict[str, Any]:
    llm = get_llm()
    engine = PolicyEngine(llm)
    rule = engine.compile_rule(user_id, req.rule)
    store.save_policy(rule)
    return {
        "policy_id": rule.id,
        "natural_language_rule": rule.natural_language_rule,
        "compiled_policy": rule.compiled_policy.model_dump(),
        "active": rule.active,
    }


@router.get("/{user_id}/policies")
def get_policies(user_id: str) -> Dict[str, Any]:
    policies = store.get_user_policies(user_id)
    return {
        "user_id": user_id,
        "policies": [
            {
                "id": p.id,
                "rule": p.natural_language_rule,
                "compiled": p.compiled_policy.model_dump(),
                "active": p.active,
            }
            for p in policies
        ],
    }
