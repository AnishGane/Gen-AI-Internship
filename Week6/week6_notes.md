# Week 6 — Vector Databases + Semantic Search — Notes

---

## Week5 -> Week6 Carryover

Week 6 builds directly on the embeddings and semantic search concepts learned in Week 5.

| Week 5 Concept      | Used Again in Week 6                      |
| ------------------- | ----------------------------------------- |
| Generate embeddings | Convert document chunks into vectors      |
| Batch embeddings    | Embed multiple chunks efficiently         |
| Cosine similarity   | Measure semantic similarity               |
| Manual ranking      | Understand what vector databases automate |
| Semantic search     | Retrieve relevant document chunks         |

In Week 5, embeddings were stored and compared manually in Python:

```text
Query
  ↓
Generate Query Embedding
  ↓
Loop Through All Candidate Vectors
  ↓
Calculate Similarity Manually
  ↓
Sort Results
  ↓
Return Most Similar Result
```

Week6 introduces a new more scalable approach:

```text
Documents
    ↓
Split into Chunks
    ↓
Generate Embeddings
    ↓
Store Vectors in Qdrant
    ↓
Query
    ↓
Generate Query Embedding
    ↓
Qdrant Vector Search
    ↓
Return Most Relevant Chunks
```

The main goal of Week 6 is to understand how embeddings move from simple Python lists into a dedicated vector database.

---

## Important Week6 Concepts

**1. Vector Database:** A database designed to store and search vector embeddings efficiently.

- embedding looks like this:
- [
  0.189,
  0.254,
  ...
  ]

Instead of mannually managing:

```text
   Vectors
   Similarity calculations
   Ranking
   Storage
   Metadata
   Searching
```

we can use:

```text
   Qdrant
     ↓
   Store vectors
     ↓
   Store metadata
     ↓
   Perform vector search
     ↓
   Return relevant results
```

**2. Semantic Search**: Traditional keyword search looks for matching words.

For Example:

```text
Query:
"best football player"
```

Traditional search may look for documents containing:

```text
football
player
best
```

Semantic search instead tries to understand the meaning of the query.

For example:

```text
Query:
"How do I reset my account password?"
```

A semantic search system may retrieve:

```text
"Instructions for changing your login credentials."
```

Even though the words are different, the meanings are related.

The basic process is:

```text
Query
  ↓
Generate Query Embedding
  ↓
Search Similar Vectors
  ↓
Return Relevant Documents
```

**3. Vector Database Collection**: A collection is similar to a table in a traditional database.

For example:

```text
   Traditional Database
   --------------------

   users
   products
   orders
```

In a vector database:

```text
Vector Database
---------------

documents
articles
products
knowledge_base
```

Each collection stores vectors with the same structure and configuration.

For this project, a collection might contain document embeddings.

Example:

```text
Collection: internship_documents

Point 1
├── ID
├── Vector
└── Payload

Point 2
├── ID
├── Vector
└── Payload
```

**4. Point**: In Qdrant, each stored item is called a point.
A point usually contains:

- A unique ID
- A vector embedding
- Payload or metadata

Example:

```python
{
    "id": 1,
    "vector": [0.12, -0.45, 0.78, ...],
    "payload": {
        "text": "Python is a popular programming language.",
        "source": "python_notes.txt"
    }
}
```

**5. Payload**: A vector alone is not useful to a user.

For example:

```python
[0.12, -0.45, 0.78, ...]
```

A user needs to know what that vector represents.

This information is stored as payload.

Example:

```python
payload = {
    "text": "Python supports object-oriented programming.",
    "source": "python_notes.txt",
    "chunk_index": 3
}
```

When Qdrant finds the most similar vector, it can also return the payload.

Example result:

```text
Score: 0.91

Text:
Python supports object-oriented programming.

Source:
python_notes.txt
```

**6. Similarity Search**: Similarity search finds vectors that are closest to a query vector.

Example:

```text
Query:
"What is Python used for?"
```

The query is converted into an embedding:

```text
Query Vector
```

The vector database compares it with stored vectors:

```text
Stored Vector 1 → Score: 0.92
Stored Vector 2 → Score: 0.84
Stored Vector 3 → Score: 0.31
```

The database returns the most relevant results:

```text
1. Score: 0.92
2. Score: 0.84
3. Score: 0.31
```

Higher similarity generally means the result is more semantically related.

**7. Qdrant**: Qdrant is a vector database designed for storing and searching embeddings.

