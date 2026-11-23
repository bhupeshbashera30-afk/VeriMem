"""
Operation-Level Evaluation Metrics (Section 16).

Implements HaluMem-inspired metrics across extraction, updating, QA, and policy compliance.
"""

from __future__ import annotations

from typing import Dict, List, Any


def compute_extraction_metrics(gold_memories: List[str], extracted_memories: List[str], distractor_memories: List[str]) -> Dict[str, float]:
    gold_set = set(gold_memories)
    extracted_set = set(extracted_memories)
    distractor_set = set(distractor_memories)

    tp = len(gold_set & extracted_set)
    fn = len(gold_set - extracted_set)
    fp = len(extracted_set - gold_set)
    fp_distractors = len(extracted_set & distractor_set)

    recall = tp / max(len(gold_set), 1)
    precision = tp / max(len(extracted_set), 1)
    f1 = (2 * precision * recall) / max(precision + recall, 1e-6)
    false_memory_resistance = 1.0 - (fp_distractors / max(len(distractor_set), 1))

    return {
        "memory_recall": round(recall, 4),
        "memory_precision": round(precision, 4),
        "extraction_f1": round(f1, 4),
        "false_memory_resistance": round(max(false_memory_resistance, 0.0), 4),
    }


def compute_update_metrics(expected_updates: int, successful_updates: int, incorrect_updates: int) -> Dict[str, float]:
    acc = successful_updates / max(expected_updates, 1)
    hallucination_rate = incorrect_updates / max(expected_updates, 1)

    return {
        "update_accuracy": round(acc, 4),
        "update_hallucination_rate": round(hallucination_rate, 4),
    }


def compute_qa_metrics(total_questions: int, correct_answers: int, hallucinated_answers: int, cited_correctly: int) -> Dict[str, float]:
    acc = correct_answers / max(total_questions, 1)
    hal_rate = hallucinated_answers / max(total_questions, 1)
    citation_prec = cited_correctly / max(correct_answers, 1)

    return {
        "qa_accuracy": round(acc, 4),
        "qa_hallucination_rate": round(hal_rate, 4),
        "citation_precision": round(citation_prec, 4),
        "groundedness_score": round(1.0 - hal_rate, 4),
    }


def compute_policy_metrics(total_policy_checks: int, complied_checks: int) -> Dict[str, float]:
    compliance = complied_checks / max(total_policy_checks, 1)
    return {
        "policy_compliance_rate": round(compliance, 4),
    }
