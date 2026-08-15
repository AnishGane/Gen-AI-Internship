"""
Mini Project: Interactive Chatbot (via OpenRouter)

Combines everything from this week: multi-turn memory (Day 4),
configurable system prompt (Day 2), adjustable temperature (Day 1),
and visible token usage per turn (Day 3) -- into one working program.
"""

import os
from openai import OpenAI
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

def run_chatbot():
    print("=== Mini Chatbot ===")
    system_prompt = input("System Prompt (Enter for default): ").strip()
    
    if not system_prompt:
        system_prompt = "You are a helpful, concise assistant. Answer directly without showing reasoning."

    temp_input = input("Enter Temperature 0.0 - 1.0 (Enter for 0.7): ").strip()
    temperature = float(temp_input) if temp_input else 0.7
    
    history = [{"role": "system", "content": system_prompt}]
    total_tokens_used = 0
    
    print("\nChat started. Type 'quit' to exit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "quit":
            break
        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=temperature,
            messages=history,
        )
        reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": reply})

        total_tokens_used += response.usage.total_tokens
        print(f"Bot: {reply}")
        print(f"   [turn: {response.usage.total_tokens} tokens | session total: {total_tokens_used}]\n")
        
    print(f"\nSession ended. Total tokens used: {total_tokens_used}")
    return history  # handed off to Task 2 for saving

if __name__ == "__main__":    
    run_chatbot()