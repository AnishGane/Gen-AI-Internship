from qdrant_client import QdrantClient
from Week8.config import settings

def test_qdrant_setup():
    print("QDRANT_URL: ", settings.qdrant_url)
    print("QDRANT_API_KEY loaded:", bool(settings.qdrant_api_key))

    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key
    )

    collections = client.get_collections()

    print("Collections:", collections)