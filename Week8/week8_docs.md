# Week 8: Document RAG application

A reusable Streamlit app built from scratch around the Week 5–7 concepts:

1. **Embeddings and semantic search (Week 5):** OpenAI embeddings turn text chunks and questions into vectors.
2. **Vector database (Week 6):** ChromaDB stores vectors and metadata locally and searches by cosine distance.
3. **RAG (Week 7):** retrieved excerpts are passed to a chat model, instructed to answer only from them and cite sources.
4. **Reliability (Week 8):** the UI handles unreadable or empty documents, configuration and API errors, and no relevant context.

## Project layout

```text
app.py                 Streamlit interface
config.py              Settings and validation
core/documents.py      PDF/text/Markdown parsing and chunking
core/embeddings.py     Embedding provider adapter
core/vector_store.py   Persistent ChromaDB adapter
core/pipeline.py       Indexing, retrieval, and grounded generation
```

The UI is separate from ingestion, embedding, storage, and question answering; `core/` can be imported in another Python program.

## Setup and run

Requires Python 3.10 or newer and an Openrouter API key. API usage may incur charges.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
uv run pip install -r requirements.txt
uv run streamlit run app.py
```

Enter your key in the sidebar. Alternatively, add `OPENROUTER_API_KEY = "..."` to `.streamlit/secrets.toml` (do not commit this file). Upload PDF, TXT, or Markdown documents, select **Index documents**, then ask a question. Scanned/image-only PDFs need OCR and currently produce an empty-text warning.

The vector index persists in `.rag_index/`. The sidebar lets you select another local path and model names. If you change the embedding model while reusing an index, clear the index first so all vectors use the same embedding space.

## Retrieval behavior and limits

Documents are normalized and split into overlapping 800-character chunks (120-character overlap by default). Chunks and filename/chunk-number metadata are stored in a cosine-distance Chroma collection. The app returns the five closest chunks by default and drops matches with distance above `0.75`. This is a starting cutoff, not a calibrated confidence score; tune it against your documents. If all matches are filtered out, the app abstains rather than asking the model to guess.

Answers include source-number citations and the UI shows the exact retrieved text. The model is instructed to use only retrieved excerpts, but output can still be wrong; check the citations against the displayed passages. The local vector database is not encrypted or access-controlled. This is a learning project, not a multi-user production service.

## Question-based manual evaluation

After indexing a small document set, try these questions and record the actual answer and sources in your internship notes:

| Check | Example question | Expected behavior |
| --- | --- | --- |
| Direct fact | “What is the stated renewal period?” | Answer the fact and cite the passage containing it. |
| Semantic paraphrase | “How often does the plan renew?” | Retrieve the same passage despite different wording; cite it. |
| Multi-passage | “What are the deadline and responsible team?” | Answer only details supported by retrieved passages and cite them. |
| Out of scope | “What is the capital of France?” (when absent) | Show the no-relevant-context response without citations. |

These are evaluation prompts, not recorded execution results. Run them against your uploaded documents after setup; results depend on your files and model responses.
