"""Document parsing and overlapping chunk creation."""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from typing import Iterable
from Week8.models import Document, TextChunk

def parse_uploads(uploads: Iterable[object]) -> tuple[list[Document], list[str]]:
    """Extract UTF-8 text and PDF text from Streamlit UploadedFile-like objects."""
    documents: list[Document] = []
    warnings: list[str] = []
    for upload in uploads:
        name = getattr(upload, "name", "uploaded-file")
        raw = upload.getvalue()
        try:
            suffix = name.lower().rsplit(".", 1)[-1]
            if suffix == "pdf":
                from pypdf import PdfReader

                reader = PdfReader(io.BytesIO(raw))
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
            elif suffix in {"txt", "md"}:
                text = raw.decode("utf-8-sig")
            else:
                warnings.append(f"{name}: unsupported file type; skipped.")
                continue
        except Exception as exc:
            warnings.append(f"{name}: could not read file ({exc}); skipped.")
            continue
        text = text.strip()
        if text:
            documents.append(Document(filename=name, text=text))
        else:
            warnings.append(f"{name}: no extractable text found; skipped.")
    return documents, warnings

def chunk_documents(
    documents: Iterable[Document], *, chunk_size: int = 800, overlap: int = 120
) -> list[TextChunk]:
    """Split text by character windows with overlap; retain source and chunk number."""
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Require chunk_size > 0 and 0 <= overlap < chunk_size.")
    chunks: list[TextChunk] = []
    step = chunk_size - overlap
    for document in documents:
        normalized = re.sub(r"\s+", " ", document.text).strip()
        for index, start in enumerate(range(0, len(normalized), step)):
            text = normalized[start : start + chunk_size].strip()
            if text:
                chunks.append(TextChunk(document.filename, index, text))
            if start + chunk_size >= len(normalized):
                break
    return chunks
