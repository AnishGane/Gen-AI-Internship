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

### Task 3 — Implement abstention(choosing not to answer rather than guessing) and hallucination tests

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

---

**1.** `logger.py`

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

**2.** `embeddings.py`:

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

---

**3.** `llm_service.py`:

This class sends prompts to OpenRouter through its OpenAI-compatible API. It tracks token usage and retries certain temporary failures.

**Setup**

The imports load the OpenAI client, your settings, your app’s `LLMError`, and the logging helpers.

```python
settings.validate_for_llm()
```

checks required configuration before the client is created. Then:

```python
self.client = OpenAI(
    api_key=settings.openrouter_api_key,
    base_url=settings.base_url,
    timeout=settings.llm_timeout_s,
    max_retries=0,
)
```

creates the client pointed at OpenRouter. `max_retries`= 0 disables the client’s automatic retries because this class has its own retry loop. `self.usage` starts counters for successful calls and reported token usage.

`complete()`

This method takes a system prompt and a user prompt, sends them to the configured model, and returns the model’s text response.

```python
response = self.client.chat.completions.create(
    model=settings.llm_model,
    messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ],
    max_tokens=max_tokens,
    temperature=temperature,
)

answer = response.choices[0].message.content
```

- If usage data is present, prompt_tokens and completion_tokens are added to the counters. Then the method returns the text, or an empty string if the response has no text.

**Retries and errors**
- The loop makes up to settings.llm_max_retries attempts. Connection errors, timeouts, rate limits, and server errors are treated as temporary: they’re logged, then retried after a delay that grows with each attempt (2**attempt seconds).
- Other OpenAI API errors are wrapped as app’s LLMError and raised immediately. If all retry attempts fail, the method raises LLMError with the last failure.

---

**4.** `answer_evaluator.py`:

- This code evaluates RAG answers in three ways: `did the system answer or abstain appropriately`, `did the answer include expected keywords`, and `did a model judge consider its claims supported by the retrieved context?`

**Keyword score**

```python
def keyword_correct(answer: str, expected_keywords: list[str]) -> float:
    if not expected_keywords:
        return 1.0

    answer_lower = answer.lower()
    return sum(
        keyword.lower() in answer_lower
        for keyword in expected_keywords
    ) / len(expected_keywords)
```

- This returns a score from `0.0` to `1.0`. For example, if two of four expected keywords appear in the answer, the score is 0.5. It checks for simple text matches, not whether the keywords are used correctly.

**Faithfulness judge**

- **JUDGE_SYS** asks the LLM to decide whether every factual claim in an answer is supported by the supplied context, and to respond in JSON.

`judge_faithfulness()` sends the context and answer to your LLMService, tries to parse the JSON, and returns the judge’s faithful value. If parsing fails, it returns False.

```python
def judge_faithfulness(
    llm: LLMService,
    context: str,
    answer: str,
) -> bool:
    prompt = f"<context>\n{context}\n</context>\n\nAnswer: {answer}"
    raw = llm.complete(JUDGE_SYS, prompt, max_tokens=300)

    try:
        start = raw.find("{")
        if start == -1:
            return False

        result, _ = json.JSONDecoder().raw_decode(raw[start:])
        return result.get("faithful") is True
    except (json.JSONDecodeError, AttributeError):
        return False
```

- `raw_decode()` reads one JSON object from the response, even if the model adds text before it.

**Evaluate a dataset**

- `evaluate_answers()` runs ask_fn for every dataset question. It expects each call to return something shaped roughly like:

```python
{
    "answer": {
        "answer": "The answer text...",
        "insufficient_evidence": False,
    }
}
```

- For answerable questions, it adds the keyword score and checks that the system did not abstain. For unanswerable questions, it checks that the system did abstain.
- If both `llm` and `rag_context_fn` are supplied, it also asks the judge to score each non-abstained answer. `rag_context_fn(result)` should return the context that was used to produce that result.

The returned metrics are:
- `abstention_or_answer_accuracy`: how often the system made the right answer versus abstain decision.
- `keyword_correctness`: average expected-keyword match for answerable questions.
- `faithfulness`: share of judged answers the LLM marked faithful, or None if no answers were judged.
- `n`: number of dataset questions.

---

*5.* `retrieval_evaluator.py`:

This code measures retrieval quality: whether your search finds the right documents, how many it finds, and how high they appear in the results.

