"""Rewrite a query that retrieved weak results."""
from langchain_core.output_parsers import StrOutputParser

from Week10.core.llm import get_llm
from Week10.core.prompts import REWRITE_PROMPT

def rewrite_query(question: str, previous_query: str, reason: str) -> str:
    chain = REWRITE_PROMPT | get_llm(temp=0.3) | StrOutputParser()
    new = chain.invoke({"question": question, "previous_query": previous_query, "reason": reason}).strip()
    return new.strip('"') or question
