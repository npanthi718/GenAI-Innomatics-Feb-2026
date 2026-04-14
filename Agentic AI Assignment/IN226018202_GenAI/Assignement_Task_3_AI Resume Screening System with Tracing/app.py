import streamlit as st
import os
import tempfile
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from chains.screener_logic import run_screening

# 1. Load Environment (This triggers LangSmith Tracing)
load_dotenv()


def extract_pdf_text(uploaded_pdf) -> str:
    """Extract plain text from an uploaded PDF file."""
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_pdf.getvalue())
            tmp_path = tmp.name

        pages = PyPDFLoader(tmp_path).load()
        return " ".join([page.page_content for page in pages]).strip()
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


def build_submission_markdown(result: dict, jd_mode: str, resume_name: str, jd_name: str) -> str:
    score = result.get("fit_score", "Not detected")
    recommendation = result.get("recommendation", "Not detected")
    model = result.get("model", "Not detected")
    pipeline = result.get("models_used", "Not detected")

    return f"""# Screening Output Summary

Generated On: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Run Context
- Resume File: {resume_name}
- JD Source: {jd_mode}
- JD File: {jd_name}
- Model Used: {model}
- Pipeline: {pipeline}

## Decision
- Recommendation: {recommendation}
- Fit Score: {score}

## Recruiter Evaluation
{result.get("evaluation", "No evaluation generated.")}

## Extracted JD Profile
{result.get("jd_profile", "No JD profile generated.")}

## Extracted Candidate Profile
{result.get("extracted_data", "No extraction generated.")}
"""

