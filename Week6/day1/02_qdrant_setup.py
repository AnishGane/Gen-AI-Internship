# from qdrant_client import QdrantClient
from Week6.qdrant_client import QdrantClient
from Week6.config import QDRANT_PATH
# from Week6.exceptions import VectorDatabaseException
# from Week6.logger import logger

def create_qdrant_client() -> QdrantClient:
    """
    Create a local Qdrant Client
    """

    # try:
    #     client = QdrantClient(path = QDRANT_PATH)

    #     logger.info(
    #         "Qdrant intialized at %s",
    #         QDRANT_PATH
    #     )

    #     return client

    # except Exception as exc:
    #     logger.exception(
    #         "Failed to intialize Qdrant client"
    #     )

    #     raise VectorDatabaseException(
    #         "Failed to intialize Qdrant client"
    #     ) from exc
    
    return QdrantClient(path = QDRANT_PATH)

def main():
    client = create_qdrant_client()

    print("=" * 8)
    print(client.get_collections())
    print("=" * 8)

    print("\nQdrant client created successfully.")
    print(f"Storage path: {QDRANT_PATH}")

    collections = client.get_collections()

    print("\nAvailable collections:")

    if not collections.collections:
        print("No collections found.")

    else:
        for collection in collections.collections:
            print(f"- {collection.name}")

    client.close()


if __name__ == "__main__":
    main()
