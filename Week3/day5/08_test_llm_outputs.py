"""
Testing LLM Outputs (via OpenRouter)

LLM output is non-deterministic, so you can't test it like normal code ("assert output == exact string"). Instead, you test PROPERTIES of the output: is it non-empty? does it contain an expected keyword? does it match a required format? This is the basic idea behind LLM evaluation ("evals") in real applications.
"""

import os
import json
from openai import OpenAI
from Week2.config import BASE_URL, API_KEY, MODEL, MAX_TOKENS

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

DEFAULT_SYSTEM = "Answer directly and concisely. Do not show your reasoning or thinking process."

def ask(prompt, system = None):
    messages = []
    if system:
        messages.append({"role": "system", "content": system or DEFAULT_SYSTEM})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(model=MODEL, max_tokens=MAX_TOKENS, messages=messages)
    return response.choices[0].message.content

passed = 0
failed = 0

def check(description, condition):
    global passed, failed
    if condition:
        print(f"PASS: {description}")
        passed += 1
    else:
        print(f"FAIL: {description}")
        failed += 1

def test_non_empty_response():
    output = ask("Say hello in one word.")
    check("response is non-empty", bool(output and output.strip()))

def test_keyword_present():
    output = ask("What is the chemical symbol for gold? Answer with just the symbol.")
    check("response mentions 'Au'", "Au" in output)
    
def test_format_constraint():
    output = ask("List exactly 3 fruits, comma separated, nothing else.")
    if not output:
        check("response has exactly 3 comma-separated items (got no response)", False)
        return
    items = [item.strip() for item in output.split(",")]
    check(f"response has exactly 3 comma-separated items (got {len(items)})", len(items) == 3)

def test_json_output():
    output = ask(
        'Respond with ONLY this JSON: {"status": "ok"}',
        system="Respond with only valid JSON, no other text.",
    )
    try:
        parsed = json.loads(output)
        check("response is valid JSON", True)
        check("response has 'status' key equal to 'ok'", parsed.get("status") == "ok")
    except json.JSONDecodeError:
        check("response is valid JSON", False)
        check("response has 'status' key equal to 'ok'", False)
        
if __name__ == "__main__":
    test_non_empty_response()
    test_keyword_present()
    test_format_constraint()
    test_json_output()

    print(f"\n{passed} passed, {failed} failed")