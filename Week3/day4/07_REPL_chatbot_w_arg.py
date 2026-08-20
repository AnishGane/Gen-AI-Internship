"""
REPL Commands with Arguments + Session Load/Undo (via OpenRouter)

Task 1's commands were all standalone (/reset, /save, /history -- no extra input needed). Real CLI tools also need commands that take
ARGUMENTS: /system <new prompt>, /temp <value>. Parsing "command + rest of the line" is a different (and more common) pattern than matching exact fixed strings.

This version also adds:
- /load <filename>  -- resume a PREVIOUSLY saved session (pairs with Task 1's /save -- together they make sessions actually persistent across separate runs of the program, not just within one run).
- /undo  -- remove the last user+assistant exchange, useful if a reply went off-topic and you don't want it polluting future context.
"""

import os
import json
import glob
from datetime import datetime
from openai import OpenAI
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)

HELP_TEXT = """Available commands:
  /help              Show this help message
  /reset             Clear conversation history (keeps current system prompt)
  /history           Print the full conversation so far
  /save              Save conversation to a JSON file
  /load <filename>   Load a previously saved session (filename only, not full path)
  /system <prompt>   Change the system prompt for the rest of the conversation
  /temp <value>      Change the sampling temperature (0.0-1.0)
  /undo              Remove the last user+assistant exchange
  /quit              Exit the chatbot
Anything else is sent to the model as a normal message.
"""

class ChatSession:
    def __init__(self, system_prompt="You are a helpful assistant", temperature=0.7):
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.history = [{"role": "system", "content": system_prompt}]

    def reset(self):
        self.history = [{"role": "system", "content": self.system.prompt}]

    def set_system_prompt(self, new_prompt):
        self.system_prompt = new_prompt
        self.history[0] = [{"role": "system", "content": new_prompt}]

    def undo_last_exchange(self):
        # Remove the most recent user+assistant pair, if one exists
        if len(self.history) >= 3:
            self.history = self.history[:-2] 
            return True
        return False

    def send(self, user_input):
        self.history.append({"role": "user", "content": user_input})
        response = client.chat.completions.create(
            model = MODEL,
            max_tokens = MAX_TOKENS,
            temperature = self.temperature,
            messages = self.history
        )
        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})
        return reply
    
    def print_history(self):
        for msg in self.history:
            print(f"[{msg['role']}] {msg['content']}")

    def save(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(SESSIONS_DIR, f"session_{timestamp}.json")
        with open(filepath, "w") as f:
            json.dump({"system_prompt": self.system_prompt, "history": self.history}, f, indent = 2)
        return filepath

    def load(self, filename):
        filepath = os.path.join(SESSIONS_DIR, filename)
        if not os.path.exists(filepath):
            matches = glob.glob(os.path.join(SESSIONS_DIR, f"{filename}*.json"))
            if not matches:
                return False
            filepath = matches[0]
        
        with open(filepath, "r") as f:
            data = json.load(f)
        self.system_prompt = data["system_prompt"]
        self.history = data["history"]
        return True

def parse_command(user_input):
    """Split '/command rest of the line' into ('/command', 'rest of the line')."""
    parts = user_input.split(maxsplit=1)
    command = parts[0].lower()
    argument = parts[1] if len(parts) > 1 else ""
    return command, argument

def run_repl():
    session = ChatSession()
    print("Chatbot REPL started. Type /help for commands.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue

        if user_input.startswith("/"):
            command, argument = parse_command(user_input)

            if command == "/quit":
                print("GOODBYE!")
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

            elif command == "/load":
                if not argument:
                    print("Usage: /load <filename>")
                elif session.load(argument):
                    print(f"Loaded session '{argument}'. {len(session.history)} messages restored.")
                else:
                    print(f"No saved session found matching '{argument}'.")

            elif command == "/system":
                if not argument:
                    print("Usage: /system <new prompt text>")
                
                else:
                    session.set_system_prompt(argument)
                    print(f"System prompt updated to: {argument}")

            elif command == "/temp":
                try:
                    value = float(argument)
                    if 0.0 <= value <= 1.0:
                        session.temperature = value
                        print(f"Temperature set to {value}")
                    else:
                        print("Temperature must be between 0.0 and 1.0")
                except ValueError:
                    print("Usage: /temp <number between 0.0 and 1.0>")

            elif command == "/undo":
                if session.undo_last_exchange():
                    print("Removed the last exchange.")
                else:
                    print("Nothing to undo.")

            else: 
                print(f"Unknown command: {command}. Type /help for options.")

            continue

        reply = session.send(user_input)
        print(f"Bot: {reply}\n")

if __name__ == "__main__":
    run_repl()