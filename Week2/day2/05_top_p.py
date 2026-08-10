"""
top_p / Nucleus Sampling (via OpenRouter)

Along with `temperature` that controls the randomness, `top_p` (nucleus sampling) works differently: instead of scaling ALL probabilties, it restricts the model to choosing only from the smallest set of tokens whose combined probabilty adds up to `top_p`.

    - top_p = 1.0 -> conside almost all possible next tokens
    - top_p = 0.1 -> only consider the tiny handful of tokens that makes up the top 10% of probability -> very focused.
    
In practice, most APIs recommend adjusting EITHER temperature OR top_p, not both at once -- this exercise is about seeing top_p's effect in isolation, with temperature left at its default.

"""

import os
from Week2.config import API_KEY, MODEL, MAX_TOKENS, BASE_URL
from openai import OpenAI

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

PROMPT = "Suggest a name for a new podcast about science for beginners."
SYSTEM_PROMPT = "Answer directly and concisely. Do not show your reasoning or thinking process."

TOP_P_VALUES = [0.1, 0.45, 1.0]

def ask_model(prompt, top_p):
    response = client.chat.completions.create(
        model = MODEL,
        max_tokens = MAX_TOKENS,
        top_p = top_p,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    for p in TOP_P_VALUES:
        print(f"\n --- top_p: {p} ---")
        print(f"Response: {ask_model(PROMPT, p)}")