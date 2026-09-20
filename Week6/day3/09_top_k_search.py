from Week6.config import QDRANT_PATH, TOP_K
from Week6.embeddings import EmbeddingService
from Week6.qdrant_client import QdrantService

def search(query: str, top_k: int):
    embedding_service = EmbeddingService()
    
    query_vector = embedding_service.embed_text(query)

    qdrant = QdrantService(path=str(QDRANT_PATH))
    
    try:
        return qdrant.search_qdrant(query_vector, limit=top_k)
    finally:
        qdrant.close()

def main():
    print("=" * 20)
    print("WEEK 6 - TOP K SEARCH")
    print("=" * 20)

    query = "What is used for building user interfaces/UI?"
    
    print(f"\nQuery: {query}")
    print(f"Top-K: {TOP_K}")

    results = search(
        query=query,
        top_k=TOP_K,
    )

    print(
        f"\nRetrieved {len(results)} results."
    )

    for rank, result in enumerate(
        results,
        start=1,
    ):

        print("\n" + "=" * 50)

        print(f"Rank: {rank}")
        print(f"Score: {result.score:.4f}")
        print(
            f"Source: "
            f"{result.payload.get('source')}"
        )
        print(
            f"Chunk ID: "
            f"{result.payload.get('chunk_id')}"
        )
        print(
            f"Text: "
            f"{result.payload.get('text')}"
        )

if __name__ == "__main__":
    main()
    