"""
Cosine Similarity vs. Euclidean Distance vs. Dot Product

There are multiple ways to compare vectors. This script computes all three on the SAME pairs so you can see how they can disagree, and why cosine similarity is the standard choice for embeddings specifically (it's insensitive to vector magnitude, which dot product and Euclidean distance are not).
"""

import os
import numpy as np
from openai import OpenAI
from Week5.config import API_KEY, BASE_URL, EMBEDDING_MODEL

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

def get_embedding(text):
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=text, encoding_format="float")
    return np.array(response.data[0].embedding)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def euclidean_distance(a, b):
    return np.linalg.norm(a - b)  # lower = more similar (opposite direction from the other two!)

def dot_product(a, b):
    return np.dot(a, b)

if __name__ == "__main__":
    anchor_text = "The weather is sunny and warm today."
    candidates = [
        "It's a bright, hot day outside.",
        "The stock price dropped after the announcement.",
        "The weather is sunny and warm today.",  # identical
    ]
    
    anchor_vec = get_embedding(anchor_text)

    print(f"Anchor: '{anchor_text}'\n")
    for candidate in candidates:
        vec = get_embedding(candidate)
        cos = cosine_similarity(anchor_vec, vec)
        euc = euclidean_distance(anchor_vec, vec)
        dot = dot_product(anchor_vec, vec)

        print(f"Candidate: '{candidate}'")
        print(f"  Cosine similarity (higher = more similar): {cos:.4f}")
        print(f"  Euclidean distance (LOWER = more similar): {euc:.4f}")
        print(f"  Dot product:                                {dot:.4f}\n")
