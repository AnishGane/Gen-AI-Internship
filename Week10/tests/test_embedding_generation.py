from Week10.core.llm import get_embeddings

def test_embedding_generation():
    embeddings = get_embeddings()

    vector = embeddings.embed_query(
        "React is a JavaScript library."
    )

    assert isinstance(vector, list)
    assert len(vector) == 2048
    assert all(isinstance(value, (int, float)) for value in vector)

    print("\nEmbedding generated successfully!")
    print("Dimensions:", len(vector))

def test_batch_embedding_generation():
    embeddings = get_embeddings()

    texts = [
        "React is a JavaScript library for building user interfaces.",
        "Python is a popular programming language.",
    ]

    vectors = embeddings.embed_documents(texts)

    assert len(vectors) == len(texts)
    assert all(len(vector) == 2048 for vector in vectors)

    print("\nBatch embedding generation successful!")
    print("Documents:", len(vectors))
    print("Dimensions:", len(vectors[0]))
