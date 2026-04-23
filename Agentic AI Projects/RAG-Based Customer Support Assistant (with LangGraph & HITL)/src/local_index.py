from __future__ import annotations

import re
from hashlib import blake2b
from pathlib import Path

import chromadb
import numpy as np

from src.config import settings


INDEX_VERSION = 3
VECTOR_DIM = 1024
COLLECTION_NAME = "customer_support_kb"


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


def _text_to_vector(text: str, dim: int = VECTOR_DIM) -> list[float]:
    vec = np.zeros(dim, dtype=np.float32)
    tokens = _tokenize(text)
    if not tokens:
        return vec.tolist()

    for tok in tokens:
        digest = blake2b(tok.encode("utf-8"), digest_size=8).digest()
        index = int.from_bytes(digest, byteorder="big") % dim
        vec[index] += 1.0

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


def _client() -> chromadb.PersistentClient:
    index_dir = Path(settings.index_dir)
    index_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(index_dir))


def _collection() -> chromadb.Collection:
    return _client().get_or_create_collection(name=COLLECTION_NAME)


def index_exists() -> bool:
    try:
        collection = _client().get_collection(name=COLLECTION_NAME)
        return collection.count() > 0
    except Exception:
        return False


def build_index(chunks: list[dict[str, str]]) -> int:
    if not chunks:
        raise ValueError("No chunks provided for indexing")

    client = _client()
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass

    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    ids = [f"chunk-{i}" for i in range(len(chunks))]
    documents = [item["text"] for item in chunks]
    metadatas = [{"source": item.get("source", "unknown"), "version": INDEX_VERSION} for item in chunks]
    embeddings = [_text_to_vector(text) for text in documents]

    collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
    return len(chunks)


def ensure_index() -> bool:
    if index_exists():
        return False

    from src.ingest import run_ingest

    run_ingest()
    return True


def retrieve_top_k(query: str, k: int) -> list[dict[str, str]]:
    ensure_index()

    collection = _collection()
    result = collection.query(query_embeddings=[_text_to_vector(query)], n_results=k)

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]

    return [
        {
            "text": document,
            "source": str(metadata.get("source", "unknown")) if metadata else "unknown",
        }
        for document, metadata in zip(documents, metadatas)
    ]
