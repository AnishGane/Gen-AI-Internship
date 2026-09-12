# Week 5 --- Embeddings & Semantic Search --- Notes

---

## Week 4 → Week 5 Carryover

Week 4 focused mainly on **prompt engineering, structured outputs,
validation, and LLM-based text processing**.

Week 5 moves one level deeper into how text can be represented
numerically so that we can compare **meaning** between pieces of text.

The main progression is:

```text
Text
  ↓
Embedding Model
  ↓
Vector
  ↓
Similarity Calculation
  ↓
Ranking
  ↓
Semantic Search
```

Unlike keyword search, semantic search can find relevant text even when
the query and document use **different words with similar meanings**.

---

## Day 1 - Introduction to Text Embeddings

### Task 1 - Generate a Single Text Embedding

**Concept:** An embedding is a numerical representation of text.

Instead of representing a sentence as individual words, an embedding
model converts the sentence into a vector of numbers that captures its
**semantic meaning**.

For example:

```text
"Python is useful for AI"
        ↓
Embedding Model
        ↓
[0.021, -0.143, 0.872, ...]
```

The actual embedding contains many dimensions, depending on the model.

The important idea is:

```text
Similar meaning → Similar vectors
Different meaning → Different vectors
```

Run: `uv run Week5/day1/01_first_embedding.py`

### Task 2 - Batch Embeddings

**Concept:** Instead of sending one sentence at a time, multiple texts
can be embedded in a single API request.

Example:

```python
texts = [
    "Python is used for AI.",
    "Machine learning learns patterns from data.",
    "React is used for frontend development."
]

response = client.embeddings.create(
    model=EMBEDDING_MODEL,
    input=texts,
    encoding_format="float"
)
```

The result contains one vector for each input text:

```text
Text 1 → Vector 1
Text 2 → Vector 2
Text 3 → Vector 3
```

Batch processing is useful because a search system may need to embed
**many documents**.

Run: `uv run Week5/day1/02_batch_embeddings.py`

### Task 3 - Dot Product and Embedding Intuition

**Concept:** A dot product gives a numerical indication of how strongly
two vectors point in a similar direction.

For two vectors:

```text
A = [a1, a2, a3]
B = [b1, b2, b3]
```

The dot product is:

```text
A · B = a1b1 + a2b2 + a3b3
```

For embeddings, vectors representing related meanings can have stronger
alignment.

Example:

```text
"Python programming"
        ↕
"Writing code using Python"

→ likely more similar
```

while:

```text
"Python programming"
        ↕
"Football match"

→ likely less similar
```

Run: `uv run Week5/day1/03_embedding_intuition.py`

---

## Day 2 - Measuring Similarity Between Embeddings

### Task 1 - Cosine Similarity

**Concept:** Cosine similarity measures the angle between two vectors.

The formula is:

```text
                  A · B
Cosine Similarity = ─────────
                   ||A|| ||B||
```

Its common interpretation is:

```text
1     → very similar direction
0     → little/no directional similarity
-1    → opposite direction
```

For many text embedding applications, higher cosine similarity means
that two texts are more semantically related.

Example:

```text
Query:
"How do I learn Python?"

Document:
"Python programming tutorials for beginners"

→ High similarity
```

Run: `uv run Week5/day2/04_cosine_similarity.py`

### Task 2 - Compare Similarity Metrics

**Concept:** Three important vector comparison methods were explored:

Metric Basic idea

---

Cosine Similarity Compares vector direction
Dot Product Measures vector alignment and magnitude
Euclidean Distance Measures physical distance between vectors

Euclidean distance:

```text
distance = √Σ(Ai - Bi)²
```

For Euclidean distance:

```text
Smaller distance → more similar
```

For cosine similarity:

```text
Higher score → more similar
```

Run: `uv run Week5/day2/05_similarity_metrics.py`

### Task 3 - Rank Documents by Similarity

**Concept:** Instead of checking whether one document is similar to a
query, we can compare the query against **multiple documents** and rank
them.

Example:

