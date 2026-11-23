"""
Streamlit 5-Tab Dashboard UI for VeriMem (Section 20).
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import streamlit as st
from app.llm_client import HeuristicLLMClient
from app.memory.conflict_detector import ConflictDetector
from app.memory.decision_controller import MemoryDecisionController
from app.memory.decomposer import AtomicFactDecomposer
from app.memory.extractor import MemoryCandidateExtractor
from app.memory.policy_engine import PolicyEngine
from app.memory.retriever import HybridRetriever
from app.memory.store import MemoryStore
from app.memory.verifier import EvidenceGroundingVerifier
from app.schemas import Speaker, Turn
from evaluation.halumem_runner import EvaluationRunner

st.set_page_config(page_title="VeriMem Dashboard", page_icon="🧠", layout="wide")

st.title("🧠 VeriMem: Hallucination-Aware Memory Layer")
st.caption("Natural-Language Programmable Memory Engine for Agentic AI")

user_id = st.sidebar.text_input("User ID", value="u_001")
session_id = st.sidebar.text_input("Session ID", value="s_001")

store = MemoryStore()
llm = HeuristicLLMClient()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 Chat", "🧠 Memories", "📜 Policies", "🔍 Audit Log", "📊 Evaluation"])

# --- Tab 1: Chat ---
with tab1:
    st.subheader("Interactive Dialogue & Memory Extractor")

    turns = store.get_turns_for_session(session_id)
    for t in turns:
        role = "user" if t.speaker == Speaker.USER else "assistant"
        st.chat_message(role).write(t.text)

    user_input = st.chat_input("Say something to the assistant...")
    if user_input:
        t_user = Turn(
            id=f"t_{len(turns)+1:03d}",
            conversation_id=session_id,
            user_id=user_id,
            speaker=Speaker.USER,
            text=user_input,
        )
        store.save_turn(t_user)

        # Pipeline execution
        all_turns = store.get_turns_for_session(session_id)
        extractor = MemoryCandidateExtractor(llm)
        decomposer = AtomicFactDecomposer(llm)
        verifier = EvidenceGroundingVerifier(llm)
        conflict_detector = ConflictDetector(llm)
        policy_engine = PolicyEngine(llm)
        decision_controller = MemoryDecisionController()

        candidates = extractor.extract([t_user])
        existing_memories = store.get_user_memories(user_id, status="active")
        user_policies = store.get_user_policies(user_id)

        for cand in candidates:
            store.save_candidate(cand)
            facts = decomposer.decompose(cand)
            grounding = verifier.verify(cand, facts, all_turns)
            conflict = conflict_detector.detect_conflict(cand, existing_memories)
            p_action = policy_engine.evaluate_policies(cand, grounding.grounding_label, user_policies)
            decision = decision_controller.decide(cand, grounding, conflict, p_action)
            store.commit_memory_decision(cand, grounding, decision)

        st.rerun()

    st.markdown("---")
    st.subheader("Ask Memory Question")
    q_input = st.text_input("Ask a question based on stored memories:")
    if st.button("Ask Question") and q_input:
        active_mem = store.get_user_memories(user_id, status="active")
        retriever = HybridRetriever()
        retrieved = retriever.retrieve(q_input, active_mem, top_k=5)
        if retrieved:
            ans = f"Based on verified memories ({', '.join([m.id for m, _ in retrieved])}): Your verified memories match '{retrieved[0][0].memory_text}'."
            st.success(ans)
        else:
            st.warning("I do not have enough verified memory to answer this question.")

# --- Tab 2: Memories ---
with tab2:
    st.subheader("Stored Memory Lifecycle States")
    m_status_filter = st.selectbox("Status Filter", ["all", "active", "uncertain", "retired", "rejected"])
    filter_val = None if m_status_filter == "all" else m_status_filter
    memories = store.get_user_memories(user_id, status=filter_val)

    if memories:
        for m in memories:
            with st.expander(f"[{m.status.value.upper()}] {m.id}: {m.memory_text}"):
                st.write(f"**Type:** {m.memory_type.value}")
                st.write(f"**Confidence:** {m.confidence}")
                st.write(f"**Version:** {m.version}")
                st.write(f"**Evidence Turns:** {m.evidence_turn_ids}")
    else:
        st.info("No memories found for this user.")

# --- Tab 3: Policies ---
with tab3:
    st.subheader("Natural Language Memory Policies")
    new_rule = st.text_input("Add a natural language memory rule:", placeholder="e.g. Do not remember assistant assumptions. Ask me before changing project goals.")
    if st.button("Compile & Activate Policy") and new_rule:
        p_engine = PolicyEngine(llm)
        rule = p_engine.compile_rule(user_id, new_rule)
        store.save_policy(rule)
        st.success(f"Policy '{rule.compiled_policy.name}' compiled and activated!")

    policies = store.get_user_policies(user_id)
    st.markdown("### Active Policies")
    for p in policies:
        st.json(p.compiled_policy.model_dump())

# --- Tab 4: Audit Log ---
with tab4:
    st.subheader("Memory Decision Audit Trail")
    logs = store.get_audit_logs(user_id)
    if logs:
        df_logs = pd.DataFrame([
            {
                "Time": l.created_at.strftime("%H:%M:%S"),
                "Operation": l.operation,
                "Candidate Ref": l.input_ref,
                "Decision": l.decision,
                "Reason": l.reason,
                "Confidence": l.confidence,
            }
            for l in logs
        ])
        st.dataframe(df_logs, use_container_width=True)
    else:
        st.info("No audit entries recorded.")

# --- Tab 5: Evaluation ---
with tab5:
    st.subheader("Operation-Level Hallucination Benchmark")
    if st.button("Run HaluMem Benchmark Evaluation"):
        runner = EvaluationRunner()
        results = runner.run_benchmark()
        st.json(results)
