from Week6.config import CHUNK_SIZE, CHUNK_OVERLAP
from Week6.exceptions import DocumentProcessingError
from Week6.models import DocumentChunk

def chunk_text(
    text: str,
    source: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[DocumentChunk]:
    """
    Split text into overlapping word-based chunks.
    """

    if not text.strip():
        raise DocumentProcessingError(
            "Cannot chunk empty text."
        )
        
    if chunk_size <= 0:
        raise DocumentProcessingError(
            "Chunk size must be greater than 0."
        )

    if overlap < 0:
        raise DocumentProcessingError(
            "Overlap must be greater than or equal to 0."
        )

    if overlap >= chunk_size:
        raise DocumentProcessingError(
            "overlap must be smaller than chunk_size."
        )

    words = text.spilt()

    chunks: list[DocumentChunk] = []

    step = chunk_size - overlap

    for chunk_id, start in enumerate(
        range(0, len(words), step)
    ):
        chunk_words = words[
            start: start + chunk_size
        ]

        if not chunk_words:
            continue

        chunks.append(
            DocumentChunk(
                text = " ".join(chunk_words),
                source = source,
                chunk_id = chunk_id
            )
        )

    return chunks