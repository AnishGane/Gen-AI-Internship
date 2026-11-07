"""Dense + sparse (BM25) embeddings via fastembed."""
from functools import lru_cache
from qdrant_client import models
from Week7.config import settings

class EmbeddingService:
    def __init__(self):
        from fastembed import TextEmbedding, SparseTextEmbedding

        settings.validate_for_dense()
        self.dense_embedding = TextEmbedding(settings.dense_model)
        self.sparse_embedding = SparseTextEmbedding("Qdrant/bm25")

    def embed_dense(self, texts: list[str]) -> list[list[float]]:
         return [
            vector.tolist()
            for vector in self.dense_embedding.embed(texts)
        ]

    def embed_sparse(self, texts: list[str]) -> list[models.SparseVector]:
        return [
            models.SparseVector(
                indices=embedding.indices.tolist(),
                values=embedding.values.tolist(),
            )
            for embedding in self.sparse_embedding.embed(texts)
        ]

    def embed_sparse_query(self, query: str) -> models.SparseVector:
        embedding = next(
            iter(self.sparse_embedding.query_embed(query))
        )
        return models.SparseVector(
            indices=embedding.indices.tolist(),
            values=embedding.values.tolist(),
        )

@lru_cache(maxsize=1)
def get_embedder() -> EmbeddingService:
    return EmbeddingService()