from openai import OpenAI
from Week5.config import API_KEY, BASE_URL, EMBEDDING_MODEL

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

DOCUMENTS = [
    "Python is a popular programming language used for AI.",
    "Machine learning allows computers to learn patterns from data.",
    "React is used to build interactive web interfaces.",
    "PostgreSQL is a relational database management system.",
    "Docker runs applications inside isolated containers.",
]

def get_embeddings(texts):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
        encoding_format="float",
    )

    return [item.embedding for item in response.data]

def cosine_similarity(vec_a, vec_b):
    dot = sum(a * b for a, b in zip(vec_a, vec_b))

    mag_a = sum(x ** 2 for x in vec_a) ** 0.5
    mag_b = sum(x ** 2 for x in vec_b) ** 0.5

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot / (mag_a * mag_b)

def semantic_search(query, documents):
    vectors = get_embeddings([query] + documents)

    query_vector = vectors[0]
    document_vectors = vectors[1:]

    results = []

    for document, vector in zip(documents, document_vectors):
        score = cosine_similarity(
            query_vector,
            vector,
        )

        results.append((document, score))

    return sorted(
        results,
        key=lambda item: item[1],
        reverse=True,
    )

if __name__ == "__main__":
    query = "How can I learn artificial intelligence programming?"

    results = semantic_search(
        query,
        DOCUMENTS,
    )

    print(f"Query: {query}\n")

    for rank, (document, score) in enumerate(results, start=1):
        print(f"{rank}. [{score:.4f}] {document}")