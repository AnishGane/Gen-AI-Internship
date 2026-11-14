from uuid import uuid4

import pytest
from qdrant_client import QdrantClient
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore

from Week10.config import settings
from Week10.core.llm import get_embeddings

@pytest.fixture
def qdrant_client():
    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )

    yield client

    client.close()

def test_document_insertion(qdrant_client):
    collection_name = f"test_documents_{uuid4().hex[:12]}"

    documents = [
        Document(
            page_content="React is a JavaScript library for building user interfaces.",
            metadata={"source": "react.txt"},
        ),
        Document(
            page_content="Python is a popular programming language.",
            metadata={"source": "python.txt"},
        ),
    ]

    try:
        vector_store = QdrantVectorStore.from_documents(
            documents=documents,
            embedding=get_embeddings(),
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            collection_name=collection_name,
            content_payload_key=settings.qdrant_content_key,
        )

        assert qdrant_client.collection_exists(collection_name)

        points = qdrant_client.count(
            collection_name=collection_name,
            exact=True,
        )

        assert points.count == len(documents)

        print("\nDocuments inserted successfully!")
        print("Stored points:", points.count)

    finally:
        if qdrant_client.collection_exists(collection_name):
            qdrant_client.delete_collection(collection_name)