st.set_page_config(page_title="AI Resume Screener", layout="wide")
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

        :root {
            --bg-1: #f9f7f3;
            --bg-2: #eef3ee;
            --ink: #1f2a24;
            --muted: #4f5d55;
            --brand: #0f6b4f;
            --brand-soft: #d8efe2;
            --card: #ffffff;
            --line: #d7e5da;
        }

        html, body, [class*="css"] {
            font-family: 'Manrope', sans-serif;
            color: var(--ink);
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 10%, #f6eed8 0%, transparent 38%),
                radial-gradient(circle at 92% 8%, #dbeee2 0%, transparent 36%),
                linear-gradient(160deg, var(--bg-1) 0%, var(--bg-2) 100%);
        }

        .block-container {
            padding-top: 1.8rem;
            max-width: 1200px;
        }

        .hero-card {
            background: linear-gradient(135deg, #0f4f3f 0%, #143d33 55%, #1a2d28 100%);
            border: 1px solid #2f6657;
            border-radius: 20px;
            padding: 1.35rem 1.45rem;
            margin-bottom: 1.1rem;
            color: #f3f8f5;
            box-shadow: 0 18px 40px rgba(9, 40, 31, 0.2);
        }

        .hero-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.75rem;
            font-weight: 700;
            letter-spacing: 0.1px;
            margin-bottom: 0.25rem;
        }

        .hero-sub {
            color: #cfe5dc;
            font-size: 0.97rem;
            margin: 0;
        }

        .panel {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 0.95rem 1rem;
            margin-bottom: 0.8rem;
        }

        .panel-title {
            font-weight: 800;
            letter-spacing: 0.1px;
            color: var(--brand);
            margin-bottom: 0.25rem;
        }

        .mini-note {
            color: var(--muted);
            font-size: 0.93rem;
            margin: 0;
        }

        .chip-row {
            display: flex;
            gap: 0.45rem;
            flex-wrap: wrap;
            margin-top: 0.6rem;
        }

        .chip {
            background: var(--brand-soft);
            color: #16573f;
            border: 1px solid #b8dcc8;
            border-radius: 999px;
            padding: 0.2rem 0.55rem;
            font-size: 0.78rem;
            font-weight: 700;
        }

        .stButton>button {
            border-radius: 12px;
            border: 1px solid #176145;
            background: linear-gradient(135deg, #0f6b4f 0%, #1b7f60 100%);
            color: #f6fff9;
            font-weight: 700;
            padding: 0.55rem 1rem;
        }

        .stButton>button:hover {
            background: linear-gradient(135deg, #0d5d45 0%, #176d54 100%);
            border-color: #0e563f;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">AI Resume Screening System</div>
        <p class="hero-sub">Recruiter-grade screening with Groq, weighted fit scoring, and downloadable evaluation artifacts.</p>
        <div class="chip-row">
            <span class="chip">JD Text + JD PDF</span>
            <span class="chip">Resume PDF Extraction</span>
            <span class="chip">Fit Score + Recommendation</span>
            <span class="chip">LangSmith Trace Ready</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Job Description Input")
    jd_mode = st.radio(
        "Choose JD Source",
        options=["Paste Text", "Upload PDF"],
        index=0,
        horizontal=True,
    )

    jd_input = ""
    jd_pdf_file = None
    if jd_mode == "Paste Text":
        jd_input = st.text_area("Paste the JD here:", height=360)
    else:
        jd_pdf_file = st.file_uploader("Upload JD PDF", type="pdf", key="jd_pdf")

st.markdown(
    """
    <div class="panel">
        <div class="panel-title">Workflow</div>
        <p class="mini-note">1) Upload resume PDF, 2) provide JD (text or PDF), 3) run analysis, 4) download report for internship submission evidence.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Candidate Resume")
uploaded_file = st.file_uploader("Upload Resume PDF", type="pdf")

if st.button("Analyze Resume"):
    if not uploaded_file:
        st.error("Please upload a resume PDF before analyzing.")
        st.stop()

    if jd_mode == "Paste Text":
        if not jd_input or not jd_input.strip():
            st.error("Please provide a job description in the sidebar.")
            st.stop()
        if len(jd_input.strip()) < 120:
            st.warning("JD text looks very short. Add a fuller description for better scoring quality.")
    else:
        if not jd_pdf_file:
            st.error("Please upload a JD PDF in the sidebar.")
            st.stop()

    with st.spinner("Processing through LangChain pipeline..."):
        try:
            resume_text = extract_pdf_text(uploaded_file)
            if jd_mode == "Upload PDF":
                jd_input = extract_pdf_text(jd_pdf_file)

            if not resume_text:
                st.error("No readable text was found in the uploaded PDF.")
                st.stop()
            if not jd_input:
                st.error("No readable text was found in the JD input.")
                st.stop()

            result = run_screening(resume_text=resume_text, job_description=jd_input)

            st.session_state["screening_result"] = result
            st.session_state["resume_name"] = uploaded_file.name
            st.session_state["jd_name"] = jd_pdf_file.name if jd_pdf_file else "Pasted text"
            st.session_state["jd_mode"] = jd_mode
            st.session_state["run_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            st.success("Groq analysis completed successfully.")

        except Exception as exc:
            st.error("Analysis failed. Please verify your GROQ_API_KEY, model access, and rate limits.")
            st.exception(exc)

if "screening_result" in st.session_state:
    result = st.session_state["screening_result"]

    st.subheader("Screening Result")

    top_left, top_mid, top_right = st.columns(3)
    with top_left:
        score = result.get("fit_score")
        if score is not None:
            st.metric("Fit Score", f"{score}/100")
            st.progress(min(max(int(score), 0), 100))
        else:
            st.metric("Fit Score", "Not detected")
    with top_mid:
        st.metric("Recommendation", result.get("recommendation", "Not detected"))
        st.caption(f"Run time: {st.session_state.get('run_time')}")
    with top_right:
        st.metric("Model", result.get("model", "Not detected"))
        st.caption(f"Pipeline: {result.get('models_used', 'Not detected')}")

    tab_eval, tab_jd, tab_resume, tab_export = st.tabs([
        "Recruiter Evaluation",
        "JD Profile",
        "Candidate Profile",
        "Export",
    ])

    with tab_eval:
        st.markdown(result.get("evaluation", "No evaluation generated."))
        st.info("Check LangSmith for trace-level details when tracing is enabled.")

    with tab_jd:
        st.markdown(result.get("jd_profile", "No JD profile generated."))

    with tab_resume:
        st.markdown(result.get("extracted_data", "No extraction generated."))

    with tab_export:
        export_payload = {
            "run_time": st.session_state.get("run_time"),
            "resume_file": st.session_state.get("resume_name"),
            "jd_mode": st.session_state.get("jd_mode"),
            "jd_file": st.session_state.get("jd_name"),
            **result,
        }
        markdown_report = build_submission_markdown(
            result=result,
            jd_mode=st.session_state.get("jd_mode", "Unknown"),
            resume_name=st.session_state.get("resume_name", "Unknown"),
            jd_name=st.session_state.get("jd_name", "Unknown"),
        )

        st.download_button(
            label="Download Markdown Report",
            data=markdown_report,
            file_name="screening_report.md",
            mime="text/markdown",
            use_container_width=True,
        )
        st.download_button(
            label="Download JSON Output",
            data=json.dumps(export_payload, indent=2),
            file_name="screening_output.json",
            mime="application/json",
            use_container_width=True,
        )