"""
CLI Chatbot with argparse (via OpenRouter)

Real CLI tools take flags instead of hardcoded values or interactive prompts -- this makes a script scriptable, testable, and usable in pipelines (e.g. `python bot.py --prompt "..." --temperature 0.2`). `argparse` is Python's standard library tool for this.

We also introduce a `ChatSession` class -- instead of loose functions and a raw list, the conversation state and config live together in one reusable object.
"""

import os
from openai import OpenAI
import argparse
from Week2.config import API_KEY, BASE_URL, MODEL as DEFAULT_MODEL, MAX_TOKENS as DEFAULT_MAX_TOKENS

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

class ChatSession:
    """Bundles a model config and conversation history together."""

    def __init__(self, system_prompt, model, temperature, max_tokens):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.history = [{"role": "system", "content": system_prompt}]
        
    def send(self, user_input):
        self.history.append({"role": "user", "content": user_input})
        response = client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=self.history,
        )
        
        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})
        return reply
    
def build_parser():
    parser = argparse.ArgumentParser(description="A configurable command-line chatbot.")
    parser.add_argument("--prompt", type=str, required=True, help="The message to send to the model.")
    parser.add_argument("--system", type=str, default="You are a helpful assistant.", help="System prompt / persona.")
    parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature (0.0-1.0).")
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS, help="Max tokens in the response.")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Model ID to use.")
    return parser

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    
    session = ChatSession(
        system_prompt = args.system,
        model = args.model,
        temperature = args.temperature,
        max_tokens = args.max_tokens
    )
    
    reply = session.send(args.prompt)
    print(reply)