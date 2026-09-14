def main():
    print("=" * 8)
    print("VECTOR DATABASE CONCEPT")
    print("=" * 8)

    print("\n1. Vector")
    print("A vector is a list of numbers representing the meaning of data.")

    print("\nExample:")
    print("[0.12, -0.45, 0.78, 0.21, ...]")

    print("\n2. Embedding")
    print("An embedding model converts text into a vector.")

    print("\nExample:")
    print('"Python is a programming language"')
    print("              |")
    print("         Embedding Model")
    print("              |")
    print("      [0.12, -0.45, 0.78, ...]")

    print("\n3. Vector Database")
    print("A vector database stores vectors and allows efficient similarity search.")

    print("\n4. Collection")
    print("A collection is similar to a table in a traditional database.")
    print("It stores vectors with the same configuration.")

    print("\n5. Payload")
    print("Payload contains additional information associated with a vector.")

    print("\nExample payload:")
    print(
        {
            "text": "Python is a programming language.",
            "source": "python.txt",
            "chunk_id": 0,
        }
    )

    print("\n6. Similarity Search")
    print("Similarity search finds vectors that are most similar to a query vector.")

    print("\n7. Top-K")
    print("Top-K means returning the K most relevant results.")

    print("\n" + "=" * 8)
    print("WEEK 6 VECTOR DATABASE FLOW")
    print("=" * 8)

    print(
        """
            Document
                |
            Chunking
                |
            Embedding Model
                |
            Vector
                |
            Qdrant
                |
            Vector Search
                |
            Top-K Relevant Chunks
        """
    )

if __name__ == "__main__":
    main()