"""
Your First Embedding Call (via OpenRouter)

An embedding is a list of numbers (a vector) that represents the MEANING of a piece of text. Unlike a chat completion, an embedding call doesn't generate new text -- it converts input text into a fixed-length numeric representation you can do math on.
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

if __name__ == "__main__":
    text = "The cat sat on the mat."
    vector = get_embedding(text)

    print(f"Text: {text}")
    print(f"Embedding length (dimensions): {len(vector)}")
    print(f"First 5 values: {vector[:5]}")
    print(f"Data type of a single value: {type(vector[0])}")