The “golden dataset” is a set of test questions with the filenames that should be relevant to each question. For example:

```python
{
    "question": "How do I configure Qdrant?",
    "relevant_sources": ["qdrant_setup.pdf"],
    "answerable": True,
}
```

**The three metrics**
- `Recall@K`: Of all the relevant documents, what fraction appeared in the first K results? Higher recall means fewer relevant documents were missed.
- `Precision@K`: Of the first K results, what fraction were relevant? Higher precision means fewer irrelevant results were returned.
- `MRR (Mean Reciprocal Rank)`: How high was the first relevant result? If it’s first, the score is 1; second, 1/2; third, 1/3. If no relevant result appears, it’s 0. The evaluator averages this score across questions.
Here, **K** is a cutoff such as 1, 3, or 5.

**What the functions do**

- `recall_at_k()` compares the unique sources in the first `K` results with the relevant-source set:

```python
len(set(retrieved[:k]) & relevant) / len(relevant)
```

- `precision_at_k()` counts relevant results among the first `K` and divides by `K`. If fewer than `K` results are returned, this implementation still divides by `K`, which penalizes missing results.

- `reciprocal_rank()` finds the position of the first relevant source and returns its reciprocal. If none is found, it returns `0`.

`evaluate_retrieval()`:

1. Keeps answerable dataset questions that have at least one known relevant source.
2. Calls retrieve_fn(question) to get retrieved chunks.
3. Compares each chunk’s source filename with the relevant filenames.
4. Calculates the requested recall and precision values, plus MRR.
5. Averages each metric across the kept questions and returns the number evaluated as n.
Unanswerable questions are skipped because this code evaluates whether search finds known relevant documents; it doesn’t evaluate whether the RAG system correctly abstains.

---

*6.* `answer_generator.py`:

This is the answer-generation stage of the RAG system. It takes retrieved context and a question, asks the LLM for a structured answer with citations, checks that the answer’s citation IDs are valid, and abstains if it can’t produce a verifiable answer.

**Imports and answer format**

- `BuiltContext` represents the retrieved context, including its text, sources, and source IDs. `LLMService` sends the prompt to your model. `Answer` is a Pydantic model that defines the expected response fields. `OutputValidationError` reports malformed output or invalid citations.
- The system prompt tells the model to use evidence from source tags, treat source text as untrusted data, cite factual claims, and report when evidence is insufficient. It asks for JSON shaped like:

```python
{
  "answer": "The answer text [S1].",
  "citations": ["S1"],
  "confidence": "high",
  "insufficient_evidence": false
}
```

**The abstention response**

```python
ABSTAIN = Answer(
    answer="I don't have enough information in the provided documents to answer this.",
    citations=[],
    confidence="high",
    insufficient_evidence=True,
)
```

This is the standard response when no evidence is retrieved, or when two attempts fail validation.

**Parsing and validating the model’s JSON**

- `_parse(raw)` extracts a JSON object from the model’s text, loads it, and uses `Answer` to check that the fields and values have the expected types. If parsing or validation fails, it raises `OutputValidationError`.

**Generating the answer**

`generate()` receives:
- `question`: the user’s question
- `ctx`: retrieved context
- `history_text`: optional conversation history
If `ctx.sources` is empty, it returns the abstention response without calling the LLM.

Otherwise, it sends the `history`, `context`, and `question` to the model. It allows two attempts. For each response, it:
1. Parses the JSON into an Answer.
2. Checks that every cited ID exists in ctx.source_ids.
3. Rejects a substantive answer that has no citations.
4. Returns the answer if those checks pass.
If validation fails, it logs the error and asks the model to correct its JSON, including the valid source IDs. If the second response is still invalid, it returns a fallback abstention message.

The citation check confirms that an ID exists; it does not confirm that the cited source actually supports the claim. The prompt asks the model to make that connection, but this code doesn’t independently verify it.

---

*7.* `context_builder.py`:

This is the **context-building stage**: it cleans up retrieved chunks, optionally shortens them, fits them into a token budget, orders them, and labels them so the answer generator can cite them as `[S1]`, `[S2]`, and so on.

**Token estimates and text matching**

```python
def approx_tokens(text: str) -> int:
    return max(1, len(text) // 4)
```

This estimates token count as roughly one token per four characters. It’s a quick estimate, not an exact tokenizer count. The `max(1, ...)` means even empty text is charged at least one token.

```python
def _tokens(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.lower()))
```

