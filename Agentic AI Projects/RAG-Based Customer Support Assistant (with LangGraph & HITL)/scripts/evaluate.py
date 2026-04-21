from __future__ import annotations

from pathlib import Path
import sys
from dataclasses import dataclass

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rag_graph import SupportAssistant


@dataclass
class EvalCase:
    query: str
    expected_keywords: list[str]


CASES = [
    EvalCase("How can I reset my account password?", ["password", "reset", "email"]),
    EvalCase("When will my prepaid order be delivered?", ["delivery", "prepaid", "3-5"]),
    EvalCase("I want legal action for billing fraud.", ["support", "escalate"]),
]


def score_keywords(answer: str, expected_keywords: list[str]) -> float:
    a = answer.lower()
    hits = sum(1 for k in expected_keywords if k.lower() in a)
    return hits / max(1, len(expected_keywords))


def run_eval() -> None:
    assistant = SupportAssistant()
    total = len(CASES)
    keyword_scores: list[float] = []
    escalations = 0

    for i, case in enumerate(CASES, start=1):
        result = assistant.ask(case.query, thread_id=f"eval-{i}")
        keyword_scores.append(score_keywords(result["answer"], case.expected_keywords))
        escalations += int(result["escalated_to_human"])
        print(f"Case {i}: {case.query}")
        print(f"Answer: {result['answer']}")
        print(f"Score: {keyword_scores[-1]:.2f} | Escalated: {result['escalated_to_human']}\n")

    avg_score = sum(keyword_scores) / total if total else 0.0
    escalation_ratio = escalations / total if total else 0.0

    print("===== Evaluation Summary =====")
    print(f"Average keyword coverage: {avg_score:.2f}")
    print(f"Escalation ratio: {escalation_ratio:.2f}")
    print("Tip: Improve coverage by adding more KB docs and query variants.")


if __name__ == "__main__":
    run_eval()
