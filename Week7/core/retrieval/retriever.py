"""Single entry point for candidate generation: mode x multi-query x filters."""
from Week7.core.retrieval.bm25_search import bm25_search
from Week7.core.retrieval.dense_search import dense_search
from Week7.core.retrieval.hybrid_search import hybrid_search, rrf_merge
from Week7.core.vector_store import VectorStore
from Week7.models import RetrievedChunk

class Retriever:
    def __init__(self, store: VectorStore):
        self.store = store

    def retrieve(self, queries: list[str] | str, mode: str = "hybrid", k: int = 20,
                 filters: dict | None = None, score_threshold: float | None = None) -> list[RetrievedChunk]:
        queries = [queries] if isinstance(queries, str) else queries
        fn = {"dense": lambda q: dense_search(self.store, q, k, filters, score_threshold),
              "sparse": lambda q: bm25_search(self.store, q, k, filters),
              "hybrid": lambda q: hybrid_search(self.store, q, k, filters)}[mode]
        results = [fn(q) for q in queries]
        return results[0] if len(results) == 1 else rrf_merge(*results, top=k)
