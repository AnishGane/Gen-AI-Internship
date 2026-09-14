from Week6.embeddings import EmbeddingService
from Week6.exceptions import Week6Error
from Week6.logger import logger
from Week6.qdrant_client import QdrantService
from Week6.config import COLLECTION_NAME

def main():
    print("="*8)
    print("CREATE QDRANT COLLECTION")
    print("="*8)

    try:
        embedding_service = EmbeddingService()

        print("\nGenerating test embedding...")

        test_vector = embedding_service.embed_text(
            "This is a test document for Week 6."
        )
        
        vector_size = len(test_vector)
        print(f"Vector dimension: {vector_size}")
        
        qdrant = QdrantService()

        qdrant.create_collection(
            vector_size=vector_size,
            collection_name=COLLECTION_NAME,
        )

        print(
            f"\nCollection '{COLLECTION_NAME}' "
            "is ready."
        )

        print("\nAvailable collections:")

        for collection in qdrant.get_collections():
            print(f"- {collection}")

        qdrant.close()

    except Week6Error as exc:
        logger.error("Week 6 error: %s", exc)
        print(f"\nError: {exc}")

    except Exception as exc:
        logger.exception(
            "Unexpected application error"
        )
        print(
            f"\nUnexpected error: {exc}"
        )

if __name__ == "__main__":
    main()