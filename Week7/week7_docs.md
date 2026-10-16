## Week7 roadmap

---

**01**

> Working RAG pipeline
> Connect Week 6 retrieval to the LLM, create reusable generation code, and return source citations.
> Deliverable: end-to-end RAG query

**02**

> Retrieval engineering
> Improve chunking and metadata, tune Top-K, add query rewriting and multi-query retrieval.
> Deliverable: better retrieval candidates

**03**

> Reranking and context construction
> Rerank retrieved chunks, remove duplicates, control context size, and order evidence.
> Deliverable: higher-quality evidence selection

**04**

> Grounding and reliability
> Handle missing context, enforce structured responses, validate citations, and detect unsupported answers.
> Deliverable: safer answer generation

**05**

> Advanced retrieval
> Explore hybrid dense + sparse search, Reciprocal Rank Fusion (RRF), and metadata-aware retrieval.
> Deliverable: semantic + keyword retrieval experiment

**06**

> Conversation and evaluation
> Add conversational history, follow-up question handling, test datasets, Recall@K, MRR, and answer faithfulness checks.
> Deliverable: measurable conversational RAG

**07**

> Capstone and testing
> Assemble the reusable components into a CLI application, run regression tests, measure latency, and document limitations.
> Deliverable: complete document question-answering system

---

### Project Structure

```text
    Week7/
    ├── day1/
    │ ├── 01_llm_service.py
    │ ├── 02_context_builder.py
    │ └── 03_basic_rag_pipeline.py
    ├── day2/
    │ ├── 04_retrieval_tuning.py
    │ ├── 05_query_rewriting.py
    │ └── 06_multi_query_retrieval.py
    ├── day3/
    │ ├── 07_reranking.py
    │ ├── 08_context_compression.py
    │ └── 09_context_selection.py
    ├── day4/
    │ ├── 10_abstention.py
    │ ├── 11_structured_answers.py
    │ └── 12_citation_validation.py
    ├── day5/
    │ ├── 13_hybrid_search.py
    │ ├── 14_reciprocal_rank_fusion.py
    │ └── 15_retrieval_benchmark.py
    ├── day6/
    │ ├── 16_conversation_memory.py
    │ ├── 17_rag_evaluation.py
    │ └── 18_regression_tests.py
    ├── day7/
    │ ├── 19_rag_cli.py
    │ ├── 20_end_to_end_tests.py
    │ └── 21_final_rag_app.py
    ├── data/
    │ └── test_questions.json
    ├── config.py
    ├── llm_service.py
    ├── context_builder.py
    ├── rag_service.py
    ├── models.py
    ├── exceptions.py
    ├── logger.py
```

---

## Day 1 - Build the actual RAG pipeline

I have implemented three real components:

1. An LLM service using OpenRouter.
2. A context builder that formats retrieved chunks with source IDs.
3. A RAG pipeline that retrieves, generates, and returns an answer with citations.

### Task 1

---
