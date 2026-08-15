"""
Chatbot with Session Logging to JSON (via OpenRouter)

Ties back to Week 1's file-handling skills: instead of losing the conversation when the program exits, save it to a JSON file so it can be reloaded, reviewed, or analyzed later.
"""

import os
import json
from datetime import datetime
from openai import OpenAI
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

LOG_DIR = os.path.join(os.path.dirname(__file__), "chat_logs")
os.makedirs(LOG_DIR, exist_ok=True)

def save_session(history, total_tokens):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(LOG_DIR, f"session_{timestamp}.json")
    with open(filepath, "w") as f:
        json.dump({"history": history, "total_tokens": total_tokens}, f, indent=2)
    return filepath

def run_chatbot():
    print("=== Chatbot with Logging ===")
    history = [{"role": "system", "content": "You are a helpful, concise assistant."}]
    total_tokens_used = 0

    print("Chat started. Type 'quit' to exit and save.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "quit":
            break
        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})
        response = client.chat.completions.create(model=MODEL, max_tokens=MAX_TOKENS, messages=history)
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})

        total_tokens_used += response.usage.total_tokens
        print(f"Bot: {reply}\n")

    filepath = save_session(history, total_tokens_used)
    print(f"Session saved to: {filepath}")


if __name__ == "__main__":
    run_chatbot()