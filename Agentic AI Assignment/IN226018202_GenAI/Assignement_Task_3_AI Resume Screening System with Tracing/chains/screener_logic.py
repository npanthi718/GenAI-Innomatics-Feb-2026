import os
import re
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from prompts.templates import extraction_template, jd_extraction_template, screening_template

# CRITICAL: Load the API keys BEFORE initializing the LLM
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

MODEL_CANDIDATES: List[str] = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
]


def _extract_fit_score(text: str) -> Optional[int]:
    """Best-effort extraction of numeric fit score from model output."""
    patterns = [
        r"fit\s*score\s*[:\-]?\s*(\d{1,3})",
        r"score\s*[:\-]?\s*(\d{1,3})\s*/\s*100",
        r"(\d{1,3})\s*/\s*100",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            score = int(match.group(1))
            return max(0, min(score, 100))
    return None


def _extract_recommendation(text: str) -> Optional[str]:
    """Extract recommendation label from evaluation output."""
    match = re.search(
        r"recommendation\s*[:\-]?\s*(strong\s*fit|moderate\s*fit|low\s*fit)",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None

    raw = re.sub(r"\s+", " ", match.group(1)).strip().lower()
    if raw == "strong fit":
        return "Strong Fit"
    if raw == "moderate fit":
        return "Moderate Fit"
    if raw == "low fit":
        return "Low Fit"
    return None



def _build_chains(model_name: str):
    llm = ChatGroq(model=model_name, temperature=0, groq_api_key=api_key)
    jd_chain = jd_extraction_template | llm | StrOutputParser()
    extraction_chain = extraction_template | llm | StrOutputParser()
    evaluation_chain = screening_template | llm | StrOutputParser()
    return jd_chain, extraction_chain, evaluation_chain


def _run_with_model_fallback(payload: Dict[str, str], stage: str) -> Tuple[str, str]:
    last_error: Optional[Exception] = None
    for model_name in MODEL_CANDIDATES:
        try:
            jd_chain, extraction_chain, evaluation_chain = _build_chains(model_name)

            if stage == "jd":
                return jd_chain.invoke({"job_description": payload["job_description"]}), model_name
            if stage == "resume":
                return extraction_chain.invoke({"resume_text": payload["resume_text"]}), model_name
            if stage == "evaluation":
                return (
                    evaluation_chain.invoke(
                        {
                            "extracted_data": payload["extracted_data"],
                            "job_description": payload["job_description"],
                        }
                    ),
                    model_name,
                )
            raise ValueError(f"Unsupported stage: {stage}")
        except Exception as exc:
            last_error = exc
            continue

    raise RuntimeError(
        "Groq request failed for all configured models. "
        f"Stage: {stage}. Last error: {last_error}"
    )


def run_screening(resume_text: str, job_description: str) -> Dict[str, Optional[str]]:
    """Run JD extraction, resume extraction, and final evaluation using Groq."""
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing in .env")

    jd_profile, jd_model = _run_with_model_fallback(
        {"job_description": job_description}, stage="jd"
    )
    extracted_data, resume_model = _run_with_model_fallback(
        {"resume_text": resume_text}, stage="resume"
    )
    evaluation, eval_model = _run_with_model_fallback(
        {"extracted_data": extracted_data, "job_description": jd_profile},
        stage="evaluation",
    )

    fit_score = _extract_fit_score(evaluation)
    recommendation = _extract_recommendation(evaluation)
    return {
        "model": eval_model,
        "mode": "groq-ai",
        "models_used": f"jd={jd_model}, resume={resume_model}, evaluation={eval_model}",
        "jd_profile": jd_profile,
        "extracted_data": extracted_data,
        "evaluation": evaluation,
        "fit_score": fit_score,
        "recommendation": recommendation,
        "error": None,
    }