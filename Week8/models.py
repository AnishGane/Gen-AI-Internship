from dataclasses import dataclass

@dataclass(frozen=True)
class Document:
    filename: str
    text: str

@dataclass(frozen=True)
class TextChunk:
    filename: str
    chunk_index: int
    text: str