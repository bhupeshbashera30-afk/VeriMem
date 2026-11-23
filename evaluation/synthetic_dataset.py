"""
Synthetic Dataset Generator (Section 17 - Dataset Plan Level 1).

Generates synthetic user dialogues, gold memories, updates, and QA pairs for evaluation.
"""

from __future__ import annotations

import json
from typing import Dict, List, Any


def generate_synthetic_dataset(num_users: int = 10) -> Dict[str, Any]:
    dataset = []

    topics = [
        ("AI research on hallucination-aware memory", "machine learning", "Agentic AI & Natural Language Programming"),
        ("Starting a weekly book club in Jaipur", "fiction and science", "Jaipur Book Club"),
        ("Learning Python web development with FastAPI", "Python programming", "FastAPI web backend"),
        ("Training for a half marathon in autumn", "running & health", "Autumn Half Marathon"),
        ("Building a personal smart home system", "home automation", "Raspberry Pi home server"),
    ]

    for i in range(1, num_users + 1):
        uid = f"u_{i:03d}"
        topic, pref, goal = topics[(i - 1) % len(topics)]

        user_data = {
            "user_id": uid,
            "sessions": [
                {
                    "session_id": f"s_{uid}_01",
                    "dialogue": [
                        {"speaker": "user", "text": f"I am planning a major project about {topic}.", "turn_id": f"t_{uid}_01"},
                        {"speaker": "assistant", "text": "That sounds like a great project idea!", "turn_id": f"t_{uid}_02"},
                        {"speaker": "user", "text": f"I really enjoy {pref} and my goal is {goal}.", "turn_id": f"t_{uid}_03"},
                    ],
                    "gold_memories": [
                        {"memory_text": f"User is planning a major project about {topic}.", "type": "goal"},
                        {"memory_text": f"User enjoys {pref}.", "type": "preference"},
                        {"memory_text": f"User's project goal is {goal}.", "type": "goal"},
                    ],
                    "distractors": [
                        "User is a final-year computer science student.",
                        "User lives in London.",
                    ],
                    "qa_pairs": [
                        {
                            "question": f"What is user's project about?",
                            "answer": f"User is planning a major project about {topic}.",
                            "expected_memories": [f"User is planning a major project about {topic}."],
                        }
                    ],
                }
            ],
        }
        dataset.append(user_data)

    return {"dataset": dataset, "num_users": num_users}


if __name__ == "__main__":
    ds = generate_synthetic_dataset(10)
    print(f"Generated synthetic dataset with {ds['num_users']} users.")
