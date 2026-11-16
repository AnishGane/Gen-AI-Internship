"""Persistent ChromaDB adapter for storing and retrieving embedded chunks."""

from __future__ import annotations

import chromadb

class ChromaVectorStore:
    def __init__(self, path: str, collection_name: str) -> None:
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def replace_source(
        self, filename: str, ids: list[str], texts: list[str], embeddings: list[list[float]],
        metadata: list[dict[str, str | int]],
    ) -> None:
        existing = self.collection.get(where={"filename": filename}, include=[])
        if existing["ids"]:
            self.collection.delete(ids=existing["ids"])
        if ids:
            self.collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadata)

    def search(self, embedding: list[float], *, limit: int) -> list[dict]:
        if self.collection.count() == 0:
            return []
        result = self.collection.query(
            query_embeddings=[embedding], n_results=min(limit, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )
        rows = []
        for index, text in enumerate(result["documents"][0]):
            rows.append({
                "text": text,
                "metadata": result["metadatas"][0][index],
                "distance": result["distances"][0][index],
            })
        return rows
