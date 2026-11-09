"""Day 2 / Task 3 - LangChain retrieval backed by Qdrant (Week 7 collection).

Usage:
  python 06_langchain_retrieval.py --ingest      # (optional) load data/sample_docs into the QDRANT_COLLECTION
  python 06_langchain_retrieval.py               # retriever + RAG chain + agent with a retrieval tool
"""
import sys
from pathlib import Path
from langchain_core.messages import HumanMessage
from Week8.config import settings
from Week8.lc.agents import build_agent
from Week8.lc.retrieval import build_rag_chain, get_retriever, search_knowledge_base
from Week8.core.tools import calculator, get_current_datetime

project_root = Path(__file__).resolve().parent.parent
data_dir = project_root / "data" / "sample_docs"

if not data_dir.exists():
    raise FileNotFoundError(
        f"Sample documents directory not found: {data_dir}"
    )

def main():
    if "--ingest" in sys.argv:
        from Week8.RAG.ingest import ingest

        confirmation = input(
            f"WARNING: This will delete and rebuild the collection "
            f"'{settings.collection_name}'. Continue? (yes/no): "
        ).strip().lower()

        if confirmation != "yes":
            print("Ingestion cancelled.")
            return

        n = ingest(str([data_dir]), collection=settings.collection_name, recreate=True)
        print(f"Ingested {n} chunks into '{settings.collection_name}'")

    q = "What is the difference between a thread_id and a checkpoint?"

    print("== retriever ==")
    for d in get_retriever(k=3).invoke(q):
        print("-", d.metadata.get("source"), "|", d.page_content[:90].replace("\n", " "))

    print("\n== RAG chain ==")
    print(build_rag_chain().invoke(q))

    print("\n== agent with calculator + retrieval tool ==")
    agent = build_agent([calculator, get_current_datetime, search_knowledge_base])
    for question in ["What is 365 * 24?", "How does Qdrant choose a distance metric?"]:
        out = agent.invoke({"messages": [HumanMessage(question)]})
        print(f"Q: {question}\nA: {out['messages'][-1].content}\n")


if __name__ == "__main__":
    main()
