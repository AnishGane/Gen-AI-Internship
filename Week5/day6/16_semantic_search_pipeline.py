import json

from openai import OpenAI

from Week5.config import API_KEY, BASE_URL, EMBEDDING_MODEL

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)

DATA_FILE = "Week5/day4/embeddings.json"

def get_embedding(text):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
        encoding_format="float",
    )

    return response.data[0].embedding

def cosine_similarity(a, b):
    dot = sum(
        x * y
        for x, y in zip(a, b)
    )

    mag_a = sum(
        x ** 2
        for x in a
    ) ** 0.5

    mag_b = sum(
        x ** 2
        for x in b
    ) ** 0.5

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot / (mag_a * mag_b)

def load_documents():
    with open(
        DATA_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)
    
def search(query, documents, top_k=3):
    query_vector = get_embedding(query)

    results = []

    for document in documents:
        score = cosine_similarity(
            query_vector,
            document["embedding"],
        )

        results.append(
            {
                "text": document["text"],
                "score": score,
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:top_k]

if __name__ == "__main__":
    documents = load_documents()

    query = "How is Python useful in AI?"

    results = search(
        query,
        documents,
        top_k=3,
    )

    print(f"Query: {query}\n")

    for rank, result in enumerate(
        results,
        start=1,
    ):
        print(
            f"{rank}. "
            f"[{result['score']:.4f}] "
            f"{result['text']}"
        )