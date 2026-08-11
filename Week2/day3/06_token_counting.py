"""
Token Counting and Usage Inspection (via OpenRouter)

A "token" is the basic unit of text a model reads/generates -- roughly 3/4 of a word in English, though it varies. You don't have to guess: every API response includes exact token counts in `response.usage`.

WHAT THIS CODE DOES:
Compares a naive character-based token estimate against the REAL count the API reports, for prompts of different lengths.
"""

import os
from openai import OpenAI
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

SYSTEM_PROMPT = "Answer directly and concisely. Do not show your reasoning or thinking process."

def naive_token_estimate(text):
    """ 1 token per 4 char of English text (roughly) """
    return len(text) // 4

def report_tokens(label, prompt):
    response = client.chat.completions.create(
        model = MODEL,
        max_tokens = MAX_TOKENS,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    
    usage = response.usage
    
    print(f"\n=== {label} ===")
    print(f"Prompt length (characters): {len(prompt)}")
    print(f"Naive estimate (tokens):    {naive_token_estimate(prompt)}")
    print(f"Actual prompt tokens:       {usage.prompt_tokens}")
    print(f"Completion tokens:          {usage.completion_tokens}")
    print(f"Total tokens (this call):   {usage.total_tokens}")

if __name__ == "__main__":
    report_tokens("Short Prompt", "What is the capital of France?")

    report_tokens(
        "Medium prompt",
        "Summarize the following in one sentence: Large language models "
        "are trained on massive amounts of text data and learn statistical "
        "patterns in how language is used.",
    )
    
    long_text = "Large language models process text as tokens. " * 20
    report_tokens("Long, repetitive prompt", "Summarize this: " + long_text)