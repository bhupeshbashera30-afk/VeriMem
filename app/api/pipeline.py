"""
Pipeline Execution Tracing API for Visual n8n Canvas Inspector.
"""

from __future__ import annotations

import uuid
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL, ENABLE_OFFLINE_HEURISTICS
from app.llm_client import AnthropicLLMClient, HeuristicLLMClient
from app.memory.conflict_detector import ConflictDetector
from app.memory.decision_controller import MemoryDecisionController
from app.memory.decomposer import AtomicFactDecomposer
from app.memory.extractor import MemoryCandidateExtractor
from app.memory.policy_engine import PolicyEngine
from app.memory.store import MemoryStore
from app.memory.verifier import EvidenceGroundingVerifier
from app.memory.retriever import HybridRetriever
from app.agents.answer_agent import AnswerAgent
from app.schemas import Speaker, Turn

from app.llm_client import AnthropicLLMClient, HeuristicLLMClient, GeminiLLMClient, get_default_llm_client

router = APIRouter(prefix="/pipeline", tags=["Pipeline Inspector"])
store = MemoryStore()


def get_llm():
    if ENABLE_OFFLINE_HEURISTICS:
        return HeuristicLLMClient()
    return get_default_llm_client()


class TraceTurnRequest(BaseModel):
    user_id: str
    speaker: str = "user"
    text: str
    session_id: Optional[str] = None


class TraceRecallRequest(BaseModel):
    user_id: str
    question: str


from app.memory.extractor import MemoryCandidateExtractor, is_question_text


