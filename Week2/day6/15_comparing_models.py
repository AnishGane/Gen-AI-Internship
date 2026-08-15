"""
Comparing Two Different Models Side-by-Side (via OpenRouter)

Not all models are equal -- different models (even both "free") vary in
reasoning ability, speed, verbosity, and reliability. Picking the right
model for a task is itself a real skill, not just an implementation detail.
"""

import os 
from openai import OpenAI
from Week2.config import API_KEY, BASE_URL, MAX_TOKENS

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

MODEL_A = "google/gemma-4-26b-a4b-it:free"
MODEL_B = "nvidia/nemotron-3.5-lightning:free"

PROMPT = "A farmer has 17 sheep. All but 9 die. How many sheep are left?"

def ask(model, prompt):
    response = client.chat.completions.create(
        model=model,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content

if __name__ == "__main__":
    print("=== Model A ===")
    print(ask(MODEL_A, PROMPT))

    print("\n=== Model B ===")
    print(ask(MODEL_B, PROMPT))



