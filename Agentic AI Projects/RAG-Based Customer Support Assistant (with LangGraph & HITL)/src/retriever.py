from __future__ import annotations

from src.config import settings
from src.local_index import retrieve_top_k


def retrieve_chunks(query: str) -> list[dict[str, str]]:
    return retrieve_top_k(query=query, k=settings.top_k)
