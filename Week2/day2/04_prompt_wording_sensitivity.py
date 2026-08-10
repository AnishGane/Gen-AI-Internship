"""
How Wording Changes the Output given by the LLMs (via OpenRouter)

LLMs are sensitive to exactly how a question is phrased -- not just WHAT you ask, but HOW. Vague instructions get vague, generic answers. Specific instructions (with format, constraints, or length) get more usable, structured answers.

WHAT THIS CODE DOES:
Sends a vague version and a specific version of essentially the same request, so you can compare the actual difference in usefulness.
"""

import os
from openai import OpenAI
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

SYSTEM_PROMPT = "Answer directly and concisely. Do not show your reasoning or thinking process."

def ask(prompt):
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    print("=== Vague prompt ===")
    print(ask("Tell me about dogs."))
    
    print("\n=== Specific prompt ===")
    print(ask(
        "List 3 dog breeds well-suited to apartment living. "
        "For each, give a one-line reason. Format as a numbered list. "
        "Do not include any other text."
    ))
    
    print("\n\n=== Open-ended prompt ===")
    print(ask("How should I price my product?"))
    
    print("\n=== Constrained prompt (same underlying question) ===")
    print(ask(
        "I sell handmade candles, cost $4 each to make, competitors sell "
        "similar candles for $12-$18. Suggest ONE specific price and a "
        "one-sentence justification. Answer in under 40 words."
    ))    