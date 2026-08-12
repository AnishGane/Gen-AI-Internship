"""
Managing Growing Conversation History (via OpenRouter) 

Every turn you keep in `history` gets resent on every future call --
so a long conversation costs more tokens each turn, and can eventually
exceed the context window. A common real-world fix: keep only the last
N messages ("sliding window") instead of the entire history.

WHAT THIS CODE DOES:
Simulates a growing conversation, shows prompt_tokens increasing each
turn, then demonstrates trimming the history to a fixed window size.
"""

import os
from openai import OpenAI
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

SYSTEM_PROMPT = "Answer in one short sentence, no reasoning shown."

MAX_HISTORY_MESSAGES = 4

def trim_history(history, keep_last = MAX_HISTORY_MESSAGES):
    system_msgs = [m for m in history if m["role"] == "system"]
    other_msgs = [m for m in history if m["role"] != "system"]
    return system_msgs + other_msgs[-keep_last:]

if __name__ == "__main__":
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    fake_turns = [
        "Tell me a fact about the ocean.",
        "Tell me a fact about space.",
        "Tell me a fact about volcanoes.",
        "Tell me a fact about the rainforest.",
        "Tell me a fact about deserts.",
    ]
    
    for i , user_msg in enumerate(fake_turns, start = 1):
        history.append({"role": "user", "content": user_msg})

        # trimmed before sending
        trimmed = trim_history(history)

        resp = client.chat.completions.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=trimmed
        )
        
        reply = resp.choices[0].message.content
        history.append({"role": "assistant", "content": reply})

        print(f"Turn {i}: prompt_tokens = {resp.usage.prompt_tokens}, "
            f"messages_sent={len(trimmed)}, full_history_len={len(history)}"
        )