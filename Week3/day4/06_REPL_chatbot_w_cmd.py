"""
REPL Chatbot with Special Commands (via OpenRouter)

Real CLI chat tools support special commands alongside normal messages (e.g. Claude Code's /help, /clear). This is a common CLI UX pattern: anything starting with "/" is a command handled locally; everything else is a message sent to the model.
"""

import os
import json
from datetime import datetime
from openai import OpenAI
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

SYSTEM_PROMPT = "Respond with ONLY valid JSON, no other text, no markdown formatting."

HELP_TEXT = """Available commands:
  /help      Show this help message
  /reset     Clear conversation history (keeps system prompt)
  /history   Print the full conversation so far
  /save      Save conversation to a JSON file
  /quit      Exit the chatbot
Anything else is sent to the model as a normal message.
"""

class ChatSession:
    def __init__(self, system_prompt = "You are a helpful assistant."):
        self.system_prompt = system_prompt
        self.history = [{"role": "system", "content": system_prompt}]
        
    def reset(self):
        self.history = [{"role": "system", "content": self.system_prompt}]
        
    def send(self, user_input):
        self.history.append({"role": "user", "content": user_input})
        response = client.chat.completions.create(model=MODEL, max_tokens=MAX_TOKENS, messages=self.history)
        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})
        return reply
    
    def print_history(self):
        for msg in self.history:
            print(f"[{msg['role']}] {msg['content']}")
            
    def save(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(os.path.dirname(__file__), f"session_{timestamp}.json")
        with open(filepath, "w") as f:
            json.dump(self.history, f, indent=2)
        return filepath

def run_repl():
    session = ChatSession()
    print("Chatbot REPL started. Type /help for commands.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        
        if user_input.startswith("/"):
            command = user_input.lower()
            if command == "/quit":
                print("Goodbye!")
                break
            elif command == "/help":
                print(HELP_TEXT)
            elif command == "/reset":
                session.reset()
                print("Conversation history cleared.")
            elif command == "/history":
                session.print_history()
            elif command == "/save":
                path = session.save()
                print(f"Saved to {path}")
            else:
                print(f"Unknown command: {user_input}. Type /help for options.")
            continue
        
        reply = session.send(user_input)
        print(f"Bot: {reply}\n")
        
if __name__ == "__main__":
    run_repl()