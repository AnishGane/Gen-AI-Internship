"""Reusable LCEL chains."""
from langchain_core.output_parsers import StrOutputParser
from Week10.core.llm import get_llm
from Week10.core.prompts import EXTRACTION_PROMPT
from Week10.models import Extracted_info

def build_extraction_chain():
    """text -> prompt -> model(structured) -> ExtractedInfo (Pydantic-validated)."""
    structured_llm = get_llm().with_structured_output(Extracted_info, method="function_calling")
    return EXTRACTION_PROMPT | structured_llm


def build_text_chain(system: str = "You are a concise assistant."):
    """question -> prompt -> model -> str (good for streaming demos)."""
    from langchain_core.prompts import ChatPromptTemplate

    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "{question}")])
    return prompt | get_llm(temp=0.3) | StrOutputParser()