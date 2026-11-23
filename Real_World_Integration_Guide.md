# Real-World Production Integration Guide for VeriMem

This guide outlines how to integrate **VeriMem** into production AI applications, customer support agents, personal AI assistants, or enterprise workflow engines.

---

## 🏗️ 1. Architecture Overview (Sidecar / Microservice Pattern)

In production, VeriMem acts as an independent **Memory Middleware Microservice** between your Chat Interface/LLM Agent and your Primary Database.

```
┌─────────────────┐       1. User Message       ┌────────────────────────┐
│  React/Mobile   │ ──────────────────────────► │  Your Backend Application│
│  Chat Frontend  │                             │  (Node.js/Python/Go)   │
└─────────────────┘                             └───────────┬────────────┘
         ▲                                                  │
         │ 6. Grounded Response                             │ 2. Ingest Turn
         │                                                  ▼
┌────────┴────────┐       5. Query Grounded     ┌────────────────────────┐
│  LLM Provider   │ ◄────────────────────────── │  VeriMem API Engine    │
│ (Claude / GPT-4)│       Active Memories       │  (FastAPI on Port 8000)│
└─────────────────┘                             └───────────┬────────────┘
                                                            │
                                                            │ 3. Extract, Verify,
                                                            │    Policy & Write
                                                            ▼
                                                ┌────────────────────────┐
                                                │ Production Database    │
                                                │ (PostgreSQL + pgvector)│
                                                └────────────────────────┘
```

---

## 🔌 2. Step-by-Step API Integration Flow

### Step A: Ingest Conversation Turns
After every user message in your chat app, send the turn to VeriMem:
```bash
POST http://verimem-service:8000/sessions/{session_id}/turns
Content-Type: application/json

{
  "user_id": "usr_9921",
  "speaker": "user",
  "text": "Actually, I prefer TypeScript over JavaScript for backend development."
}
```

### Step B: Trigger Background Memory Processing
Run memory extraction, evidence grounding verification, policy check, and temporal updates asynchronously (via Celery, Redis Queue, or FastAPI background task):
```bash
POST http://verimem-service:8000/sessions/{session_id}/process-memory
```
*VeriMem will:*
1. Extract candidate facts.
2. Decompose into atomic claims.
3. Verify evidence grounding against dialogue turns.
4. Detect preference conflicts (retires old JavaScript memory, activates TypeScript memory).

### Step C: Retrieve Grounded Context for LLM Prompts
Before generating an AI response to a user prompt, query VeriMem for verified memories:
```bash
POST http://verimem-service:8000/users/usr_9921/ask
Content-Type: application/json

{
  "question": "What language should we use for the new backend project?"
}
```

*Response:*
```json
{
  "answer": "Based on your verified memory: User prefers TypeScript over JavaScript [mem_88a91c].",
  "confidence": 0.95,
  "citations": [{"memory_id": "mem_88a91c", "memory_text": "User prefers TypeScript"}]
}
```

---

## 🗄️ 3. Scaling the Database (SQLite → PostgreSQL + pgvector)

For high-concurrency production deployments handling millions of users:

1. **Replace SQLite with PostgreSQL**: Update `DB_PATH` in `app/config.py` to a PostgreSQL connection URI:
   ```env
   DATABASE_URL="postgresql://user:pass@ep-prod.postgres.database.azure.com:5432/verimem_db"
   ```
2. **Enable Vector Embeddings**: Store semantic vector embeddings (`pgvector` or Supabase Vector) alongside atomic memories in `memories` table for sub-millisecond semantic retrieval.

---

## 🔑 4. Production LLM Configuration

To connect production AI models (Anthropic Claude 3.5 Sonnet / OpenAI GPT-4o), configure environment variables:

```env
# Disable test heuristics & enable Production LLMs
ENABLE_OFFLINE_HEURISTICS=0

# Provider Credentials
ANTHROPIC_API_KEY="sk-ant-api03-..."
VERIMEM_MODEL="claude-3-5-sonnet-20241022"

# Security & CORS
ALLOWED_ORIGINS="https://your-production-app.com"
```

---

## 🛡️ 5. Real-World Use Cases

| Industry | Real-World Application | VeriMem Value Proposition |
| :--- | :--- | :--- |
| **Personal AI Assistants** | Long-term memory across sessions | Retires outdated preference shift memories (e.g. diet shifts, tech stack changes). |
| **Healthcare & Telemedicine** | Patient intake AI bot | Enforces natural-language policy: *"Require user confirmation before recording medical history"*. |
| **Enterprise Customer Support** | Automated support agents | Prevents memory hallucinations; only answers based on grounded conversation turns with citations. |
| **Financial AI Advisors** | Wealth management agents | Logs complete operation audit trails for regulatory compliance. |
