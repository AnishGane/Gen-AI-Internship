"""Tools the model may request.

The model never runs these. It only returns a structured request; our code
validates it and runs the matching function (see execute_tool).
"""
import json
from datetime import datetime, timezone

# ---- 1. The real Python functions ------------------------------------------
def add_numbers(a: float, b: float) -> float:
    return a + b

def subtract_numbers(a: float, b: float) -> float:
    return a - b

def multiply_numbers(a: float, b: float) -> float:
    return a * b

def divide_numbers(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def get_utc_time() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

# ---- 2. Schemas shown to the model (OpenAI/OpenRouter "function" format) ----
def _math_schema(name: str, description: str) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "The first number"},
                    "b": {"type": "number", "description": "The second number"},
                },
                "required": ["a", "b"],
            },
        },
    }

TOOL_SCHEMAS = [
    _math_schema("add_numbers", "Add two numbers and return the exact sum."),
    _math_schema("subtract_numbers", "Subtract b from a and return the exact result."),
    _math_schema("multiply_numbers", "Multiply two numbers and return the exact product."),
    _math_schema("divide_numbers", "Divide a by b and return the exact quotient."),
    {
        "type": "function",
        "function": {
            "name": "get_utc_time",
            "description": "Get the current date and time in UTC.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

# ---- 3. Registry: the ONLY functions the model is allowed to trigger --------
TOOL_REGISTRY = {
    "add_numbers": add_numbers,
    "subtract_numbers": subtract_numbers,
    "multiply_numbers": multiply_numbers,
    "divide_numbers": divide_numbers,
    "get_utc_time": get_utc_time,
}

MATH_TOOLS = {"add_numbers", "subtract_numbers", "multiply_numbers", "divide_numbers"}

def execute_tool(name: str, raw_arguments: str | dict | None) -> str:
    """Validate and run a requested tool. Always returns a JSON string.

    Errors are returned as {"error": ...} so the model can recover
    instead of the whole program crashing.
    """
    func = TOOL_REGISTRY.get(name)
    if func is None:
        return json.dumps({"error": f"Unknown tool: {name}"})

    try:
        if isinstance(raw_arguments, dict):
            args = raw_arguments
        else:
            args = json.loads(raw_arguments or "{}")
        if not isinstance(args, dict):
            raise ValueError("Arguments must be a JSON object")

        if name in MATH_TOOLS:
            for key in ("a", "b"):
                if key not in args:
                    raise ValueError(f"Missing argument: {key}")
                if isinstance(args[key], bool) or not isinstance(args[key], (int, float)):
                    raise ValueError(f"Argument {key} must be a number")
            result = func(float(args["a"]), float(args["b"]))
        else:
            result = func()
        return json.dumps({"result": result})
    except Exception as exc:
        return json.dumps({"error": str(exc)})