It can be used for:

- Semantic search
- Retrieval-Augmented Generation (RAG)
- Recommendation systems
- AI assistants
- Document search
- Similarity search
- Image search
- Product recommendations

In this internship project, Qdrant is used as a local vector database.

The basic architecture is:

```text
Documents
    ↓
Chunking
    ↓
Embedding Model
    ↓
Embeddings
    ↓
Qdrant
    ↓
Similarity Search
    ↓
Relevant Chunks
```

**8. Local Qdrant Storage**: Qdrant can be used locally without running a separate database server.

The project uses a storage path:

```python
QDRANT_PATH = "storage/qdrant"
```

The client is initialized using:

```python
from qdrant_client import QdrantClient

client = QdrantClient(
    path=QDRANT_PATH
)
```

This creates persistent local storage.

The structure may look like:

```text
storage/
└── qdrant/
    └── collection_data
```

This means vectors can remain available after the Python program stops.

## Week6 Project Architecture

```text
Week6/
│
├── config.py
├── embeddings.py
├── chunking.py
├── qdrant_client.py
├── models.py
├── search.py
├── exceptions.py
├── logger.py
│
└── day1/
    ├── 01_vector_database_intro.py
    ├── 02_qdrant_setup.py
    └── 03_create_collection.py
    └── ...
```

**9. config.py**: This file stores configuration variables. Keeping configuration separate makes the application easier to maintain.

**10. embeddings.py**: This module is responsible for generating embeddings.

Example responsibility:

```text
Text
 ↓
EmbeddingService
 ↓
Embedding Vector
```

Example:

```python
embedding = service.embed_text(
"Vector databases are useful for semantic search."
)
```

The embedding service handles communication with the embedding API.

**11. chunking.py**: Large documents are usually too large to store as one single embedding.

Example:

``text
Large Document

Paragraph 1
Paragraph 2
Paragraph 3
Paragraph 4
Paragraph 5

````

Instead, the document is divided into smaller pieces called chunks.

Example:

```text

Document
│
├── Chunk 1
├── Chunk 2
├── Chunk 3
├── Chunk 4
└── Chunk 5
````

Each chunk receives its own embedding.

```text
Chunk 1 → Vector 1
Chunk 2 → Vector 2
Chunk 3 → Vector 3
```

Chunking is important because semantic search usually retrieves the most relevant section instead of an entire document.

**12. qdrant_client.py**: This module manages communication with Qdrant.

Instead of directly creating the Qdrant client throughout the application:

client = QdrantClient(path=QDRANT_PATH)

the project uses a service:

```python
from Week6.qdrant_client import QdrantService

client = QdrantService(
path=QDRANT_PATH
)
```

This keeps Qdrant-specific logic in one place.

The service can later handle:

- Creating collections
- Listing collections
- Storing points
- Searching vectors
- Deleting collections
- Closing the database

**13. models.py**: This file defines the structure of application data.

The project can use Pydantic models for validation.

Example:

```python
from pydantic import BaseModel


class DocumentChunk(BaseModel):
    text: str
    source: str
    chunk_index: int
```

This ensures the application uses predictable data.

Example:

```python
chunk = DocumentChunk(
text="Qdrant is a vector database.",
source="week6_notes.md",
chunk_index=1
)
```

Pydantic validates the input data and makes invalid data easier to detect.

**14. search.py**: This module will contain semantic search functionality.

The basic process will be:

```text
User Query
↓
Generate Embedding
↓
Send Vector to Qdrant
↓
Retrieve Similar Vectors
↓
Return Relevant Document Chunks
```

Example:

```python
results = search_service.search(
query="What is a vector database?"
)
```

**15. exceptions.py**: This module contains custom exceptions.

Example:

```python
class VectorDatabaseException(Exception):
    """Base exception for vector database errors."""
```

Custom exceptions make errors easier to understand.

Instead of:

```text
Exception: Something went wrong
```

we can raise:

```python
raise VectorDatabaseException(
    "Failed to create Qdrant collection."
)
```

**16. logger.py**: This module provides structured logging.

Example:

```python
logger.info("Qdrant initialized successfully.")
```

If an error occurs:

```python
logger.exception(
"Failed to generate embedding."
)
```

This makes debugging easier because the application records useful information such as:

- Time
- Log level
- Module
- Error details

Example output:

```text
2026-09-14 08:49:58 | INFO | Week6 | Qdrant initialized successfully.
```


