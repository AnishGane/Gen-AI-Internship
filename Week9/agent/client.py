"""Thin wrapper around the OpenAI SDK pointed at OpenRouter."""
from openai import OpenAI
from Week9.agent.config import BASE_URL, get_api_key

def make_client() -> OpenAI:
    return OpenAI(
        base_url=BASE_URL,
        api_key=get_api_key(),
        max_retries=2,  # SDK retries transient errors / 429s with backoff
        default_headers={"X-Title": "Week 9 Tool Agent"},
    )

def chat(client: OpenAI, messages: list, tools: list, models: list[str]):
    """One model call. `models` is OpenRouter's fallback list: if the first
    model is rate limited or down, OpenRouter tries the next one."""
    response = client.chat.completions.create(
        model=models[0],
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=1000,
        extra_body={"models": models},
    )
    # OpenRouter can return an error payload with no choices.
    if not response.choices:
        raise RuntimeError(f"No choices returned: {response}")
    return response
