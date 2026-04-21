# 💬 RAG-Based Customer Support Assistant

Grounded customer support assistant built with **LangGraph**, **RAG**, and **human-in-the-loop review**. The app answers from your own support knowledge base, keeps risky cases under control, and gives you a clean demo experience in CLI, API, and Streamlit.

## ✨ Highlights

- 📚 Answers only from your knowledge base
- 🧠 Uses LangGraph for a clear step-by-step workflow
- 🛡️ Flags sensitive or low-confidence questions for human review
- ⚡ Works with Groq by default, Gemini as a fallback option
- 🖥️ Includes a polished Streamlit demo UI
- 🔍 Shows sources used for the answer

## 🧩 How it works

1. A user asks a support question.
2. The assistant retrieves the most relevant document chunks.
3. A grounded answer is generated from the retrieved context.
4. The assistant scores the answer for confidence and risk.
5. Risky cases are sent to human review before the final response.

## 🧠 Tech Stack

- LangGraph for orchestration
- Groq or Gemini for generation
- Lightweight hashing vectorization for local retrieval
- Local file-based index for retrieval
- FastAPI for API access
- Streamlit for the demo UI

## 📁 Project Structure

```text
.
|-- data/
|   |-- knowledge_base/
|-- diagrams/
|-- scripts/
|-- src/
|-- tests/
|-- .env.example
|-- requirements.txt
|-- README.md
```

## 🚀 Quick Start

Create and activate the environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file and set one provider:

```text
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.1-70b-versatile
```

Or use Gemini:

```text
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash
```

## ▶ Run the Project

Build the index from your knowledge base:

```powershell
python -m src.ingest
```

Run the Streamlit UI:

```powershell
streamlit run src/app_streamlit.py
```

If you are inside the `src` folder:

```powershell
streamlit run app_streamlit.py
```

Run the CLI demo:

```powershell
python -m src.app_cli
```

Run the API:

```powershell
uvicorn src.app_api:app --reload
```

Run tests:

```powershell
pytest -q
```

## 📚 Supported Knowledge Base Files

Drop your support content into `data/knowledge_base/` using any of these formats:

- `.md`
- `.txt`
- `.pdf`

The app will pick them up when you run ingestion or when retrieval auto-builds the local index.

## 🎯 Good Demo Questions

Try these in Streamlit:

- How can I track my order?
- How do I reset my password?
- My prepaid order is delayed, what should I do?
- I want to file legal action for billing fraud.

## 🧪 What the demo shows

- Grounded retrieval from your docs
- Confidence and escalation handling
- Human review for risky requests
- Source visibility for transparency

## 🗺 Architecture

The Mermaid source is in [diagrams/workflow.mmd](diagrams/workflow.mmd). Export it to PNG or SVG if you want to include it in a report or slide deck.

## 🛠 Troubleshooting

- If Streamlit cannot import the package, run it from the project root or use the command shown above.
- If you add new knowledge documents, run `python -m src.ingest` once.
- If a question is outside the knowledge base, the assistant will respond conservatively or escalate.

## 🔒 Security Note

Keep `.env` private. Never commit API keys to GitHub.
