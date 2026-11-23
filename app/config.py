import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.environ.get("VERIMEM_DB_PATH", str(BASE_DIR / "data" / "verimem.db"))
LLM_MODEL = os.environ.get("VERIMEM_MODEL", "gemini-3.8-flash")
ANTHROPIC_MODEL = LLM_MODEL
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ENABLE_OFFLINE_HEURISTICS = os.environ.get("VERIMEM_OFFLINE", "0").lower() in ("1", "true", "yes")

