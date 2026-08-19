"""
Function calling / Tool use (via OpenRouter)

Function calling lets the model request that YOUR code run a specific function, then feed the result back so the model can use it in its final answer. The model never actually executes code -- it just outputs "please call this function with these arguments," and your program decides whether to actually do it.

This is how LLM apps get real-time data (weather, database lookups, calculator results) instead of guessing.

IMPORTANT CAVEAT: not all free models support tool calling reliably -- this is a real limitation of smaller/free models. If `tool_calls` comes back empty even for obviously math-related prompts, try a specific model tagged as supporting tools on https://openrouter.ai/models instead of the "openrouter/free" auto-router.

"""

import os
from openai import OpenAI
import json
from Week2.config import API_KEY, BASE_URL, MODEL, MAX_TOKENS

client = OpenAI(
    base_url = BASE_URL,
    api_key = API_KEY
)

def calculate(expression: str) -> str:
    """
    The actual local function the model can request to be run.
    """
    allowed_chars= set("0123456789+-*/(). ")
    if not set(expression) <= allowed_chars:
        return "Error: invalid characters in expression"
    
    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"
    
# Describe the function to the model in the standard tool-calling schema
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a basic arithmetic expression and return the numeric result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A math expression, e.g. '23 * 47 + 10'",
                    }
                },
                "required": ["expression"],
            }
        }
    }
]

AVAILABEL_FUNCTIONS = {"calculate": calculate}

def run_with_tools(user_message):
    messages = [
        {"role": "system", "content": "Use the calculate tool for any arithmetic instead of computing it yourself."},
        {"role": "user", "content": user_message}
    ]
    
    response = client.chat.completions.create(
        model = MODEL,
        max_tokens = MAX_TOKENS,
        messages = messages,
        tools=TOOLS,
    )
    
    choice = response.choices[0]
    tool_calls = choice.message.tool_calls
    
    if not tool_calls:
        # Model answered directly, no tool needed
        return choice.message.content

    # Record the assistant's tool-call request in the conversation
    messages.append({
            "role": "assistant",
            "content": choice.message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }   
                for tc in tool_calls
            ]
        })
    
    # Actually run each requested function locally, and feed results back
    for tool_call in tool_calls:
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)

        if func_name in AVAILABEL_FUNCTIONS:
            result = AVAILABEL_FUNCTIONS[func_name](**func_args)
        else:
            result = f"Error: unknown function {func_name}"
            
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result
        })
        
    # Second call: model produces a final answer using the tool's result
    final_response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=messages,
    )
    return final_response.choices[0].message.content

if __name__ == "__main__":
    print("=== Should trigger the calculate tool ===")
    print(run_with_tools("What is 84 times 37, plus 15?"))
    
    print("\n=== Should NOT need the tool ===")
    print(run_with_tools("What's the capital of Japan?"))