```text
Query:
"How can I learn Python?"

Documents:

1. Python beginner tutorial
2. React frontend guide
3. Database administration
4. Python programming course
```

After calculating similarity:

```text
1. Python beginner tutorial     → 0.91
2. Python programming course    → 0.87
3. React frontend guide         → 0.42
4. Database administration      → 0.25
```

The most relevant documents appear first.

Run: `uv run Week5/day2/06_ranking_by_similarity.py`

---

## Day 3 - Building Semantic Search

### Task 1 - Keyword Search vs Semantic Search

**Concept:** Traditional keyword search looks for matching words.

Example:

```text
Query:
"How can I create a website?"
```

A keyword search primarily looks for words such as:

```text
create
website
```

Semantic search instead compares the **meaning** of the query with the
meaning of documents.

Therefore, a document containing:

```text
"Building web applications with React"
```

can still be considered relevant even though it does not contain the
exact phrase `"create a website"`.

### Main Difference

```text
Keyword Search
→ Matches words

Semantic Search
→ Matches meaning
```

Run: `uv run Week5/day3/07_keyword_vs_semantic.py`

### Task 2 - Basic Semantic Search Engine

**Concept:** A basic semantic search engine follows four main steps:

```text
1. Store documents
2. Generate document embeddings
3. Generate query embedding
4. Compare query with document embeddings
```

Example:

```text
Documents
    ↓
Embedding Model
    ↓
Document Vectors

User Query
    ↓
Embedding Model
    ↓
Query Vector

Query Vector + Document Vectors
    ↓
Cosine Similarity
    ↓
Best Match
```

Run: `uv run Week5/day3/08_semantic_search.py`

### Task 3 - Top-K Retrieval

**Concept:** Top-K retrieval means returning the **K most relevant
results** instead of returning only one result.

For example:

```text
K = 3
```

means:

```text
Return the top 3 most similar documents.
```

Example:

```text
Query:
"Programming languages for AI"

Top 3:

1. Python is widely used for AI.
2. Machine learning uses programming languages.
3. Deep learning uses Python libraries.
```

The general process is:

```python
scores = []

for document in documents:
    score = cosine_similarity(query_vector, document_vector)
    scores.append((document, score))

results = sorted(scores, key=lambda x: x[1], reverse=True)

top_k = results[:k]
```

Run: `uv run Week5/day3/09_top_k_retrieval.py`

---

## Day 4 - Storing and Reusing Embeddings

### Task 1 - Precompute Document Embeddings

**Concept:** Generating embeddings for every document every time a user
searches would be inefficient.

Instead, document embeddings can be generated **once** and stored.

Without precomputation:

```text
Search
 ↓
Embed all documents
 ↓
Embed query
 ↓
Compare
```

With precomputation:

```text
Documents
 ↓
Generate embeddings once
 ↓
Store embeddings
       ↓
User Search
       ↓
Embed only query
       ↓
Compare with stored vectors
```

This makes repeated searches much more efficient.

Run: `uv run Week5/day4/10_precompute_embeddings.py`

### Task 2 - Store and Load Embeddings

**Concept:** Embeddings are numerical data, so they can be stored
locally for later use.

The Week 5 implementation stores the vectors in a JSON file.

Example structure:

```json
[
  {
    "text": "Python is used for AI.",
    "embedding": [0.021, -0.143, 0.872]
  },
  {
    "text": "React builds web interfaces.",
    "embedding": [0.112, 0.321, -0.452]
  }
]
```

This separates the expensive embedding-generation step from the search
step.

Basic workflow:

```text
Generate embeddings
        ↓
Save embeddings.json
        ↓
Load embeddings.json
        ↓
Perform searches
```

Run: `uv run Week5/day4/11_store_load_embeddings.py`

### Task 3 - Search Stored Embeddings

**Concept:** Once document embeddings have been stored, the search
system does not need to embed the documents again.

Only the user's query needs a new embedding.

```text
Stored Documents
      ↓
Stored Embeddings
      ↓
      ↕
Query → Query Embedding
      ↓
Similarity Calculation
      ↓
Ranking
      ↓
Search Results
```

