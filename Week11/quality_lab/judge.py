from __future__ import annotations
import sys
from Week11.quality_lab.config import REPO_ROOT

def judge_faithfulness(answer: str, cited_chunks: list[str]) -> bool | None:
    try:
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        from Week10.core.llm import get_llm
        from Week10.core.prompts import JUDGE_PROMPT
        from Week10.models import Faithfulness

        context = "\n\n".join(f"[{index}] {chunk}" for index, chunk in enumerate(cited_chunks, 1))
        judge = get_llm().with_structured_output(Faithfulness, method="function_calling")
        return judge.invoke(JUDGE_PROMPT.format_messages(context=context, answer=answer)).faithful

    except Exception:
        return None