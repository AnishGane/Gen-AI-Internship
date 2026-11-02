# Week 7 — RAG Learning Roadmap

## Project: Document Intelligence RAG System

**Goal:** Build a working, maintainable RAG application in seven days by extending the Week 6 project built with Qdrant, embeddings, document chunking, and semantic search. The roadmap starts with the real application on Day 1 and adds retrieval optimization, reranking, hybrid search, grounded generation, evaluation, and production practices.

## Day 1 — Build the complete RAG pipeline

**Focus:** Core implementation

**Objective:** Connect the Week 6 Qdrant retrieval system to an LLM and create a reusable RAG service.

### Task 1 — Build document ingestion and indexing

- Reuse the Week 6 document loader, chunker, embedding service, and Qdrant service.
- Improve document metadata with `document_id`, `source`, `chunk_id`, `page`, and `created_at`.
- Create stable document and chunk IDs so a document can be updated or deleted without rebuilding the entire collection.
- **Learn:** Ingestion pipelines, indexing, metadata, and idempotency.

### Task 2 — Build the retrieval and generation pipeline

- Implement the flow: query → embedding → Qdrant retrieval → context construction → LLM → answer.
- Create reusable `LLMService`, `ContextBuilder`, and `RAGService` modules.
- Keep retrieval and generation separate so each can be improved independently.
- **Learn:** RAG architecture, context injection, prompt construction, and retrieval-generation separation.

### Task 3 — Test the end-to-end system

- Ask at least 10 questions about your own documents.
- Include questions whose answers are present, partially present, and absent.
- Display the answer, source documents, chunk IDs, retrieval scores, and execution time.
- **Learn:** Grounding, source traceability, and failure analysis.

**Deliverable:** A working RAG pipeline that answers questions using the Week 6 documents.

## Day 2 — Advanced retrieval engineering

**Focus:** Retrieval optimization

**Objective:** Improve what the system retrieves before trying to improve the LLM's answer.

### Task 1 — Improve chunking and metadata

- Compare fixed-size, recursive, and structure-aware chunking.
- Experiment with chunk size and overlap.
- Preserve headings, page numbers, document IDs, and section metadata.
- **Learn:** Parent-child chunking, semantic chunking, metadata filtering, and chunk boundaries.

### Task 2 — Implement query rewriting and multi-query retrieval

- Rewrite vague questions into clearer search queries.
- Generate multiple search queries from one user question.
- Retrieve results for each query, merge them, and deduplicate by stable point ID.
- **Learn:** Query expansion, query rewriting, multi-query retrieval, and retrieval diversity.

### Task 3 — Implement metadata filtering and retrieval tuning

- Filter by document, category, source, or other metadata.
- Compare `top_k` values of 3, 5, 10, and 20.
- Experiment with similarity thresholds where appropriate.
- Record which settings retrieve the most useful chunks.
- **Learn:** Top-K selection, metadata-aware retrieval, score calibration, and recall versus precision.

**Deliverable:** An improved retrieval service that can rewrite questions, retrieve multiple candidate sets, filter, and deduplicate results.

## Day 3 — Reranking and context engineering

**Focus:** Advanced RAG

**Objective:** Retrieve broadly, then select the strongest evidence before sending it to the LLM.

### Task 1 — Implement a reranking system

- Retrieve 15–30 candidate chunks from Qdrant.
- Rerank them using a cross-encoder or a supported reranking API/model.
- Compare the original retrieval order with the reranked order.
- **Learn:** Cross-encoder reranking, bi-encoder versus cross-encoder, and two-stage retrieval.

### Task 2 — Implement context compression and selection

- Remove duplicate and near-duplicate chunks.
- Remove irrelevant sentences from otherwise useful chunks.
- Limit context using a token budget.
- Preserve source IDs and document metadata during compression.
- **Learn:** Contextual compression, token budgeting, redundancy reduction, and evidence selection.

### Task 3 — Build an advanced context builder

- Combine the best reranked chunks while preserving document and section relationships.
- Order evidence logically and stay within the LLM's context window.
- Compare answers generated from raw retrieved chunks with answers generated from reranked, compressed context.
- **Learn:** Context ordering, context assembly, and the lost-in-the-middle problem.

**Deliverable:** A two-stage retrieval pipeline that retrieves candidates, reranks them, and constructs high-quality context.

## Day 4 — Grounded generation and hallucination control

**Focus:** Answer reliability

**Objective:** Make the LLM answer from evidence rather than produce plausible but unsupported information.

### Task 1 — Implement grounded answer generation

- Create a strict system prompt that requires answers to use only retrieved evidence.
- Instruct the model to distinguish facts, inferences, and missing information.
- Treat retrieved document text as untrusted input.
- **Learn:** Grounding, prompt injection in retrieved content, instruction hierarchy, and evidence-based generation.

### Task 2 — Implement citations and structured responses

- Require citations such as `[S1]` and `[S2]`.
- Create a Pydantic response model with fields such as `answer`, `citations`, `confidence`, and `insufficient_evidence`.
- Validate that every cited source ID exists in the retrieved context.
- **Learn:** Structured output, Pydantic validation, citation attribution, and source verification.

