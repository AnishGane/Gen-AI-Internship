import math

from Week6.config import QDRANT_PATH
from Week6.embeddings import EmbeddingService
from Week6.qdrant_client import QdrantService
from Week6.utils import EVALUATION_DATASET

def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Vectors must have the same dimension."
        )

    dot_product = sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b,
        )
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return (
        dot_product
        / (magnitude_a * magnitude_b)
    )

def main():
    print("=" * 20)
    print("WEEK 5 vs WEEK 6 SEARCH COMPARISON")
    print("=" * 20)

    query = "What is Python used for?"

    print(f"\nQuery: {query}")

    embedding_service = EmbeddingService()

    qdrant = QdrantService(
        path=str(QDRANT_PATH)
    )
    
    try:
        # 1. Generate query embedding
        query_vector = (
            embedding_service.embed_text(query)
        )

        # 2. Retrieve stored points
        stored_points = qdrant.get_points(
            limit=100
        )

        # 3. Manual Week 5 similarity calculation
        manual_results = []

        for point in stored_points:

            # get_points() does not currently request
            # vectors, so this section assumes vectors
            # are available if requested from Qdrant.

            manual_results.append(
                {
                    "id": point.id,
                    "source": point.payload.get(
                        "source"
                    ),
                    "text": point.payload.get(
                        "text"
                    ),
                }
            )
            
        # 4. Qdrant search
        qdrant_results = qdrant.search_qdrant(
            query_vector=query_vector,
            limit=5,
        )

        print("\n" + "=" * 20)
        print("QDRANT RESULTS")
        print("=" * 20)

        for rank, result in enumerate(
            qdrant_results,
            start=1,
        ):

            print(
                f"\nRank: {rank}"
            )

            print(
                f"Score: "
                f"{result.score:.4f}"
            )

            print(
                f"Source: "
                f"{result.payload.get('source')}"
            )

            print(
                f"Text: "
                f"{result.payload.get('text')}"
            )

        # 5. Display manual dataset
        print("\n" + "=" * 20)
        print("WEEK 5 MANUAL APPROACH")
        print("=" * 20)

        print(
            f"\nStored points available: "
            f"{len(manual_results)}"
        )

        for result in manual_results:

            print(
                f"\nID: {result['id']}"
            )

            print(
                f"Source: {result['source']}"
            )

            print(
                f"Text: {result['text']}"
            )

        print("\n" + "=" * 20)
        print("COMPARISON")
        print("=" * 20)

        print(
            "\nWeek 5:"
            "\n- Embeddings handled manually"
            "\n- Similarity calculation handled manually"
            "\n- Sorting handled manually"
            "\n- Entire vector set must be available"
        )

        print(
            "\nWeek 6:"
            "\n- Embeddings are still generated"
            "\n- Vectors are stored in Qdrant"
            "\n- Qdrant performs vector search"
            "\n- Payload is returned with results"
        )

    finally:
        qdrant.close()

if __name__ == "__main__":
    main()