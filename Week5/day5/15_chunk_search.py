from openai import OpenAI

from Week5.config import API_KEY, BASE_URL, EMBEDDING_MODEL

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)

def chunk_text(
    text,
    chunk_size=50,
    overlap=10,
):
    words = text.split()

    step = chunk_size - overlap

    chunks = []

    for start in range(
        0,
        len(words),
        step,
    ):
        chunk = " ".join(
            words[start:start + chunk_size]
        )

        if chunk:
            chunks.append(chunk)

    return chunks

def get_embeddings(texts):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
        encoding_format="float",
    )

    return [item.embedding for item in response.data]


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))

    mag_a = sum(x ** 2 for x in a) ** 0.5
    mag_b = sum(x ** 2 for x in b) ** 0.5

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot / (mag_a * mag_b)

def search_chunks(query, chunks, top_k=3):
    vectors = get_embeddings(
        [query] + chunks
    )

    query_vector = vectors[0]

    results = []

    for chunk, vector in zip(
        chunks,
        vectors[1:],
    ):
        score = cosine_similarity(
            query_vector,
            vector,
        )

        results.append(
            {
                "chunk": chunk,
                "score": score,
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:top_k]

if __name__ == "__main__":
    document = """
    Python is a popular programming language.
    Python is used in web development.
    Python is widely used in data science.
    Machine learning uses algorithms to learn patterns.
    Deep learning uses neural networks.
    React is used for building user interfaces.
    PostgreSQL is a relational database.
    Docker provides application containers.
    """

    chunks = chunk_text(
        document,
        chunk_size=20,
        overlap=5,
    )

    query = "What is Python used for?"

    results = search_chunks(
        query,
        chunks,
        top_k=3,
    )

    print(f"Query: {query}\n")

    for rank, result in enumerate(results, start=1):
        print(
            f"{rank}. "
            f"[{result['score']:.4f}]"
        )
        print(result["chunk"])
        print()