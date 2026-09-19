from Week6.config import CHUNK_SIZE, CHUNK_OVERLAP, DOCUMENT_PATH
from Week6.chunking import chunk_text

def load_documents():
    chunks = []

    for document_path in DOCUMENT_PATH.glob("*.txt"):
        text = document_path.read_text(encoding="utf-8")

        chunks = chunk_text(
            text = text,
            source = document_path.name,
            chunk_size = CHUNK_SIZE,
            overlap = CHUNK_OVERLAP,
        )

        chunks.extend(chunks)

    return chunks