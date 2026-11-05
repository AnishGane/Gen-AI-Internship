"""Day 5: hybrid retrieval (server-side RRF) + client-side RRF for merging multi-query results."""
from Week7.core.embeddings import get_embedder
from Week7.core.vector_store import VectorStore
from Week7.models import RetrievedChunk

def hybrid_search(store: VectorStore, query: str, k=10, filters=None) -> list[RetrievedChunk]:
    emb = get_embedder()
    return store.search(
        mode="hybrid",
        dense_vec=emb.embed_dense([query])[0],
        sparse_vec=emb.embed_sparse_query(query),
        limit=k,
        filters=filters
    )

def rrf_merge(result_lists: list[list[RetrievedChunk]], k: int = 60, top: int | None = None) -> list[RetrievedChunk]:
    """Reciprocal Rank Fusion: score = sum(1 / (k + rank)). Dedupes by stable point_id."""
    scores: dict[str, float] = {}
    by_id: dict[str, RetrievedChunk] = {}
    for lst in result_lists:
        for rank, c in enumerate(lst, 1):
            scores[c.point_id] = scores.get(c.point_id, 0.0) + 1.0 / (k + rank)
            by_id.setdefault(c.point_id, c)
    merged = sorted(by_id.values(), key=lambda c: scores[c.point_id], reverse=True)
    merged = [c.model_copy(update={"score": scores[c.point_id]}) for c in merged]
    return merged[:top] if top else merged
