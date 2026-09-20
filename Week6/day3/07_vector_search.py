from Week6.config import QDRANT_PATH
from Week6.embeddings import EmbeddingService
from Week6.qdrant_client import QdrantService
from Week6.logger import logger

def main():
    print("=" * 20)
    print("WEEK 6 - BASIC VECTOR SEARCH")
    print("=" * 20)

    query = "What is Python used for?"

    print(f"\nQuery: {query}")

    # 1. Generate query embeddings
    embedding_service = EmbeddingService()
    
    query_vector = embedding_service.embed_text(
        query
    )

    logger.info(
        "Length of query vector: %s", len(query_vector)
    )

    # 2. Connect to qdrant
    qdrant = QdrantService(
        path=str(QDRANT_PATH)
    )

    try:
        # 3. Search from qdrant
        results = qdrant.search_qdrant(
            query_vector = query_vector,
            limit = 5
        )
        
        logger.info(
            "Results found: %s", len(results)
        )

        # 4. Display Results
        for idx, result in enumerate(results, start=1):
            print("\n" + "=" * 20)

            print(f"Rank: {idx}")
            print(f"Score: {result.score}")
            print(f"ID: {result.id}")
            print(
                f"Source: "
                f"{result.payload.get('source')}"
            )
            print(
                f"Text: "
                f"{result.payload.get('text')}"
            )
    finally:
        qdrant.close()

if __name__ == "__main__":
    main()