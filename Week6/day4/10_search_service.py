from Week6.search import SearchService

def main():
    service = SearchService()
    
    try:
        
        query = "Is Python a good programming language for AI?"
    
        results = service.search(query=query, limit=5)
    
        print("=" * 20)
        print("SEARCH SERVICE")
        print("=" * 20)

        print(f"\nQuery: {query}")

        for rank, result in enumerate(
            results,
            start=1,
        ):

            print("\n" + "=" * 50)

            print(f"Rank: {rank}")
            print(f"Score: {result.score:.4f}")
            print(f"Source: {result.source}")
            print(f"Chunk ID: {result.chunk_id}")
            print(f"Text: {result.text}")

    finally:
        service.close()
    
if __name__ == "__main__":
    main()