@router.post("/ingest-trace")
def trace_ingest_turn(req: TraceTurnRequest) -> Dict[str, Any]:
    session_id = req.session_id or f"sess_{uuid.uuid4().hex[:8]}"
    
    try:
        spk = Speaker(req.speaker)
    except ValueError:
        spk = Speaker.USER

    turn_id = f"t_{uuid.uuid4().hex[:8]}"
    turn = Turn(
        id=turn_id,
        conversation_id=session_id,
        user_id=req.user_id,
        speaker=spk,
        text=req.text,
    )
    store.save_turn(turn)
    turns = store.get_turns_for_session(session_id)
    
    # Auto-detect questions sent via ingest route and answer them from verified memory bank
    if is_question_text(req.text):
        recall_res = trace_recall(TraceRecallRequest(user_id=req.user_id, question=req.text))
        return {
            "mode": "recall",
            "is_question": True,
            "session_id": session_id,
            "turn_id": turn_id,
            "nodes": recall_res.get("nodes", []),
            "edges": recall_res.get("edges", []),
            "answer": recall_res.get("answer", {}),
            "processed_candidates": []
        }

    llm = get_llm()
    extractor = MemoryCandidateExtractor(llm)
    decomposer = AtomicFactDecomposer(llm)
    verifier = EvidenceGroundingVerifier(llm)
    conflict_detector = ConflictDetector(llm)
    policy_engine = PolicyEngine(llm)
    decision_controller = MemoryDecisionController()

    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    # Node 1: User Turn Input
    nodes.append({
        "id": "node_input",
        "label": "User Input Ingestion",
        "type": "trigger",
        "icon": "MessageSquare",
        "status": "success",
        "timestamp": turn.timestamp.isoformat(),
        "details": {
            "session_id": session_id,
            "turn_id": turn_id,
            "speaker": req.speaker,
            "text": req.text,
            "total_turns_in_session": len(turns)
        }
    })

    # Step 2: Extraction
    candidates = extractor.extract(turns)
    nodes.append({
        "id": "node_extractor",
        "label": "Candidate Extractor",
        "type": "processor",
        "icon": "Filter",
        "status": "success" if candidates else "idle",
        "details": {
            "candidates_count": len(candidates),
            "candidates": [
                {
                    "id": c.id,
                    "text": c.memory_text,
                    "category": c.memory_type.value,
                    "confidence": c.extraction_confidence
                } for c in candidates
            ]
        }
    })
    edges.append({"from": "node_input", "to": "node_extractor", "label": f"{len(candidates)} Candidate(s)"})

    processed_candidates = []
    existing_memories = store.get_user_memories(req.user_id, status="active")
    user_policies = store.get_user_policies(req.user_id)

    for idx, cand in enumerate(candidates):
        store.save_candidate(cand)

        # Decompose
        facts = decomposer.decompose(cand)
        
        # Verify
        grounding = verifier.verify(cand, facts, turns)
        
        # Conflict
        conflict = conflict_detector.detect_conflict(cand, existing_memories)
        
        # Policy
        policy_action = policy_engine.evaluate_policies(cand, grounding.grounding_label, user_policies)
        
        # Decision
        decision = decision_controller.decide(cand, grounding, conflict, policy_action)
        
        # Commit
        mem_item = store.commit_memory_decision(cand, grounding, decision)

        processed_candidates.append({
            "candidate": cand.model_dump(),
            "facts": [f.model_dump() for f in facts],
            "grounding": grounding.model_dump(),
            "conflict": conflict.model_dump(),
            "policy_action": policy_action.value,
            "decision": decision.model_dump(),
            "committed_memory_id": mem_item.id if mem_item else None
        })

    # Node 3: Fact Decomposer
    all_facts = []
    for pc in processed_candidates:
        all_facts.extend(pc["facts"])
    
    nodes.append({
        "id": "node_decomposer",
        "label": "Atomic Fact Decomposer",
        "type": "processor",
        "icon": "Split",
        "status": "success" if all_facts else "idle",
        "details": {
            "total_atomic_facts": len(all_facts),
            "facts": all_facts
        }
    })
    edges.append({"from": "node_extractor", "to": "node_decomposer", "label": f"{len(all_facts)} Fact(s)"})

    # Node 4: Evidence Grounding Verifier
    nodes.append({
        "id": "node_verifier",
        "label": "Evidence Grounding Verifier",
        "type": "verifier",
        "icon": "ShieldCheck",
        "status": "success" if processed_candidates else "idle",
        "details": {
            "verifications": [
                {
                    "candidate_id": pc["candidate"]["id"],
                    "grounding_label": pc["grounding"]["grounding_label"],
                    "confidence": pc["grounding"]["grounding_confidence"],
                    "evidence_turns": [s.get("turn_id") for s in pc["grounding"].get("evidence_spans", [])],
                    "reason": pc["grounding"].get("rationale") or "Evidence verified"
                } for pc in processed_candidates
            ]
        }
    })
    edges.append({"from": "node_decomposer", "to": "node_verifier", "label": "Grounding Check"})

    # Node 5: Conflict & Update Detector
    nodes.append({
        "id": "node_conflict",
        "label": "Conflict & Update Detector",
        "type": "detector",
        "icon": "Zap",
        "status": "success" if processed_candidates else "idle",
        "details": {
            "conflicts": [
                {
                    "candidate_id": pc["candidate"]["id"],
                    "status": pc["conflict"]["conflict_status"],
                    "action": pc["conflict"]["recommended_action"],
                    "related_memories": pc["conflict"]["related_memory_ids"],
                    "reason": pc["conflict"]["reason"]
                } for pc in processed_candidates
            ]
        }
    })
    edges.append({"from": "node_verifier", "to": "node_conflict", "label": "Conflict Resolution"})

    # Node 6: Policy Engine
    nodes.append({
        "id": "node_policy",
        "label": "Natural-Language Policy Engine",
        "type": "policy",
        "icon": "FileText",
        "status": "success" if processed_candidates else "idle",
        "details": {
            "active_policies_count": len(user_policies),
            "evaluations": [
                {
                    "candidate_id": pc["candidate"]["id"],
                    "action": pc["policy_action"]
                } for pc in processed_candidates
            ]
        }
    })
    edges.append({"from": "node_conflict", "to": "node_policy", "label": "Policy Evaluation"})

    # Node 7: Decision Controller & SQLite Store
    nodes.append({
        "id": "node_store",
        "label": "Decision Controller & Memory Store",
        "type": "store",
        "icon": "Database",
        "status": "success" if processed_candidates else "idle",
        "details": {
            "committed_operations": [
                {
                    "candidate_id": pc["candidate"]["id"],
                    "decision": pc["decision"]["decision"],
                    "reason": pc["decision"]["reason"],
                    "committed_memory_id": pc["committed_memory_id"]
                } for pc in processed_candidates
            ],
            "total_active_memories": len(store.get_user_memories(req.user_id, status="active"))
        }
    })
    edges.append({"from": "node_policy", "to": "node_store", "label": "DB Commit"})

    return {
        "mode": "ingest",
        "session_id": session_id,
        "turn_id": turn_id,
        "nodes": nodes,
        "edges": edges,
        "processed_candidates": processed_candidates
    }


