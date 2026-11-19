"""Step 2: the optional extension. Several tools, several steps, one loop.
"""
import sys

from Week9.agent.client import make_client
from Week9.agent.loop import run_agent
from Week9.agent.models import pick_models

DEFAULT = "Multiply 238 by 417, then add 1000 to that, then divide the total by 7."

def main():
    prompt = " ".join(sys.argv[1:]) or DEFAULT
    models = pick_models()
    print("Models (priority order):", models)
    print("Question:", prompt)
    answer = run_agent(make_client(), models, prompt)
    print("\nFinal answer:", answer)

if __name__ == "__main__":
    main()