This lowercases text, extracts word-like pieces, and returns unique terms. These sets are used for duplicate detection and simple compression.

**Remove similar chunks**

- `dedupe()` walks through the chunks and keeps a chunk unless it is too similar to one already kept, or has the same `point_id`.

- Similarity is measured with **Jaccard similarity:**

> shared unique terms ÷ all unique terms across both chunks

The default threshold is `0.85`, so chunks must share a large proportion of their terms to be treated as duplicates. Since it compares sets, repeated words don’t affect the score.

**Optional extractive compression**

- `compress()` splits a chunk into sentences, then keeps sentences sharing terms with the query. It removes a few common words from the query first.
- It only uses the shortened version when at least min_keep sentences match; the default is two. Otherwise, it returns the original chunk.
- This is a simple keyword technique. It may miss useful sentences that use synonyms, and it may keep a sentence that shares a query word without answering the question.

**BuiltContext**

```python
@dataclass
class BuiltContext:
    text: str
    sources: dict[str, RetrievedChunk] = field(default_factory=dict)
```

- `text` is the assembled context sent to the LLM. `sources` maps citation IDs, such as `"S1"`, back to the retrieved chunks that produced them.
- The `source_ids` property returns the set of those IDs. The answer generator uses it to check that the model’s citations refer to real sources.

**ContextBuilder.build()**

The builder processes chunks in this order:
1. Deduplicate them.
2. Optionally compress each chunk.
3. Apply the token budget. Each chunk costs the estimated body tokens plus 20 tokens for its labels and formatting. Chunks that don’t fit are skipped.
4. Order the selected chunks.
5. Assign source IDs and assemble the labelled context.

The `order` setting controls step 4:
- `"score"` keeps the input order, which the code assumes is best score first.
- `"document"` sorts by document ID and chunk index, which is useful for reading nearby chunks in sequence.
- `edges"` puts alternating chunks toward the beginning and end, aiming to place strong evidence away from the middle of a long context.

Source IDs are assigned after ordering, so `[S1]` matches the first source in the final context.

---

*8.* `chunking.py`:

Code in this file splits long documents into chunks using three approaches:
- `Fixed`: cuts text at regular character intervals.
- `Recursive`: tries to split at paragraph or sentence boundaries before falling back to fixed cuts.
- `Structure-aware`: splits Markdown into heading sections, then recursively chunks each section while keeping its heading.
The returned chunks are text strings, or `(section_heading, chunk_text)` pairs.

**Fixed chunking**

```python
def fixed_chunk(text: str, size: int = 800, overlap: int = 100) -> list[str]:
```

- `size` is the maximum slice length in characters. `overlap` is how many characters successive chunks share. The step is `size - overlap`, so the next chunk starts before the previous one ends. The `.strip()` calls remove surrounding whitespace, and empty chunks are skipped.
- For example, with a size of 800 and overlap of 100, each chunk starts 700 characters after the previous one.

**Recursive chunking**

```python
def recursive_chunk(
    text: str,
    size: int = 800,
    overlap: int = 100,
    seps: tuple[str, ...] = ("\n\n", "\n", ". ", " "),
) -> list[str]:
```

- If the text already fits, it returns it as one chunk. Otherwise, it picks the first separator found, in this order:
1. Paragraph break ("\n\n")
2. Line break ("\n")
3. Sentence boundary (". ")
4. Space (" ")
- It joins smaller pieces until adding another would exceed `size`. At that point it saves the current chunk and carries the last `overlap` characters into the next one. If a single piece is still too large, it tries the remaining separators; when there are none, it falls back to fixed chunking.
- The goal is to keep chunks near the requested size while avoiding cuts in the middle of paragraphs or sentences where possible.

**Markdown sections**

```python
def markdown_sections(text: str) -> list[tuple[str | None, str]]:
```

- This looks for Markdown headings from `#` through `######`. It returns each section as `(heading, body)`. Text before the first heading gets `None` as its heading. If there are no headings, the whole document is returned as one section.

The regular expression in your pasted code has formatting artifacts. In the Python file it should be:

```python
parts = re.split(r"(?m)^(#{1,6}\s+.+)$", text)
```

**chunk_text()**

This is the main function that selects a strategy:
- `"fixed"` calls `fixed_chunk()`.
- `"structure"` splits by Markdown headings, recursively chunks each section, and adds that section’s heading to each chunk.
- Any other value uses recursive chunking.
In structure mode, the heading helps preserve context—for instance, a chunk containing a definition still carries the heading that tells you which topic it belongs to.

