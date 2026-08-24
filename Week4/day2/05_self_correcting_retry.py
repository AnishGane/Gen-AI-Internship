"""
Self-Correcting Retry Loop for Invalid Output (via OpenRouter)

Instead of giving up when validation fails, feed the VALIDATION ERROR back to the model and ask it to fix its own output. A common pattern for improving structured-output reliability without just hoping the first attempt is correct.
"""

import os
import json
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)

class ProductInfo(BaseModel):
    name: str
    price: float
    in_stock: bool

MAX_ATTEMPTS = 3

def extract_with_retry(description):
    messages = [
        {"role": "system", "content": "Respond with ONLY valid JSON, no other text, no markdown formatting."},
        {"role": "user", "content": (
            f'Extract structured product info from: "{description}"\n\n'
            'Respond with ONLY a JSON object: {"name": "...", "price": <number>, "in_stock": true/false}'
        )},
    ]

    for attempt in range(1, MAX_ATTEMPTS + 1):
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=messages,
        )
        raw_text = response.choices[0].message.content
        messages.append({"role": "assistant", "content": raw_text})

        try:
            raw_dict = json.loads(raw_text)
            product = ProductInfo(**raw_dict)
            print(f"Attempt {attempt}: succeeded.")
            return product
        except (json.JSONDecoderError, ValidationError) as e:
            print(f"Attempt {attempt}: failed validation -- {e}")
            if attempt < MAX_ATTEMPTS:
                messages.append({
                    "role": "user",
                    "content": f"That response was invalid: {e}. Please respond again with ONLY the corrected JSON object, matching the required shape exactly.",
                })
    print("Gave up after max attempts.")
    return None

if __name__ == "__main__":
    result = extract_with_retry("The Wireless Mouse costs twenty-five dollars and is out of stock.")
    if result:
        print("\nFinal validated result:", result)