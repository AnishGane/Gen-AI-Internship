"""
Streaming Response (via OpenRouter)

By default, an API call waits for the ENTIRE response to be generated
before returning anything -- for a long answer, you just stare at a
blank screen until it's all done. Streaming instead sends back small
chunks of the response AS they're generated, so you can print/display
text as it arrives (this is why ChatGPT-style UIs show text appearing
word by word instead of all at once).
"""

import os
from openai import OpenAI
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

PROMPT = "Write a short paragraph about why the sky is blue."
SYSTEM_PROMPT = "Answer directly and concisely. Do not show your reasoning or thinking process."

def ask_streaming(prompt):
    stream = client.chat.completions.create(
        model = MODEL,
        max_tokens = MAX_TOKENS,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        stream = True
    )
    
    full_response = ""

    for chunk in stream:
        full_response += chunk.choices[0].delta.content

    return full_response

if __name__ == "__main__":
    print("Streaming response:\n")
    result = ask_streaming(PROMPT)
    print("\n\n--- Full response collected ---")
    print(result)
