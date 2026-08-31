"""
Building Intuition: Similar vs. Different Meanings

Before learning the formal cosine similarity formula (Day 2), build intuition by directly comparing raw embedding vectors for sentences that mean similar things vs. sentences about unrelated topics -- using a simple dot product as a rough first signal.
"""

import os
from openai import OpenAI
from Week5.config import API_KEY, BASE_URL, EMBEDDING_MODEL

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

def get_embedding(text):
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=text, encoding_format="float")
    return response.data[0].embedding

def dot_product(vec_a, vec_b):
    return sum(a * b for a, b in zip(vec_a, vec_b))

if __name__ == "__main__":
    anchor = "I love going for a run in the morning."
    similar = "Jogging early in the day is my favorite exercise."
    different = "The recipe calls for two cups of flour and one egg."

    anchor_vec = get_embedding(anchor)
    similar_vec = get_embedding(similar)
    different_vec = get_embedding(different)

    print(f"Anchor: '{anchor}'")
    print(f"Similar meaning: '{similar}'")
    print(f"  Dot product with anchor: {dot_product(anchor_vec, similar_vec):.4f}")

    print(f"\nUnrelated meaning: '{different}'")
    print(f"  Dot product with anchor: {dot_product(anchor_vec, different_vec):.4f}")