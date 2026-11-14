from langchain.agents import create_agent
from Week10.core.llm import get_llm
from Week10.core.tools import calculator, get_current_datetime, search_text

SYSTEM_PROMPT = (
    "You are a helpful assistant with tools. Use `calculator` for ANY arithmetic, "
    "a search tool for knowledge questions, and `get_current_datetime` for date/time. "
    "Never guess numbers. If tools return nothing useful, say so."
)

def build_agent(tools: list | None = None, checkpointer=None):
    tools = tools or [calculator, get_current_datetime, search_text]
    return create_agent(model=get_llm(), tools=tools, system_prompt=SYSTEM_PROMPT, checkpointer=checkpointer)