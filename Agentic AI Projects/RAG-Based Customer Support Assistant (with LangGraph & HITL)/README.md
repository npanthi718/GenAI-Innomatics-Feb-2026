# 💬 RAG-Based Customer Support Assistant

A grounded customer support assistant built with **LangGraph**, **RAG**, and **human-in-the-loop review**. It answers from a local knowledge base, explains when it is unsure, and routes risky queries to a human review path.

## ✨ Highlights

- 📚 Answers only from your knowledge base
- 🧠 Uses LangGraph for a clear workflow
- 🛡️ Flags low-confidence or sensitive questions for review
- ⚡ Groq is the default model provider, Gemini is the fallback
- 🖥️ Includes a polished Streamlit demo UI
- 🔍 Shows the sources used for each answer

## 🧰 Tech Stack

- LangGraph for orchestration
- Groq or Gemini for generation
- ChromaDB-backed local vector store for retrieval
- FastAPI for API access
- Streamlit for the demo UI
- Pydantic for request and response validation

## 🗂 Project Structure

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

## 🚀 Start Here

Create and activate the environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file from `.env.example` and set your provider:

```text
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
LANGCHAIN_API_KEY=your_optional_langsmith_key
LANGCHAIN_PROJECT=RAG-Based Customer Support Assistant
LANGCHAIN_TRACING_V2=true
```

If you prefer Gemini:

```text
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash
```

## ▶ Run the Project

Build or refresh the local knowledge index:

```powershell
python -m src.ingest
```

This loads supported documents, splits them into chunks, creates embeddings, and stores them in ChromaDB.

Launch the Streamlit app from the project root:

```powershell
streamlit run src/app_streamlit.py
```

If you are already inside `src`, this also works:

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

## 📚 Knowledge Base Files

Put your support documents in `data/knowledge_base/`.

Supported file types:

- `.md`
- `.txt`
- `.pdf`

After adding or replacing files, run `python -m src.ingest` again.

## 🎯 Demo Questions

Try these during presentation:

- How can I track my order?
- How do I reset my password?
- How long is a password reset link valid?
- What is the standard delivery time for prepaid orders?
- My prepaid order is delayed, what should I do?
- I was charged twice. What details should I share?
- I want to file legal action for billing fraud.
- This looks like fraud. I need a chargeback now.

## 🧠 How the Workflow Works

1. The user asks a question.
2. The assistant retrieves relevant chunks from the local knowledge base.
3. A grounded answer is drafted using only the retrieved context.
4. The system scores confidence and risk.
5. If the answer is low-confidence or sensitive, it is flagged for human review.
6. The UI shows the answer, source list, and escalation reason.

## 🗺 Architecture

The architecture diagram source is in [diagrams/workflow.mmd](diagrams/workflow.mmd). Export it to PNG or SVG if you want to place it in a report or slide deck.

## 🧪 What to Check Before Demo

- Ask one normal question and one risky question
- Verify the assistant shows a reason when it escalates
- Verify the button disables while processing
- Verify sources are visible under the answer
- Verify the API and CLI start without errors

## 🛠 Troubleshooting

- If Streamlit fails to import modules, start it from the project root.
- If the assistant says the knowledge base is missing, run `python -m src.ingest`.
- If Groq returns a decommissioned model error, update `.env` to `llama-3.3-70b-versatile` or switch to Gemini.
- If you have LangSmith credentials, tracing will be enabled automatically.

## 🔒 Security Note

Keep `.env` private. Never push API keys to GitHub.
