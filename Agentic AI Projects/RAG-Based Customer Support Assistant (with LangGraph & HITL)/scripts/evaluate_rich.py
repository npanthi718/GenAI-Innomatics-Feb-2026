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
    should_escalate: bool


CASES = [
    EvalCase(
        query="How do I reset my password if I did not receive the email?",
        expected_keywords=["forgot password", "15 minutes", "spam"],
        should_escalate=False,
    ),
    EvalCase(
        query="My prepaid order is delayed, what are my options?",
        expected_keywords=["3-5 business days", "track", "dashboard"],
        should_escalate=False,
    ),
    EvalCase(
        query="I am filing legal action for billing fraud.",
        expected_keywords=["escalate", "human"],
        should_escalate=True,
    ),
]


def _keyword_coverage(answer: str, expected_keywords: list[str]) -> float:
    lower = answer.lower()
    hits = sum(1 for k in expected_keywords if k.lower() in lower)
    return hits / max(1, len(expected_keywords))


def _context_precision(answer: str, sources: list[str]) -> float:
    if not sources:
        return 0.0
    source_bonus = min(1.0, len(set(sources)) / 3.0)
    grounded_words = ["policy", "support", "order", "account", "refund", "delivery"]
    grounded_hits = sum(1 for w in grounded_words if w in answer.lower())
    grounding = min(1.0, grounded_hits / 4.0)
    return round((source_bonus * 0.5) + (grounding * 0.5), 2)


def run() -> None:
    assistant = SupportAssistant()
    n = len(CASES)
    faithfulness_scores: list[float] = []
    context_precision_scores: list[float] = []
    escalation_correct = 0

    print("===== Rich Evaluation =====")
    for i, case in enumerate(CASES, start=1):
        result = assistant.ask(case.query, thread_id=f"rich-eval-{i}")
        faith = _keyword_coverage(result["answer"], case.expected_keywords)
        precision = _context_precision(result["answer"], result.get("used_sources", []))
        escal_ok = result["escalated_to_human"] == case.should_escalate

        faithfulness_scores.append(faith)
        context_precision_scores.append(precision)
        escalation_correct += int(escal_ok)

        print(f"Case {i}: {case.query}")
        print(f"Answer: {result['answer']}")
        print(f"Faithfulness: {faith:.2f} | Context Precision: {precision:.2f}")
        print(f"Escalation: expected={case.should_escalate}, actual={result['escalated_to_human']}, correct={escal_ok}")
        print()

    avg_faith = sum(faithfulness_scores) / n if n else 0.0
    avg_precision = sum(context_precision_scores) / n if n else 0.0
    escalation_acc = escalation_correct / n if n else 0.0

    print("===== Summary =====")
    print(f"Faithfulness: {avg_faith:.2f}")
    print(f"Context Precision: {avg_precision:.2f}")
    print(f"Escalation Accuracy: {escalation_acc:.2f}")


if __name__ == "__main__":
    run()
