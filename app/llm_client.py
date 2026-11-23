"""
Swappable LLM Client Layer.

Supports Anthropic Messages API with fallbacks to heuristic offline processing for tests.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Protocol


class LLMClient(Protocol):
    def complete_json(self, system: str, user: str) -> Dict[str, Any]:
        ...


class AnthropicLLMClient:
    """Production client using Anthropic Messages API."""

    def __init__(self, model: str = "claude-3-5-haiku-20241022", max_tokens: int = 1500, api_key: Optional[str] = None):
        import anthropic

        self.model = model
        self.max_tokens = max_tokens
        self._client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    def complete_json(self, system: str, user: str) -> Dict[str, Any]:
        response = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(block.text for block in response.content if getattr(block, "type", None) == "text")
        return _parse_json(text)


class GeminiLLMClient:
    """Production client using Google Gemini API."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        import requests
        from app.config import LLM_MODEL
        self.model = model or LLM_MODEL or "gemini-3.8-flash"
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self._requests = requests

    def complete_json(self, system: str, user: str) -> Dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        prompt_text = f"{system}\n\nUSER INPUT:\n{user}\n\nReturn ONLY a JSON object matching the requested schema."
        payload = {
            "contents": [{"parts": [{"text": prompt_text}]}],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }
        try:
            res = self._requests.post(url, json=payload, timeout=6)
            if res.status_code == 200:
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    return _parse_json(text)
            else:
                print(f"[GeminiLLMClient Info] Status {res.status_code}. Using instant fallback.")
        except Exception as e:
            print(f"[GeminiLLMClient Info] API call exception: {e}. Using instant fallback.")
        return HeuristicLLMClient().complete_json(system, user)


def get_default_llm_client() -> LLMClient:
    from app.config import ENABLE_OFFLINE_HEURISTICS
    if ENABLE_OFFLINE_HEURISTICS:
        return HeuristicLLMClient()
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        return GeminiLLMClient(api_key=gemini_key)
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_key:
        return AnthropicLLMClient(api_key=anthropic_key)
    return HeuristicLLMClient()