---

*9.* `document_loader.py`:

This loader accepts `.txt`, `.md`, and `.pdf` files and turns them into a list of `Page` records. A PDF gets one record per page; a text or Markdown file gets one record for the whole file.

**Page**

```python
@dataclass
class Page:
    text: str
    page: int | None
    source: str
```

- Each record stores the extracted text, its page number if available, and the source filename. For text and Markdown files, `page` is `None`.

`validate_file()`

Before loading, it checks that:
- The path exists.
- The file extension is allowed.
- The file is no larger than the configured max_upload_mb limit.
It raises `IngestionError` with a message if a check fails.

One useful addition would be checking `path.is_file()` too. As written, an existing directory with an allowed-looking name could pass these checks, then fail when the loader tries to read it.

`load_document()`

- The function converts the input to a `Path` and validates it first.
- For PDFs, it imports `PdfReader` and extracts text page by page. Page numbering starts at 1. If a PDF page has no extractable text, it gets an empty string.
- For `.txt` and `.md` files, it reads the entire file as UTF-8. `errors="ignore"` skips bytes that aren’t valid UTF-8 instead of raising a decoding error.
- Finally, it removes records whose text is empty or whitespace. If no readable text remains, it raises `IngestionError`; otherwise, it returns the records.

---

*10.* `document_processor.py`:

- It takes one document, splits it into chunks, creates embeddings, and stores the chunks in your vector store. It aims to make re-ingesting the same document safe by assigning stable IDs and deleting the document’s old chunks before inserting the new ones.

**Stable IDs**

```python
def document_id_for(path: Path) -> str:
    return hashlib.sha1(path.name.encode()).hexdigest()[:12]
```

This creates a `12-character ID from the filename`. The same filename produces the same ID, which lets the app find and delete that document’s existing chunks.
- 
```python
def point_id_for(document_id: str, chunk_index: int) -> str:
    return str(uuid.uuid5(NS, f"{document_id}:{chunk_index}"))
```

- This creates a repeatable `UUID` for each document-and-chunk-index pair. If a document is split the same way again, the corresponding chunks get the same point IDs. Qdrant accepts `UUIDs` as point IDs.

`DocumentProcessor`

- The constructor receives a VectorStore and a chunking strategy, defaulting to "recursive".

- `ingest()` does the following:
    1. Converts the input into a `Path` and loads its pages.
    2. Creates a document ID.
    3. Chunks each page using the configured size, overlap, and strategy.
    4. Creates a Chunk for every text piece, recording its point ID, document ID, source name, chunk index, page, section, and text.
    5. Gets the embedding service and generates dense and sparse embeddings for the chunk texts.
    6. Ensures the Qdrant collection exists.
    7. Deletes the old chunks for that document, then upserts the newly built chunks and embeddings.
    8. Logs the result and returns the document ID, filename, and number of chunks.
- The pasted `chunk_id` expression appears corrupted by formatting. It likely should be:

```python
chunk_id=f"{doc_id}-{idx:04d}"
```

That formats the index with leading zeroes, such as `abc123-0007`.

*Deleting a document*

```python
def delete(self, document_id: str) -> None:
```

---

*11.* `vector_store.py`:

This wraps `Qdrant` for your RAG app. It creates a collection for `dense` and `BM25` sparse vectors, stores document chunks, deletes or lists documents, and searches using filters.

**Connection and collection setup**

```python
self.client = client or QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key,
)
self.collection = collection or settings.collection_name
```

We can pass in an existing Qdrant client and collection name, or the class uses settings. For Qdrant Cloud, `qdrant_url` should be your cluster URL and `qdrant_api_key` its database API key.

`ensure_collection()` checks whether the collection already exists. If not, it creates one with:
- A named dense vector called `"dense"`, with size `settings.dense_dim` and cosine distance.
- A named sparse vector called `"bm25"`, with Qdrant’s IDF modifier.
- Keyword indexes on `document_id` and `source`, to support efficient filters on those fields.

**Writing and deleting**

`upsert()` builds one Qdrant point per chunk. Each point contains:
- The chunk’s stable `point_id`.
- Both its `dense` and `sparse vectors`.
- The chunk’s other fields as `payload`, excluding `point_id`.
It then sends the points to Qdrant and waits for the write to finish.

