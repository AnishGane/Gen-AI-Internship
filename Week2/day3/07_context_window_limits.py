"""
Hitting Context/Output Limits on Purpose (via OpenRouter)

`max_tokens` caps how many tokens the model is ALLOWED to generate in
its reply. If the model wants to say more than that, it gets cut off
mid-thought -- and `finish_reason` tells you this happened: "stop"
means it finished naturally, "length" means it got cut off by the cap.

This matters because the context window is a hard ceiling: prompt
tokens + completion tokens must fit within the model's total limit.
"""

import os
from openai import OpenAI
from Week2.config import API_KEY, BASE_URL, MODEL

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

PROMPT = "Explain how photosynthesis works, in detail, step by step."
SYSTEM_PROMPT = "Answer directly and concisely. Do not show your reasoning or thinking process."

def ask_with_budget(max_tokens):
    response = client.chat.completions.create(
        model = MODEL,
        max_tokens = max_tokens,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": PROMPT}
        ]
    )
    
    choice = response.choices[0]

    print(f"\n--- max_tokens = {max_tokens} ---")
    print(f"finish_reason: {choice.finish_reason}")
    print(f"completion_tokens used: {response.usage.completion_tokens}")
    print(f"Response: {choice.message.content}")
    
if __name__ == "__main__":
    ask_with_budget(max_tokens=8)
    ask_with_budget(max_tokens=40)
    ask_with_budget(max_tokens=400)
    
