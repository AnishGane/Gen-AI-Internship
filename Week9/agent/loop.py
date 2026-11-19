"""The tool cycle: request -> run -> return result -> final answer."""
from Week9.agent.client import chat
from Week9.agent.tools import TOOL_SCHEMAS, execute_tool

SYSTEM_PROMPT = (
    "You are a careful assistant. For any arithmetic, use the provided tools "
    "instead of calculating in your head. Use the current-time tool for time "
    "questions. For explanations or opinions, just answer directly."
)

def _assistant_message(msg) -> dict:
    """Rebuild the assistant turn explicitly (safer across providers than dumping the object)."""
    return {
        "role": "assistant",
        "content": msg.content or "",
        "tool_calls": [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
            }
            for tc in msg.tool_calls
        ],
    }

def run_agent(client, models: list[str], user_prompt: str, max_steps: int = 5, verbose: bool = True) -> str:
    """Run the loop until the model answers without requesting a tool."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    for step in range(1, max_steps + 1):
        response = chat(client, messages, TOOL_SCHEMAS, models)
        msg = response.choices[0].message

        if verbose:
            print(f"\n[step {step}] model used: {getattr(response, 'model', '?')}")

        if not msg.tool_calls:  # plain answer: we're done
            return msg.content or ""

        messages.append(_assistant_message(msg))
        for tc in msg.tool_calls:
            result = execute_tool(tc.function.name, tc.function.arguments)
            if verbose:
                print(f"  model requested: {tc.function.name}({tc.function.arguments})")
                print(f"  our program ran it -> {result}")
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    return "Stopped: reached max_steps without a final answer."
