"""
Temperature Experiment (via OpenRouter)

- Temperature controls how the model samples it next word/token from its predicted probabilties.
    - temperature = 0.0 -> nearly always picks the single most likely token -> repeatable, focuses, "safe" outptu
    - temperature = 1.0 -> more varied, creative, sometimes less predictable

WHAT WE DO BELOW:
- Sends the SAME prompt twice at three different temperatures, so we can directly compare how repeatable (or not) the output is.

GOAL: 
- Send the SAME  prompt at different temperatures and observe how the output/response changes. Temperature controls the randomness:
    - Low (0.0)  -> focused, deterministic, repeatable answers
    - High (1.0) -> more varied, creative, sometimes less predictable
"""

import os
from openai import OpenAI
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

PROMPT = "Write a one-sentence tagline for a coffee shop."
TEMPERATURES = [0.0, 0.5, 1.0]
SYSTEM_INSTRUCTION="Answer directly and concisely. Do not show your reasoning or thinking process."

def ask_model(prompt, temperature):
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_INSTRUCTION
            },
            {
                "role": "user",
                "content": prompt
        }]
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    for temp in TEMPERATURES:
        print(f"\n --- Temperature: {temp} ---")

        # Run twice at the same temperature to see how repeatable it is
        for attempt in (1, 2):
            output = ask_model(PROMPT, temp)
            print(f"Attempt {attempt}: {output}")
            
# At temperature 0.0, both attempts should be identical or very close
# At temperature 1.0, the two attempts are more likely to differ