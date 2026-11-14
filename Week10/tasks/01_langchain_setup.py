from langchain_core.messages import HumanMessage, SystemMessage
from Week10.core.llm import get_llm
import asyncio

def main():
    llm = get_llm()

    # 1) invoke: a string becomes a HumanMessage
    print("invoke  ->", llm.invoke("Say hello in one short sentence.").content)

     # 2) message types: System / Human / (AI, Tool)
    messages = [SystemMessage("You are terse."), HumanMessage("What is LangChain in one sentence?")]
    resp = llm.invoke(messages)
    print("messages->", resp.content)
    print("usage   ->", resp.usage_metadata)

    # 3) stream: tokens arrive as chunks
    print("stream  -> ", end="")
    for chunk in llm.stream("Count from 1 to 5, comma separated."):
        print(chunk.content, end="", flush=True)
    print()

    # 4) batch: several inputs, run concurrently
    for r in llm.batch(["Capital of France? One word.", "Capital of Japan? One word."]):
        print("batch   ->", r.content)

    # 5) async
    async def amain():
        r = await llm.ainvoke("Name one programming language.")
        print("async   ->", r.content)

    asyncio.run(amain())

if __name__ == "__main__":
    main()