# AI Resume Screening System

An internship-grade AI application for recruiter-style resume evaluation against a Job Description.

## 🚀 Snapshot

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![LangChain](https://img.shields.io/badge/LangChain-Orchestration-success)
![Groq](https://img.shields.io/badge/Groq-LLM%20Provider-0b7d61)
![LangSmith](https://img.shields.io/badge/LangSmith-Tracing-purple)
![Status](https://img.shields.io/badge/Submission-Internship%20Ready-brightgreen)

## ✨ Key Features

- 📄 Resume PDF upload with extraction
- 🧾 Job Description input in 2 modes:
  - Paste text
  - Upload JD PDF
- 🧠 Three-stage AI pipeline:
  - JD normalization
  - Candidate profile extraction
  - Final recruiter decision
- 📊 Fit score + recommendation + gap analysis
- 🔍 Model and fallback transparency
- 📥 One-click export for:
  - `screening_report.md`
  - `screening_output.json`

## 🧭 Assignment Rubric Mapping

- Problem Understanding: Strong role-fit evaluation workflow
- AI Integration: Groq + LangChain chain pipeline
- Prompt Design: Structured templates for deterministic output format
- Product UX: Beautiful Streamlit UI + clean result navigation tabs
- Traceability: LangSmith tracing compatible
- Submission Discipline: docs + evidence + tested files included

## 🏗️ Project Structure

- `app.py` → UI + workflow + export actions
- `chains/screener_logic.py` → model fallback orchestration + scoring extraction
- `prompts/templates.py` → JD extraction, resume extraction, evaluation prompts
- `Outputs Screenshots/` → evidence screenshots
- `Outputs Screenshots/Json Output/` → run output snapshots
- `Tested PDF/` → sample resumes + JD PDFs used for testing
- `INTERNSHIP_SUBMISSION_REPORT.md` → formal evaluator report

## ⚙️ Setup

### 1) Create virtual environment

```powershell
python -m venv venv
```

### 2) Install dependencies into venv

```powershell
venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3) Configure environment variables

Create `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=Resume_Screener_Analysis
```

### 4) Run app (recommended safe command)

```powershell
venv\Scripts\python.exe -m streamlit run app.py
```

Or use helper script:

```powershell
.\run_app.ps1
```

## 🛠️ Important Runtime Note

If you run only `streamlit run app.py`, your system may use global/Anaconda Streamlit instead of this project venv and fail with missing modules.

Always prefer:

```powershell
venv\Scripts\python.exe -m streamlit run app.py
```

## 🧾 Why Two Markdown Files?

- `README.md` → repository-facing documentation (setup, architecture, usage)
- `INTERNSHIP_SUBMISSION_REPORT.md` → internship evaluator-facing report (audit, coverage, readiness)

This is intentional and aligns with professional submission format.

## 🔐 Submission Hygiene

- `.env` and venv folders are ignored via `.gitignore`
- Secrets are not committed
- Evidence assets remain committed for evaluation

## 💻 Tech Stack

- Python
- Streamlit
- LangChain
- Groq
- LangSmith
