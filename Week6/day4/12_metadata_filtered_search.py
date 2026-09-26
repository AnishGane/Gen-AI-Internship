from Week6.qdrant_client import QdrantService
from Week6.config import QDRANT_PATH
from Week6.embeddings import EmbeddingService

def main():
    qdrant = QdrantService(path=str(QDRANT_PATH))
    
    query = "How is React used?"

    query_vector = EmbeddingService().embed_text(query)
    
    source = "React.txt"
    
    results = qdrant.search_qdrant(query_vector, limit=5, source=source)
    
    for result in results:
        # Grab the payload dictionary from the ScoredPoint object
        payload = result.payload or {}
        
        # Print fields directly from the object (.score) or payload dict
        print(f"Score: {result.score:.4f}")
        print(f"Source: {payload.get('source')}")
        print(f"Chunk ID: {payload.get('chunk_id')}")
        print(f"Text: {payload.get('text')}")
        print("-" * 20)  # Separator line for readability
    
if __name__ == "__main__":
    main()