from __future__ import annotations

from pathlib import Path
import sys
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException

from src.rag_graph import SupportAssistant
from src.schemas import QueryRequest, QueryResponse


app = FastAPI(title="RAG Customer Support Assistant", version="1.0.0")
assistant = SupportAssistant()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "RAG Customer Support Assistant API is running.",
        "health": "/health",
        "ask": "/ask",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=QueryResponse)
def ask(req: QueryRequest) -> QueryResponse:
    try:
        result = assistant.ask(req.query, thread_id=f"api-{uuid4().hex}")
        return QueryResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
