# Week3 - Working with LLM APIs - Notes

---

## Week 2 → Week 3 Carryover

These Week 3 task-list items were already covered in Week 2 — noted here for the record rather than redone:

| Week 3 task                        | Covered in                                                                          |
| ---------------------------------- | ----------------------------------------------------------------------------------- |
| CLI chatbot sending input to API   | `Week2/day6/11_mini_chatbot.py`                                                     |
| System prompt for role/personality | `Week2/day2/03_system_vs_user_prompt.py`                                            |
| Conversation history across turns  | `Week2/day4/07_multiturn_conversation.py`                                           |
| Temperature/max_tokens experiments | `Week2/day1/02_temperature_experiment.py`, `Week2/day3/06_context_window_limits.py` |

**Week 3** instead goes deeper into what makes an LLM integration production-grade: CLI design, tool use, logging, testing, and concurrency.

---

## Day1 - CLI Design with `argparse`

**Concept:** Real CLI takes flags instead of hardcoded values or ineractive `input()` prompts - this makes the scripts scriptable, automatable, and usable in pipelines.

```python
parser = argparse.ArgumentParser(description="A configurable chatbot.")
parser.add_argument("--prompt", type=str, required=True)
parser.add_argument("--temperature", type=float, default=0.7)
args = parser.parse_args()
```

Run: `uv run Week3/day1/01_cli_chatbot_w_argparse.py --prompt "..." --temperature 0.3`

Also introduced: a `ChatSession` class — bundling model config + history into one reusable object instead of loose functions and a raw list.

**What each parameter changes:**

- `--temperature` — output randomness (0.0 = focused/repeatable, 1.0 = varied).
- `--max-tokens` — hard cap on reply length; too low → truncated output (`finish_reason: "length"`).
- `--system` — the model's role/persona for the whole exchange.
- `--model` — which underlying model handles the request.

---

## Day2 - Function Calling / Tool Use

**Concept:** The model can request that YOUR code run a specific function (with specific arguments), then use the result in its final answer. The model never executes code itself — it just says "call this function with these arguments," and your program decides whether to actually do it.

```python
TOOLS = [{
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Evaluate a basic arithmetic expression.",
        "parameters": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    },
}]

response = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
tool_calls = response.choices[0].message.tool_calls
# if tool_calls exists, run the matching local function, feed result back,
# then call the API again for a final answer using that result
```

Run: `uv run Week3/day2/02_function_calling.py`

**Important limitation:** not all free models support tool calling reliably. If `tool_calls` comes back empty for obviously math-related prompts, that's a model capability gap, not a bug in the code.

### Task 2 — Multi-Tool Selection & `tool_choice`

**Concept:** Task 1 offered exactly one tool. Real applications usually offer several, and the model has to pick the right one (or several at once) based on what's actually being asked. This task also covers `tool_choice`, which lets you force a specific tool or forbid tool use entirely:

```python
tool_choice="auto"    # model decides (default)
tool_choice="none"    # model must NOT use any tool
tool_choice={"type": "function", "function": {"name": "calculate"}}  # force a specific tool
```

It also handles multiple tool calls returned in a **single** response — one question needing both a weather lookup and a time lookup at once.

Run: `uv run Week3/day2/03_multi_tool_selection.py`

---

## Day3 - Structured Logging + Conversation Summarization

**Concept, part 1 — Logging:** Python's `logging` module (not scattered `print()` calls) gives timestamps, severity levels, and can write to console AND a file simultaneously.

```python
logger = logging.getLogger("chatbot")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("chatbot.log")
logger.addHandler(file_handler)
logger.info("Sending request with %d messages.", len(history))
```

