"""
Multi-Tool Selection and tool_choice (via OpenRouter)

Task 1 gave the model exactly one tool. Real applications usually offer SEVERAL tools, and the model has to pick the right one (or several) based on what's actually being asked -- that decision-making is the interesting part of tool use, not just the mechanics of one function call.


This script covers three things Task 1 didn't:
1. Multiple distinct tools, and letting the model choose which (if any) to use.
2. Forcing the model to use a SPECIFIC tool via `tool_choice`.
3. Handling MULTIPLE tool calls returned in a single response (one user question needing both tools at once).
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

# Two local functions the model can choose between 

def calculate(expression: str) -> str:
    allowed_chars = set("0123456789+-*/(). ")
    if not set(expression) <= allowed_chars:
        return "Error: invalid characters in expression"
    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"
    
def get_weather(city: str) -> str:
    fake_data = {
        "tokyo": "18°C, light rain",
        "kathmandu": "22°C, partly cloudy",
        "new york": "9°C, clear skies",
    }
    
    return fake_data.get(city.lower(), f"No weather data found for {city}")

def get_current_time(timezone_label: str) -> str:
    return f"(Simulated) current time for {timezone_label} is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

TOOLS = [{
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
},
{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather in a given city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The name of the city to check the weather for.",
                }
            },
            "required": ["city"],
        }
    }     
},{
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "Get the current time in a given timezone.",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone_label": {
                    "type": "string",
                    "description": "The label of the timezone to get the current time for.",
                }
            },
            "required": ["timezone_label"],
        }
    }
}]

AVAILABLE_FUNCTIONS = {
    "calculate": calculate,
    "get_weather": get_weather,
    "get_current_time": get_current_time
}

def run_with_tools(user_message, tool_choice="auto"):
    """
    tool_choice options:
    "auto"     -> model decides whether/which tool to use (default)
    "none"     -> model must NOT use any tool, answers directly
    {"type": "function", "function": {"name": "..."}}  -> force a SPECIFIC tool
    """
    messages = [
        {"role": "system", "content": "Use the available tools whenever they'd give a more accurate answer than guessing."},
        {"role": "user", "content": user_message},
    ]

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=messages,
        tools=TOOLS,
        tool_choice=tool_choice,
    )
    
    choice = response.choices[0]
    tool_calls = choice.message.tool_calls
    
    if not tool_calls:
        # Model answered directly, no tool needed
        return choice.message.content
    
    # Record the assistant's tool-call request
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
    
    # Handle EVERY tool call returned -- there can be more than one at once
    print(f"  (model requested {len(tool_calls)} tool call(s): {[tc.function.name for tc in tool_calls]})")
    for tool_call in tool_calls:
        func_name = tool_call.function.name
        func_arg = json.loads(tool_call.function.arguments)
        
        if func_name not in AVAILABLE_FUNCTIONS:
            return f"Error: unknown function {func_name}"
        else:
            result = AVAILABLE_FUNCTIONS[func_name](**func_arg)
            
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        })
        
    final_response = client.chat.completions.create(
        model=MODEL, max_tokens=MAX_TOKENS, messages=messages,
    )
    return final_response.choices[0].message.content


if __name__ == "__main__":
    print("=== Auto: should pick calculate ===")
    print(run_with_tools("What is 156 divided by 12?"))

    print("\n=== Auto: should pick get_weather ===")
    print(run_with_tools("What's the weather like in Tokyo right now?"))

    print("\n=== Auto: needs BOTH tools in one turn ===")
    print(run_with_tools("What's the weather in Kathmandu, and what's the current time there?"))

    print("\n=== Forced tool_choice: force calculate even for a non-math question ===")
    print(run_with_tools(
        "Tell me something interesting.",
        tool_choice={"type": "function", "function": {"name": "calculate"}},
    ))

    print("\n=== tool_choice='none': model must NOT use any tool ===")
    print(run_with_tools("What's the weather in New York?", tool_choice="none"))