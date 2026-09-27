from Week6.config import QDRANT_PATH
from Week6.embeddings import EmbeddingService
from Week6.qdrant_client import QdrantService
from Week6.utils import EVALUATION_DATASET

def calculate_recall(
    retrieved_sources: list[str],
    expected_sources: list[str]
):
    if not expected_sources:
        return 0.0

    retrieved = set(retrieved_sources)

    relevant_found = (
        retrieved & expected_sources
    )

    return (
        len(relevant_found)
        / len(expected_sources)
    )

def calculate_precision(
    retrieved_sources: list[str],
    expected_sources: set[str],
) -> float:

    if not retrieved_sources:
        return 0.0

    relevant_found = [
        source
        for source in retrieved_sources
        if source in expected_sources
    ]

    return (
        len(relevant_found)
        / len(retrieved_sources)
    )



def main():
    print("=" * 20)
    print("WEEK 6 - VECTOR SEARCH EVALUATION")
    print("=" * 20)

    embedding_service = EmbeddingService()

    qdrant = QdrantService(
        path=str(QDRANT_PATH)
    )

    total_recall = 0.0
    total_precision = 0.0

    try:

        for index, evaluation in enumerate(
            EVALUATION_DATASET,
            start=1,
        ):

            query = evaluation.query
            expected_sources = (
                evaluation.expected_sources
            )

            print("\n" + "=" * 20)
            print(f"Query {index}")
            print(f"Question: {query}")
            print(
                f"Expected: "
                f"{expected_sources}"
            )

            query_vector = (
                embedding_service.embed_text(
                    query
                )
            )

            results = qdrant.search_qdrant(
                query_vector=query_vector,
                limit=3,
            )

            retrieved_sources = [
                result.payload.get("source")
                for result in results
            ]

            recall = calculate_recall(
                retrieved_sources,
                expected_sources,
            )

            precision = calculate_precision(
                retrieved_sources,
                expected_sources,
            )

            total_recall += recall
            total_precision += precision

            print(
                f"Retrieved: "
                f"{retrieved_sources}"
            )

            print(
                f"Recall@3: "
                f"{recall:.2f}"
            )

            print(
                f"Precision@3: "
                f"{precision:.2f}"
            )

    finally:

        qdrant.close()

    count = len(EVALUATION_DATASET)

    average_recall = (
        total_recall / count
    )

    average_precision = (
        total_precision / count
    )

    print("\n" + "=" * 20)
    print("FINAL EVALUATION")
    print("=" * 20)

    print(
        f"Average Recall@3: "
        f"{average_recall:.2f}"
    )

    print(
        f"Average Precision@3: "
        f"{average_precision:.2f}"
    )

if __name__ == "__main__":
    main()