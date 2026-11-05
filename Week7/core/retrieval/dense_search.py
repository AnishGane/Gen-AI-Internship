from Week7.core.embeddings import get_embedder
from Week7.core.vector_store import VectorStore


def dense_search(store: VectorStore, query: str, k=10, filters=None, score_threshold=None):
    return store.search(
        mode="dense", 
        dense_vec=get_embedder().embed_dense([query])[0],
        limit=k,
        filters=filters,
        score_threshold=score_threshold
    )
