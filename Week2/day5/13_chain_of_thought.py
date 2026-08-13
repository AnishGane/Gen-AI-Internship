"""
Direct Answer vs. Step-by-Step (Chain-of-Thought) (via OpenRouter)

Asking a model to "think step by step" before giving a final answer (chain-of-thought prompting) often improves accuracy on problems that need multiple reasoning steps, like math or logic puzzles -- because it gives the model room to work through intermediate steps rather than jumping straight to a guess.
"""

import os
from openai import OpenAI
from Week2.config import API_KEY, BASE_URL, MODEL

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

PROBLEM = (
    "A store had 120 apples. It sold 35% of them in the morning and "
    "then sold 28 more in the afternoon. How many apples are left?"
)

def ask(prompt, max_tokens=300):
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content

if __name__ == "__main__":
    print("=== Direct answer only ===")
    direct = ask(f"{PROBLEM} Answer with just the final number, nothing else.", max_tokens=20)
    print(direct)

    print("\n=== Step-by-step (chain-of-thought) ===")
    step_by_step = ask(f"{PROBLEM} Think through it step by step, then give the final answer.")
    print(step_by_step)