from Week6.config import QDRANT_PATH
from Week6.embeddings import EmbeddingService
from Week6.models import SearchChunk
from Week6.qdrant_client import QdrantService


class InteractiveSearch:

    def __init__(self):

        self.embedding_service = EmbeddingService()

        self.qdrant = QdrantService(
            path=str(QDRANT_PATH)
        )

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[SearchChunk]:

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

        print("\nNo results found.")

        return

    for rank, result in enumerate(
        results,
        start=1,
    ):

        print("\n" + "-" * 20)

        print(f"Rank: {rank}")
        print(f"Score: {result.score:.4f}")
        print(f"Source: {result.source}")
        print(f"Chunk ID: {result.chunk_id}")

        print(
            f"\n{result.text}"
        )


def main():

    search = InteractiveSearch()

    print("=" * 20)
    print("WEEK 6 - INTERACTIVE VECTOR SEARCH")
    print("=" * 20)

    print(
        "\nType 'exit' or 'quit' to stop."
    )

    try:

        while True:

            query = input(
                "\nSearch: "
            ).strip()

            if query.lower() in {
                "exit",
                "quit",
            }:

                print(
                    "\nExiting search."
                )

                break

            if not query:

                print(
                    "Please enter a search query."
                )

                continue

            try:

                results = search.search(
                    query=query,
                    limit=5,
                )

                display_results(results)

            except Exception as exc:

                print(
                    f"\nSearch failed: {exc}"
                )

    finally:

        search.close()

if __name__ == "__main__":
    main()