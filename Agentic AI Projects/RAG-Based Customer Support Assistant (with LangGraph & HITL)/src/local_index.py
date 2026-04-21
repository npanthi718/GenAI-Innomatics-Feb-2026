from __future__ import annotations

import json
import re
from hashlib import blake2b
from pathlib import Path

import numpy as np

from src.config import settings


INDEX_VERSION = 2
VECTOR_DIM = 1024


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


def _text_to_vector(text: str, dim: int = VECTOR_DIM) -> np.ndarray:
    vec = np.zeros(dim, dtype=np.float32)
    tokens = _tokenize(text)
    if not tokens:
        return vec

    for tok in tokens:
        digest = blake2b(tok.encode("utf-8"), digest_size=8).digest()
        index = int.from_bytes(digest, byteorder="big") % dim
        vec[index] += 1.0

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec


def _index_dir() -> Path:
    path = Path(settings.index_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _meta_path() -> Path:
    return _index_dir() / "meta.json"


def _is_index_compatible() -> bool:
    meta_file = _meta_path()
    if not meta_file.exists():
        return False

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except Exception:
        return False

    return bool(meta.get("version") == INDEX_VERSION and meta.get("dim") == VECTOR_DIM)


def index_exists() -> bool:
    index_dir = _index_dir()
    return (index_dir / "vectors.npy").exists() and (index_dir / "chunks.json").exists() and _is_index_compatible()


def build_index(chunks: list[dict[str, str]]) -> int:
    if not chunks:
        raise ValueError("No chunks provided for indexing")

    texts = [item["text"] for item in chunks]
    vectors = np.vstack([_text_to_vector(text) for text in texts])

    index_dir = _index_dir()
    np.save(index_dir / "vectors.npy", vectors)
    (index_dir / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=True, indent=2), encoding="utf-8")
    _meta_path().write_text(
        json.dumps({"version": INDEX_VERSION, "dim": VECTOR_DIM, "kind": "hashing_bow"}, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )
    return len(chunks)


def ensure_index() -> bool:
    if index_exists():
        return False

    from src.ingest import run_ingest

    run_ingest()
    return True


def retrieve_top_k(query: str, k: int) -> list[dict[str, str]]:
    ensure_index()

    index_dir = _index_dir()
    vectors_file = index_dir / "vectors.npy"
    chunks_file = index_dir / "chunks.json"

    if not vectors_file.exists() or not chunks_file.exists():
        raise FileNotFoundError("Local index missing. Check data/knowledge_base and run ingestion once.")

    vectors = np.load(vectors_file)
    chunks = json.loads(chunks_file.read_text(encoding="utf-8"))

    query_vec = _text_to_vector(query)
    scores = vectors @ query_vec
    top_indices = np.argsort(scores)[::-1][:k]

    return [chunks[int(i)] for i in top_indices]
