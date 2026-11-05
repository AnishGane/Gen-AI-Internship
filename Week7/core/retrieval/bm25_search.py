from Week7.core.embeddings import get_embedder
from Week7.core.vector_store import VectorStore

def bm25_search(store: VectorStore, query: str, k = 10, filters = None):
    return store.search(
        mode="sparse",
        sparse_vec=get_embedder().embed_sparse_query(query),
        limit=k,
        filters=filters
    )