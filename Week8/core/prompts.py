"""All prompts are set here"""
from langchain_core.prompts import ChatPromptTemplate

EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You extract structured information from text. Stay faithful to the text; never invent facts."),
    ("human", "Text:\n{text}"),
])

ROUTE_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Classify the user's query.\n"
     "- math: needs arithmetic/calculation\n"
     "- technical: about LangChain, LangGraph, RAG, vector databases, APIs, software\n"
     "- general: anything else (chit-chat, writing, general knowledge)"),
    ("human", "{query}"),
])

MATH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Turn the question into ONE plain arithmetic expression using only numbers and + - * / ** % ( ). "
               "{hint}"),
    ("human", "{query}"),
])

ANSWER_PROMPT_SIMPLE = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. If a tool result or context is given, base your answer on it."),
    ("human", "Question: {query}\n\nTool result / context:\n{context}"),
])

RAG_ROUTE_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Decide whether the question needs the document knowledge base.\n"
     "- knowledge: asks about specific facts, products, technical topics or documents that should be sourced\n"
     "- general: greetings, chit-chat, creative writing, simple reasoning, questions about the conversation itself"),
    ("human", "{question}"),
])

GENERAL_SYSTEM = "You are a friendly, concise assistant. Use the conversation history when relevant."

GRADER_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You grade retrieval quality. Given a question and retrieved passages, rate from 0 to 1 how well the passages "
     "contain the information needed to answer. Set relevant=true only if score >= 0.6. Be strict: topical overlap "
     "without the actual answer is a low score."),
    ("human", "Question: {question}\n\nPassages:\n{context}"),
])

REWRITE_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You rewrite search queries for a vector database. The previous query retrieved weak results. Produce ONE better "
     "query: expand abbreviations, add likely technical terms and synonyms, remove filler. Output only the query."),
    ("human", "Original question: {question}\nPrevious query: {previous_query}\nWhy it was weak: {reason}"),
])

GROUNDED_ANSWER_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Answer using ONLY the numbered passages. Cite passages inline like [1] or [2][3]. "
     "If the passages do not contain the answer, set sufficient_evidence=false and say you could not find it. "
     "Never use outside knowledge. `citations` must list the passage numbers you used."),
    ("human", "Passages:\n{context}\n\nQuestion: {question}"),
])

JUDGE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a strict evaluator. Decide whether the answer is fully supported by the passages."),
    ("human", "Passages:\n{context}\n\nAnswer:\n{answer}"),
])

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Answer ONLY from the context. If it is not there, say you don't know. Cite passages like [1]."),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])