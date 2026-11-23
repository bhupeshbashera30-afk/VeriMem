# VeriMem: Hallucination-Aware Natural-Language Programmable Memory for Agentic AI

VeriMem is a long-term memory layer for AI agents that extracts, verifies, updates, retrieves, and uses memories while systematically eliminating memory hallucinations.

## Key Features

1. **Operation-Level Hallucination Mitigation**: Verifies every memory candidate against conversation evidence turns before writing to memory.
2. **Deterministic Safety Safeguards**: Rejects assistant-originated assumptions without user confirmation.
3. **Atomic Fact Decomposition**: Decomposes complex multi-claim statements into minimal atomic facts to prevent half-true memories.
4. **Natural-Language Programmable Memory Policy Layer**: Users define memory policies in natural English, compiled into executable JSON policy schemas.
5. **Conflict & Temporal Update Resolution**: Versioned memory updates supporting preference shifts, value conflicts, and temporal timelines.
6. **Multi-Signal Hybrid Retriever**: Scores active memories based on semantic similarity, keyword overlap, recency, confidence, and policy permissions.
7. **Evidence-Grounded QA & Audit Trail**: Answers questions using only verified active memories with citations and confidence scores.

---

## Project Structure

```
verimem/
├── app/
│   ├── main.py                     # FastAPI application entry point
│   ├── config.py                   # Environment & system configuration
│   ├── schemas.py                  # Pydantic data models & DB schemas
│   ├── llm_client.py               # Swappable LLM interface (Anthropic API + Heuristic)
│   ├── memory/
│   │   ├── extractor.py            # Section 7.2: Candidate Memory Extractor
│   │   ├── decomposer.py           # Section 7.4: Atomic Fact Decomposer
│   │   ├── verifier.py             # Section 7.3: Evidence Grounding Verifier
│   │   ├── conflict_detector.py    # Section 7.5: Conflict & Update Detector
│   │   ├── policy_engine.py        # Section 7.6 / 13: Policy Engine & Compiler
│   │   ├── decision_controller.py  # Section 7.7: Memory Decision Controller
│   │   ├── store.py                # Section 7.8 / 10: SQLite Hybrid Store
│   │   └── retriever.py            # Section 7.9: Multi-Signal Hybrid Retriever
│   ├── agents/
│   │   ├── answer_agent.py         # Section 7.10: Grounded Answer Agent
│   │   └── audit_agent.py          # Section 12: Audit Log Explanation Agent
│   └── api/
│       ├── sessions.py             # Session turn ingestion & memory processing API
│       ├── memories.py             # Active memory retrieval API
│       ├── policies.py             # Natural-language policy API
│       ├── ask.py                  # Grounded QA query API
│       └── audit.py                # Audit log & explanation API
├── evaluation/
│   ├── metrics.py                  # Operation-level evaluation metrics
│   ├── synthetic_dataset.py        # Synthetic dataset generator (Level 1)
│   └── halumem_runner.py          # Benchmark comparison runner
├── ui/
│   └── streamlit_app.py            # 5-Tab Streamlit Dashboard UI
├── tests/
│   ├── test_extraction.py         # Extractor tests
│   ├── test_verification.py       # Evidence verifier tests
│   ├── test_conflicts.py          # Conflict detector tests
│   ├── test_policy_engine.py      # Policy engine tests
│   └── test_qa_grounding.py       # Grounded QA tests
├── scripts/
│   └── demo_e2e.py                 # End-to-End demonstration script
├── data/                           # SQLite database & JSON benchmarks
├── requirements.txt
└── README.md
```

---

## Quickstart Guide

### 1. Installation
```bash
cd verimem
pip install -r requirements.txt
```

### 2. Run End-to-End Demo Script
```bash
python -m scripts.demo_e2e
```

### 3. Run Automated Unit Tests
```bash
python -m pytest tests/ -v
```

### 4. Start FastAPI Backend Server
```bash
python -m app.main
```
FastAPI interactive Swagger documentation will be available at: `http://localhost:8000/docs`

### 5. Launch Streamlit UI Dashboard
```bash
streamlit run ui/streamlit_app.py
```

---

## Environment Variables (Optional)

- `ANTHROPIC_API_KEY`: Anthropic API key for production LLM operations.
- `VERIMEM_MODEL`: Model name (default: `claude-sonnet-4-6`).
- `VERIMEM_OFFLINE`: Set to `1` to run in deterministic offline heuristic mode without API keys.
