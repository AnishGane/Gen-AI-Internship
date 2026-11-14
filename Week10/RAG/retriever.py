"""Retrieval that returns plain dicts (easy to checkpoint, log and send over an API)."""
from typing import TypedDict

from Week10.config import settings
from Week10.exceptions import RetrievalError
from Week10.lc.retrieval import get_vector_store

class Chunk(TypedDict):
    content: str
    source: str
    score: float

def _source_of(meta: dict) -> str:
    for key in ("source", "file", "filename", "title", "doc_id"):
        if meta.get(key):
            return str(meta[key])
    return "unknown"

def retrieve_chunks(query: str, k: int | None = None) -> list[Chunk]:
    try:
        results = get_vector_store().similarity_search_with_score(query, k=k or settings.top_k)
    except Exception as exc:
        raise RetrievalError(f"Qdrant search failed: {exc}") from exc
    return [{"content": d.page_content, "source": _source_of(d.metadata), "score": float(s)} for d, s in results]
