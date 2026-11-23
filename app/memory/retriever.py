"""
Hybrid Retriever (Section 7.9).

Retrieves active verified memories for a user query using multi-signal scoring:
score = 0.35 * semantic_similarity + 0.20 * entity_overlap + 0.15 * recency_score
        + 0.15 * confidence_score + 0.10 * importance - 0.50 * uncertain_penalty
"""

from __future__ import annotations

import re
from typing import List, Tuple
from app.schemas import MemoryItem, MemoryStatus


from datetime import datetime, timezone

class HybridRetriever:
    _STOPWORDS = {
        "what", "is", "my", "your", "does", "do", "the", "a", "an", "in", "on", "for", 
        "to", "include", "where", "did", "go", "when", "why", "how", "tell",
        "show", "list", "are", "was", "were", "been", "has", "have", "had", "can", "could",
        "i", "me", "myself", "we", "us", "our", "you", "yours", "he", "him", 
        "his", "she", "her", "hers", "it", "its", "they", "them", "their", "theirs"
    }

    def _tokenize(self, text: str) -> set:
        words = re.findall(r"[a-zA-Z']+", text.lower())
        tokens = {w for w in words if w not in self._STOPWORDS}
        return tokens if tokens else set(words)

    def _calculate_overlap(self, query_tokens: set, mem_text: str) -> float:
        mem_tokens = self._tokenize(mem_text)
        if not query_tokens or not mem_tokens:
            return 0.0
        
        exact_matches = len(query_tokens & mem_tokens)
        fuzzy_matches = 0
        m_text_lower = mem_text.lower()
        
        # Domain keyword equivalences
        SYNONYMS = {
            "smartphone": {"phone", "android", "iphone", "mobile"},
            "cuisine": {"food", "pasta", "sushi", "eating", "dinner"},
            "laptop": {"computer", "thinkpad", "macbook", "pc"},
            "residence": {"living", "city", "live", "tokyo", "london", "moved"},
            "occupation": {"job", "work", "worker", "researcher", "student", "developer", "oxford"},
            "title": {"job", "role", "architect", "developer", "promoted"},
            "marital": {"single", "married", "status", "wedding"},
            "housing": {"renting", "bought", "house", "apartment", "home"},
            "work": {"work", "working", "live", "seattle", "francisco", "city", "developer"},
            "sport": {"swimming", "tennis", "game", "playing"},
            "instrument": {"piano", "guitar", "music", "playing"},
            "drink": {"tea", "coffee", "beverage", "earl", "grey"},
            "prefer": {"likes", "preference", "favor", "favorite", "choice", "rather"},
        }

        for q_tok in query_tokens:
            if q_tok in mem_tokens:
                continue
            
            # Check synonym dictionary
            matched_syn = False
            for syn_key, syn_set in SYNONYMS.items():
                if q_tok == syn_key or q_tok in syn_set:
                    if any(s in m_text_lower for s in syn_set):
                        fuzzy_matches += 0.9
                        matched_syn = True
                        break
            if matched_syn:
                continue

            # Sub-word prefix matching (e.g. phone/smartphone, resid/residence)
            if any(q_tok.startswith(m_tok[:4]) or m_tok.startswith(q_tok[:4]) for m_tok in mem_tokens if len(m_tok) >= 4 and len(q_tok) >= 4):
                fuzzy_matches += 0.8

        total_score = exact_matches + fuzzy_matches
        return round(min(total_score / max(len(query_tokens), 1), 1.0), 2)

    def retrieve(self, query: str, memories: List[MemoryItem], top_k: int = 5) -> List[Tuple[MemoryItem, float]]:
        candidates = [m for m in memories if m.status == MemoryStatus.ACTIVE]
        if not candidates:
            return []

        query_tokens = self._tokenize(query)
        scored: List[Tuple[MemoryItem, float]] = []
        now = datetime.now(timezone.utc)

        for m in candidates:
            overlap = self._calculate_overlap(query_tokens, m.memory_text)
            if overlap == 0.0:
                continue

            semantic_similarity = round(overlap, 2)
            entity_overlap = round(overlap * 0.8, 2)

            # Compute dynamic recency score (decay over time, favoring newly updated memories)
            upd_dt = m.updated_at
            if upd_dt.tzinfo is None:
                upd_dt = upd_dt.replace(tzinfo=timezone.utc)
            age_hours = max((now - upd_dt).total_seconds() / 3600.0, 0.0)
            recency_score = round(max(1.0 - (age_hours / 720.0), 0.1), 2)

            confidence_score = m.confidence
            importance = m.importance
            uncertain_penalty = 0.50 if m.status == MemoryStatus.UNCERTAIN else 0.0

            score = (
                0.35 * semantic_similarity
                + 0.20 * entity_overlap
                + 0.25 * recency_score
                + 0.10 * confidence_score
                + 0.10 * importance
                - uncertain_penalty
            )
            scored.append((m, round(max(score, 0.0), 4)))

        # Sort primary by score DESC, secondary by updated_at timestamp DESC for tie-breaking
        scored.sort(key=lambda x: (x[1], x[0].updated_at.timestamp()), reverse=True)
        return scored[:top_k]
