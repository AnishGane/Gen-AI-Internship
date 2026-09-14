from Week6.qdrant_client import QdrantService
from Week6.config import QDRANT_PATH

def create_qdrant_client() -> QdrantService:
    """
    Create a local Qdrant Client
    """
    
    return QdrantService(path = QDRANT_PATH)

def main():
    client = None

    try:
        client = create_qdrant_client()
        
        print("=" * 8)
        collections = client.get_collections()

        print(collections)
        print("=" * 8)

        print("\nQdrant client created successfully.")

        print(f"Storage path: {QDRANT_PATH}")

        if not collections:
            print("\nNo collections found.")

        else:
            print("\nAvailable collections:")

            for col in collections:
                print("-" + col)

    finally:
        if client: 
            client.close()

if __name__ == "__main__":
    main()
