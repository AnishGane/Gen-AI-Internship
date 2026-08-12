"""
Multi-turn Conversations and Memory (via OpenRouter)

The API is STATELESS. The model has no memory of past calls unless
YOU resend the full conversation history every single time. Chat apps
"remember" you purely by re-sending everything said so far as part of
the `messages` list on each request.

"""

import os
from openai import OpenAI
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

def ask(messages: list):
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=messages
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    print("=== WITHOUT memory: two separate, unrelated calls ===")
    print("Turn 1:", ask([{"role": "user", "content": "My name is Anish Gane."}]))

    # Fresh call, no history included
    print("Turn 2 (no history sent):", ask([{"role": "user", "content": "What is my name?"}]))

    print("\n=== WITH memory: full history re-sent every call ===")
    history = [{"role": "system", "content": "Answer directly, without showing reasoning."}]
    
    history.append({"role": "user", "content": "My name is Anish Gane."})
    reply = ask(history)
    print("Turn 1:", reply)
    history.append({"role": "assistant", "content": reply})  # save the model's own reply too

    history.append({"role": "user", "content": "What is my name?"})
    reply = ask(history)
    print("Turn 2 (history sent):", reply)
    history.append({"role": "assistant", "content": reply})