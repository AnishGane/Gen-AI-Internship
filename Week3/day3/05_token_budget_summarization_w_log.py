"""
Token-Budget-Aware Summarization + Log Levels & Rotation (via OpenRouter)

CONCEPT, part 1 -- Log levels:
Task 1 only used logger.info(). Real applications use different SEVERITY LEVELS deliberately:
    - DEBUG    -- fine-grained detail, only useful when actively debugging
    - INFO     -- normal expected events (a request was sent, a reply arrived)
    - WARNING  -- something worth flagging but not broken (approaching a limit)
    - ERROR    -- something actually failed
logger.exception() is a special case of ERROR that also captures the full traceback automatically -- much more useful than a bare print() when something crashes.

CONCEPT, part 2 -- Token-based (not message-count-based) summarization:
Task 1 summarized once history passed a fixed MESSAGE COUNT. That's a rough proxy -- a conversation with 6 very long messages could blow the token budget long before 6 short ones would. This version instead checks the ACTUAL token count reported by the API (`response.usage`) and summarizes once a real token budget is approached -- which is what production systems actually care about, since that's what the context window and billing are both measured in.

CONCEPT, part 3 -- Log rotation:
A log file that grows forever eventually becomes a problem. RotatingFileHandler automatically starts a new file once the current one hits a size limit, keeping only a fixed number of old ones.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from openai import OpenAI, APIError
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

# --- Logging setup: levels + rotation ---
logger = logging.getLogger("chatbot_v2")
logger.setLevel(logging.DEBUG)  # capture everything; handlers below filter what's shown/saved

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # console only shows INFO and above (hides DEBUG noise)
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
logger.addHandler(console_handler)

# Rotates once the log file hits 5KB, keeps 3 old backups (.1, .2, .3)
file_handler = RotatingFileHandler(
    os.path.join(os.path.dirname(__file__), "chatbot_rotating.log"),
    maxBytes=5_000,
    backupCount=3,
)
file_handler.setLevel(logging.DEBUG)  # file gets EVERYTHING, including DEBUG detail
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(file_handler)

# --- Token-budget-based summarization ---
TOKEN_BUDGET = 600          # once total_tokens from the last call exceeds this, summarize
WARNING_THRESHOLD = 400     # log a WARNING once we're getting close, before we actually hit the budget
KEEP_RECENT_MESSAGES = 2

def summarize_messages(messages_to_summarize):
    logger.debug(f"Summarizing {len(messages_to_summarize)} messages: {messages_to_summarize}")
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

def maybe_compress_history(history, last_total_tokens):
    if last_total_tokens is None:
        return history  # first call, nothing to check yet

    if last_total_tokens >= TOKEN_BUDGET:
        system_msgs = [m for m in history if m["role"] == "system"]
        other_msgs = [m for m in history if m["role"] != "system"]
        to_summarize = other_msgs[:-KEEP_RECENT_MESSAGES]
        to_keep = other_msgs[-KEEP_RECENT_MESSAGES:]

        logger.warning(f"Token budget hit ({last_total_tokens} >= {TOKEN_BUDGET}). Summarizing {len(to_summarize)} messages.")
        summary_text = summarize_messages(to_summarize)
        summary_message = {"role": "system", "content": f"Earlier conversation summary: {summary_text}"}
        return system_msgs + [summary_message] + to_keep

    elif last_total_tokens >= WARNING_THRESHOLD:
        logger.warning(f"Approaching token budget: {last_total_tokens}/{TOKEN_BUDGET} tokens used.")

    return history

def chat_turn(history, user_input, last_total_tokens):
    history.append({"role": "user", "content": user_input})
    history = maybe_compress_history(history, last_total_tokens)

    logger.debug(f"Outgoing request: model={MODEL}, message_count={len(history)}")
    try:
        response = client.chat.completions.create(model=MODEL, max_tokens=MAX_TOKENS, messages=history)
    except APIError:
        logger.exception("API call failed.")
        return history, None, last_total_tokens

    reply = response.choices[0].message.content
    total_tokens = response.usage.total_tokens
    logger.info(f"Reply received. total_tokens this call: {total_tokens}")

    history.append({"role": "assistant", "content": reply})
    return history, reply, total_tokens

if __name__ == "__main__":
    history = [{"role": "system", "content": "Answer in 2-3 sentences."}]
    last_total_tokens = None

    fake_turns = [
        "Tell me a detailed fact about the Pacific Ocean's depth and creatures.",
        "Now tell me a detailed fact about the history of space exploration.",
        "Now a detailed fact about how volcanoes form.",
        "Now a detailed fact about the rainforest's biodiversity.",
        "What was the very first thing I asked you about?",
    ]

    for turn in fake_turns:
        history, reply, last_total_tokens = chat_turn(history, turn, last_total_tokens)
        print(f"Bot: {reply}\n")

    logger.info(f"Session ended. Final history length: {len(history)} messages.")
