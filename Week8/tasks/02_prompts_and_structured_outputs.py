from pydantic import ValidationError
from Week8.models import Extracted_info
from Week8.lc.chains import build_extraction_chain
from Week8.core.prompts import EXTRACTION_PROMPT

SAMPLE = """Qdrant, the open-source vector database, announced a new release that speeds up filtered search.
Developers building retrieval-augmented generation apps can now combine payload filters with HNSW indexes
with much lower latency, which matters for production chatbots serving many tenants."""

def main():
    # A prompt template is just a function: variables -> list of messages.
    print(EXTRACTION_PROMPT.format_messages(text="hello world"))

    chain = build_extraction_chain()
    result: Extracted_info = chain.invoke(
        {"text": SAMPLE}
    )

    print(type(result).__name__)
    print(result.model_dump_json(indent=2))

    # Validation protects downstream code from bad model output:
    try:
        Extracted_info.model_validate({"title": "x", "summary": "y", "keywords": ["a"], "category": "sports"})
    except ValidationError as e:
        print("Validation caught bad output:", e.error_count(), "errors")

if __name__ == "__main__":
    main()