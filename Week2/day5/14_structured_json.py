"""
Getting Structured (JSON) Output (via OpenRouter)

LLMs generate free-form text by default -- but real applications often need STRUCTURED data (a dict/JSON) they can actually use in code, not a paragraph a human has to read. You can steer a model toward valid JSON output by being explicit about the format in your prompt, and then parsing the result yourself.
"""

import os
from openai import OpenAI
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS
import json

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

SYSTEM_PROMPT = "Respond with ONLY valid JSON, no other text, no markdown formatting."

def get_structured_output(description):
    prompt = (
        f'Extract structured product information from the following text: "{description}"\n\n'
        'Respond with ONLY a JSON object in exactly this shape:\n'
        '{"name": "...", "price": <number>, "in_stock": true/false}'
    )

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    raw_text = response.choices[0].message.content

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        print("Model did not return valid JSON. Raw output was:")
        print(raw_text)
        parsed = None

    return parsed

if __name__ == "__main__":
    result = get_structured_output(
        "The Wireless Mouse costs $25.99 and is currently out of stock."
    )
    print("Parsed result:", result)
    if result:
        print("Type:", type(result))
        print("Just the price:", result.get("price"))