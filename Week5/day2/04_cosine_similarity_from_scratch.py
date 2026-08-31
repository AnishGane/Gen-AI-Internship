"""
Cosine Similarity, Implemented from Scratch

Cosine similarity measures the ANGLE between two vectors, ignoring their magnitude (length). This matters because a longer sentence might produce a "bigger" vector than a short one even if they mean similar things -- raw dot product can be skewed by vector length, but cosine similarity isn't.

Formula: cosine_similarity(A, B) = (A . B) / (||A|| * ||B||)
    where A . B is the dot product, and ||A|| is the vector's magnitude
    (square root of the sum of squares).

Result ranges from -1 (opposite meaning) to 1 (identical meaning), with 0 meaning unrelated/orthogonal.
"""

import os
import math
from openai import OpenAI
from Week5.config import API_KEY, BASE_URL, EMBEDDING_MODEL

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

def get_embedding(text):
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=text, encoding_format="float")
    return response.data[0].embedding

def magnitude(vec):
    return math.sqrt(sum(x ** 2 for x in vec))

def cosine_similarity(vec_a, vec_b):
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = magnitude(vec_a)
    mag_b = magnitude(vec_b)
    if mag_a == 0 or mag_b == 0:
        return 0.0  # avoid division by zero for an all-zero vector
    return dot / (mag_a * mag_b)

if __name__ == "__main__":
    pairs = [
        ("I love going for a run in the morning.", "Jogging early in the day is my favorite exercise."),
        ("I love going for a run in the morning.", "The recipe calls for two cups of flour and one egg."),
        ("I love going for a run in the morning.", "I love going for a run in the morning."),  # identical
    ]

    for text_a, text_b in pairs:
        vec_a = get_embedding(text_a)
        vec_b = get_embedding(text_b)
        similarity = cosine_similarity(vec_a, vec_b)
        print(f"'{text_a[:40]}...' vs '{text_b[:40]}...'")
        print(f"  Cosine similarity: {similarity:.4f}\n")