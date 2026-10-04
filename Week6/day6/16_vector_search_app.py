from Week6.config import QDRANT_PATH
from Week6.embeddings import EmbeddingService
from Week6.models import SearchChunk
from Week6.qdrant_client import QdrantService

class VectorSearchApp:
    """
    High-level application for semantic vector search.
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()
        
        self.qdrant = QdrantService(
            path=str(QDRANT_PATH)
        )
        
    def search(self, query: str, limit: int = 5, min_score: float = 0.0) -> list[SearchChunk]:
        if not query.strip():
            raise ValueError(
                "Search query cannot be empty."
            )

        if limit <= 0:
            raise ValueError(
                "Limit must be greater than zero."
            )

        query_vector = (
            self.embedding_service.embed_text(
                query
            )
        )

        results = self.qdrant.search_qdrant(
            query_vector=query_vector,
            limit=limit,
        )

        search_results = []

        for result in results:

            if result.score < min_score:
                continue

            search_results.append(
                SearchChunk(
                    text=result.payload.get("text"),
                    source=result.payload.get("source"),
                    chunk_id=result.payload.get("chunk_id"),
                    score=result.score,
                )
            )

        return search_results

    def close(self):

        self.qdrant.close()

def display_results(
    results: list[SearchChunk],
):

    if not results:

        print("\nNo relevant results found.")

        return

    for rank, result in enumerate(
        results,
        start=1,
    ):

        print("\n" + "=" * 20)

        print(f"Rank: {rank}")
        print(f"Score: {result.score:.4f}")
        print(f"Source: {result.source}")
        print(f"Chunk ID: {result.chunk_id}")
        print(f"Text: {result.text}")


def main():

    app = VectorSearchApp()

    try:

        query = "What is React used for?"

        print("=" * 20)
        print("VECTOR SEARCH APPLICATION")
        print("=" * 20)

        print(f"\nQuery: {query}")

        results = app.search(
            query=query,
            limit=5,
            min_score=0.0,
        )

        display_results(results)

    finally:
        app.close()

if __name__ == "__main__":
    main()