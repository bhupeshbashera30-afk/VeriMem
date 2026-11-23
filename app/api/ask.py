"""
Grounded QA API (Section 14.4).
"""

from __future__ import annotations

from typing import Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.answer_agent import AnswerAgent
from app.config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL, ENABLE_OFFLINE_HEURISTICS
from app.llm_client import AnthropicLLMClient, HeuristicLLMClient, GeminiLLMClient, get_default_llm_client
from app.memory.retriever import HybridRetriever
from app.memory.store import MemoryStore

router = APIRouter(prefix="/users", tags=["QA"])
store = MemoryStore()


def get_llm():
    if ENABLE_OFFLINE_HEURISTICS:
        return HeuristicLLMClient()
    return get_default_llm_client()


class AskRequest(BaseModel):
    question: str


@router.post("/{user_id}/ask")
def ask_question(user_id: str, req: AskRequest) -> Dict[str, Any]:
    active_memories = store.get_user_memories(user_id, status="active")
    retriever = HybridRetriever()
    retrieved = retriever.retrieve(req.question, active_memories, top_k=5)

    llm = get_llm()
    answer_agent = AnswerAgent(llm)
    grounded_ans = answer_agent.generate_answer(req.question, retrieved)

    return grounded_ans.model_dump()
