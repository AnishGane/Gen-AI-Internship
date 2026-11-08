
"""Load documents, split them, generate embeddings, and store them in Qdrant."""
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from Week8.config import settings
from Week8.core.llm import get_embeddings

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "sample_docs"

def load_documents(paths: list[str]):
    files: list[Path] = []

    for p in map(Path, paths):
        if p.is_dir():
            files.extend(
                f for f in p.rglob("*")
                if f.is_file() and f.suffix.lower() in {".md", ".txt", ".pdf"}
            )
        elif p.is_file():
            if p.suffix.lower() in {".md", ".txt", ".pdf"}:
                files.append(p)

    documents = []

    for file in sorted(files):
        loader = (
            PyPDFLoader(str(file))
            if file.suffix.lower() == ".pdf"
            else TextLoader(str(file), encoding="utf-8")
        )

        loaded_documents = loader.load()

        for document in loaded_documents:
            resolved = file.resolve()
            try:
                document.metadata["source"] = resolved.relative_to(DATA_DIR.resolve()).as_posix()
            except ValueError:
                document.metadata["source"] = resolved.name

        documents.extend(loaded_documents)

    return documents

def ingest(
    paths: list[str],
    collection: str | None = None,
    recreate: bool = False,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> int:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    documents = load_documents(paths)

    if not documents:
        raise ValueError("No supported documents found.")

    chunks = splitter.split_documents(documents)

    if not chunks:
        raise ValueError("Document splitting produced no chunks.")

    print(f"Documents loaded: {len(documents)}")
    print(f"Chunks generated: {len(chunks)}")

    for index, chunk in enumerate(chunks):
        print(f"Chunk {index + 1}: {len(chunk.page_content)} characters")

    QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        collection_name=collection or settings.collection_name,
        content_payload_key=settings.qdrant_content_key,
        force_recreate=recreate,
    )

    return len(chunks)

if __name__ == "__main__":
    import sys

    paths = sys.argv[1:] or [str(DATA_DIR)]

    total_chunks = ingest(
        paths,
        recreate=False,
    )

    print(f"{total_chunks} chunks ingested successfully.")
