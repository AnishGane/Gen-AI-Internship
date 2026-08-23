"""
Positive vs. Negative (Counter-)Examples in Few-Shot Prompts

Week 2's few-shot example only showed CORRECT examples. You can also show what NOT to do -- explicitly labeled counter-examples -- which can help the model avoid a specific failure mode more directly than positive examples alone.
"""

import os
from openai import OpenAI
from Week2.config import API_KEY, BASE_URL, MODEL

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)

TASK_INPUT = "Write a product description for a reusable water bottle."

def ask(prompt, max_tokens = 200):
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content

if __name__ == "__main__":
    print("=== Positive examples only ===")
    positive_only_prompt = f"""Write product descriptions in this style:
    
        Example: "The ComfortGrip Mug keeps your coffee hot for 6 hours, with a
        non-slip handle that fits any hand size."

        Example: "The TrailPack Backpack has 12 pockets, is fully waterproof,
        and weighs under 1kg."

        Now write one for: {TASK_INPUT}"""
    print(ask(positive_only_prompt))

    print("\n=== Positive AND negative (counter-)examples ===")
    with_negative_prompt = f"""Write product descriptions in this style:

        GOOD: "The ComfortGrip Mug keeps your coffee hot for 6 hours, with a
        non-slip handle that fits any hand size."
        BAD (too vague, no specifics): "This mug is really great and comfortable
        and you will love it."

        GOOD: "The TrailPack Backpack has 12 pockets, is fully waterproof, and
        weighs under 1kg."
        BAD (too vague, no specifics): "This backpack is amazing and durable
        and perfect for any adventure."

        Now write one for: {TASK_INPUT}
        Avoid the vague, hype-heavy style shown in the BAD examples."""
    print(ask(with_negative_prompt))