from __future__ import annotations

from typing import Any, Literal, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from src.config import settings
from src.observability import setup_langsmith
from src.model_provider import get_chat_model
from src.prompts import CONFIDENCE_PROMPT, SYSTEM_PROMPT
from src.retriever import normalize_query, retrieve_chunks


setup_langsmith()


class GraphState(TypedDict, total=False):
    query: str
    normalized_query: str
    retrieved_context: str
    source_names: list[str]
    draft_answer: str
    confidence: float
    risk: Literal["low", "medium", "high"]
    reason: str
    needs_human: bool
    final_answer: str


def _llm() -> Any:
    return get_chat_model()


def _safe_text(value: Any, fallback: str = "") -> str:
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else fallback
    if value is None:
        return fallback
    cleaned = str(value).strip()
    return cleaned if cleaned else fallback


def retrieve_node(state: GraphState) -> GraphState:
    normalized_query = normalize_query(state["query"])
    docs = retrieve_chunks(normalized_query)
    context = "\n\n".join([d["text"] for d in docs])
    source_names = sorted({d.get("source", "unknown") for d in docs})
    return {"normalized_query": normalized_query, "retrieved_context": context, "source_names": source_names}


def answer_node(state: GraphState) -> GraphState:
    model = _llm()
    normalized_query = state.get("normalized_query", state["query"])
    prompt = (
        f"Customer query (original):\n{state['query']}\n\n"
        f"Customer query (normalized):\n{normalized_query}\n\n"
        f"Retrieved context:\n{state['retrieved_context']}\n\n"
        "Write a support response using only the retrieved context. "
        "If the query asks about delay, no movement, or late delivery, include delay-specific next steps from context."
    )
    msg = model.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    return {"draft_answer": _safe_text(msg.content, "I could not draft a grounded answer from the current context.")}


def _risk_flags(query: str, context: str, draft_answer: str) -> tuple[float, Literal["low", "medium", "high"], str]:
    query_text = query.lower()
    context_text = context.lower()
    answer_text = draft_answer.lower()

    risky_terms = ["legal", "fraud", "chargeback", "lawsuit", "regulator", "consumer court", "refund dispute"]
    support_terms = ["password", "refund", "delivery", "order", "billing", "account"]

    risky_hits = sum(1 for term in risky_terms if term in query_text)
    support_hits = sum(1 for term in support_terms if term in context_text)
    answer_hits = sum(1 for term in support_terms if term in answer_text)

    if risky_hits:
        return 0.35, "high", "Sensitive query detected"

    if not context_text.strip():
        return 0.10, "high", "No retrieved context"

    if answer_hits == 0:
        return 0.42, "medium", "Draft answer is weakly grounded"

    if support_hits >= 3 and answer_hits >= 2:
        return 0.86, "low", "Good context match"

    return 0.66, "medium", "Moderate grounding"


def confidence_node(state: GraphState) -> GraphState:
    confidence, risk, reason = _risk_flags(
        state["query"],
        state.get("retrieved_context", ""),
        state["draft_answer"],
    )

    needs_human = confidence < settings.confidence_threshold or risk == "high"
    if risk == "high":
        reason = f"High-risk query detected: {reason}"
    elif needs_human:
        reason = f"Confidence score below {settings.confidence_threshold:.2f}: {reason}"

    return {
        "confidence": confidence,
        "risk": risk,
        "reason": reason,
        "needs_human": needs_human,
    }


def route_after_confidence(state: GraphState) -> str:
    return "human_review" if state.get("needs_human", False) else "finalize"


def human_review_node(state: GraphState):
    decision = interrupt(
        {
            "query": state["query"],
            "draft_answer": state["draft_answer"],
            "confidence": state.get("confidence", 0.0),
            "risk": state.get("risk", "high"),
            "reason": state.get("reason", ""),
        }
    )

    approved = bool(decision.get("approved", False))
    edited_answer = decision.get("edited_answer", "").strip()
    if approved and edited_answer:
        return {"final_answer": edited_answer}
    if approved:
        return {"final_answer": state["draft_answer"]}
    return {"final_answer": "Escalated to human agent. Please wait for manual resolution."}


