from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from Week10.config import settings
from Week10.core.llm import get_embeddings

def test_dqrant_vectorstore_connection():
    client = QdrantClient(
        url = settings.qdrant_url,
        api_key = settings.qdrant_api_key
    )

    collection_name = settings.collection_name

    assert client.collection_exists(collection_name), (
        f"Collection '{collection_name}' does not exist"
    )

     # Initialize LangChain vector store
    store = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=get_embeddings(),
        content_payload_key=settings.qdrant_content_key,
    )

    assert isinstance(store, QdrantVectorStore)

    print("QdrantVectorStore initialized successfully!")

    client.close()