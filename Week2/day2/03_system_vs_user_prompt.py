"""
SYSTEM PROMPT vs USER PROMPT (via OpenRouter)
System Prompt: sets the model's role, tone, and rules for the WHOLE conversation. Set once, not treated as something "the user said."

User Prompt:  the actual message/question being asked right now.

The same user question can produce very different answers depending
entirely on the system prompt around it -- that's what this script
demonstrates directly.
"""

import os
from openai import OpenAI
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

USER_PROMPT = "How do I fix a bug where my Python loop never ends?"

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

def ask_with_system(system_prompt: str, user_prompt: str):
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    print("--- No system prompt (model's default behavior) ---")
    default_response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": USER_PROMPT}],
    )
    print(default_response.choices[0].message.content)
    
    print("\n--- System prompt: strict senior engineer ---")
    print(ask_with_system(
        "You are a strict senior engineer doing a code review. "
        "Be blunt and terse. No pleasantries. Answer directly without showing reasoning.",
        USER_PROMPT,
    ))
    
    print("\n--- System prompt: friendly beginner tutor ---")
    print(ask_with_system(
        "You are a friendly, patient coding tutor teaching a complete beginner. "
        "Use simple language and encouragement. Answer directly without showing reasoning.",
        USER_PROMPT,
    ))

