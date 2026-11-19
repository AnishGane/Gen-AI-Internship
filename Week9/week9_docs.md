# Week 9: A First Tool-Using Agent (OpenRouter + Free Models)

---
 
## 1. What are we building
 
An **agent** is a model that can choose an action (such as calling a function) and then use the result.
 
A **tool** is a normal Python function your program makes available to the model. The key rule:
 
> The model never runs your function. It only returns a structured *request*. Your program checks the request, runs the function, and sends the result back.
 
### The tool cycle
 
```
 You ── question + tool descriptions ──> Model
 You <── "please call multiply_numbers(238, 417)" ── Model      (request)
 You run multiply_numbers(238, 417) → 99246                   (your code runs it)
 You ── tool result: 99246 ──> Model
 You <── "238 × 417 = 99,246" ── Model                          (final answer)
```
 
| Stage | Who does it | Code location |
| --- | --- | --- |
| 1. Describe the tools | You | `TOOL_SCHEMAS` in `agent/tools.py` |
| 2. Choose: answer or request a tool | Model | `chat()` in `agent/client.py` |
| 3. Execute the function | Your program | `execute_tool()` in `agent/tools.py` |
| 4. Return the result | Your program | `role: "tool"` message in `agent/loop.py` |
| 5. Write the final answer | Model | next `chat()` call, no `tool_calls` |
 
### Learning outcomes
 
- Explain the difference between a plain text response and a tool-using model.
- Describe the tool cycle.
- Run an example with tools you defined.
- Say when a tool helps and when a prompt is enough.
**Time:** about 60 to 90 minutes.
 
---
 
## 2. Prerequisites
 
- Python 3.10 or newer (`python --version`). The code uses `str | None` type syntax.
- An OpenRouter account and API key: https://openrouter.ai/keys
- Free models need no credit purchase.

---
 
## 3. Setup (step by step)
 
Run everything from the project root folder (`Week9/`).
 
### 3.1 Create a virtual environment
 
macOS / Linux:
 
```bash
python -m venv .venv
source .venv/bin/activate
```
 
Windows PowerShell:
 
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
 
Windows cmd:
 
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```
 
### 3.2 Install dependencies
 
```bash
pip install -r requirements.txt
```
 
Installs: `openai` (SDK, used against OpenRouter's compatible API), `httpx` (lists models), `python-dotenv` (reads `.env`), `pytest` (tests).
 
### 3.3 Add your API key
 
macOS / Linux:
 
```bash
cp .env.example .env
```
 
Windows:
 
```powershell
copy .env.example .env
```
 
Open `.env` and replace the placeholder:
 
```
OPENROUTER_API_KEY=sk-or-...your-real-key...
```
 
---
 
## 4. Running everything
 
Always use `uv run scripts.<name>` from the project root. Plain `python scripts/x.py` will fail with `ModuleNotFoundError: agent`.
 
| # | Command | Needs key? | Purpose |
| --- | --- | --- | --- |
| 1 | `uv run pytest .\tests\test_tools.py` | No | Offline tests of tools and the loop |
| 2 | `uv run .\scripts\list_free_models.py` | No | Show free, tool-capable models now |
| 3 | `uv run .\scripts\step1_basic_cycle.py` | Yes | The core lesson, one tool call |
| 4 | `uv run .\scripts\step2_agent_loop.py ` | Yes | Multi-step loop with several tools |
| 5 | `uv run .\scripts\step3_tool_or_not.py` | Yes | Tool vs. plain prompt comparison |
 
### 4.1 Offline tests
 
```bash
uv run pytest .\tests\test_tools.py
```
 
Expected: `6 passed`.
 
### 4.2 List free models
 
```bash
uv run .\scripts\list_free_models.py
```
 
Prints each free model that supports tools, plus the priority list the agent will use. Output varies because the free list rotates.
 
### 4.3 Step 1: the basic cycle
 
```bash
uv run .\scripts\step1_basic_cycle.py
```
 
Typical output (wording and model vary):
 
```
Models (priority order): ['nvidia/nemotron-3-ultra-550b-a55b:free', ...]
 
Model REQUESTED: multiply_numbers({"a": 238, "b": 417})
Our program RAN it, result: {"result": 99246.0}
 
