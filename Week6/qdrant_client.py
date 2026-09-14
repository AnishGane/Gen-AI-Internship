from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models

from Week6.config import COLLECTION_NAME, QDRANT_PATH
from Week6.exceptions import VectorDatabaseError
from Week6.logger import logger

class QdrantService:
    """
    Handles all Qdrant database operations
    """

    def __init__(self, path: str = QDRANT_PATH):
        try:
            self.client = QdrantClient(path = path)

            logger.info(
                "Qdrant intialized at %s",
                path
            )

        except Exception as exc:
            logger.exception(
                "Failed to intialize Qdrant client"
            )

            raise VectorDatabaseError(
                "Failed to intialize Qdrant client"
            ) from exc

    def collection_exists(self, collection_name: str = COLLECTION_NAME) -> bool:
        """
        Check  whether a collection exists.
        """

        try:
            return self.client.collection_exists(
                collection_name = collection_name
            )

        except Exception as exc:
            logger.exception(
                "Failed to check collection"
            )

            raise VectorDatabaseError(
                "Failed to check collection."
            ) from exc

    def create_collection(
        self,
        vector_size: int,
        collection_name: str = COLLECTION_NAME
    ) -> None:
        """
        Create a Qdrant collection usinf cosine similarity.
        """

        if vector_size <= 0:
            raise VectorDatabaseError(
                "vector_size must be greater than zero."
            )

        try:
            if self.collection_exists(collection_name):
                logger.info(
                    "Collection %s already exists.",
                    collection_name
                )
                return

            self.client.create_collection(
                collection_name = collection_name,
                vectors_config = models.VectorParams(
                    size = vector_size,
                    distance = models.Distance.COSINE,
                ),
            )

            logger.info(
                "Created collection '%s'",
                collection_name
            )

        except Exception as exc:
            logger.exception(
                "Failed to create collection"
            )

            raise VectorDatabaseError(
                f"Failed to create collection "
                f"'{collection_name}'."
            ) from exc

    def get_collections(self) -> list[str]:
            """
            Return all collection names.
            """

            try:
                response = self.client.get_collections()

                return [
                    collection.name
                    for collection in response.collections
                ]

            except Exception as exc:
                logger.exception(
                    "Failed to retrieve collections"
                )

                raise VectorDatabaseError(
                    "Failed to retrieve collections."
                ) from exc

    def delete_collection(
            self,
            collection_name: str = COLLECTION_NAME,
        ) -> None:
            """
            Delete a collection.
            """

            try:
                self.client.delete_collection(
                    collection_name=collection_name
                )

                logger.info(
                    "Deleted collection '%s'",
                    collection_name,
                )

            except Exception as exc:
                logger.exception(
                    "Failed to delete collection"
                )

                raise VectorDatabaseError(
                    f"Failed to delete collection "
                    f"'{collection_name}'."
                ) from exc

    def close(self) -> None:
            """
            Close the Qdrant client.
            """

            self.client.close()