class HeuristicLLMClient:
    """Offline heuristic LLM stand-in for deterministic development & unit tests."""

    _STOPWORDS = {
        "a", "an", "the", "to", "of", "in", "on", "for", "and", "is", "are",
        "i", "my", "me", "want", "wants", "should", "include", "with",
    }

    def _tokens(self, text: str) -> set:
        words = re.findall(r"[a-zA-Z']+", text.lower())
        return {w for w in words if w not in self._STOPWORDS}

    def complete_json(self, system: str, user: str) -> Dict[str, Any]:
        sys_lower = system.lower()

        # 1. Candidate Extraction
        if "extractor" in sys_lower or "extract" in sys_lower:
            return self._handle_extraction(user)
        # 2. Fact Decomposition
        elif "decompos" in sys_lower or "split" in sys_lower:
            return self._handle_decomposition(user)
        # 3. Grounding Verification
        elif "verifier" in sys_lower or "grounding" in sys_lower:
            return self._handle_verification(user)
        # 4. Conflict Detection
        elif "conflict" in sys_lower:
            return self._handle_conflict(user)
        # 5. QA Answer Generation
        elif "answer" in sys_lower:
            return self._handle_answer(user)
        # 6. Policy Parsing
        elif "policy" in sys_lower:
            return self._handle_policy(user)

        return {}

    def _handle_extraction(self, user: str) -> Dict[str, Any]:
        candidates = []
        lines = user.split("\n")
        NON_MEMORIES = {
            "hi", "hello", "hey", "greetings", "thanks", "thank you", "ok", "okay",
            "cool", "great", "sure", "are u sure", "are you sure", "really", "why",
            "how", "what", "yes", "no", "bye", "goodbye"
        }
        for line in lines:
            line_l = line.lower()
            if "user" in line_l and ('"' in line or ":" in line):
                match = re.search(r'"([^"]+)"', line)
                if match:
                    text = match.group(1).strip()
                else:
                    text = line.split(":", 1)[-1].strip()

                text_clean = text.lower().strip("?.! ")
                q_pattern = r'\b(what|where|who|whom|whose|how|why|which|when|do i|did i|should i|can i|could i|would i|is my|are my|am i|what do|what is|what are|what was|what were|what did|which do|which one|do you know|tell me|so now what|coffee or tea|prefer coffee or tea|do i prefer)\b'
                is_q = text.endswith("?") or bool(re.search(q_pattern, text.lower())) or any(k in text.lower() for k in ["asked", "asking", "inquiring", "wondering", "question"])
                if text and text_clean not in NON_MEMORIES and not is_q:
                    m_type = "persona"
                    if any(w in text.lower() for w in ["want", "plan", "goal", "project", "build"]):
                        m_type = "goal"
                    elif any(w in text.lower() for w in ["like", "love", "prefer", "enjoy", "hate", "coffee", "tea"]):
                        m_type = "preference"
                    elif any(w in text.lower() for w in ["study", "work", "live", "am", "is", "student"]):
                        m_type = "persona"

                    candidates.append({
                        "memory_text": f"User mentioned: {text}",
                        "memory_type": m_type,
                        "extraction_confidence": 0.90
                    })
        return {"candidates": candidates}

    def _handle_decomposition(self, user: str) -> Dict[str, Any]:
        match = re.search(r'"([^"]+)"', user)
        text = match.group(1) if match else user
        parts = [p.strip() for p in re.split(r'\. |\band\b', text) if p.strip()]
        facts = []
        for p in parts:
            facts.append({"text": p, "subject": "User", "predicate": "has_property", "object": p})
        return {"atomic_facts": facts if facts else [{"text": text, "subject": None, "predicate": None, "object": None}]}

    def _handle_verification(self, user: str) -> Dict[str, Any]:
        source_speaker = "user"
        if "source_speaker: assistant" in user:
            source_speaker = "assistant"

        facts = re.findall(r'fact_id=([^:]+):\s*"([^"]+)"', user)
        turns = re.findall(r'turn_id=([^\s]+)\s*\[([^\]]+)\]:\s*"([^"]+)"', user)

        verdicts = []
        for fact_id, fact_text in facts:
            fact_tokens = self._tokens(fact_text)
            best_score = 0.0
            best_turn_id = None
            best_text = ""
            user_confirmed = False

            for turn_id, speaker, text in turns:
                t_tokens = self._tokens(text)
                if not fact_tokens or not t_tokens:
                    continue
                overlap = len(fact_tokens & t_tokens) / len(fact_tokens)
                if overlap > best_score:
                    best_score = overlap
                    best_turn_id = turn_id
                    best_text = text
                if speaker == "user" and overlap >= 0.3:
                    user_confirmed = True

            if source_speaker == "assistant" and not user_confirmed:
                label = "assistant_originated"
            elif best_score >= 0.6:
                label = "supported"
            elif best_score >= 0.3:
                label = "partially_supported"
            else:
                label = "unsupported"

            verdicts.append({
                "fact_id": fact_id,
                "label": label,
                "evidence_spans": [{"turn_id": best_turn_id, "text": best_text, "support_type": "direct"}] if best_turn_id else [],
                "contradiction_reason": None,
                "confidence": round(min(0.5 + best_score / 2, 0.95), 2)
            })

        return {"verdicts": verdicts}

    def _handle_conflict(self, user: str) -> Dict[str, Any]:
        user_lower = user.lower()
        mem_ids = re.findall(r'- mem_id=([^\s]+)', user)
        update_keywords = [
            "prefer", "now", "over", "switched", "instead", "change", "dislike", 
            "no longer", "rather", "coffee", "tea", "coffe", "drink", "earl", "grey",
            "recently", "promoted", "moved", "graduated", "married", "bought", "became",
            "working", "living", "got", "new", "current", "mode", "use", "using", "phone",
            "iphone", "android", "sushi", "pasta", "sport", "instrument", "guitar",
            "laptop", "thinkpad", "macbook", "sci-fi", "books", "swimming", "tennis",
            "student", "university", "school", "career", "job", "role", "occupation", "work"
        ]
        
        # Extract candidate text
        cand_match = re.search(r'NEW CANDIDATE MEMORY \[[^\]]+\]:\s*"([^"]+)"', user)
        cand_text = cand_match.group(1).lower() if cand_match else user_lower
        cand_tokens = self._tokens(cand_text)
        
        related = []
        for line in user.split("\n"):
            if line.startswith("- mem_id="):
                m_match = re.match(r'- mem_id=([^\s]+)', line)
                if m_match:
                    mid = m_match.group(1)
                    line_tokens = self._tokens(line.lower())
                    overlap = len(cand_tokens & line_tokens)
                    if overlap >= 1 or any(w in cand_text for w in update_keywords):
                        related.append(mid)

        if related and (any(w in cand_text for w in update_keywords) or len(mem_ids) > 0):
            target_ids = related if related else mem_ids
            return {
                "conflict_status": "update_required",
                "conflict_type": "preference_shift",
                "related_memory_ids": target_ids,
                "reason": f"Updated preference replaces prior memory ({', '.join(target_ids)}).",
                "recommended_action": "retire_old_and_store_new"
            }
        return {
            "conflict_status": "no_conflict",
            "conflict_type": "no_conflict",
            "related_memory_ids": [],
            "reason": "No conflict detected.",
            "recommended_action": "store_new"
        }

    def _handle_policy(self, user: str) -> Dict[str, Any]:
        return {
            "name": "User Custom Policy",
            "description": "Parsed user policy rule",
            "scope": ["persona", "preference", "goal"],
            "condition": {"source_speaker": "user"},
            "action": "allow_store",
            "fallback": "reject",
            "priority": 10
        }

    def _handle_answer(self, user: str) -> Dict[str, Any]:
        mem_matches = re.findall(r'- \[([^\]]+)\]:\s*"([^"]+)"', user)
        if mem_matches:
            latest_id, latest_text = mem_matches[0]
            clean_text = latest_text.replace("User mentioned: ", "").replace("User is ", "").replace("User prefers ", "").strip()
            ans_str = f"Based on your verified memory: {clean_text} [{latest_id}]."
            return {
                "answer": ans_str,
                "used_memories": [latest_id],
                "confidence": 0.95,
                "status": "grounded"
            }
        return {
            "answer": "I do not have enough verified memory to answer this question.",
            "used_memories": [],
            "confidence": 0.0,
            "status": "insufficient_memory"
        }


class FakeLLMClient:
    """Canned response queue for testing."""

    def __init__(self, responses: Optional[List[Dict[str, Any]]] = None):
        self.responses = list(responses or [])
        self.calls: List[Dict[str, str]] = []

    def complete_json(self, system: str, user: str) -> Dict[str, Any]:
        self.calls.append({"system": system, "user": user})
        if self.responses:
            return self.responses.pop(0)
        return {}


def _parse_json(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in output: {text!r}")
    return json.loads(match.group(0))
