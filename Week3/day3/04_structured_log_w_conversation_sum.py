"""
Structured Logging + Conversation Summarization (via OpenRouter)

Real applications use Python's `logging` module, not scattered print() statements -- it gives timestamps, severity levels, and can write to both console and a file at once.
- Instead of just DROPPING old messages when history grows too long (like Week 2's sliding-window trimming), this script SUMMARIZES older turns into a short paragraph, preserving key facts while still saving tokens -- a smarter middle ground.
"""

import os
import logging
from openai import OpenAI
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# --- Logging setup ---
logger = logging.getLogger("chatbot")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
logger.addHandler(console_handler)

file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), "chatbot.log"))
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(file_handler)

SUMMARIZE_AFTER_N_MESSAGES = 6  # once history (excluding system) exceeds this, summarize older turns
KEEP_RECENT_MESSAGES = 2        # always keep the most recent N messages verbatim

def summarize_messages(messages_to_summarize):
    conversation_text = "\n".join(f"{m['role']}: {m['content']}" for m in messages_to_summarize)
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=150,
        messages=[
            {"role": "system", "content": "Summarize this conversation in 2-3 sentences, keeping key facts."},
            {"role": "user", "content": conversation_text},
        ],
    )
    return response.choices[0].message.content

def maybe_compress_history(history):
    system_msgs = [m for m in history if m["role"] == "system"]
    other_msgs = [m for m in history if m["role"] != "system"]
    
    if len(other_msgs) <= SUMMARIZE_AFTER_N_MESSAGES:
        return history
    
    to_summarize = other_msgs[:-KEEP_RECENT_MESSAGES]
    to_keep = other_msgs[-KEEP_RECENT_MESSAGES:]
    
    logger.info(f"History grew to {len(other_msgs)} messages -- summarizing {len(to_summarize)} older ones.")
    summary_text = summarize_messages(to_summarize)
    logger.info(f"Summary produced: {summary_text}")
    
    summary_message = {"role": "system", "content": f"Earlier conversation summary: {summary_text}"}
    return system_msgs + [summary_message] + to_keep

def chat_turn(history, user_input):
    history.append({"role": "user", "content": user_input})
    history = maybe_compress_history(history)
    
    logger.info(f"Sending request with {len(history)} messages.")
    response = client.chat.completions.create(model=MODEL, max_tokens=MAX_TOKENS, messages=history)
    reply = response.choices[0].message.content
    
    logger.info(f"Received reply ({response.usage.total_tokens} tokens total).")
    history.append({"role": "assistant", "content": reply})
    return history, reply

if __name__ == "__main__":
    history = [{"role": "system", "content": "Answer briefly."}]
    fake_turns = [
        "Tell me a fact about the ocean.",
        "Tell me a fact about space.",
        "Tell me a fact about volcanoes.",
        "Tell me a fact about deserts.",
        "Tell me a fact about rainforests.",
        "Tell me a fact about glaciers.",
        "Now, what was the very first fact you told me?",
    ]
    for turn in fake_turns:
        history, reply = chat_turn(history, turn)
        print(f"Bot: {reply}\n")

    print(f"Final history length: {len(history)} messages")