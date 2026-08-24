"""
Structured Output Validated with Pydantic (via OpenRouter)

json.loads() only confirms text IS valid JSON, not that it has the RIGHT SHAPE (right fields, right types). Pydantic defines a schema once, then validates AND parses in one step, raising a clear error if a field is missing or the wrong type.
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

def extract_product_info(description):
    prompt = (
        f'Extract structured product info from: "{description}"\n\n'
        'Respond with ONLY a JSON object: {"name": "...", "price": <number>, "in_stock": true/false}'
    )

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": "Respond with ONLY valid JSON, no other text, no markdown formatting."},
            {"role": "user", "content": prompt},
        ],
    )
    raw_text = response.choices[0].message.content

    try:
        raw_dict = json.loads(raw_text)
    except json.JSONDecodeError:
        print("Model did not return valid JSON. Raw output was:")
        print(raw_text)
        return None

    try:
        return ProductInfo(**raw_dict)
    except ValidationError:
        print("Model returned invalid JSON. Raw output was:")
        print(raw_text)
        return None

if __name__ == "__main__":
    result = extract_product_info("The Wireless Mouse costs $25.99 and is currently out of stock.")
    if result:
        print("Validated result:", result)
        print("Type:", type(result))
        print("Price (as a real float):", result.price)