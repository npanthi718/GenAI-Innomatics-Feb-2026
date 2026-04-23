from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rag_graph import SupportAssistant


st.set_page_config(page_title="Customer Support Assistant", page_icon="💬", layout="wide")

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.4rem; max-width: 1180px; }
    .hero {
        padding: 1.35rem 1.4rem;
        border-radius: 24px;
        background: smokewhite;
        color: black;
        margin-bottom: 1rem;
        box-shadow: 0 18px 50px rgba(8, 47, 73, 0.25);
        border: 1px solid rgba(255,255,255,0.14);
    }
    .hero h1 { margin: 0; font-size: 2rem; }
    .hero p { margin: 0.35rem 0 0 0; opacity: 0.92; }
    .metric-card {
        padding: 1rem 1rem;
        border-radius: 18px;
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
        min-height: 96px;
    }
    .metric-label { font-size: 0.82rem; color: #475569; margin-bottom: 0.35rem; }
    .metric-value { font-size: 1.35rem; font-weight: 700; color: #0f172a; }
    .metric-hint { font-size: 0.82rem; color: #64748b; margin-top: 0.2rem; }
    .answer-box {
        padding: 1rem 1.05rem;
        border-radius: 18px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
    }
    .chip {
        display:inline-block;
        padding:0.28rem 0.74rem;
        border-radius:999px;
        background:#ecfeff;
        color:#155e75;
        border:1px solid #99f6e4;
        margin-right:0.4rem;
        font-size:0.85rem;
    }
    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin: 0.15rem 0 0.55rem 0;
        color: #0f172a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<div class='hero'><h1>💬 Customer Support Assistant</h1><p>Grounded customer-support answers powered by RAG, LangGraph, and human review for risky cases.</p></div>",
    unsafe_allow_html=True,
)

assistant = SupportAssistant()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "query_text" not in st.session_state:
    st.session_state.query_text = ""

if "run_query" not in st.session_state:
    st.session_state.run_query = False

if "status_note" not in st.session_state:
    st.session_state.status_note = "Ready"

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

st.sidebar.title("📘 Demo Guide")
st.sidebar.caption("Use these prompts to show different behaviors during your presentation.")

question_bank = {
    "✅ Normal Questions": [
        "How can I track my order?",
        "How do I reset my password?",
        "How long is a password reset link valid?",
        "What is standard delivery time for prepaid orders?",
        "When are refunds processed after cancellation?",
    ],
    "⚠️ Medium Support Questions": [
        "My prepaid order is delayed, what should I do?",
        "I was charged twice. What details should I share?",
        "I did not receive my reset email. What should I do now?",
        "My order has not moved for two days. Can support check?",
    ],
    "🛡️ Risk and Escalation Questions": [
        "I want to file legal action for billing fraud.",
        "This looks like fraud. I need a chargeback now.",
        "I want to complain to the regulator for this billing issue.",
        "Please escalate my case to a human support manager.",
    ],
}

for title, questions in question_bank.items():
    st.sidebar.markdown(f"#### {title}")
    for q in questions:
        if st.sidebar.button(q, use_container_width=True):
            st.session_state.query_text = q
            st.session_state.run_query = True
    st.sidebar.write("")

st.sidebar.divider()
st.sidebar.markdown("### What this shows")
st.sidebar.write("- Grounded answer from your knowledge base")
st.sidebar.write("- Confidence and escalation decision")
st.sidebar.write("- Human review path for risky queries")
st.sidebar.write("- Sources shown for transparency")

metric_left, metric_mid, metric_right = st.columns(3)

with metric_left:
    st.markdown(
        "<div class='metric-card'><div class='metric-label'>Mode</div><div class='metric-value'>RAG + HITL</div><div class='metric-hint'>Grounded answers with human fallback</div></div>",
        unsafe_allow_html=True,
    )
with metric_mid:
    st.markdown(
        "<div class='metric-card'><div class='metric-label'>Knowledge Base</div><div class='metric-value'>Multiple Docs</div><div class='metric-hint'>Markdown, text, and PDF support</div></div>",
        unsafe_allow_html=True,
    )
with metric_right:
    st.markdown(
        "<div class='metric-card'><div class='metric-label'>Risk Handling</div><div class='metric-value'>Escalate</div><div class='metric-hint'>Fraud, legal, chargeback, low confidence</div></div>",
        unsafe_allow_html=True,
    )

st.write("")

col_left, col_right = st.columns([1.15, 0.85])

with col_left:
    st.markdown("<div class='section-title'>Ask a support question</div>", unsafe_allow_html=True)
    query = st.text_area(
        label="",
        placeholder="Example: My prepaid order is delayed and I want to know the refund policy.",
        height=130,
        key="query_text",
    )
    run_manual = st.button("Run assistant", type="primary", use_container_width=True, disabled=st.session_state.is_processing)
    run = run_manual or st.session_state.run_query

    if run and query.strip():
        st.session_state.is_processing = True
        st.session_state.status_note = "Thinking..."
        try:
            with st.spinner("Working on your answer..."):
                result = assistant.ask(query.strip(), thread_id="streamlit-thread")
            st.session_state.last_result = result
            st.session_state.messages.append(("user", query.strip()))
            st.session_state.messages.append(("assistant", result["answer"]))
            st.session_state.status_note = "Done"
        except Exception as exc:
            st.session_state.status_note = "Error"
            st.error("The assistant could not process this query. Please verify API key setup and knowledge-base files.")
            st.caption(str(exc))
        finally:
            st.session_state.run_query = False
            st.session_state.is_processing = False

with col_right:
    st.markdown("<div class='section-title'>Live status</div>", unsafe_allow_html=True)
    if st.session_state.is_processing:
        st.info("Processing your question... please wait.")
    else:
        st.info(st.session_state.status_note)

    st.markdown("<div class='section-title'>Demo Notes</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <span class='chip'>Grounded RAG</span>
        <span class='chip'>Human Review</span>
        <span class='chip'>Fast Demo</span>
        """,
        unsafe_allow_html=True,
    )
    st.write("Ask a normal question first, then a risky one to show escalation and human review.")
    if st.session_state.is_processing:
        st.caption("The previous question is still running.")

if st.session_state.last_result:
    result = st.session_state.last_result
    st.divider()
    st.markdown("<div class='section-title'>Assistant Output</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='answer-box'>{result['answer']}</div>", unsafe_allow_html=True)

    r1, r2, r3 = st.columns(3)
    with r1:
        st.metric("Confidence", f"{result['confidence']:.2f}")
    with r2:
        st.metric("Escalated", "Yes" if result["escalated_to_human"] else "No")
    with r3:
        st.metric("Sources", str(len(result.get("used_sources", []))))

    if result["used_sources"]:
        st.caption("Sources: " + ", ".join(result["used_sources"]))

    if result.get("reason"):
        st.info(f"Escalation reason: {result['reason']}")

    if result["escalated_to_human"]:
        st.warning("This query was flagged for human review because the grounding score was low or the topic was sensitive.")
        edited = st.text_area("Human-approved response", value=result["answer"], height=150)
        if st.button("Save human-approved response", use_container_width=True):
            st.success("Approved response saved for the demo run.")
            st.session_state.last_result = {
                **result,
                "answer": edited,
                "escalated_to_human": True,
            }

st.divider()
st.markdown("<div class='section-title'>Conversation</div>", unsafe_allow_html=True)
for role, text in st.session_state.messages[-8:]:
    prefix = "You" if role == "user" else "Assistant"
    st.markdown(f"**{prefix}:** {text}")
