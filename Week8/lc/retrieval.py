from functools import lru_cache
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import tool
from langchain_qdrant import QdrantVectorStore
from Week8.config import settings
from Week8.core.llm import get_embeddings, get_llm
from Week8.core.prompts import RAG_PROMPT

@lru_cache(maxsize=1)
def get_vector_store(collection: str | None = None) -> QdrantVectorStore:
    return QdrantVectorStore.from_existing_collection(
        embedding=get_embeddings(),
        collection_name=collection or settings.collection_name,
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        content_payload_key=settings.qdrant_content_key,
        vector_name=settings.qdrant_vector_name,
        validate_collection_config=False,
    )

def get_retriever(k: int = settings.top_k):
    return get_vector_store().as_retriever(search_kwargs={"k": k})

def format_docs(docs: list[Document]) -> str:
    return "\n\n".join(f"[{i}] ({d.metadata.get('source', 'unknown')}) {d.page_content}" for i, d in enumerate(docs, 1))

def build_rag_chain():
    """Classic RAG with LCEL: question -> retriever -> prompt -> model -> text."""
    return (
        {"context": get_retriever() | format_docs, "question": RunnablePassthrough()}
        | RAG_PROMPT
        | get_llm()
        | StrOutputParser()
    )

@tool
def search_knowledge_base(query: str) -> str:
    """Search the document knowledge base (Qdrant) for facts. Use for knowledge/technical questions."""
    docs = get_retriever().invoke(query)
    return format_docs(docs) if docs else "No relevant documents found."