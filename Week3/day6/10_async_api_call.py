"""
Async API Calls (via OpenRouter)

Sending API requests one at a time (sequentially) means total time = sum of each individual request's time. `asyncio` lets you fire multiple requests CONCURRENTLY instead -- while one is waiting on the network, others can proceed -- so total time is closer to the SLOWEST single request, not the sum of all of them.
"""

import os
import time
import asyncio
from openai import OpenAI, AsyncOpenAI
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

sync_client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

async_client = AsyncOpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

PROMPTS = [
    "What is the capital of France?",
    "What is the capital of Japan?",
    "What is the capital of Brazil?",
    "What is the capital of Egypt?",
]

def ask_sync(prompt):
    response = sync_client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content

async def ask_async(prompt):
    response = await async_client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS, 
        messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content

def run_sequential():
    start = time.time()
    results = [ask_sync(p) for p in PROMPTS]
    elapsed = time.time() - start
    return results, elapsed

async def run_concurrent():
    start = time.time()
    results = await asyncio.gather(*[ask_async(p) for p in PROMPTS])
    elapsed = time.time() - start
    return results, elapsed

if __name__ == "__main__":
    print("=== Sequential (one at a time) ===")
    seq_results, seq_time = run_sequential()
    for r in seq_results:
        print("-, r")
    print(f"Sequential time: {seq_time:.2f}s\n")

    print("=== Concurrent (multiple at once) ===")
    conc_results, conc_time = asyncio.run(run_concurrent())
    for r in conc_results:
        print("-", r)
    print(f"Concurrent time: {conc_time:.2f}s")

    print(f"\nSpeedup: {seq_time / conc_time:.2f}x faster")
