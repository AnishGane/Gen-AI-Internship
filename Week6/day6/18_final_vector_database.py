from qdrant_client.http.models import PointStruct

from Week6.config import (
    COLLECTION_NAME,
    QDRANT_PATH,
)
from Week6.embeddings import EmbeddingService
from Week6.qdrant_client import QdrantService
from Week6.utils import load_documents


class VectorDatabaseApplication:

    def __init__(self):

        self.embedding_service = (
            EmbeddingService()
        )

        self.qdrant = QdrantService(
            path=str(QDRANT_PATH)
        )

    def prepare_database(self):

        print("\nLoading documents...")

        chunks = load_documents()

        if not chunks:

            raise ValueError(
                "No document chunks found."
            )

        print(
            f"Loaded {len(chunks)} chunks."
        )

        print(
            "\nGenerating embeddings..."
        )

        embeddings = (
            self.embedding_service.embed_batch(
                [chunk.text for chunk in chunks]
            )
        )

        if not embeddings:

            raise ValueError(
                "No embeddings generated."
            )

        vector_size = len(
            embeddings[0]
        )

        print(
            f"Embedding dimension: "
            f"{vector_size}"
        )

        print(
            "\nCreating Qdrant collection..."
        )

        self.qdrant.create_collection(
            vector_size=vector_size,
            collection_name=COLLECTION_NAME,
        )

        points = []

        for index, (
            chunk,
            embedding,
        ) in enumerate(
            zip(chunks, embeddings)
        ):

            points.append(
                PointStruct(
                    id=index,
                    vector=embedding,
                    payload={
                        "text": chunk.text,
                        "source": chunk.source,
                        "chunk_id": chunk.chunk_id,
                    },
                )
            )

        print(
            f"\nStoring {len(points)} "
            f"points..."
        )

        self.qdrant.insert_points(
            points
        )

        print(
            "Database preparation complete."
        )

    def search(
        self,
        query: str,
        limit: int = 5,
    ):

        if not query.strip():

            raise ValueError(
                "Query cannot be empty."
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

        return results

    def close(self):

        self.qdrant.close()


def display_results(results):

    if not results:

        print(
            "\nNo relevant results found."
        )

        return

    for rank, result in enumerate(
        results,
        start=1,
    ):

        payload = result.payload

        print("\n" + "=" * 20)

        print(
            f"Rank: {rank}"
        )

        print(
            f"Score: {result.score:.4f}"
        )

        print(
            f"Source: "
            f"{payload.get('source')}"
        )

        print(
            f"Chunk ID: "
            f"{payload.get('chunk_id')}"
        )

        print(
            f"\n{payload.get('text')}"
        )


def main():

    app = VectorDatabaseApplication()

    try:

        print("=" * 20)
        print("WEEK 6 - FINAL VECTOR DATABASE")
        print("=" * 20)

        app.prepare_database()

        print(
            "\nDatabase is ready."
        )

        print(
            "Type 'exit' or 'quit' to stop."
        )

        while True:

            query = input(
                "\nSearch: "
            ).strip()

            if query.lower() in {
                "exit",
                "quit",
            }:

                break

            if not query:

                print(
                    "Please enter a query."
                )

                continue

            try:

                results = app.search(
                    query=query,
                    limit=5,
                )

                display_results(results)

            except Exception as exc:

                print(
                    f"\nSearch failed: {exc}"
                )

    finally:

        app.close()

    print(
        "\nVector search application "
        "closed."
    )

if __name__ == "__main__":
    main()