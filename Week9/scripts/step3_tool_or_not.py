"""Step 3: when does a tool help, and when is a prompt enough?

Both questions get the same tools. Watch which ones trigger a tool request.
"""
from Week9.agent.client import make_client
from Week9.agent.loop import run_agent
from Week9.agent.models import pick_models

QUESTIONS = [
    "What is 48213 times 9157?",                       # exact arithmetic -> tool
    "Explain what multiplication means to a 10-year-old.",  # explanation -> no tool
    "What is the current date and time in UTC?",        # current info -> tool
]

def main():
    client, models = make_client(), pick_models()
    for q in QUESTIONS:
        print("\n" + "=" * 70 + f"\nQ: {q}")
        print("A:", run_agent(client, models, q))

if __name__ == "__main__":
    main()
