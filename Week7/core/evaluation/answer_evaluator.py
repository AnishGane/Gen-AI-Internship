
import json
from Week7.core.generation.llm_service import LLMService

JUDGE_SYS =  ('You are a strict grader. Given a context and an answer, decide whether EVERY factual claim '
             'in the answer is supported by the context. Return ONLY JSON: '
             '{"faithful": true|false, "unsupported_claims": [str]}')

def keyword_correct(answer: str, expected_keywords: list[str]) -> float:
    if not expected_keywords:
        return 1.0
    a = answer.lower()
    return sum(k.lower() in a for k in expected_keywords) / len(expected_keywords)

def judge_faithfulness(
    llm: LLMService,
    context: str,
    answer: str,
) -> bool:
    prompt = f"<context>\n{context}\n</context>\n\nAnswer: {answer}"
    raw = llm.complete(JUDGE_SYS, prompt, max_tokens=300)

    try:
        start = raw.find("{")
        if start == -1:
            return False

        result, _ = json.JSONDecoder().raw_decode(raw[start:])
        return result.get("faithful") is True
    except (json.JSONDecodeError, AttributeError):
        return False

def evaluate_answers(dataset: list[dict], ask_fn, rag_context_fn=None, llm: LLMService | None = None) -> dict:
    """ask_fn(question) -> result dict from RAGService.ask. dataset keys: question, answerable,
    expected_keywords. Optional LLM faithfulness judge when llm + rag_context_fn(result) provided."""
    tot = {"abstain_ok": 0, "keyword_correct": 0.0, "faithful": 0, "judged": 0, "answerable": 0}
    for d in dataset:
        r = ask_fn(d["question"])
        ans = r["answer"]
        if d.get("answerable", True):
            tot["answerable"] += 1
            tot["keyword_correct"] += keyword_correct(ans["answer"], d.get("expected_keywords", []))
            tot["abstain_ok"] += 0 if ans["insufficient_evidence"] else 1
            if llm and rag_context_fn and not ans["insufficient_evidence"]:
                tot["judged"] += 1
                tot["faithful"] += judge_faithfulness(llm, rag_context_fn(r), ans["answer"])
        else:
            tot["abstain_ok"] += 1 if ans["insufficient_evidence"] else 0
    n, na = max(len(dataset), 1), max(tot["answerable"], 1)
    return {"abstention_or_answer_accuracy": round(tot["abstain_ok"] / n, 3),
            "keyword_correctness": round(tot["keyword_correct"] / na, 3),
            "faithfulness": round(tot["faithful"] / tot["judged"], 3) if tot["judged"] else None,
            "n": len(dataset)}
