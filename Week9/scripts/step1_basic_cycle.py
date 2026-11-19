"""Step 1: the tool cycle written out by hand (mirrors the Week 9 handout).

One tool, one request, one result, one final answer. Every stage is printed
so you can fill in the trace in notes/learning_notes.md.

Run:  python -m scripts.step1_basic_cycle
"""
from Week9.agent.client import chat, make_client
from Week9.agent.models import pick_models
from Week9.agent.tools import TOOL_SCHEMAS, execute_tool

QUESTION = "What is 238 multiplied by 417? Use the calculator."

def main():
    client = make_client()
    models = pick_models()
    print("Models (priority order):", models)

    only_multiply = [t for t in TOOL_SCHEMAS if t["function"]["name"] == "multiply_numbers"]
    messages = [{"role": "user", "content": QUESTION}]

    # (1)+(2) We describe the tool; the model chooses whether to request it.
    first = chat(client, messages, only_multiply, models)
    msg = first.choices[0].message
    if not msg.tool_calls:
        print("Model answered directly (no tool request):", msg.content)
        return
    call = msg.tool_calls[0]
    print(f"\nModel REQUESTED: {call.function.name}({call.function.arguments})")

    # (3) Our program executes the function. The model cannot do this itself.
    result = execute_tool(call.function.name, call.function.arguments)
    print("Our program RAN it, result:", result)

    # (4) Send the model's request plus our result back.
    messages.append(
        {
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {"name": call.function.name, "arguments": call.function.arguments},
                }
            ],
        }
    )
    messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    # (5) The model writes the final answer using the result.
    second = chat(client, messages, only_multiply, models)
    print("\nClaude-style final answer:", second.choices[0].message.content)

if __name__ == "__main__":
    main()
