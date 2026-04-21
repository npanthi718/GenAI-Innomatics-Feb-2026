from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rag_graph import SupportAssistant


def main() -> None:
    print("Customer Support Assistant (RAG + LangGraph + HITL)")
    print("Type 'exit' to quit.\n")

    assistant = SupportAssistant()

    while True:
        query = input("Customer> ").strip()
        if query.lower() in {"exit", "quit"}:
            print("Bye.")
            break
        if not query:
            continue

        result = assistant.ask_with_hitl(query=query, thread_id="cli-thread")
        print("\nAssistant:", result["answer"])
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Escalated: {result['escalated_to_human']}")
        print(f"Sources: {', '.join(result['used_sources']) if result['used_sources'] else 'None'}\n")


if __name__ == "__main__":
    main()
