"""
Prompt Version Comparison Harness (via OpenRouter)

When iterating on prompt wording, you want a repeatable way to compare "version A" vs "version B" across multiple inputs, not just eyeball one example. Combines Week 3's LLM-as-judge idea with a small harness that runs both versions and tallies which the judge preferred.
"""

import os
from openai import OpenAI
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

def ask(prompt):
    response = client.chat.completions.create(
        model = MODEL,
        max_tokens = MAX_TOKENS,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content    

def prompt_v1(text):
    return f"Summarize this: {text}"

def prompt_v2(text):
    return (
        f"Summarize the following text in exactly one clear, specific sentence. "
        f"Avoid vague phrases like 'discusses various topics'.\n\nText: {text}"
    )

def judge_preference(text, summary_a, summary_b):
    judge_prompt = f"""Original text: {text}

Summary A: {summary_a}
Summary B: {summary_b}

Which summary is more specific and useful -- A or B? Answer with ONLY
the single letter A or B."""

    verdict = ask(judge_prompt)
    return verdict.strip().upper()[:1] if verdict else None

TEST_INPUTS = [
    "The company reported strong revenue growth this quarter driven by international expansion, though profit margins narrowed due to rising shipping costs.",
    "Local officials announced a new recycling program starting next month, aiming to reduce landfill waste by encouraging residents to sort materials at curbside bins.",
]

if __name__ == "__main__":
    v1_wins = 0
    v2_wins = 0

    for text in TEST_INPUTS:
        summary_a = ask(prompt_v1(text))
        summary_b = ask(prompt_v2(text))
        winner = judge_preference(text, summary_a, summary_b)

        print(f"\nText: {text[:60]}...")
        print(f"  V1: {summary_a}")
        print(f"  V2: {summary_b}")
        print(f"  Judge preferred: {winner}")

        if winner == "A":
            v1_wins += 1
        elif winner == "B":
            v2_wins += 1
            
    print(f"\n=== Final tally: V1 wins={v1_wins}, V2 wins={v2_wins} ===")