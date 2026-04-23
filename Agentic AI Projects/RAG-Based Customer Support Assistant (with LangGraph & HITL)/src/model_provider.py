from __future__ import annotations

from typing import Any

from src.config import settings


def _groq_model_candidates() -> list[str]:
    candidates = [settings.groq_model, "llama-3.3-70b-versatile", "qwen/qwen3-32b"]
    unique: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in unique:
            unique.append(candidate)
    return unique


def get_chat_model() -> Any:
    provider = settings.llm_provider.lower().strip()

    if provider == "gemini":
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is missing in .env")
        # Import lazily so non-Gemini runs do not trigger Gemini package warnings.
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
            temperature=0,
        )

    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is missing in .env")

    from langchain_groq import ChatGroq

    last_error: Exception | None = None
    for model_name in _groq_model_candidates():
        try:
            return ChatGroq(
                model=model_name,
                groq_api_key=settings.groq_api_key,
                temperature=0,
            )
        except Exception as exc:
            last_error = exc

    if settings.gemini_api_key:
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
            temperature=0,
        )

    if last_error is not None:
        raise RuntimeError(f"No supported Groq model available. Last error: {last_error}") from last_error

    raise RuntimeError("No supported model provider available.")
