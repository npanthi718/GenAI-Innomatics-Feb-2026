from __future__ import annotations

import re

from src.config import settings
from src.local_index import retrieve_top_k


_MISSPELLINGS = {
    "orepaid": "prepaid",
    "preapid": "prepaid",
    "dealyed": "delayed",
    "delyed": "delayed",
    "oreder": "order",
}


def normalize_query(query: str) -> str:
    normalized = query.lower().strip()
    for wrong, right in _MISSPELLINGS.items():
        normalized = re.sub(rf"\b{re.escape(wrong)}\b", right, normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def retrieve_chunks(query: str) -> list[dict[str, str]]:
    return retrieve_top_k(query=normalize_query(query), k=settings.top_k)