Claude-style final answer: 238 multiplied by 417 equals 99,246.
```
 
The correct result is **99246**. (238 × 400 = 95200, plus 238 × 17 = 4046.) The original handout's `99146.0` is a typo.
 
### 4.4 Step 2: the agent loop
 
```bash
uv run .\scripts\step2_agent_loop.py
uv run .\scripts\step2_agent_loop.py "Divide 99246 by 7, then add 15"
```
 
The default question needs three tool calls: multiply, add, divide. You will see `[step N]` lines, each showing what the model requested and what your program returned.
 
### 4.5 Step 3: tool or not
 
```bash
uv run .\scripts\step3_tool_or_not.py
```
 
Asks three questions with the same tools available:
 
1. `48213 × 9157`: exact arithmetic, so the model should use a tool.
2. "Explain multiplication to a 10-year-old": no tool needed.
3. "Current date and time in UTC": needs `get_utc_time`.

### 4.6 Force a specific model (optional)
 
In `.env`:
 
```
OPENROUTER_MODEL=google/gemma-4-31b-it:free
```
 
Use an ID from `list_free_models`. Remove the line to return to automatic selection.
 
---
 
## 5. Project structure
 
```
week9-tool-agent/
├── README.md              short overview
├── week9_docs.md          this file
├── requirements.txt       dependencies
├── .env.example           template for your key
├── .gitignore             keeps .env, .venv, caches out of git
├── agent/                 the reusable library
│   ├── __init__.py
│   ├── config.py          URL, key loading, fallback models
│   ├── models.py          discovers free, tool-capable models
│   ├── tools.py           functions, schemas, registry, execute_tool()
│   ├── client.py          OpenAI SDK pointed at OpenRouter
│   └── loop.py            the agent loop
├── scripts/               runnable lessons
│   ├── __init__.py
│   ├── list_free_models.py
│   ├── step1_basic_cycle.py
│   ├── step2_agent_loop.py
│   └── step3_tool_or_not.py
├── tests/
│   ├── __init__.py
│   └── test_tools.py      offline tests
```
 
Design idea: `agent/` holds reusable logic, `scripts/` holds small programs that use it. The `__init__.py` files make folders importable as packages, which is why `uv run .\scripts\step1_basic_cycle.py` works.
 
---
 
## 6. Code walkthrough
 
### 6.1 `agent/config.py`: settings
 
```python
BASE_URL = "https://openrouter.ai/api/v1"
FALLBACK_MODELS = [...]
ROUTER_MODEL = "openrouter/free"
```
 
- `load_dotenv()` reads `.env` into environment variables.
- `BASE_URL` is the only change needed to point the OpenAI SDK at OpenRouter.
- `get_api_key()` reads `OPENROUTER_API_KEY` and exits with a clear message if it is missing.
- `forced_model()` returns `OPENROUTER_MODEL` if set.
- `FALLBACK_MODELS` is a static list used only if the live lookup fails. Free IDs rotate, so this list can go stale.
- `ROUTER_MODEL` (`openrouter/free`) lets OpenRouter pick a free model that suits the request.

### 6.2 `agent/models.py`: find usable free models
 
`fetch_free_tool_models()` calls the public `GET /models` endpoint (no key needed) and keeps a model only if all three are true:
 
1. its ID ends in `:free`
2. prompt and completion pricing are both 0
3. `"tools"` is in its `supported_parameters`
Results are sorted by context length. Context length is not a quality ranking.
 
`pick_models(n=3)` builds the priority list:
 
1. If `OPENROUTER_MODEL` is set, use only that.
2. Otherwise fetch the live list. If the network call fails, print a notice and continue.
3. Put the known-good `FALLBACK_MODELS` that are live first, then other live ones, capped at `n`.
4. If nothing was found, use the static fallback, and add the router if there is room.

### 6.3 `agent/tools.py`: tools, schemas, safe execution
 
The file has three layers.
 
**Layer 1: plain Python functions.** `add_numbers`, `subtract_numbers`, `multiply_numbers`, `divide_numbers` (raises on division by zero), `get_utc_time`.
 
**Layer 2: schemas (`TOOL_SCHEMAS`).** This is what the model sees: a name, a description, and a JSON Schema for inputs.
 
```python
{
  "type": "function",
  "function": {
    "name": "multiply_numbers",
    "description": "Multiply two numbers and return the exact product.",
    "parameters": {
      "type": "object",
      "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
      "required": ["a", "b"],
    },
  },
}
```
 
Good descriptions matter: the model decides whether to use a tool based on them. `_math_schema()` avoids repeating this block for the four math tools.
 
**Layer 3: registry and executor.**
 
`TOOL_REGISTRY` maps names to functions. It is the allow-list: only names in this dictionary can ever run, however the model phrases its request.
 
`execute_tool(name, raw_arguments)` does the following:
 
1. Looks up the name. Unknown tool returns `{"error": "Unknown tool: ..."}`.
2. Parses the arguments. OpenRouter sends them as a JSON **string**, so `json.loads` is needed.
3. Validates that arguments are a JSON object, that `a` and `b` exist, and that they are real numbers (booleans are rejected).
4. Calls the function and returns `{"result": ...}`.
5. Wraps everything in `try/except`. Any failure becomes `{"error": "..."}`.
It never raises, and it always returns a JSON string. Returning errors to the model lets it explain or retry instead of crashing your program. This is the "validate tool inputs and limit what a tool may do" advice from the handout.
 
### 6.4 `agent/client.py`: talking to OpenRouter
 
```python
OpenAI(base_url=BASE_URL, api_key=get_api_key(), max_retries=2, ...)
```
 
- Same SDK as OpenAI, different `base_url`.
- `max_retries=2` lets the SDK retry transient errors and rate limits with backoff.
- The `X-Title` header is an optional app label.
`chat(client, messages, tools, models)` makes one model call:
 
- `model=models[0]` is required by the SDK.
- `extra_body={"models": models}` sends OpenRouter's fallback list, so it moves to the next model on rate limits or provider downtime.
- `tool_choice="auto"` lets the model decide whether to use a tool.
- `max_tokens=1000` leaves room for reasoning models.
- OpenRouter can return an error body with no `choices`. The code raises a clear `RuntimeError` instead of failing later with a confusing `IndexError`.
### 6.5 `agent/loop.py`: the agent loop
 
`run_agent(client, models, user_prompt, max_steps=5)`:
 
1. Starts `messages` with a system prompt and the user question.
2. Calls `chat(...)` and reads `response.choices[0].message`.
3. **No `tool_calls`?** The model has answered. Return `msg.content`.
4. **Has `tool_calls`?**
   - Append the assistant's request to `messages`.
   - For each call, run `execute_tool(...)` and append a message with `role: "tool"` and the matching `tool_call_id`.
   - Loop again so the model can use the results.
5. After `max_steps` rounds, stop with a message. This prevents runaway loops, which matter because free models have request caps.
`_assistant_message(msg)` rebuilds the assistant turn field by field instead of dumping the SDK object. Some providers reject unexpected extra fields, so this is safer.
 
The `tool_call_id` must match the ID the model supplied. It links each result to its request.
 
### 6.6 What the `messages` list looks like
 
After one tool call, the second request sends:
 
```json
[
  {"role": "system", "content": "You are a careful assistant..."},
  {"role": "user", "content": "What is 238 multiplied by 417?"},
  {"role": "assistant", "content": "", "tool_calls": [
    {"id": "call_abc123", "type": "function",
     "function": {"name": "multiply_numbers", "arguments": "{\"a\": 238, \"b\": 417}"}}
  ]},
  {"role": "tool", "tool_call_id": "call_abc123", "content": "{\"result\": 99246.0}"}
]
```
 
The `tools` list must be included on **every** request, including the second one, so OpenRouter can validate the schema each time.
 
### 6.7 `scripts/step1_basic_cycle.py`
 
The loop written out by hand, with no helper hiding the steps. It sends only the `multiply_numbers` schema, prints the request the model made, runs it, appends the assistant and tool messages, and calls the model again for the final text. Use this to fill in the trace in `notes/learning_notes.md`.
 
### 6.8 `scripts/step2_agent_loop.py`
 
Calls `run_agent` with all five tools. A question like "multiply, then add, then divide" cannot be answered in one call, because each step depends on the previous result. The loop handles this automatically. This is the handout's optional extension, and it also shows why the dispatch uses the *requested name* instead of a hardcoded function.
 
### 6.9 `scripts/step3_tool_or_not.py`
 
Runs three questions through the same agent. Observe which ones trigger tool requests. This answers learning outcome 4.
 
### 6.10 `scripts/list_free_models.py`
 
Prints the live list from `fetch_free_tool_models()` and the final priority order from `pick_models()`.
 
### 6.11 `tests/test_tools.py`
 
Six offline tests, no network or key:
 
| Test | Checks |
| --- | --- |
| `test_multiply_is_exact` | 238 × 417 = 99246.0 |
| `test_divide_by_zero_returns_error` | error JSON, no crash |
| `test_unknown_tool_rejected` | non-registered names are refused |
| `test_bad_inputs_rejected` | wrong types, missing args, invalid JSON |
| `test_loop_runs_tool_then_answers` | fake model asks for a tool; loop runs it and passes the result back |
| `test_loop_stops_at_max_steps` | endless tool requests are cut off |
 
The loop tests use `monkeypatch` to replace `chat` with a fake, so the whole cycle is tested without a real model.
 
---
 
## 7. Free models: what to know
 
- Free model IDs end in `:free` and cost $0 per token.
- The free list rotates with little warning, so the project discovers models live and uses a fallback list.
- Limits apply to your whole account, not per model: **20 requests per minute**, and **50 per day** (1000 per day if you have bought at least $10 in credits at any time). One agent run may use 2 to 5 requests.
- Free providers may log prompts. Do not send secrets or personal data.
- Tool-calling quality varies between models. If a model ignores or misuses tools, try another.
- Keep every model in the fallback list a `:free` model. If the list falls through to a paid one, you pay that model's rate.
Current model details: https://openrouter.ai/collections/free-models
Tool calling docs: https://openrouter.ai/docs/guides/features/tool-calling
 
---
 
## 8. Troubleshooting
 
| Problem | Cause and fix |
| --- | --- |
| `ModuleNotFoundError: agent` | Run `uv run .\scripts\<name>` from the project root. |
| `OPENROUTER_API_KEY is not set` | Create `.env` from `.env.example`; make sure it is in the project root. |
| `401` / authentication error | Key is wrong or has extra spaces or quotes. Regenerate it. |
| `429` / rate limit | You hit 20/min or the daily cap. Wait, or switch model. |
| `[models] live lookup failed` | No network or OpenRouter is down. The fallback list is used; may still work. |
| Model never calls the tool | Try another model via `OPENROUTER_MODEL`, or make the question explicit ("use the calculator"). |
| Model returns an error or empty choices | Free model unavailable. Run `list_free_models` and pick another. |
| `TypeError: unsupported operand type(s) for |` | Python older than 3.10. Upgrade Python. |
| Answer is wrong or inconsistent | Compare with the printed tool result; the tool result is the truth, the model's wording is not. |
 
---
 
## 9. Exercises
 
1. **Trace the cycle.** Run step 1.
2. **Add a tool.** Add `power_numbers(a, b)`: write the function, add its schema to `TOOL_SCHEMAS`, add it to `TOOL_REGISTRY`, and add `"power_numbers"` to `MATH_TOOLS`. Then add a test.
3. **Break it on purpose.** Ask for a square root with no tool available. What does the model do?
4. **Compare models.** Run step 3 with different `OPENROUTER_MODEL` values. Which handle tools best?
5. **Test safety.** Temporarily make a tool raise an exception. Confirm the program survives and the model sees the error.
6. **Reflection.** Complete the three sentences about when tools help, when a prompt is enough, and what tool you would add next.
 
---
 
## 10. Command cheat sheet
 
```bash
# one-time setup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # then edit .env
 
# every session
source .venv/bin/activate       # Windows: .venv\Scripts\activate
uv run pytest .\tests\test_tools.py
uv run .\scripts\list_free_models.py
uv run .\scripts\step1_basic_cycle.py
uv run .\scripts\step2_agent_loop.py 
uv run .\scripts\step2_agent_loop.py "your own math question"
uv run .\scripts\step3_tool_or_not.py
```
 
## 11. Key takeaways
 
- A tool-using model **proposes** calls; your program **controls** what runs.
- The cycle is request, run, return result, final answer.
- A tool helps for exact math, current information, lookups, and actions. A prompt is enough for explanations, rewriting, and brainstorming.
- Always validate inputs, allow-list functions, return errors as data, and cap loop steps.
 