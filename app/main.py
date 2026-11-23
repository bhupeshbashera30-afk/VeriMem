"""
VeriMem FastAPI Server Application Entry Point.
"""

from __future__ import annotations

import os
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api import ask, audit, memories, policies, sessions, pipeline

app = FastAPI(
    title="VeriMem API",
    description="Hallucination-Aware Natural-Language Programmable Memory for Agentic AI",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router)
app.include_router(memories.router)
app.include_router(policies.router)
app.include_router(ask.router)
app.include_router(audit.router)
app.include_router(pipeline.router)

# Legacy fallback routes for cached client requests
@app.get("/memories/{user_id}")
def legacy_get_memories(user_id: str, status: Optional[str] = "active"):
    return memories.get_user_memories(user_id, status=status)

@app.get("/policies/{user_id}")
def legacy_get_policies(user_id: str):
    return policies.get_policies(user_id)

@app.get("/audit/{user_id}")
def legacy_get_audit(user_id: str):
    return audit.get_user_audit_logs(user_id)

dist_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard", "dist")
if os.path.exists(dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")

    @app.get("/")
    def serve_dashboard():
        return FileResponse(os.path.join(dist_path, "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "status": "online",
            "system": "VeriMem",
            "description": "Hallucination-Aware Natural-Language Programmable Memory Engine",
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
