"""
Test Suites, Pass Rates & LLM-as-Judge (via OpenRouter)

CONCEPT, part 1 -- Parametrized test cases:
Task 1 wrote one function per test. That doesn't scale -- real eval suites define test cases as DATA (a list of dicts), then loop over them. Adding a new test case means adding one entry, not writing a new function.

CONCEPT, part 2 -- Pass rate instead of pass/fail: Since output is non-deterministic, running a test ONCE and getting a PASS doesn't prove the behavior is reliable -- it might fail the very next run. Real eval suites run each case multiple times and report a PASS RATE (e.g. "9/10 runs passed"), which is much more honest evidence.

CONCEPT, part 3 -- LLM-as-judge:
Some things can't be checked with simple string matching -- e.g. "was this response actually HELPFUL and on-topic?" is subjective. A common technique: use a SECOND API call, with a clear rubric, to have the model grade the FIRST response. This is imperfect (the judge can be wrong too) but is widely used in practice for open-ended quality checks.
"""

import os
from openai import OpenAI
from Week2.config import BASE_URL, API_KEY, MODEL, MAX_TOKENS

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

DEFAULT_SYSTEM = "Answer directly and concisely. Do not show your reasoning or thinking process."

def ask(prompt, system=None, max_tokens=400):
    messages = [{"role": "system", "content": system or DEFAULT_SYSTEM}, {"role": "user", "content": prompt}]
    response = client.chat.completions.create(model=MODEL, max_tokens=MAX_TOKENS or max_tokens, messages=messages)
    return response.choices[0].message.content

TEST_CASES = [
    {
        "name": "capital_of_france",
        "prompt": "What is the capital of France? Answer with just the city name.",
        "check": lambda output: bool(output) and "paris" in output.lower(),
    },
    {
        "name": "basic_math",
        "prompt": "What is 12 + 7? Answer with just the number.",
        "check": lambda output: bool(output) and "19" in output,
    },
    {
        "name": "refuses_impossible_request",
        "prompt": "What will the exact stock price of a random company be exactly one year from today?",
        "check": lambda output: bool(output) and any(
            word in output.lower() for word in ["cannot", "can't", "unable", "don't know", "impossible", "no way"]
        ),
    },
]

RUNS_PER_CASE = 3  # keep small for a free API

def run_test_suite():
    print("=== Test Suite: Pass Rate Over Multiple Runs ===\n")
    results = {}

    for case in TEST_CASES:
        pass_count = 0
        for _ in range (RUNS_PER_CASE):
            output = ask(case["prompt"])
            if case["check"](output):
                pass_count += 1

        rate = pass_count / RUNS_PER_CASE
        results[case["name"]] = rate
        status = "STABLE" if rate == 1.0 else ("FLAKY" if 0 < rate < 1.0 else "FAILING")
        print(f"{case['name']}: {pass_count}/{RUNS_PER_CASE} passed ({rate:.0%}) -- {status}")

    return results

# LLM as judge
def judge_response(original_question, response_to_judge, rubric):
    """
    Uses a SEPARATE API call to grade a response against a rubric.
    Returns "YES" or "NO" (kept binary here to make parsing easy).
    """
    judge_prompt = (
        f"Question asked: {original_question}\n\n"
        f"Response to evaluate: {response_to_judge}\n\n"
        f"Rubric: {rubric}\n\n"
        "Does the response satisfy the rubric? Answer with ONLY the single word YES or NO."
    )
    verdict = ask(judge_prompt, max_tokens=10)
    return bool(verdict) and verdict.strip().upper().startswith("YES")

def run_judge_examples():
    print("\n=== LLM-as-Judge: grading open-ended responses ===\n")

    question = "Explain what a for loop does, for someone who has never programmed before."
    response = ask(question)
    print(f"Response to grade: {response}\n")

    is_beginner_friendly = judge_response(
        question, response,
        rubric="The explanation avoids jargon and would make sense to someone with zero programming background.",
    )
    print(f"Judge verdict -- beginner-friendly: {is_beginner_friendly}")

    is_off_topic = judge_response(
        question, response,
        rubric="The response is completely unrelated to for loops or programming.",
    )
    print(f"Judge verdict -- is off-topic (should be False): {is_off_topic}")

if __name__ == "__main__":
    run_test_suite()
    run_judge_examples()