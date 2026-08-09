"""
First API Call (via OpenRouter)

An LLM API call is just an HTTP request: We send a prompt(as JSON), the provider runs it through a model, and it sends back the JSON response containing the generated text + metadatas like total token count, model used, why it stopped generating, etc.

WHAT WE DO BELOW:
- Sends one message to a free OpenRouter model and prints both the response and the metadata around it.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url = "https://openrouter.ai/api/v1",
    api_key = os.getenv("OPENROUTER_API_KEY")
)

MODEL = "openrouter/free"
USER_PROMPT = "Explain what a large language model is, in 3 sentences."
SYSTEM_PROMPT = "Answer directly and concisely, without showing your reasoning or thinking process."

response = client.chat.completions.create(
    model=MODEL,
    max_tokens=300,
    messages=[
        {
            "role": "user",
            "content": USER_PROMPT
        }, 
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]
)

# print the generated text
print("\n--- Response ---")
print(response.choices[0].message.content)


# Useful things to inspect while you're learning:
print("\n--- Metadata ---")
print("Model used:", response.model)
print("Finish reason:", response.choices[0].finish_reason)
print("Input tokens:", response.usage.prompt_tokens)
print("Output tokens:", response.usage.completion_tokens)
print("Total tokens:", response.usage.total_tokens)

"""
- prompt_tokens: the number of tokens in the prompt
- completion_tokens: the number of tokens in the completion
- total_tokens: the total number of tokens in the prompt and completion. This total is what counts against a model's context window on every single call.
"""