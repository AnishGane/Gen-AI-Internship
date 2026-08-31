"""
Ranking a List of Candidates by Similarity to a Query

The actual practical use of cosine similarity: given one query and a list of candidate sentences, compute similarity for EACH candidate, then sort them from most to least similar. This is the core operation underneath every semantic search system.
"""

import os
from openai import OpenAI
from Week5.config import API_KEY, BASE_URL, EMBEDDING_MODEL

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

CANDIDATES = [
    "The Eiffel Tower is located in Paris, France.",
    "Mount Everest is the tallest mountain on Earth.",
    "The Great Wall of China stretches thousands of kilometers.",
    "Paris is known for its art museums and cafes.",
    "The stock market had a volatile trading session.",
]

def get_embeddings_batch(texts):
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts, encoding_format="float")
    return [item.embedding for item in response.data]

def cosine_similarity(vec_a, vec_b):
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = sum(a ** 2 for a in vec_a) ** 0.5
    mag_b = sum(b ** 2 for b in vec_b) ** 0.5
    return dot / (mag_a * mag_b) if mag_a and mag_b else 0.0

def rank_by_similarity(query, candidates):
    all_texts = [query] + candidates
    all_vectors = get_embeddings_batch(all_texts)
    query_vector, candidate_vectors = all_vectors[0], all_vectors[1:]

    scored = [
        (candidate, cosine_similarity(query_vector, vec))
        for candidate, vec in zip(candidates, candidate_vectors)
    ]
    return sorted(scored, key=lambda pair: pair[1], reverse=True)

if __name__ == "__main__":
    query = "Tell me about famous landmarks in France."
    ranked_results = rank_by_similarity(query, CANDIDATES)

    print(f"Query: {query}\n")
    print("Ranked results (most to least similar):")
    for rank, (candidate, score) in enumerate(ranked_results, start=1):
        print(f"{rank}. [{score:.4f}] {candidate}")