from __future__ import annotations

from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from src.local_index import build_index
from src.config import PROJECT_ROOT


KB_DIR = PROJECT_ROOT / "data" / "knowledge_base"


def load_markdown_docs() -> list[Document]:
    docs: list[Document] = []
    for source_file in KB_DIR.rglob("*"):
        if not source_file.is_file():
            continue

        suffix = source_file.suffix.lower()
        if suffix in {".md", ".txt"}:
            text = source_file.read_text(encoding="utf-8")
        elif suffix == ".pdf":
            from pypdf import PdfReader

            reader = PdfReader(str(source_file))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            continue

        docs.append(Document(page_content=text, metadata={"source": source_file.name}))
    return docs


def split_docs(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=120)
    return splitter.split_documents(docs)


def run_ingest() -> int:
    docs = load_markdown_docs()
    if not docs:
        raise FileNotFoundError("No supported documents found in data/knowledge_base")

    chunks = split_docs(docs)
    payload = [
        {
            "text": chunk.page_content,
            "source": str(chunk.metadata.get("source", "unknown")),
        }
        for chunk in chunks
    ]
    return build_index(payload)


if __name__ == "__main__":
    total = run_ingest()
    print(f"Ingestion complete. Total chunks indexed: {total}")