`delete_document()` deletes every point whose `document_id` matches the supplied `ID`. This is how the ingestion code can remove old chunks before updating a document.

`list_documents()` repeatedly scrolls through points in batches of 256, reading only `document_id` and `source`. It returns a dictionary mapping each document ID to its filename.

**Filters**

`build_filter()` turns a dictionary into a Qdrant filter:

```python
{"source": "guide.pdf", "document_id": ["abc", "xyz"]}
```

Values that are lists, tuples, or sets become “match any” conditions. Other values become exact-value matches. Since all conditions are placed in `must`, different filter fields must all match; the multiple values for one field can match any of those values.

The fields need to exist in the stored payload. This code creates indexes for `document_id` and `source`; other fields can be filtered too, but would need appropriate indexes for efficient filtering at scale.

**Searching**

`search()` accepts a mode, vectors, result limit, optional filters, and optional score `threshold`.
- `"dense"` searches the `"dense"` vector using semantic similarity. It applies both the filter and score_threshold.
- `"sparse"` searches the `"bm25"` vector for keyword matches. It applies the filter.
- `"hybrid"` runs both searches as prefetches, asks Qdrant to combine their rankings with Reciprocal Rank Fusion (RRF), then returns the top results.

In `hybrid mode`, each search fetches up to twice the requested result count before fusion. The filter is applied to both prefetches. In this code, `score_threshold` is only passed to dense mode.

If the mode is unknown, the method raises `RetrievalError`. Other search exceptions are wrapped in `RetrievalError` with a Qdrant failure message.

Finally, each returned point becomes a `RetrievedChunk`: its Qdrant ID and score are combined with available payload fields listed in `PAYLOAD_FIELDS`.

A practical check before calling `search()` is that the vector required by the chosen mode is present: dense mode needs `dense_vec`, sparse mode needs `sparse_vec`, and hybrid mode needs both.

---

*12.* `bm25_search.py`:

This is a small helper that runs a` BM25-style keyword search` through your Qdrant `VectorStore`.

```python
from Week7.core.embeddings import get_embedder
from Week7.core.vector_store import VectorStore
```
 
- `get_embedder` provides the embedding service that creates sparse vectors for search queries.
- `VectorStore` is the Qdrant wrapper that performs the search.

```python
def bm25_search(store: VectorStore, query: str, k=10, filters=None):
```

The function takes:
- `store`: the connected Qdrant vector store.
- `query`: the user’s search text.
- `k`: how many results to return, defaulting to 10.
- `filters`: optional conditions, such as limiting results to a particular document.

Inside the function:

```python
sparse_vec = get_embedder().embed_sparse_query(query)
```

It converts the query into a `sparse BM25 vector`. `get_embedder()` reuses the cached embedding service.

Then `store.search()` is called with `mode="sparse"`, which tells your VectorStore to search the `"bm25"` vector in Qdrant. `limit=k` sets the result count, and `filters` narrows the search if provided.

**In short:**

```text
query → sparse BM25 vector → Qdrant sparse search → top k chunks
```

---

*13.* `dense_search.py`:

This helper runs a `dense semantic search` through your Qdrant `VectorStore`.

```python
def dense_search(
    store: VectorStore,
    query: str,
    k=10,
    filters=None,
    score_threshold=None,
):
```

It takes the `vector store`, the user’s `query`, how many results to return `(k)`, optional `filters`, and an optional minimum `relevance score`.

This line turns the query into a dense embedding:
```python
get_embedder().embed_dense([query])[0]
```

`embed_dense()` accepts a list of texts and returns a list of vectors. Since this search has one query, `[0]` selects its vector.

Then `store.search()` is called with `mode="dense"`, which tells your `VectorStore` to search Qdrant’s `"dense"` vector. The store applies the filters and score threshold, then returns up to `k` matching chunks.

**In short:**

```text
query → dense embedding → Qdrant semantic search → top-k chunks
```

---

*14.* `hybrid_search.py`:

It has two pieces: `hybrid_search()` combines dense and BM25 search for one query in Qdrant; `rrf_merge()` combines ranked results from multiple searches in Python.

`hybrid_search()`

```python
def hybrid_search(store, query, k=10, filters=None):
```

It gets the cached embedding service, creates both a dense vector and a BM25 sparse query vector, then calls `store.search()` in `"hybrid"` mode. In your `VectorStore`, that mode prefetches dense and sparse results and combines their rankings with Qdrant’s server-side RRF.

