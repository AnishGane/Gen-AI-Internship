"""
Zero-shot vs. Few-shot Prompting (via OpenRouter)

- Zero-shot: you ask the model to do a task with no examples, relying purely on its general training.
- Few-shot: you show the model a few example input/output pairs directly in the prompt before asking your real question -- "teaching by example" within a single request.

Few-shot often produces more consistent formatting and better accuracy on tasks where the exact desired output style matters.
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
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "user", "content": prompt}
        ])

    return response.choices[0].message.content

if __name__ == "__main__":
    print("=== Zero-shot ===")
    zero_shot = ask("Classify the sentiment: 'The delivery was three days late.'")
    print(zero_shot)
    
    print("\n=== Few-shot (with examples first) ===")
    few_shot_prompt = """Classify the sentiment as Positive, Negative, or Neutral. Respond with just the single word.

    Text: "I loved this product!"
    Sentiment: Positive

    Text: "It broke after one use."
    Sentiment: Negative

    Text: "It arrived on time."
    Sentiment: Neutral

    Text: "The delivery was three days late."
    Sentiment:"""
    
    few_shot = ask(few_shot_prompt)
    print(few_shot)