### Task 3 — Implement abstention and hallucination tests

- Return an explicit insufficient-evidence response when documents do not support an answer.
- Test misleading, contradictory, and incomplete documents.
- Test prompt-injection text embedded in documents.
- Check whether each factual claim is supported by a cited chunk.
- **Learn:** Abstention, faithfulness, hallucination detection, and contradiction handling.

**Deliverable:** A grounded RAG system that produces structured answers, validates citations, and refuses unsupported questions.

## Day 5 — Hybrid search and advanced retrieval strategies

**Focus:** Industry retrieval patterns

**Objective:** Go beyond dense semantic search and learn how production retrieval systems combine search methods.

### Task 1 — Implement BM25 keyword search

- Learn how BM25 ranks documents using keyword frequency and document statistics.
- Implement keyword retrieval alongside dense vector retrieval.
- Test exact terms, technical names, IDs, and phrases.
- **Learn:** Sparse retrieval, lexical search, BM25, and dense versus sparse retrieval.

### Task 2 — Implement hybrid search and Reciprocal Rank Fusion

- Combine dense and BM25 results.
- Implement Reciprocal Rank Fusion (RRF).
- Compare dense-only, BM25-only, and hybrid retrieval.
- **Learn:** Hybrid retrieval, rank fusion, RRF, and retrieval diversity.

### Task 3 — Implement advanced retrieval filters and reranking integration

- Combine hybrid search with metadata filters.
- Rerank the fused candidates.
- Measure whether the additional stages improve the final results.
- **Learn:** Multi-stage retrieval, candidate generation, reranking after fusion, and retrieval pipelines.

**Deliverable:** A hybrid retrieval system combining semantic search, keyword search, result fusion, and reranking.

