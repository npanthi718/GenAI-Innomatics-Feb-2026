from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RetrieveChunk(BaseModel):
    source: str
    text: str


class QueryRequest(BaseModel):
    query: str = Field(min_length=3)


class QueryResponse(BaseModel):
    answer: str
    confidence: float
    escalated_to_human: bool
    used_sources: list[str]
    status: Literal["answered", "needs_human"]