def finalize_node(state: GraphState) -> GraphState:
    return {"final_answer": state.get("final_answer", state["draft_answer"])}


def build_graph():
    graph = StateGraph(GraphState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("answer", answer_node)
    graph.add_node("score", confidence_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("finalize", finalize_node)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "answer")
    graph.add_edge("answer", "score")
    graph.add_conditional_edges("score", route_after_confidence, {"human_review": "human_review", "finalize": "finalize"})
    graph.add_edge("human_review", "finalize")
    graph.add_edge("finalize", END)

    return graph.compile(checkpointer=MemorySaver())


class SupportAssistant:
    def __init__(self) -> None:
        self.graph = build_graph()

    def ask(self, query: str, thread_id: str = "default") -> dict[str, Any]:
        config = {"configurable": {"thread_id": thread_id}}
        result = self.graph.invoke({"query": query}, config=config)

        if "__interrupt__" in result:
            payload = result["__interrupt__"][0].value
            draft_answer = _safe_text(payload.get("draft_answer"), "This question needs human review. Please provide a human-approved response.")
            return {
                "answer": draft_answer,
                "confidence": float(payload.get("confidence", 0.0)),
                "escalated_to_human": True,
                "used_sources": result.get("source_names", []),
                "reason": str(payload.get("reason", "Human review required")),
                "status": "needs_human",
            }

        final_answer = _safe_text(
            result.get("final_answer"),
            _safe_text(result.get("draft_answer"), "I could not find a grounded answer. Please rephrase your question."),
        )

        return {
            "answer": final_answer,
            "confidence": float(result.get("confidence", 0.0)),
            "escalated_to_human": bool(result.get("needs_human", False)),
            "used_sources": result.get("source_names", []),
            "reason": str(result.get("reason", "")),
            "status": "needs_human" if result.get("needs_human", False) else "answered",
        }

    def ask_with_hitl(self, query: str, thread_id: str = "default") -> dict[str, Any]:
        config = {"configurable": {"thread_id": thread_id}}
        first = self.graph.invoke({"query": query}, config=config)

        if "__interrupt__" not in first:
            final_answer = _safe_text(
                first.get("final_answer"),
                _safe_text(first.get("draft_answer"), "I could not find a grounded answer. Please rephrase your question."),
            )
            return {
                "answer": final_answer,
                "confidence": float(first.get("confidence", 0.0)),
                "escalated_to_human": bool(first.get("needs_human", False)),
                "used_sources": first.get("source_names", []),
                "reason": str(first.get("reason", "")),
                "status": "answered",
            }

        payload = first["__interrupt__"][0].value
        print("\n--- HUMAN REVIEW REQUIRED ---")
        print(f"Query: {payload['query']}")
        print(f"Draft: {_safe_text(payload.get('draft_answer'), 'No draft was generated. Please enter a human response.')}")
        print(f"Confidence: {payload['confidence']:.2f} | Risk: {payload['risk']} | Reason: {payload['reason']}")

        choice = input("Approve draft? (y/n): ").strip().lower()
        if choice == "y":
            edit = input("Optional edited response (enter to keep draft): ").strip()
            decision = {"approved": True, "edited_answer": edit or _safe_text(payload.get("draft_answer"), "Human review completed.")}
        else:
            revised = input("Enter human-approved response: ").strip()
            decision = {"approved": True, "edited_answer": revised}

        final = self.graph.invoke(Command(resume=decision), config=config)
        final_answer = _safe_text(
            final.get("final_answer"),
            _safe_text(payload.get("draft_answer"), "Escalated to human agent. Please wait for manual resolution."),
        )
        return {
            "answer": final_answer,
            "confidence": float(final.get("confidence", 0.0)),
            "escalated_to_human": True,
            "used_sources": final.get("source_names", []),
            "reason": str(final.get("reason", payload.get("reason", "Human review required"))),
            "status": "answered",
        }
