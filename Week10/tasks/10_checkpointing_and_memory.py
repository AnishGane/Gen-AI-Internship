"""Day 4 / Task 1 - checkpointer + thread_id (short-term memory) and a Store (long-term memory)."""
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore

from Week10.core.llm import get_llm
from Week10.lg.memory import get_checkpointer

def chat(state: MessagesState, config: RunnableConfig, *, store: BaseStore) -> dict:
    # Long-term memory: facts about the USER that outlive any single thread
    user_id = config["configurable"].get("user_id", "anon")
    item = store.get(("users", user_id), "profile")
    profile = item.value if item else {}
    system = SystemMessage(f"You are a helpful assistant. Known user profile: {profile or 'none'}. Be brief.")
    return {"messages": [get_llm().invoke([system, *state["messages"]])]}

def build_graph(checkpointer, store):
    b = StateGraph(MessagesState)
    b.add_node("chat", chat)
    b.add_edge(START, "chat")
    b.add_edge("chat", END)
    return b.compile(checkpointer=checkpointer, store=store)

def ask(graph, text, thread, user="alice") -> str:
    cfg = {"configurable": {"thread_id": thread, "user_id": user}}
    return graph.invoke({"messages": [HumanMessage(text)]}, cfg)["messages"][-1].content

def main():
    store = InMemoryStore()
    store.put(("users", "alice"), "profile", {"preferred_language": "English", "likes": "Python"})
    graph = build_graph(get_checkpointer("memory"), store)

    print("[thread A]", ask(graph, "Hi, my name is Priya.", "thread-A"))
    print("[thread A]", ask(graph, "What is my name?", "thread-A"))       # remembers (same thread)
    print("[thread B]", ask(graph, "What is my name?", "thread-B"))       # does NOT know (new thread)
    print("[thread B]", ask(graph, "What language do I like?", "thread-B"))  # long-term store knows

    cfg = {"configurable": {"thread_id": "thread-A"}}
    snapshot = graph.get_state(cfg)
    print("\nmessages saved in thread-A:", len(snapshot.values["messages"]), "| next:", snapshot.next)
    print("checkpoints in history:", len(list(graph.get_state_history(cfg))))

if __name__ == "__main__":
    main()