> **Qdrant project note:** Hybrid search may require a collection with sparse-vector configuration or a full-text payload index. Plan for a new collection and reindexing rather than assuming the existing dense-only collection supports it. See the [Qdrant hybrid and multi-stage queries documentation](https://qdrant.tech/documentation/hybrid-queries/).

## Day 6 — RAG evaluation, conversation memory, and testing

**Focus:** Quality measurement

**Objective:** Measure whether the RAG system is improving and identify which stage needs work.

### Task 1 — Create a RAG evaluation dataset

- Prepare at least 30–50 questions from your documents.
- Include expected answers and the document/chunk IDs containing the evidence.
- Include answerable, unanswerable, ambiguous, and multi-document questions.
- **Learn:** Golden datasets, test cases, ground truth, and offline evaluation.

### Task 2 — Implement retrieval and generation evaluation

- Measure `Recall@K`, `Precision@K`, and `MRR`.
- Measure context precision and context recall.
- Measure answer faithfulness, response relevancy, and answer correctness.
- Compare dense-only, hybrid, and reranked retrieval.
- **Learn:** Retrieval metrics, generation metrics, and evaluation frameworks such as [Ragas](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/).

These metrics assess different failure points. A good answer score alone cannot show whether retrieval or generation caused a problem.

### Task 3 — Implement conversation memory and regression tests

- Store conversation history separately from document knowledge.
- Rewrite follow-up questions using relevant conversation history.
- Keep the original question available for answer generation.
- Run the evaluation dataset after changes to catch regressions.
- **Learn:** Conversational RAG, history-aware retrieval, regression testing, and repeatability.

**Deliverable:** An evaluation suite that measures retrieval and answer quality and supports multi-turn conversations.

## Day 7 — Production-ready RAG application

**Focus:** Capstone

**Objective:** Turn the learning project into a maintainable application resembling a real-world RAG service.

### Task 1 — Build a reusable application interface

- Create a CLI or FastAPI interface.
- Support document ingestion, updates, deletion, and question answering.
- Separate API routes, services, models, configuration, and database access.
- **Learn:** Service architecture, API design, separation of concerns, and reusable components.

### Task 2 — Implement reliability, observability, and security

- Add structured logging and exception handling.
- Record retrieval latency, generation latency, token usage, and errors.
- Add timeouts, retry policies, and configuration validation.
- Validate uploaded files and restrict document access where applicable.
- Protect API keys and prevent retrieved content from overriding system instructions.
- **Learn:** Observability, latency, cost monitoring, access control, and prompt-injection defense.

### Task 3 — Run final system checks and document the project

- Run the complete evaluation dataset.
- Test empty queries, missing documents, failed embeddings, LLM errors, and malformed outputs.
- Compare the original Day 1 pipeline with the final pipeline.
- Write a README covering architecture, setup, environment variables, usage, limitations, and evaluation results.
- **Learn:** End-to-end testing, performance measurement, deployment readiness, and technical documentation.

**Deliverable:** A complete Document Intelligence RAG application with ingestion, advanced retrieval, grounded generation, evaluation, and operational logging.

## Recommended project structure

Keep reusable application code separate from daily learning and testing scripts. This is a target structure; add modules as you reach the relevant tasks rather than creating every file on Day 1.

```text
Week7/
├── core/
│   ├── ingestion/
│   │   ├── document_loader.py
│   │   ├── document_processor.py
│   │   └── chunking.py
│   ├── retrieval/
│   │   ├── dense_search.py
│   │   ├── bm25_search.py
│   │   ├── hybrid_search.py
│   │   ├── query_rewriter.py
│   │   └── reranker.py
│   ├── generation/
│   │   ├── llm_service.py
│   │   ├── context_builder.py
│   │   └── answer_generator.py
│   ├── evaluation/
│   │   ├── retrieval_evaluator.py
│   │   └── answer_evaluator.py
│   └── rag_service.py
├── day1/
├── day2/
├── day3/
├── day4/
├── day5/
├── day6/
├── day7/
├── data/
│   └── evaluation_dataset.json
├── tests/
├── config.py
├── models.py
├── exceptions.py
├── logger.py
├── .env.example
└── README.md
```

---

1. **logger.py**

```python
import json
import logging
import sys
import time
from contextlib import contextmanager
```

- `json` converts log data into JSON text.
- `logging` provides Python’s logging system.
- `sys.stderr` is where the log messages will be written.
- `time.perf_counter()` provides a precise clock for measuring elapsed time.
- `contextmanager` lets you use a function with Python’s with statement.

`JSONFormatter`:

```python
class JSONFormatter(logging.Formatter):
    def format(self, record):
        data = {
            "ts": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        data.update(getattr(record, "extra_fields", {}))

        if record.exc_info:
            data["exc"] = self.formatException(record.exc_info)

        return json.dumps(data, default=str)
```

- When Python’s logging system handles a log record, this formatter makes a dictionary containing the time, level, and message, then converts it to JSON.
- `getattr(record, "extra_fields", {})` looks for extra fields attached to the record. If there aren’t any, it uses an empty dictionary.
- If the log record includes exception details, the formatter adds them under "exc". default=str converts values that JSON cannot encode directly into strings.

`get_logger`:

```python
def get_logger(name: str = "rag") -> logging.Logger:
    log = logging.getLogger(name)

    if not log.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(JSONFormatter())
        log.addHandler(handler)
        log.setLevel(logging.INFO)

    return log
```

- This gets or creates a named logger. It adds a JSON-formatted output handler only if the logger doesn’t already have one, which helps avoid duplicate log lines.

`log_event`:

```python
def log_event(log: logging.Logger, msg: str, **fields):
    log.info(msg, extra={"extra_fields": fields})
```

- `**fields` collects additional named values into a dictionary.

**Example**:
```python
log_event(logger, "Search completed", top_k=5, result_count=12)
```

- This produces a log record containing the message plus the top_k and result_count fields.

`timer`:

```python
@contextmanager
def timer(store: dict, key: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        store[key] = round((time.perf_counter() - start) * 1000, 1)
```

This measures how long a block takes and saves the elapsed time in milliseconds. The finally block runs even if the code inside the timer raises an error.

**Example**:

```python
timings = {}

with timer(timings, "retrieval_ms"):
    results = search_documents("How does Qdrant work?")

print(timings["retrieval_ms"])
```

---

2. `embeddings.py`:

- `__init__` loads the dense and sparse models and keeps them on the service object. The `FastEmbed` imports are inside the constructor, so FastEmbed is imported when you create the service.
- `embed_dense(texts)` returns one dense vector per text.
- `embed_sparse(texts)` returns one Qdrant sparse vector per document text.
- `embed_sparse_query(query)` returns a sparse vector for a single query. It uses query_embed, which lets the sparse model process a search query separately from document text.

`get_embedder`:

```python
@lru_cache(maxsize=1)
def get_embedder() -> EmbeddingService:
    return EmbeddingService()
```

- The first call creates the service and loads the models. The cache holds that instance so later calls reuse it.

**For example**:

```python
embedder = get_embedder()

dense_vectors = embedder.embed_dense(["Qdrant stores vectors."])
sparse_vectors = embedder.embed_sparse(["Qdrant stores vectors."])
query_vector = embedder.embed_sparse_query("vector database")
```

> One thing to keep in mind: dense and sparse vectors need corresponding vector configurations in your Qdrant collection before you can store and search them together.

**Understand**:

`Dense & Sparse Embedding` give Qdrant two ways to find relevant document chunks:
- `Dense embeddings` capture meaning. A question like “How do I make a website interactive?” may find a chunk about JavaScript even if it doesn’t use the exact same words.
- Sparse embeddings capture keyword matches. They’re useful when the query includes exact terms such as Qdrant, a product name, an error code, or a specific phrase.
In this code, embed_dense() creates dense vectors for text, while embed_sparse() creates BM25-style sparse vectors for documents. embed_sparse_query() creates a sparse vector for a user’s search query.

Together, they support hybrid search: dense search finds meaning-related content, and sparse search finds keyword-related content. Qdrant can combine their results so retrieval works well for both kinds of queries.