from qdrant_client.models import PointStruct

from Week6.config import QDRANT_PATH
from Week6.chunking import chunk_text
from Week6.embeddings import EmbeddingService
from Week6.qdrant_client import QdrantService
from Week6.utils import load_documents
from Week6.logger import logger

def main():
    print("=" * 20)
    print("WEEK 6 - STORE DOCUMENT CHUNKS")
    print("=" * 20)

    # 1. Load and chunk documents
    chunks = load_documents()

    print(f"\nLoaded chunks: {len(chunks)}")
    
    print("\nChunks before embedding:")

    for index, chunk in enumerate(chunks):
        print("\n" + "=" * 50)
        print(f"Index: {index}")
        print(f"Source: {chunk.source}")
        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Text: {chunk.text}")

    if not chunks:
        logger.error("No chunks found. Please check your data.")
        return

    # 2. Generate embeddings
    embedding_service = EmbeddingService()

    texts = [
        chunk.text
        for chunk in chunks
    ]

    logger.info(
        "Generating embeddings..."
    )

    embeddings = embedding_service.embed_batch(
        texts
    )

    logger.info(
        "Generated embeddings: %d",
        len(embeddings)
    )
    
    # 3. Create Qdrant service
    qdrant = QdrantService(
        path=QDRANT_PATH
    )

    try:
        # 4. Determine vector dimension
        vector_size = len(embeddings[0])

        logger.info(
            "Vector dimension: %d",
            vector_size
        )

        # 5. Create a Collection
        qdrant.create_collection(
            vector_size=vector_size
        )

        # 6. Create Qdrant points
        points = []

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):

            point = PointStruct(
                id=index,
                vector=embedding,
                payload={
                    "text": chunk.text,
                    "source": chunk.source,
                    "chunk_id": chunk.chunk_id,
                },
            )

            points.append(point)

        # 7. Store points
        logger.info(
            "Storing %d points...",
            len(points)
        )
        
        qdrant.insert_points(points)

        count = qdrant.count_points()

        logger.info(
            "Points stored in Qdrant: %d",
            count
        )

        logger.info(
            "Stored %d points.",
            len(points)
        )

        stored_points = qdrant.get_points()

        logger.info(
            "Retrieved %d points.",
            len(stored_points)
        )
        
        for point in stored_points:
            print("\n" + "=" * 20)
            print(f"ID: {point.id}")
            print(f"Source: {point.payload.get('source')}")
            print(f"Chunk ID: {point.payload.get('chunk_id')}")
            print(f"Text: {point.payload.get('text')}")

    finally:
        qdrant.close()

if __name__ == "__main__":
    main()
