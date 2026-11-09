"""Day 2 / Task 2 - how tool selection works, then the same thing with create_agent."""
from langchain_core.messages import HumanMessage, ToolMessage

from Week8.core.llm import get_llm
from Week8.core.tools import calculator, get_current_datetime, search_text
from Week8.lc.agents import build_agent

TOOLS = [calculator, get_current_datetime, search_text]

def manual_tool_loop(question: str):
    """What an agent does internally: model -> tool calls -> run tools -> model -> final answer."""
    llm = get_llm().bind_tools(TOOLS)  # sends tool schemas along with the prompt
    registry = {t.name: t for t in TOOLS}
    messages = [HumanMessage(question)]
    for _ in range(5):  # hard cap = bounded loop
        ai = llm.invoke(messages)
        messages.append(ai)
        if not ai.tool_calls:
            return ai.content
        for call in ai.tool_calls:
            print(f"   model chose tool: {call['name']}({call['args']})")
            result: ToolMessage = registry[call["name"]].invoke(call)  # passing the call returns a ToolMessage
            messages.append(result)
    return "stopped: too many steps"

def main():
    print("== manual loop ==")
    print(manual_tool_loop("What is 17.5% of 2480?"))

    print("\n== create_agent ==")
    agent = build_agent()
    for q in ["What is 2 ** 16 divided by 8?", "According to the docs, what does a checkpointer do?", "Hi!"]:
        print("\nQ:", q)
        for step in agent.stream({"messages": [HumanMessage(q)]}, stream_mode="values"):
            step["messages"][-1].pretty_print()

if __name__ == "__main__":
    main()
