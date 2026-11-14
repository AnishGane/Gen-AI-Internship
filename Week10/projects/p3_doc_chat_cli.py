"""PROJECT 3 - Chat with your documents (CLI): ingest -> persistent multi-thread chat with citations.

  uv run .\Week8\projects\p3_doc_chat_cli.py --ingest .\Week8\data\sample_docs\langgraph_overview.md     # (re)build the collection from .md/.txt/.pdf
  uv run .\Week8\projects\p3_doc_chat_cli.py --thread alice         # chat; history persists in SQLite per thread
Commands inside the chat: /new  /sources  /quit
"""

import argparse
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from Week10.lg.memory import get_checkpointer
from Week10.RAG.workflow import ask, build_rag_graph

def main():
    ap = argparse.ArgumentParser(
        description="Chat with your documents using persistent RAG."
    )

    ap.add_argument(
        "--ingest",
        nargs="+",
        help="Files or folders to ingest before starting chat."
    )

    ap.add_argument(
        "--recreate",
        action="store_true",
        help="Delete and rebuild the existing collection before ingestion."
    )

    ap.add_argument(
        "--thread",
        default="default",
        help="Conversation thread ID."
    )

    args = ap.parse_args()

    if args.recreate and not args.ingest:
        ap.error("--recreate requires --ingest.")

    if args.ingest:
        from Week10.RAG.ingest import ingest

        if args.recreate:
            confirmation = input(
                "WARNING: This will delete the existing collection. "
                "Continue? (yes/no): "
            ).strip().lower()

            if confirmation != "yes":
                print("Ingestion cancelled.")
                return

        chunks = ingest(args.ingest, recreate=args.recreate)

        mode = "recreated" if args.recreate else "appended"
        print(f"Successfully {mode} collection. Chunks processed: {chunks}")

    graph = build_rag_graph(
        checkpointer=get_checkpointer("sqlite"),
        adaptive=True
    )

    thread, last = args.thread, {}

    print(f"Thread '{thread}' - type a question (/new, /sources, /quit)")

    while True:
        try:
            q = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not q:
            continue

        if q == "/quit":
            break

        if q == "/new":
            thread = f"{args.thread}-{uuid.uuid4().hex[:6]}"
            print("New thread:", thread)
            continue

        if q == "/sources":
            for s in last.get("sources", []):
                print(f" [{s['id']}] {s['source']}: {s['snippet'][:120]}...")
            continue

        last = ask(graph, q, thread)

        print(f"\nbot> {last['answer']}")

        if last.get("rewrites"):
            print(
                f" (retrieval retried {len(last['rewrites'])}x "
                "with rewritten queries)"
            )

if __name__ == "__main__":
    main()