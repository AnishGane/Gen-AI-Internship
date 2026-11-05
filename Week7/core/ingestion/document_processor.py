"""Idempotent ingestion: stable document IDs + stable chunk/point IDs."""
import hashlib, uuid
from pathlib import Path
from Week7.config import settings
from Week7.core.embeddings import get_embedder
from Week7.core.ingestion.chunking import chunk_text
from Week7.core.ingestion.document_loader import load_document
from Week7.core.vector_store import VectorStore
from Week7.logger import get_logger, log_event
from Week7.models import Chunk

log = get_logger("ingest")
NS = uuid.UUID("6f1c2a52-0000-4000-8000-000000000007")

def document_id_for(path: Path) -> str:
    return hashlib.sha1(path.name.encode()).hexdigest()[:12]

def point_id_for(document_id: str, chunk_index: int) -> str:
    return str(uuid.uuid5(NS, f"{document_id}:{chunk_index}"))  # Qdrant needs UUID/int

class DocumentProcessor:
    def __init__(self, store: VectorStore, strategy: str = "recursive"):
        self.store, self.strategy = store, strategy

    def ingest(self, path: str | Path) -> dict:
        """Ingest or UPDATE a document. Old chunks are removed first, so re-running is safe."""
        path = Path(path)
        pages = load_document(path)
        doc_id = document_id_for(path)
        chunks, idx = [], 0
        for page in pages:
            for section, text in chunk_text(page.text, self.strategy, settings.chunk_size, settings.chunk_overlap):
                chunks.append(Chunk(point_id=point_id_for(doc_id, idx), document_id=doc_id,
                                    source=path.name, chunk_id=f"{doc_id}-{idx:04d}", chunk_index=idx,
                                    page=page.page, section=section, text=text))
                idx += 1
        emb = get_embedder()
        texts = [c.text for c in chunks]
        self.store.ensure_collection()
        self.store.delete_document(doc_id)          # idempotent update
        self.store.upsert(chunks, emb.embed_dense(texts), emb.embed_sparse(texts))
        log_event(log, "ingested", document_id=doc_id, source=path.name, chunks=len(chunks))
        return {"document_id": doc_id, "source": path.name, "chunks": len(chunks)}

    def delete(self, document_id: str) -> None:
        self.store.delete_document(document_id)
        log_event(log, "deleted", document_id=document_id)