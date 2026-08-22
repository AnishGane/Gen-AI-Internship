"""
Rate-Limited Concurrency & Per-Task Error Handling (via OpenRouter)

CONCEPT, part 1 -- Concurrency needs a cap:
Task 1 fired ALL requests at once with asyncio.gather() -- fine for 4 prompts, but scale that to 50 and you'll almost certainly hit a rate limit (e.g. "20 requests/minute"), since nothing was throttling how many were in flight simultaneously. An asyncio.Semaphore lets you say "at most N requests running at the same time" -- extra tasks simply wait their turn instead of all firing immediately.

CONCEPT, part 2 -- One failure shouldn't kill the whole batch:
By default, asyncio.gather() raises the FIRST exception it sees and cancels everything else -- one bad request kills the entire batch. Using gather(..., return_exceptions=True) instead collects exceptions as regular results, so you can process 49 successes even if 1 request failed, rather than losing all 50.
"""

import os
import asyncio
import random
from openai import AsyncOpenAI, RateLimitError, APIError
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

async_client = AsyncOpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

PROMPTS = [
    "What is the capital of France?",
    "What is the capital of Japan?",
    "What is the capital of Brazil?",
    "What is the capital of Egypt?",
    "What is the capital of China?",
    "What is the capital of India?",
    "What is the capital of Russia?",
    "What is the capital of Canada?",
    "What is the capital of Australia?",
    "What is the capital of the United States?",
]
MAX_CONCURRENT_REQUESTS = 3
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

async def ask_with_limits(prompt, index):
    """Wraps a single request: waits for a semaphore slot, then calls the API,
    catching errors so a failure here doesn't blow up the whole batch."""
    async with semaphore:
        print(f"{index} Starting: {prompt}")
        try:
            response = await async_client.chat.completions.create(
                model = MODEL,
                max_tokens = MAX_TOKENS,
                messages = [{"role": "user", "content": prompt}]
            )
            
            result = response.choices[0].message.content
            print(f"{index} Finished: {prompt}")
            return {
                "index": index,
                "prompt": prompt,
                "success": True,
                "result": result
            }
            
        except RateLimitError:
            print(f"[{index}] Rate limited.")
            return {"index": index, "prompt": prompt, "success": False, "error": "rate_limited"}

        except APIError as e:
            print(f"[{index}] API error: {e}")
            return {"index": index, "prompt": prompt, "success": False, "error": str(e)}

async def run_batch():
    tasks = [ask_with_limits(prompt, index) for index, prompt in enumerate(PROMPTS)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

def summarize_results(results):
    successes = [r for r in results if r["success"]]
    failures = [r for r in results if not r["success"]]

    print(f"\n=== Batch Summary ===")
    print(f"Total: {len(results)}  |  Succeeded: {len(successes)}  |  Failed: {len(failures)}")

    if failures:
        print("\nFailed requests:")
        for f in failures:
            print(f"  [{f['index']}] {f['prompt']} -> {f['error']}")


if __name__ == "__main__":
    print(f"Running {len(PROMPTS)} prompts with max {MAX_CONCURRENT_REQUESTS} concurrent requests...\n")
    results = asyncio.run(run_batch())
    summarize_results(results)