Here, `k=10` means “return up to 10 results.”

`rrf_merge()`

This function combines multiple ranked result lists. It’s useful for multi-query retrieval—for example, if you rewrite one question into three search queries, you can merge the three result lists.

For each result, it adds this score:

```text
1 / (rrf_constant + rank)
```

A result appearing near the top gets a larger score. A result found in multiple lists gets its scores added together.
- `k=60` is the RRF smoothing constant. It reduces how sharply ranks affect the score.
- `top` optionally limits how many merged results to return.
- `point_id` is used to recognize duplicate chunks across result lists.
- `by_id.setdefault(...) keeps the first chunk object found for each ID.
- `model_copy(update={"score": ...})` returns a copy with its score replaced by the fused RRF score.

So there are two different “K” ideas:` hybrid_search(..., k=10)` controls the number of results; `rrf_merge(..., k=60)` is the RRF constant. Naming the latter `rrf_k` can make that clearer.

---

*15.* `query_writer.py`:

This class uses the LLMService to make follow-up questions easier to search and to generate alternative phrasings for retrieval.

`rewrite()`: *make a follow-up question standalone*

If there’s no conversation history, it returns the question unchanged. Otherwise, it takes the last six messages, formats them with their roles, and asks the LLM to rewrite the latest question as a standalone search query.

For example, given this history:

```text
User: What is Qdrant?
Assistant: It is a vector database.
User: Does it support sparse search?
```

It might rewrite the last question as:

```text
Does Qdrant support sparse search?
```

`.strip()` removes whitespace; `.strip('"')` also removes quote characters at the ends. If the model returns an empty response, the original question is used.

`expand()`: *generate alternative search queries*

This asks the LLM for a JSON array of differently worded queries. It extracts the text between the first `[` and last `]`, parses it as `JSON`, then returns the original question plus generated queries that are strings.

For example:

```text
["How does Qdrant sparse search work?",
 "How are sparse vectors used for keyword retrieval?"]
```

---

*16.* `reranker.py`:

This is a **second-stage retrieval step**. Your vector search first finds candidate chunks; the reranker then scores each candidate against the original question and sorts them by likely relevance.

**Load and reuse the reranker model**

```python
@lru_cache(maxsize=1)
def _model():
    from fastembed.rerank.cross_encoder import TextCrossEncoder
    return TextCrossEncoder(settings.rerank_model)
```

`_model()` loads the configured cross-encoder. The cache keeps one instance, so repeated reranking calls don’t reload the model each time. The FastEmbed import is inside the function, so it happens when the model is first needed.

A cross-encoder looks at the query and a chunk together to score their relevance. This can provide better ordering than the initial search, though it takes more work per candidate. That’s why it’s typically used to rerank a limited set of retrieved chunks.

**Rerank candidates**

```python
def rerank(self, query, chunks, top_n=5, min_score=None):
```

If there are no chunks, it returns an empty list. Otherwise, it:
1. Sends the query and each chunk’s text to the cross-encoder.
2. Copies each chunk and attaches its reranking score as rerank_score.
3. Sorts chunks from highest score to lowest.
4. Optionally removes scores below min_score.
5. Returns up to `top_n` chunks.

Check that your `RetrievedChunk` model supports a `rerank_score` field. Also, reranker scores are model-specific relevance scores; don’t assume they’re probabilities or automatically use a universal threshold.

**Compare rankings**

`compare_orders(before, after)` helps inspect how results moved. For each reranked chunk, it returns its chunk_id, its original position, and its new position. It uses `-1` when a chunk ID wasn’t present in the original list.

The score list and chunk list are paired with `zip()`, which silently truncates if their lengths differ.

---

*17.* `retriever.py`:

`Retriever` is intended to be the single entry point for retrieval. It takes one query or several, selects dense, sparse, or hybrid search, applies filters, and combines results when there are multiple queries.

**How `retrieve()` works**

If `queries` is a string, it wraps it in a list. Then it selects the search function for mode:
- `"dense"` uses semantic vector search and can apply score_threshold.
- `"sparse"` uses BM25 keyword search.
- `"hybrid"` combines dense and sparse search inside Qdrant.
It runs the selected function for each query. With one query, it returns that result list directly. With multiple queries, it intends to merge them with RRF and return the top k chunks.

---