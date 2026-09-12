import json
from pathlib import Path

from openai import OpenAI

from Week5.config import (
    API_KEY,
    BASE_URL,
    EMBEDDING_MODEL,
)


client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)


EMBEDDINGS_FILE = (
    Path(__file__).parent.parent
    / "day4"
    / "embeddings.json"
)


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

    magnitude_a = sum(
        x ** 2
        for x in a
    ) ** 0.5

    magnitude_b = sum(
        x ** 2
        for x in b
    ) ** 0.5

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot / (
        magnitude_a * magnitude_b
    )


def load_embeddings():
    with open(
        EMBEDDINGS_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def semantic_search(
    query,
    documents,
    top_k=3,
):
    query_vector = get_embedding(query)

    scored_documents = []

    for document in documents:
        score = cosine_similarity(
            query_vector,
            document["embedding"],
        )

        scored_documents.append(
            {
                "text": document["text"],
                "score": score,
            }
        )

    scored_documents.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return scored_documents[:top_k]


def main():
    documents = load_embeddings()

    print("=" * 60)
    print("             WEEK 5 SEMANTIC SEARCH")
    print("=" * 60)

    while True:
        query = input(
            "\nEnter search query "
            "(type 'exit' to quit): "
        ).strip()

        if query.lower() == "exit":
            break

        if not query:
            continue

        results = semantic_search(
            query,
            documents,
            top_k=3,
        )

        print("\nMost Relevant Results:\n")

        for rank, result in enumerate(
            results,
            start=1,
        ):
            print(
                f"{rank}. "
                f"Similarity: "
                f"{result['score']:.4f}"
            )

            print(
                f"   {result['text']}\n"
            )


if __name__ == "__main__":
    main()