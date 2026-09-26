from Week6.embeddings import EmbeddingService
from Week6.config import QDRANT_PATH
from Week6.qdrant_client import QdrantService
from Week6.models import SearchChunk
from typing import Optional

class SearchService:
    """
    High-level service for semantic document search.

    Responsible for:
    1. Converting the query into an embedding.
    2. Searching Qdrant.
    3. Converting Qdrant results into SearchChunk objects.
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()
        
        self.qdrant = QdrantService(
            path = str(QDRANT_PATH)
        )

    def search(
        self,
        query: str,
        limit: int = 5,
        min_score: Optional[float] = None
    ) -> list[SearchChunk]:
        if not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        if limit <= 0:
            raise ValueError(
                "Limit must be greater than zero."
            )
        
        if min_score is not None and min_score < 0.3:
            raise ValueError(
                "Min score must be greater than 0.3 or None."
            )

        query_vector = self.embedding_service.embed_text(query)

        results = self.qdrant.search_qdrant(query_vector, limit)

        search_results = []

        for result in results:
            
            if min_score is not None and result.score < min_score:
                continue

            search_results.append(
                SearchChunk(
                    text = result.payload["text"],
                    source = result.payload["source"],
                    chunk_id = result.payload["chunk_id"],
                    score = result.score
                )
            )

        return search_results
    
    def close(self):
        self.qdrant.close()
        