# LLM Core Concept - Example Notes

---

## 1. Tokens

A **token** is the basic unit of text a model reads/generates — roughly 3/4 of a word in English, though it varies. Every API response tells you the exact counts via `response.usage` — no guessing required.

```python
usage = response.usage
print(usage.prompt_tokens)      # tokens in your input
print(usage.completion_tokens)  # tokens in the model's reply
print(usage.total_tokens)       # sum of both
```

A naive estimate (`len(text) // 4`) gets you in the ballpark, but the real count from `usage` is authoritative — API cost and context limits are based on the real count, not an estimate.

---

# 2. Context Window

The **context window** is the max number of tokens a model can "see" at once — system prompt + full conversation history + reserved output space, combined. Anything beyond that limit is effectively invisible to the model. `prompt_tokens + completion_tokens = total_tokens`, and `total_tokens` is
what counts against this hard ceiling on every single call.

---

# 3. `max_tokens` and `finish_reason`

`max_tokens` caps how much the model is **allowed** to generate. If it wants to say more, it gets cut off mid-thought. `finish_reason` tells you whether that happened:

- `"stop"` — the model finished naturally.
- `"length"` — it got cut off by your `max_tokens` cap.

```python
response = client.chat.completions.create(
    model=MODEL, max_tokens=8,
    messages=[{"role": "user", "content": "Explain photosynthesis in detail."}],
)
print(response.choices[0].finish_reason)  # likely "length" with only 8 tokens
```

---

## 4. Temperature

Controls how randomly the model samples its next token from its predicted probabilities.

- `temperature = 0.0` → almost always picks the single most likely token → repeatable, focused.
- `temperature = 1.0` → more willing to pick less-likely tokens → varied, creative, sometimes less coherent.

```python
response = client.chat.completions.create(
    model=MODEL, max_tokens=100, temperature=0.0,
    messages=[{"role": "user", "content": "Write a tagline for a coffee shop."}],
)
```

---

## 5. `top_p` (Nucleus Sampling)

A second, different randomness dial. Instead of reshaping the whole probability distribution (like temperature), `top_p` restricts the model to only the smallest set of tokens whose combined probability reaches `top_p`.

- `top_p = 0.1` → only the tiny set making up the top 10% of probability mass → very focused.
- `top_p = 1.0` → considers almost all possible next tokens.

```python
response = client.chat.completions.create(
    model=MODEL, max_tokens=100, top_p=0.1,
    messages=[{"role": "user", "content": "Suggest a podcast name."}],
)
```

**Important caveat from testing this:** if you're using `openrouter/free` (the auto-router), it can pick a _different underlying model_ per call — so a jump in verbosity or style between `top_p` values might be the model changing, not `top_p` itself. Pin one fixed model ID for a clean comparison.

### Temperature + `top_p` together

Both can technically be set in the same call:

```python
response = client.chat.completions.create(
    model=MODEL, temperature=0.7, top_p=0.9, ...
)
```

It won't error — but most guidance says adjust **one, not both**, since they stack in ways that are hard to reason about (temperature reshapes the distribution, `top_p` then clips the resulting pool). Pick one dial, leave the other at default.

---

## 6. System Prompt vs. User Prompt

- **System prompt**: sets the model's role, tone, and rules for the whole conversation. Set once, not treated as something "the user said."
- **User prompt**: the actual question/message being asked right now.

```python
messages = [
    {"role": "system", "content": "You are a blunt senior engineer. No pleasantries."},
    {"role": "user", "content": "How do I fix an infinite loop?"},
]
```

The exact same user question can get very different answers purely based on the system prompt around it.

---

## 7. Prompt Wording Sensitivity

LLMs are sensitive to _how_ a question is phrased, not just _what_ is asked. Vague prompts → vague, generic answers. Specific prompts (with format, constraints, length limits) → more usable, structured answers.

```python
ask("Tell me about dogs.")  # vague
ask("List 3 apartment-friendly dog breeds, one line each, numbered list only.")  # specific
```

---

## 8. Statelessness & Multi-turn Memory

The API is **stateless** — the model remembers nothing between separate calls. Chat "memory" is an illusion built entirely client-side: you keep a growing `messages` list (both user and the model's own past replies) and resend the whole thing every time.

```python
history = [{"role": "system", "content": "..."}]
history.append({"role": "user", "content": "My name is Priya."})
reply = ask(history)
history.append({"role": "assistant", "content": reply})  # save its reply too
history.append({"role": "user", "content": "What is my name?"})
reply = ask(history)  # now it knows, because the full history was resent
```

---

## 9. Context Trimming (Sliding Window)

Since every turn resends the full history, long conversations get more expensive (in tokens) with every message, and can eventually exceed the context window. A common fix: keep only the last N messages.

```python
def trim_history(history, keep_last=4):
    system_msgs = [m for m in history if m["role"] == "system"]
    other_msgs = [m for m in history if m["role"] != "system"]
    return system_msgs + other_msgs[-keep_last:]
```

Trade-off: cheaper per call, but the model loses access to anything outside the trimmed window — it can "forget" earlier context.

---

## 10. Streaming Responses

By default, an API call waits for the entire response before returning anything. Streaming instead sends chunks as they're generated, so you can display text progressively (like ChatGPT's word-by-word effect).

```python
stream = client.chat.completions.create(
    model=MODEL, max_tokens=300, messages=[...], stream=True,
)
for chunk in stream:
    piece = chunk.choices[0].delta.content
    if piece:
        print(piece, end="", flush=True)
```

**Note**: `delta.content` can be `None` on some chunks (e.g. the first/last) — always check before using/concatenating it.

---

## 11. Handling Errors & Rate Limits

Free-tier APIs have rate limits. Real applications catch specific error types and decide what to do — retry (temporary issues like rate limits) vs. fail clearly (permanent issues like a bad request).

```python
from openai import RateLimitError, APIError
import time

def ask_with_retry(prompt, max_retries=3, delay_seconds=5):
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(model=MODEL, messages=[...])
            return response.choices[0].message.content  # don't forget this return!
        except RateLimitError:
            print(f"Rate limited, retrying in {delay_seconds}s...")
            time.sleep(delay_seconds)
        except APIError as e:
            print(f"API error: {e}")
            return None  # retrying won't fix this kind of error
    return None
```

**Common bug to watch for:** forgetting to `return` inside the `try` block on success — the loop then just keeps retrying a call that already worked, and you end up with `None` even though the API succeeded.