@router.post("/recall-trace")
def trace_recall(req: TraceRecallRequest) -> Dict[str, Any]:
    active_memories = store.get_user_memories(req.user_id, status="active")
    retriever = HybridRetriever()
    retrieved = retriever.retrieve(req.question, active_memories, top_k=5)

    llm = get_llm()
    answer_agent = AnswerAgent(llm)
    grounded_ans = answer_agent.generate_answer(req.question, retrieved)

    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    # Node 1: User Query
    nodes.append({
        "id": "node_query",
        "label": "User Query Input",
        "type": "trigger",
        "icon": "HelpCircle",
        "status": "success",
        "details": {
            "user_id": req.user_id,
            "question": req.question
        }
    })

    # Node 2: Memory Bank Scan
    nodes.append({
        "id": "node_mem_scan",
        "label": "Active Memory Store Scan",
        "type": "store",
        "icon": "Database",
        "status": "success",
        "details": {
            "total_active_memories": len(active_memories),
            "memories": [m.model_dump() for m in active_memories]
        }
    })
    edges.append({"from": "node_query", "to": "node_mem_scan", "label": "Query Context"})

    # Node 3: Multi-Signal Hybrid Retriever
    retrieved_details = []
    for mem_item, score in retrieved:
        retrieved_details.append({
            "memory_id": mem_item.id,
            "text": mem_item.memory_text,
            "combined_score": round(score, 4),
            "signals": {
                "semantic": round(score, 4),
                "keyword": round(score, 4),
                "recency": 0.9,
                "confidence": mem_item.confidence,
                "policy_allowed": True
            }
        })

    nodes.append({
        "id": "node_retriever",
        "label": "Multi-Signal Hybrid Retriever",
        "type": "processor",
        "icon": "Cpu",
        "status": "success" if retrieved else "warning",
        "details": {
            "top_k": len(retrieved),
            "scoring_formula": "0.35*Semantic + 0.25*Keyword + 0.20*Recency + 0.20*Confidence",
            "results": retrieved_details
        }
    })
    edges.append({"from": "node_mem_scan", "to": "node_retriever", "label": f"{len(retrieved)} Relevant Memory(ies)"})

    # Node 4: Grounded Answer Agent
    nodes.append({
        "id": "node_answer_agent",
        "label": "Grounded Answer Agent",
        "type": "agent",
        "icon": "Sparkles",
        "status": "success",
        "details": {
            "answer": grounded_ans.answer,
            "confidence": grounded_ans.confidence,
            "citations": [c.get("memory_id") for c in grounded_ans.citations] if grounded_ans.citations else []
        }
    })
    edges.append({"from": "node_retriever", "to": "node_answer_agent", "label": "Grounded Response Generation"})

    return {
        "mode": "recall",
        "question": req.question,
        "nodes": nodes,
        "edges": edges,
        "answer": grounded_ans.model_dump()
    }
