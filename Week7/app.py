"""CLI:  python app.py ingest docs_sample/policy.md | list | delete <id> | ask "..." | chat | eval | compare"""
import argparse, json, sys
from Week7.core.evaluation.answer_evaluator import evaluate_answers
from Week7.core.evaluation.retrieval_evaluator import evaluate_retrieval
from Week7.core.rag_service import BASELINE, PipelineConfig, RAGService
from Week7.exceptions import RAGError

def show(r: dict):
    print("\nANSWER:", r["answer"]["answer"])
    a = r["answer"]
    print(f"confidence={a['confidence']} insufficient_evidence={a['insufficient_evidence']} citations={a['citations']}")
    for sid, s in r["sources"].items():
        print(f"  [{sid}] {s['source']} p={s['page']} {s['chunk_id']} ret={s['retrieval_score']} rerank={s['rerank_score']}")
    print("timings(ms):", r["timings_ms"], "tokens:", r["tokens"])

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    sub.add_parser("chat"); sub.add_parser("eval"); sub.add_parser("compare")
    for name in ("ingest", "delete", "ask"):
        sp = sub.add_parser(name); sp.add_argument("arg")
    args = p.parse_args()
    svc = RAGService()
    try:
        if args.cmd == "ingest": print(svc.ingest(args.arg))
        elif args.cmd == "list": print(json.dumps(svc.store.list_documents(), indent=2))
        elif args.cmd == "delete": svc.delete(args.arg)
        elif args.cmd == "ask": show(svc.ask(args.arg))
        elif args.cmd == "chat":
            while (q := input("\nyou> ").strip()) not in ("exit", "quit"):
                try: show(svc.ask(q, "cli"))
                except RAGError as e: print("Error:", e)
        elif args.cmd in ("eval", "compare"):
            ds = json.load(open("data/evaluation_dataset.json"))
            configs = {"dense": PipelineConfig("dense", 5, False, False, False, 5),
                       "sparse": PipelineConfig("sparse", 5, False, False, False, 5),
                       "hybrid": PipelineConfig("hybrid", 5, False, False, False, 5),
                       "hybrid+rerank": PipelineConfig("hybrid", 20, False, False, True, 5)}
            for name, cfg in configs.items():
                m = evaluate_retrieval(ds, lambda q, c=cfg: svc.retrieve(q, c)[1])
                print(f"{name:15}", m)
            if args.cmd == "eval":
                print("answers:", evaluate_answers(ds, svc.ask))
    except RAGError as e:
        print("Error:", e); sys.exit(1)

if __name__ == "__main__":
    main()
