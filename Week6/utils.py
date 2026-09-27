from Week6.config import CHUNK_SIZE, CHUNK_OVERLAP, DOCUMENT_PATH
from Week6.chunking import chunk_text
from Week6.models import EvaluationQuery

def load_documents():
    chunks = []

    for document_path in DOCUMENT_PATH.glob("*.txt"):
        text = document_path.read_text(encoding="utf-8")

        document_chunks = chunk_text(
            text = text,
            source = document_path.name,
            chunk_size = CHUNK_SIZE,
            overlap = CHUNK_OVERLAP,
        )

        chunks.extend(document_chunks)

    return chunks

EVALUATION_DATASET = [

    EvaluationQuery(
        query="What is Python used for?",
        expected_sources={"python.txt"},
    ),

    EvaluationQuery(
        query="What is React?",
        expected_sources={"React.txt"},
    ),

    EvaluationQuery(
        query="How is React used?",
        expected_sources={"React.txt"},
    ),

    EvaluationQuery(
        query="Which language is used for artificial intelligence?",
        expected_sources={"python.txt"},
    ),

]