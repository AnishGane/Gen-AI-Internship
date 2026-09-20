from Week6.models import SearchChunk
from Week6.logger import logger
from Week6.config import QDRANT_PATH
from Week6.embeddings import EmbeddingService
from Week6.qdrant_client import QdrantService

def main():
    print("=" * 20)
    print("WEEK 6 - METADATA AND PAYLOAD")
    print("=" * 20)

    query = "How is React used?"

    print(f"\nQuery: {query}")

    embedding_service = EmbeddingService()

    query_vector = embedding_service.embed_text(
        query
    )

    qdrant = QdrantService(
        path=str(QDRANT_PATH)
    )
    
    try:
        results = qdrant.search_qdrant(
            query_vector = query_vector,
            limit = 5
        )

        search_results = []

        for result in results:
            search_results.append(
                SearchChunk(
                    text = result.payload.get("text"),
                    source = result.payload.get("source"),
                    chunk_id = result.payload.get("chunk_id"),
                    score = result.score
                )
            )
            
        for rank, result in enumerate(
            search_results,
            start=1,
        ):
            print("\n" + "=" * 20)

            print(f"Rank: {rank}")
            print(f"Score: {result.score:.4f}")
            print(f"Source: {result.source}")
            print(f"Chunk ID: {result.chunk_id}")
            print(f"Text: {result.text}")
            
    finally:
        qdrant.close()
        
if __name__ == "__main__":
    main()