**Concept, part 2 — Summarization:** Instead of dropping old messages when history grows too long (Week 2's sliding-window trim), ask the model to compress older turns into a short summary, preserving key facts while still saving tokens on future calls.

```python
def summarize_messages(messages_to_summarize):
    conversation_text = "\n".join(f"{m['role']}: {m['content']}" for m in messages_to_summarize)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": "Summarize in 2-3 sentences."},
                  {"role": "user", "content": conversation_text}],
    )
    return response.choices[0].message.content
```

Run: `uv run Week3/day3/04_structured_log_w_conversation_sum.py`

### Task 2 — Token-Budget-Aware Summarization + Log Levels & Rotation

**Concept, part 1 — Log levels:** Task 1 only used `logger.info()`. Real applications use severity levels deliberately: `DEBUG` (fine-grained detail), `INFO` (normal events), `WARNING` (worth flagging, not broken), `ERROR` (something actually failed). `logger.exception()` is a special ERROR case that also captures the full traceback automatically.

**Concept, part 2 — Token-based (not message-count-based) trigger:** Task 1 summarized once history passed a fixed message count — a rough proxy. This version checks the actual `total_tokens` reported by the API and summarizes once a real token budget is approached, which is what production systems actually care about.

**Concept, part 3 — Log rotation:** `RotatingFileHandler` automatically starts a new file once the current one hits a size limit, keeping a fixed number of backups instead of growing forever.

```python
file_handler = RotatingFileHandler("chatbot_rotating.log", maxBytes=5_000, backupCount=3)
```

Run: `uv run Week3/day3/05_token_budget_summarization_w_log.py`

**Your Notes (Task 2):** _(did a WARNING log appear before summarization actually happened? Did summarization trigger earlier here than Task 1's fixed-count version, given longer messages? Did you see DEBUG lines in the log file that didn't print to console? Did `.log.1` / `.log.2` backups appear once you lowered `maxBytes`?)_

---

## Day4 - REPL with Special Commands

**Concept:** Real CLI chat tools support commands alongside normal messages — anything starting with `/` is handled locally by your code; everything else goes to the model.

```python
if user_input.startswith("/"):
    if user_input == "/reset":
        session.reset()
    elif user_input == "/history":
        session.print_history()
    elif user_input == "/save":
        session.save()
    elif user_input == "/quit":
        break
    continue  # don't send commands to the model
reply = session.send(user_input)
```

Run (interactive): `uv run Week3/day4/06_REPL_chatbot_w_cmd.py`

### Task 2 — Commands with Arguments + Session Load/Undo

**Concept:** Task 1's commands were all standalone (no extra input needed). This version adds commands that take **arguments** — `/system <new prompt>`, `/temp <value>` — parsed by splitting "command" from "rest of the line":

```python
def parse_command(user_input):
    parts = user_input.split(maxsplit=1)
    command = parts[0].lower()
    argument = parts[1] if len(parts) > 1 else ""
    return command, argument
```

Also adds `/load <filename>` (resume a previously saved session — pairs with Task 1's `/save` to make sessions persistent across separate runs) and `/undo` (remove the last user+assistant exchange).

Run (interactive): `uv run Week3/day4/07_REPL_chatbot_w_arg.py`

---

## Day5 - Testing LLM Outputs

**Concept:** LLM output is non-deterministic, so you can't test it like normal code (`assert output == exact_string`). Instead you test **properties** of the output — non-empty, contains a keyword, matches a format, parses as valid JSON. This is the basic idea behind LLM "evals."

```python
def check(description, condition):
    print("PASS" if condition else "FAIL", "-", description)

output = ask("What is the chemical symbol for gold? Answer with just the symbol.")
check("response mentions 'Au'", bool(output) and "Au" in output)
```

Run: `uv run Week3/day5/08_test_llm_outputs.py`

**Important gotcha hit in practice:** with `openrouter/free`, some routed models return `None` instead of text (a reasoning model burning its whole token budget on internal "thinking"). Every check needs to handle `output` possibly being `None` — a bad/empty response should count as a clean `FAIL`, not crash the whole script.

### Task 2 — Test Suites, Pass Rates & LLM-as-Judge

**Concept, part 1 — Parametrized test cases:** Task 1 wrote one function per test. Real eval suites define test cases as **data** (a list of dicts with a prompt + a check function), then loop over them — adding a case means adding one entry, not a new function.

**Concept, part 2 — Pass rate instead of pass/fail:** Since output is non-deterministic, one PASS doesn't prove reliability. Real eval suites run each case multiple times and report a pass rate (e.g. "9/10 runs passed") — much more honest evidence.

**Concept, part 3 — LLM-as-judge:** Some things can't be checked with string matching — e.g. "was this response actually helpful?" is subjective. A common technique: a second API call, with a clear rubric, grades the first response:

```python
def judge_response(original_question, response_to_judge, rubric):
    judge_prompt = f"Question: {original_question}\nResponse: {response_to_judge}\nRubric: {rubric}\nDoes it satisfy the rubric? Answer YES or NO."
    verdict = ask(judge_prompt, max_tokens=10)
    return bool(verdict) and verdict.strip().upper().startswith("YES")
```

Run: `uv run Week3/day5/09_test_suite_and_judge.py`

---

## Day6 - Async API Calls

**Concept:** Sequential requests mean total time = sum of every individual request's time. `asyncio` lets you fire multiple requests **concurrently** — while one waits on the network, others proceed — so total time is closer to the slowest single request, not the sum of all.

```python
async def ask_async(prompt):
    response = await async_client.chat.completions.create(model=MODEL, messages=[...])
    return response.choices[0].message.content

results = await asyncio.gather(*(ask_async(p) for p in PROMPTS))
```

Run: `uv run Week3/day6/010_async_api_call.py`

### Task 2 — Rate-Limited Concurrency & Per-Task Error Handling

**Concept, part 1 — Concurrency needs a cap:** Task 1 fired ALL requests at once — fine for 4 prompts, but scale that to 50 and you'll almost certainly hit a rate limit, since nothing was throttling how many were in flight simultaneously. An `asyncio.Semaphore` lets you say "at most N requests running at the same time" — extra tasks simply wait their turn.

```python
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

async def ask_with_limit(prompt, index):
    async with semaphore:  # blocks here if the cap is already reached
        ...
```

**Concept, part 2 — One failure shouldn't kill the whole batch:** By default, `asyncio.gather()` raises the first exception it sees and cancels everything else. Catching errors _inside_ each task (or using `gather(..., return_exceptions=True)`) means one failed/rate-limited request doesn't lose the rest of the batch:

```python
try:
    response = await async_client.chat.completions.create(...)
    return {"success": True, "result": response.choices[0].message.content}
except RateLimitError:
    return {"success": False, "error": "rate_limited"}
```

Run: `uv run Week3/day6/11_rate_limited_concurrency.py`

---

## Quick Reference Table (Day 1–5)

| Concept                                            | Script                                    |
| -------------------------------------------------- | ----------------------------------------- |
| `argparse` CLI + `ChatSession` class               | `01_cli_chatbot.py`                       |
| Function calling / tool use (single tool)          | `02_function_calling.py`                  |
| Multi-tool selection + `tool_choice`               | `03_multi_tool_selection.py`              |
| Logging + summarization (message-count trigger)    | `04_structured_log_w_conversation_sum.py` |
| Token-budget summarization + log levels/rotation   | `05_token_budget_summarization_w_log.py`  |
| REPL with `/` commands (no arguments)              | `06_REPL_chatbot_w_cmd.py`                |
| REPL commands with arguments + load/undo           | `07_REPL_chatbot_w_arg.py`                |
| Testing LLM output properties                      | `08_test_llm_outputs.py`                  |
| Test suites, pass rates, LLM-as-judge              | `09_test_suite_and_judge.py`              |
| Async concurrent API calls (basic)                 | `10_async_api_call.py`                    |
| Rate-limited concurrency + per-task error handling | `11_rate_limited_concurrency.py`          |

---

## Deliverable Summary (parameter effects, for submission)

| Parameter       | What it controls                                                 |
| --------------- | ---------------------------------------------------------------- |
| `temperature`   | Randomness of token sampling                                     |
| `max_tokens`    | Output length cap; triggers `finish_reason: "length"` if too low |
| `top_p`         | Alternate randomness control via probability-mass cutoff         |
| `system` prompt | Role/tone/rules for the whole conversation                       |

---

## Deliverable Addendum — Concurrency

| Aspect                  | What it controls                                            |
| ----------------------- | ----------------------------------------------------------- |
| `asyncio.gather()`      | Runs multiple requests concurrently instead of sequentially |
| `asyncio.Semaphore`     | Caps max simultaneous in-flight requests                    |
| Per-task error handling | Prevents one failure from cancelling the whole batch        |
