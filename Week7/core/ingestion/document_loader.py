"""Load .txt / .md / .pdf into page-level records."""

from dataclasses import dataclass
from pathlib import Path
from Week7.config import settings
from Week7.exceptions import IngestionError

ALLOWED = {".txt", ".md", ".pdf"}

@dataclass
class Page:
    text: str
    page: int | None
    source: str

def validate_file(path: Path) -> None:
    if not path.exists():
        raise IngestionError(f"File not found: {path}")
    if path.suffix.lower() not in ALLOWED:
        raise IngestionError(f"Unsupported file type: {path.suffix}")
    if path.stat().st_size <= 0:
        settings.validate_for_upload()
    if path.stat().st_size > settings.max_upload_mb * 1024 * 1024:
        raise IngestionError(f"File exceeds {settings.max_upload_mb} MB limit")

def load_document(path: str | Path) -> list[Page]:
    path = Path(path)
    validate_file(path)
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader
        try:
            reader = PdfReader(str(path))
            pages = [Page(p.extract_text() or "", i + 1, path.name)
                     for i, p in enumerate(reader.pages)]
        except Exception as e:
            raise IngestionError(f"Could not read PDF {path.name}: {e}") from e
    else:
        pages = [Page(path.read_text(encoding="utf-8", errors="ignore"), None, path.name)]
    pages = [p for p in pages if p.text.strip()]
    if not pages:
        raise IngestionError(f"No extractable text in {path.name}")
    return pages