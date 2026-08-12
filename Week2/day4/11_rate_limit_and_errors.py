"""
Handling Errors and Rate Limits (via OpenRouter)

Free-tier APIs have rate limits (e.g. "20 requests per minute"). Real
applications need to handle failures gracefully instead of crashing --
catching specific error types and deciding what to do (retry? wait?
give up with a clear message?).

"""

import os
from openai import OpenAI, RateLimitError, APIError
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)

SYSTEM_PROMPT="Answer directly and concisely. Do not show your reasoning or thinking process."

def ask_with_retry(prompt, max_retries=3, delay_second=5):
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content
            
        except RateLimitError:
            print(f"Rate limit reached. Retrying in {delay_second} seconds...")
            time.sleep(delay_second)
            
        except APIError as e:
            print(f"API error occurred: {str(e)}")
            return None
        
    print(f"Gave up after {max_retries} attempts.")
    return None

if __name__ == "__main__":
    result = ask_with_retry("What is the boiling point of water in Celsius?")
    print("Final result:", result)