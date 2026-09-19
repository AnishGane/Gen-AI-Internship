from pathlib import Path

from Week6.chunking import chunk_text
from Week6.config import CHUNK_SIZE, CHUNK_OVERLAP, DATA_DIR, DOCUMENT_PATH

def load_document(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def main():

    print(f"CHUNK_SIZE: {CHUNK_SIZE}")
    print(f"CHUNK_OVERLAP: {CHUNK_OVERLAP}")

    all_chunks = []

    for document_path in DOCUMENT_PATH.glob("*.txt"):
        text = load_document(document_path)
        
        print(f"\nDocument: {document_path}") # Document: E:\Gen AI Internship Repo\Week6\data\documents\React.txt
        print(f"\nText: {text}")
        
        chunks = chunk_text(
            text=text,
            source=document_path.name,
            chunk_size=CHUNK_SIZE,
            overlap=CHUNK_OVERLAP,
        )

        all_chunks.extend(chunks)

        print(f"\nDocument: {document_path.name}")
        print(f"Chunks: {len(chunks)}")

        for chunk in chunks:
            print(
                f"\nChunk {chunk.chunk_id}:"
                f"\n{chunk.text}"
            )
            
    print("\n" + "=" * 20)
    print(f"Total chunks: {len(all_chunks)}")

if __name__ == "__main__":
    main()