This is an important step toward a real semantic search system.

Run: `uv run Week5/day4/12_search_stored_embeddings.py`

---

## Day 5 - Text Chunking for Semantic Search

### Task 1 - Basic Text Chunking

**Concept:** Large documents should usually not be treated as one huge
piece of text.

Instead, a document can be divided into smaller **chunks**.

Example:

```text
Large Document
       ↓
 ┌─────────────┐
 │ Chunk 1     │
 ├─────────────┤
 │ Chunk 2     │
 ├─────────────┤
 │ Chunk 3     │
 └─────────────┘
```

For example, a long document can be split into chunks of 100 words:

```text
Document
 ↓
Words 1–100
Words 101–200
Words 201–300
...
```

Each chunk can then receive its own embedding.

### Why Chunk?

- Better retrieval precision
- Smaller text units
- Easier to find the exact relevant section
- Useful for large documents and RAG systems

Run: `uv run Week5/day5/13_text_chunking.py`

### Task 2 - Chunking with Overlap

**Concept:** Splitting text into completely separate chunks can break
important information between two chunks.

For example:

```text
Chunk 1:
"Python is commonly used for machine learning because..."

Chunk 2:
"...it has many useful libraries such as NumPy and PyTorch."
```

The context may be split between the chunks.

**Overlap** solves this by repeating some words between neighboring
chunks.

Example:

```text
Chunk 1:
Words 1–100

Chunk 2:
Words 81–180

Chunk 3:
Words 161–260
```

Here:

```text
Overlap = 20 words
```

The basic idea is:

```text
Chunk 1
████████████████████

        ████████████████████
        Chunk 2

                ████████████████████
                Chunk 3
```

Overlap helps preserve context across chunk boundaries.

Run: `uv run Week5/day5/14_chunking_with_overlap.py`

### Task 3 - Chunk-Based Semantic Search

**Concept:** Instead of searching whole documents, the system searches
individual chunks.

Pipeline:

```text
Large Documents
      ↓
Text Chunking
      ↓
Chunks
      ↓
Generate Embeddings
      ↓
Store Chunk Embeddings
      ↓
User Query
      ↓
Query Embedding
      ↓
Compare with Chunk Embeddings
      ↓
Rank Chunks
      ↓
Return Most Relevant Chunks
```

Example:

```text
Document: Python Tutorial

Chunk 1 → Introduction
Chunk 2 → Variables
Chunk 3 → Functions
Chunk 4 → Classes
Chunk 5 → File Handling
```

If the user asks:

```text
"How do I work with files in Python?"
```

the system should retrieve:

```text
Chunk 5 → File Handling
```

rather than returning the entire document.

This is the basic idea behind retrieval systems used in **RAG
applications**.

Run: `uv run Week5/day5/15_chunk_semantic_search.py`

---

## Day 6 - Complete Semantic Search Pipeline

### Task 1 - Build the Complete Semantic Search Pipeline

**Concept:** The previous days' individual techniques are combined into
one complete workflow.

The pipeline is:

```text
Documents
    ↓
Chunk Documents
    ↓
Generate Embeddings
    ↓
Store Embeddings
    ↓
        User Query
            ↓
      Generate Query Embedding
            ↓
     Calculate Similarity
            ↓
          Ranking
            ↓
       Top-K Results
```

The main components are:

```text
Text Chunking
      +
Embeddings
      +
Cosine Similarity
      +
Ranking
      +
Top-K Retrieval
```

Run: `uv run Week5/day6/16_semantic_search_pipeline.py`

### Task 2 - Interactive Semantic Search CLI

**Concept:** The semantic search system was converted into an
interactive command-line application.

Instead of changing the query inside the Python file, the user can
continuously enter queries.

Example:

```text
Semantic Search

Enter your query: python programming

Results:
1. Python is a popular programming language...
2. Machine learning can be implemented using Python...

Enter your query: web development

Results:
1. React is used to build interactive web interfaces...
2. JavaScript is commonly used for web applications...

Enter your query: exit
```

The basic interaction is:

```text
Start Program
     ↓
Ask for Query
     ↓
Generate Query Embedding
     ↓
Search
     ↓
Display Results
     ↓
Ask for Another Query
```

Run: `uv run Week5/day6/17_interactive_search.py`

### Task 3 - Final Semantic Search Deliverable

**Concept:** The final task combines the concepts learned throughout
Week 5 into a small working semantic search system.

The final system accepts a natural-language query and returns the most
semantically relevant items.

Example:

```text
Query:
"programming language used for artificial intelligence"

Result:
"Python is a popular programming language used for AI."
```

Notice that the query does not need to exactly match the document.

The system works based on **semantic similarity**.

### Final Pipeline

```text
             DOCUMENTS
                 ↓
          Text Chunking
                 ↓
       Generate Embeddings
                 ↓
        Store Vector Data
                 ↓
             ┌───────┐
             │ Search│
             └───┬───┘
                 ↓
           User Query
                 ↓
       Query Embedding
                 ↓
       Similarity Calculation
                 ↓
             Ranking
                 ↓
            Top-K Results
```

Run: `uv run Week5/day6/18_final_semantic_search.py`

---

# Week 5 - Key Concepts to Remember

---

Concept Simple Meaning

---

**Embedding** Converts text into numbers/vectors

**Vector** Numerical representation of text

**Semantic Similarity** How close two texts are in meaning

**Cosine Similarity** Measures similarity based on vector
direction

**Dot Product** Measures vector alignment and
magnitude

**Euclidean Distance** Measures distance between vectors

**Keyword Search** Searches for matching words

**Semantic Search** Searches based on meaning

**Top-K Retrieval** Returns the K best matches

**Precomputation** Generate document embeddings
beforehand

**Vector Storage** Save embeddings for later searches

**Chunking** Split large text into smaller
pieces

**Chunk Overlap** Repeat some text between chunks to
preserve context

**Chunk Search** Search individual chunks instead of
whole documents

---

---

# Quick Reference Table

Concept Script

---

Single text embedding `01_first_embedding_call.py`
Batch embeddings `02_batch_embeddings.py`
Dot product & embedding intuition `03_intuition_similar_vs_different.py`
Cosine similarity `04_cosine_similarity_from_scratch.py`
Similarity metrics `05_comparing_similarity_metrics.py`
Ranking by similarity `06_ranking_by_similarity.py`
Keyword vs semantic search `07_keyword_vs_semantic.py`
Basic semantic search `08_semantic_search.py`
Top-K retrieval `09_top_k_retrieval.py`
Precompute embeddings `10_precompute_embeddings.py`
Store/load embeddings `11_store_load_embeddings.py`
Search stored embeddings `12_search_stored_embeddings.py`
Text chunking `13_text_chunking.py`
Chunking with overlap `14_chunking_with_overlap.py`
Chunk-based semantic search `15_chunk_search.py`
Semantic search pipeline `16_semantic_search_pipeline.py`
Interactive semantic search `17_interactive_search.py`
Final semantic search `18_final_semantic_search.py`

---

# Week 5 - Overall Learning Progression

```text
Day 1
Embeddings
   ↓
Understand vectors

Day 2
Similarity
   ↓
Compare vectors

Day 3
Semantic Search
   ↓
Find relevant text

Day 4
Persistent Embeddings
   ↓
Store and reuse vectors

Day 5
Chunking
   ↓
Search large documents effectively

Day 6
Complete Pipeline
   ↓
Build an interactive semantic search system
```

---

## Week 5 Deliverable

### Embeddings and Semantic Search

Built a semantic search system using **text embeddings, cosine
similarity, ranking, persistent embeddings, text chunking, and Top-K
retrieval**.

The final project demonstrates:

```text
Text
 ↓
Embedding
 ↓
Vector Representation
 ↓
Similarity Calculation
 ↓
Ranking
 ↓
Top-K Semantic Search Results
```

The key lesson from Week 5 is:

> **Embeddings allow computers to represent and compare the meaning of
> text numerically, making semantic search possible.**
