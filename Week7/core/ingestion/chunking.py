"""Three chunking strategies: fixed, recursive, structure-aware (markdown)."""

import re

def fixed_chunk(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    step = max(size - overlap, 1)
    return [text[i:i + size].strip() for i in range(0, len(text), step) if text[i:i + size].strip()]

def recursive_chunk(text: str, size: int = 800, overlap: int = 100,
                    seps: tuple[str, ...] = ("\n\n", "\n", ". ", " ")) -> list[str]:
    if len(text) <= size:
        return [text.strip()] if text.strip() else []
    sep = next((s for s in seps if s in text), None)
    if sep is None:
        return fixed_chunk(text, size, overlap)
    rest = seps[seps.index(sep) + 1:] or (" ",)
    chunks, cur = [], ""
    for part in text.split(sep):
        piece = part + sep
        if len(piece) > size:
            if cur.strip():
                chunks.append(cur.strip()); cur = ""
            chunks.extend(recursive_chunk(part, size, overlap, rest))
        elif len(cur) + len(piece) > size:
            chunks.append(cur.strip())
            cur = (cur[-overlap:] if overlap else "") + piece
        else:
            cur += piece
    if cur.strip():
        chunks.append(cur.strip())
    return chunks

def markdown_sections(text: str) -> list[tuple[str | None, str]]:
    """Split on markdown headings -> [(heading, body)]. Falls back to one section."""
    parts = re.split(r"(?m)^(#{1,6}\s+.+)$", text)
    if len(parts) == 1:
        return [(None, text)]
    out = [(None, parts[0])] if parts[0].strip() else []
    for i in range(1, len(parts), 2):
        out.append((parts[i].lstrip("# ").strip(), parts[i + 1]))
    return out


def chunk_text(text: str, strategy: str = "recursive", size: int = 800,
               overlap: int = 100) -> list[tuple[str | None, str]]:
    """Returns [(section, chunk_text)]."""
    if strategy == "fixed":
        return [(None, c) for c in fixed_chunk(text, size, overlap)]
    if strategy == "structure":
        return [(h, f"{h}\n{c}" if h else c)
                for h, body in markdown_sections(text)
                for c in recursive_chunk(body, size, overlap)]
    return [(None, c) for c in recursive_chunk(text, size, overlap)]