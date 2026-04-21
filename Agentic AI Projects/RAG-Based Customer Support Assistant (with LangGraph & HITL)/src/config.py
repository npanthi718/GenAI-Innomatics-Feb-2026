from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def _resolve_path(raw_value: str, default_path: Path) -> str:
    candidate = Path(raw_value)
    if candidate.is_absolute():
        return str(candidate)
    return str((PROJECT_ROOT / candidate).resolve())


@dataclass(frozen=True)
class Settings:
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    embed_model: str = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    llm_provider: str = os.getenv("LLM_PROVIDER", "groq")
    index_dir: str = _resolve_path(os.getenv("INDEX_DIR", ".local_index"), PROJECT_ROOT / ".local_index")
    top_k: int = int(os.getenv("TOP_K", "4"))
    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.72"))


settings = Settings()
