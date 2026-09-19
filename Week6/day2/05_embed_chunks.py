from Week6.chunking import chunk_text
from Week6.embeddings import EmbeddingService
from Week6.utils import load_documents

def main():
    chunks = load_documents()

    print(f"Loaded {len(chunks)} chunks.")

    embedding_service = EmbeddingService()

    texts = [
        chunk.text
        for chunk in chunks
    ]
    
    print("\nTEXT: ", texts)

    embeddings = embedding_service.embed_batch(
        texts
    )

    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):

        print("\n" + "=" * 50)

        print(f"Chunk: {index}")
        print(f"Source: {chunk.source}")
        print(f"Text: {chunk.text}")
        print(f"Vector size: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
    
if __name__ == "__main__":
    main()