"""Orchestrates embedding, vector retrieval, and grounded answer generation."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from openai import OpenAI

from Week8.config import Settings
from Week8.core.documents import Document, chunk_documents
from Week8.core.embeddings import EmbeddingService
from Week8.core.vector_store import ChromaVectorStore

NO_CONTEXT = "I couldn't find relevant information in the indexed documents. Try rephrasing your question or indexing a document that covers it."

@dataclass(frozen=True)
class RAGAnswer:
    answer: str
    sources: tuple[dict, ...]

class RAGPipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenAI(
            api_key=settings.api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={"HTTP-Referer": "http://localhost:8501", "X-Title": "Document RAG Learning App"},
        )
        self.embeddings = EmbeddingService(settings.embedding_model)
        self.store = ChromaVectorStore(settings.index_path, settings.collection_name)

    def index_documents(self, documents: list[Document]) -> int:
        chunks = chunk_documents(
            documents, chunk_size=self.settings.chunk_size, overlap=self.settings.chunk_overlap
        )
        indexed = 0
        for document in documents:
            source_chunks = [chunk for chunk in chunks if chunk.filename == document.filename]
            texts = [chunk.text for chunk in source_chunks]
            vectors = self.embeddings.embed(texts)
            ids = [
                hashlib.sha256(f"{chunk.filename}:{chunk.chunk_index}:{chunk.text}".encode()).hexdigest()
                for chunk in source_chunks
            ]
            metadata = [
                {"filename": chunk.filename, "chunk_index": chunk.chunk_index}
                for chunk in source_chunks
            ]
            self.store.replace_source(document.filename, ids, texts, vectors, metadata)
            indexed += len(texts)
        return indexed

    def ask(self, question: str) -> RAGAnswer:
        question = question.strip()
        if not question:
            return RAGAnswer("Please enter a question.", ())
        query_vector = self.embeddings.embed([question])[0]
        matches = self.store.search(query_vector, limit=self.settings.top_k)
        relevant = [row for row in matches if row["distance"] <= self.settings.max_cosine_distance]
        if not relevant:
            return RAGAnswer(NO_CONTEXT, ())

        source_rows = []
        context_parts = []
        for source_id, row in enumerate(relevant, start=1):
            metadata = row["metadata"]
            source_rows.append({
                "id": source_id,
                "filename": metadata["filename"],
                "chunk_index": metadata["chunk_index"],
                "text": row["text"],
            })
            context_parts.append(f"[{source_id}] {metadata['filename']}\n{row['text']}")

        response = self.client.chat.completions.create(
            model=self.settings.chat_model,
            temperature=0,
            messages=[
                {"role": "system", "content": (
                    "Answer using only the supplied document excerpts. If the excerpts do not support "
                    "an answer, say you do not know. Cite every factual claim with its source number, "
                    "for example [1]. Do not invent citations."
                )},
                {"role": "user", "content": f"Question: {question}\n\nExcerpts:\n" + "\n\n".join(context_parts)},
            ],
        )
        answer = response.choices[0].message.content or NO_CONTEXT
        return RAGAnswer(answer, tuple(source_rows))
