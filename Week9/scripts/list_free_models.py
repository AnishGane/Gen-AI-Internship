"""Print the free, tool-capable models available on OpenRouter right now.
"""
from Week9.agent.models import fetch_free_tool_models, pick_models

def main():
    models = fetch_free_tool_models()
    print(f"{len(models)} free models with tool calling:\n")
    for m in models:
        print(f"  {m['id']:<55} context={m['context_length']:>9,}")
    print("\nThe agent will try, in order:", pick_models())

if __name__ == "__main__":
    main()
