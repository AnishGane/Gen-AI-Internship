"""
Batch Embedding Multiple Sentences at Once

Calling the API once per sentence in a loop works, but embedding APIs support sending a LIST of texts in one request -- much more efficient (fewer round trips) when you have many sentences to embed, like a dataset for semantic search.
"""

import os
from openai import OpenAI
from Week5.config import API_KEY, BASE_URL, EMBEDDING_MODEL

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

SENTENCES = [
    "The cat sat on the mat.",
    "A dog was resting on the rug.",
    "The stock market fell sharply today.",
    "Investors reacted to the earnings report.",
    "She baked a chocolate cake for the party.",
]

def get_embeddings_batch(texts):
    """Send a LIST of texts in one call, get back a list of vectors in the same order."""
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts, encoding_format="float")
    return [item.embedding for item in response.data]

if __name__ == "__main__":
    vectors = get_embeddings_batch(SENTENCES)

    for sentence, vector in zip(SENTENCES, vectors):
        print(f"'{sentence}' -> {len(vector)} dimensions, first 3 values: {vector[:3]}")
