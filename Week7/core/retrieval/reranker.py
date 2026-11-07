"""Day 3: cross-encoder reranking (second stage)."""
from functools import lru_cache
from Week7.config import settings
from Week7.models import RetrievedChunk

@lru_cache(maxsize=1)
def _model():
    from fastembed.rerank.cross_encoder import TextCrossEncoder

    settings.validate_for_rerank()
    return TextCrossEncoder(settings.rerank_model)

class Reranker:
    def rerank(self, query: str, chunks: list[RetrievedChunk], top_n: int = 5,
               min_score: float | None = None) -> list[RetrievedChunk]:
        if not chunks:
            return []
        scores = list(_model().rerank(query, [c.text for c in chunks]))
        ranked = [c.model_copy(update={"rerank_score": float(s)}) for c, s in zip(chunks, scores)]
        ranked.sort(key=lambda c: c.rerank_score, reverse=True)
        if min_score is not None:
            ranked = [c for c in ranked if c.rerank_score >= min_score]
        return ranked[:top_n]


def compare_orders(before: list[RetrievedChunk], after: list[RetrievedChunk]) -> list[tuple[str, int, int]]:
    """(chunk_id, original_rank, reranked_rank) for inspection."""
    pos = {c.chunk_id: i + 1 for i, c in enumerate(before)}
    return [(c.chunk_id, pos.get(c.chunk_id, -1), i + 1) for i, c in enumerate(after)]
