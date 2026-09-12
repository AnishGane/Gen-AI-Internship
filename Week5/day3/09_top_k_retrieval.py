from openai import OpenAI
from Week5.config import API_KEY, BASE_URL, EMBEDDING_MODEL


client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)


DOCUMENTS = [
    "Python is a popular programming language used for AI.",
    "Machine learning allows computers to learn patterns from data.",
    "React is used to build interactive web interfaces.",
    "PostgreSQL is a relational database management system.",
    "Docker runs applications inside isolated containers.",
    "Deep learning uses neural networks to learn complex patterns.",
    "Git tracks changes in source code.",
]


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


def top_k_search(query, documents, k=3):
    vectors = get_embeddings([query] + documents)

    query_vector = vectors[0]
    document_vectors = vectors[1:]

    results = [
        (
            document,
            cosine_similarity(query_vector, vector),
        )
        for document, vector in zip(
            documents,
            document_vectors,
        )
    ]

    results.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    return results[:k]


if __name__ == "__main__":
    query = "How does machine learning work?"

    results = top_k_search(
        query,
        DOCUMENTS,
        k=3,
    )

    print(f"Query: {query}\n")
    print("Top 3 Results:\n")

    for rank, (document, score) in enumerate(results, start=1):
        print(f"{rank}. [{score:.4f}] {document}")