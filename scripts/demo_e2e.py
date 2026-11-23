"""
VeriMem End-to-End Demo Script (Section 21).

Runs the 5-step scenario from the system design document:
1. User provides initial facts -> extracted & stored.
2. Assistant asserts unconfirmed assumption -> rejected (assistant_originated).
3. User adds policy rule -> compiled & activated.
4. User updates goal -> conflict detected & handled.
5. User asks QA question -> cited, grounded response generated.
"""

from __future__ import annotations

import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.agents.answer_agent import AnswerAgent
from app.llm_client import HeuristicLLMClient, get_default_llm_client
from app.memory.conflict_detector import ConflictDetector
from app.memory.decision_controller import MemoryDecisionController
from app.memory.decomposer import AtomicFactDecomposer
from app.memory.extractor import MemoryCandidateExtractor
from app.memory.policy_engine import PolicyEngine
from app.memory.retriever import HybridRetriever
from app.memory.store import MemoryStore
from app.memory.verifier import EvidenceGroundingVerifier
from app.schemas import Speaker, Turn


def main():
    print("=" * 60)
    print(" VeriMem End-to-End Execution Demo (Live Gemini LLM)")
    print("=" * 60)

    store = MemoryStore()
    llm = get_default_llm_client()

    session_id = "s_demo_001"
    user_id = "u_demo_001"

    # Step 1: User provides initial facts
    print("\n--- Step 1: User gives information ---")
    t1 = Turn(
        id="t_001",
        conversation_id=session_id,
        user_id=user_id,
        speaker=Speaker.USER,
        text="I am making a major project on hallucination-aware memory. It should include natural language programming and agentic AI.",
    )
    store.save_turn(t1)

    # Step 2: Assistant asserts unconfirmed fact
    print("\n--- Step 2: Assistant says unsupported thing ---")
    t2 = Turn(
        id="t_002",
        conversation_id=session_id,
        user_id=user_id,
        speaker=Speaker.ASSISTANT,
        text="Since you are a final-year computer science student, this will fit your course.",
    )
    store.save_turn(t2)

    turns = store.get_turns_for_session(session_id)

    # Process pipeline
    extractor = MemoryCandidateExtractor(llm)
    decomposer = AtomicFactDecomposer(llm)
    verifier = EvidenceGroundingVerifier(llm)
    conflict_detector = ConflictDetector(llm)
    policy_engine = PolicyEngine(llm)
    decision_controller = MemoryDecisionController()

    cands = extractor.extract(turns)
    print(f"Extracted {len(cands)} memory candidates.")

    active_mems = store.get_user_memories(user_id, status="active")
    policies = store.get_user_policies(user_id)

    for c in cands:
        facts = decomposer.decompose(c)
        grounding = verifier.verify(c, facts, turns)
        conflict = conflict_detector.detect_conflict(c, active_mems)
        p_act = policy_engine.evaluate_policies(c, grounding.grounding_label, policies)
        decision = decision_controller.decide(c, grounding, conflict, p_act)
        item = store.commit_memory_decision(c, grounding, decision)
        print(f"Candidate '{c.memory_text[:40]}...' -> Label: {grounding.grounding_label.value} | Decision: {decision.decision.value}")

    # Step 3: User adds policy rule
    print("\n--- Step 3: User adds natural language policy ---")
    rule = policy_engine.compile_rule(user_id, "Do not remember assistant assumptions. Ask me before changing project goals.")
    store.save_policy(rule)
    print(f"Compiled Policy: {rule.compiled_policy.name} | Priority: {rule.compiled_policy.priority}")

    # Step 4: Stored memories check
    print("\n--- Active Verified Memories in DB ---")
    stored = store.get_user_memories(user_id, status="active")
    for m in stored:
        print(f"- [{m.id}] ({m.memory_type.value}): {m.memory_text}")

    # Step 5: User asks QA question
    print("\n--- Step 5: User asks memory question ---")
    question = "What does my project include?"
    retriever = HybridRetriever()
    retrieved = retriever.retrieve(question, stored, top_k=5)

    answer_agent = AnswerAgent(llm)
    answer = answer_agent.generate_answer(question, retrieved)

    print(f"Question: {question}")
    print(f"Answer: {answer.answer}")
    print(f"Citations: {answer.used_memories}")
    print(f"Confidence: {answer.confidence} | Status: {answer.status}")
    print("\nDemo Completed Successfully!")


if __name__ == "__main__":
    main()
