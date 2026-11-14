"""Day 1 / Task 3 - LCEL composition: prompt | model | parser, streaming, async, parallel, retry/fallback."""
import asyncio

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel

from Week10.core.llm import get_llm
from Week10.lc.chains import build_extraction_chain, build_text_chain

TEXTS = [
    "LangGraph lets you build stateful agents as graphs with checkpoints and human approval steps.",
    "The central bank raised interest rates by 25 basis points, citing persistent services inflation.",
]

def main():
    # 1) Structured chain + a RunnableLambda that converts the Pydantic object to a plain dict
    extractor = build_extraction_chain() | RunnableLambda(lambda info: info.model_dump())
    print(extractor.invoke({"text": TEXTS[0]}))

    # 2) batch: run on many inputs concurrently
    for out in extractor.batch([{"text": t} for t in TEXTS], config={"max_concurrency": 2}):
        print(out["title"], "|", out["category"])

    # 3) streaming a text chain
    print("\nstreaming: ", end="")
    for token in build_text_chain().stream({"question": "Explain LCEL in two sentences."}):
        print(token, end="", flush=True)
    print("\n")

    # 4) RunnableParallel: same input to several branches at once
    llm = get_llm()
    parallel = RunnableParallel(
        summary=ChatPromptTemplate.from_template("Summarize in 10 words: {text}") | llm | StrOutputParser(),
        sentiment=ChatPromptTemplate.from_template("One word sentiment (positive/neutral/negative): {text}")
        | llm | StrOutputParser(),
    )
    print(parallel.invoke({"text": TEXTS[1]}))

    # 5) resilience: retry transient failures, fall back to another chain
    resilient = extractor.with_retry(
        stop_after_attempt=3,
        retry_if_exception_type=(
            TimeoutError,
            ConnectionError,
        ),
    )

    result = resilient.invoke({"text": TEXTS[0]})

    print("Retry-wrapped chain ok:", bool(result))

    # 6) async
    async def run_async():
        results = await asyncio.gather(*[extractor.ainvoke({"text": t}) for t in TEXTS])
        print("async results:", [r["title"] for r in results])

    asyncio.run(run_async())

    # Inspect the chain structure
    print(extractor.get_graph().draw_ascii())

if __name__ == "__main__":
    main()
