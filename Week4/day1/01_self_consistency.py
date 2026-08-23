"""
Day1 - Advanced Prompting Techniques

Chain-of-thought (Week 2) asks the model to reason step by step once. Self-consistency goes further: run the SAME reasoning prompt multiple times (with some temperature so runs can actually differ), then take the MAJORITY answer across all runs. Trades more API calls for higher reliability on problems where the model sometimes slips.
"""

import os
from collections import Counter
from openai import OpenAI
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)

PROBLEM = (
    "A bookstore had 84 books. They sold 25% of them on Monday, then "
    "received a shipment of 40 more books. How many books do they have now?"
)
# Correct answer: 84 - 21 (25% of 84) + 40 = 103

N_SAMPLES = 5

def get_answer(problem):
    response = client.chat.completions.create(
        model = MODEL,
        max_tokens = MAX_TOKENS,
        temperature = 0.7,
        messages = [
            {"role": "system", "content": "Think through the problem step by step, then end your response with 'FINAL ANSWER: <number>'."},
            {"role": "user", "content": problem},
        ]
    )
    return response.choices[0].message.content

def extract_final_answer(response):
    if not response or "FINAL ANSWER:" not in response:
        return None
    tail = response.split("FINAL ANSWER:")[-1].strip()
    # print("===TAIL===", tail)
    first_token = tail.split()[0] if tail.split() else ""
    # print("===FIRST TOKEN===", first_token)
    digits = "".join(ch for ch in first_token if ch.isdigit())
    # print("===DIGITS===", digits)
    return digits or None

if __name__ == "__main__":
    answers = []
    for i in range(N_SAMPLES):
        full_response = get_answer(PROBLEM)
        # print("===FULL RESPONSE===", full_response)
        answer = extract_final_answer(full_response)
        print(f"Run {i+1}: extracted answer = {answer}")
        if answer:
            answers.append(answer)

    if answers:
        vote_counts = Counter(answers)
        majority_answer, count = vote_counts.most_common(1)[0]
        print(f"\nMajority answer: {majority_answer} ({count}/{len(answers)} runs agreed)")
    else:
        print("\nNo valid answers extracted.")