# Week 6 — Vector Databases + Semantic Search — Notes

---

## Week5 to Week6 Carryover

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

The main goal of Week 6 is to understand how embeddings move from simple Python lists into a dedicated vector database.

---

**Links** to the files that are used in this project:

[chunking.py](E:\Gen AI Internship Repo\Week6\chunking.py)

[embeddings.py](E:\Gen AI Internship Repo\Week6\embeddings.py)

[exceptions.py](E:\Gen AI Internship Repo\Week6\exceptions.py)

[logger.py](E:\Gen AI Internship Repo\Week6\logger.py)

[models.py](E:\Gen AI Internship Repo\Week6\models.py)

[qdrant_client.py](E:\Gen AI Internship Repo\Week6\qdrant_client.py)

[utils.py](E:\Gen AI Internship Repo\Week6\utils.py)

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

```text
Large Document

Paragraph 1
Paragraph 2
Paragraph 3
Paragraph 4
Paragraph 5
```

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
```

Each chunk receives its own embedding.

```text
Chunk 1 → Vector 1
Chunk 2 → Vector 2
Chunk 3 → Vector 3
```

Chunking is important because semantic search usually retrieves the most relevant section instead of an entire document.

**12. qdrant_client.py**: This module manages communication with Qdrant.

Instead of directly creating the Qdrant client throughout the application:

```python
client = QdrantClient(path=QDRANT_PATH)
```

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

---

## Day 1 - Introduction to Vector Databases and Qdrant Setup

Day 1 focuses on understanding what a vector database is and setting up Qdrant locally.

The three tasks gradually move from understanding the concept to creating an actual vector collection.

---

### Task1 - Intro to Vector Databases

**Concept**: A vector database stores embeddings and allows fast similarity searches.

Week 5 used a manual approach:

```python
scores = []

for candidate, vector in zip(candidates, vectors):
  score = cosine_similarity(
  query_vector,
  vector
)

scores.append((candidate, score))

results = sorted(
scores,
key=lambda item: item[1],
reverse=True
)

```

This works for a small dataset.

However, a vector database handles this process more efficiently for larger datasets.

The basic comparison is:

```text
**Week 5**

Query
↓
Generate Embedding
↓
Loop Through Every Vector
↓
Calculate Similarity
↓
Sort Results

**Week 6**

Query
↓
Generate Embedding
↓
Vector Database
↓
Search Index
↓
Return Most Relevant Results
```

**Run**

```bash
uv run Week6/day1/01_vector_database_concept.py
```

---

### Task2 - Local Qdrant Setup

**Concept**: Set up a local Qdrant database and initialize a reusable client.

The Qdrant service is initialized using the configured storage path:

```python
from Week6.qdrant_client import QdrantService
from Week6.config import QDRANT_PATH

def create_qdrant_client() -> QdrantService:
  return QdrantService(
  path=QDRANT_PATH
)
```

The script checks the available collections:

```python
collections = client.get_collections()

if not collections:
print("No collections found.")
```

Example output:

```terminal
========
CREATE QDRANT CLIENT
========

Qdrant client created successfully.

Storage path:
storage/qdrant

No collections found.
```

At this stage, Qdrant is running locally and ready to store vector collections.

**Run**

```bash
uv run Week6/day1/02_qdrant_setup.py
```

---

### Task3 - Creating a Qdrant Collection

**Concept**: Create a collection that can store embeddings.

Before creating a collection, we need to know the embedding dimension.

Example:

```python
vector = embedding_service.embed_text(
"This is a test document."
)

vector_size = len(vector)
```

If the embedding contains:

```text
1536 numbers
```

the collection must be configured with:

```python
VectorParams(
  size=1536,
  distance=Distance.COSINE
)
```

Example collection creation:

```python
client.create_collection(
  collection_name=COLLECTION_NAME,
  vectors_config=VectorParams(
  size=vector_size,
  distance=Distance.COSINE
))
```

The collection structure is:

```text
Collection
│
├── Point 1
│ ├── ID
│ ├── Vector
│ └── Payload
│
├── Point 2
│ ├── ID
│ ├── Vector
│ └── Payload
│
└── Point 3
├── ID
├── Vector
└── Payload
```

The embedding dimension must match the collection configuration.

For example:

```text
Collection vector size: 1536

Stored vector size: 1536
```

If the sizes do not match, Qdrant cannot store the vector correctly.

Run

```bash
uv run Week6/day1/03_create_collection.py
```

---

## Day 2 - Document chunking, embedding chunk & Store chunks in qdrant storage

In day2, we have chunked the text that is present in the `data/documents` (_python.txt_, _react.txt_).

`python.txt` contains:

```text
Python is a high-level programming language.
Python is commonly used for web development,
data science, automation and artificial intelligence.
```

### Task1 - Chunking documents

Here, first of all we have `load_document(document_path: str)` that reads the text from the `document_path` (_python.txt_), which is basically name of the txt file.

```python
def load_document(path: Path) -> str:
    return path.read_text(encoding="utf-8")
```

then, we have `main()`:

```python
all_chunks = []

    for document_path in DOCUMENT_PATH.glob("*.txt"):
        text = load_document(document_path)

        print(f"\nDocument: {document_path}") # Document: E:\Gen AI Internship Repo\Week6\data\documents\React.txt
        print(f"\nText: {text}")

        chunks = chunk_text(
            text=text,
            source=document_path.name,
            chunk_size=CHUNK_SIZE,
            overlap=CHUNK_OVERLAP,
        )

        all_chunks.extend(chunks)
```

Here, `chunk_text()` is used to chunk the text from the document.

**Run**

```bash
uv run Week6/day2/04_document_chunk.py

```

---

### Task2 - Embedding the chunk

Here, we have used the reusable `load_documents()` from `utils.py`.

```python
from Week6.config import CHUNK_SIZE, CHUNK_OVERLAP, DOCUMENT_PATH
from Week6.chunking import chunk_text

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
```

then, after loading the chunks, now we embed them using `embed_batch(texts: list[str])` from `EmbeddingService`:

```python
  texts = [
        chunk.text
        for chunk in chunks
    ]

    print("\nTEXT: ", texts)

    embeddings = embedding_service.embed_batch(
        texts
    )
```

This is how all the texts are converted to the embedding vectors.

**Run**:

```bash
uv run Week6/day2/05_embed_chunks.py

```

---

### Task3 - Store the chunks into qdrant

After chunking documents and embedding them, now we store the chunk into the qdrant storage.

```python
from qdrant_client.models import PointStruct

from Week6.config import QDRANT_PATH
from Week6.chunking import chunk_text
from Week6.embeddings import EmbeddingService
from Week6.qdrant_client import QdrantService
from Week6.utils import load_documents

chunks = load_documents()

embedding_service = EmbeddingService()

texts = [
  chunk.text
  for chunk in chunks
]

embeddings = embedding_service.embed_batch(
  texts
)

qdrant = QdrantService(
  path=QDRANT_PATH
)

qdrant.create_collection(
  vector_size=vector_size
)

points = []

for index, (chunk, embedding) in enumerate(
  zip(chunks, embeddings)
):

  point = PointStruct(
    id=index,
    vector=embedding,
    payload={
      "text": chunk.text,
      "source": chunk.source,
      "chunk_id": chunk.chunk_id,
    },
  )

points.append(point)

qdrant.insert_points(points)

count = qdrant.count_points()

```

**Run**:

```bash
uv run Week6/day2/06_store_chunks_in_qdrant.py

```

---

## Day 3 - Vector Search, Top K & Metadata Payload

In Day 3, here we have performed vector search from the points that we store into qdrant from Day 2. Retrieve the top-k value and display the metadata payload stored in points.

```text
User Query
    ↓
Query Embedding
    ↓
Qdrant Vector Search
    ↓
Top-K Results
    ↓
Relevant Chunks
```

The query itself must also become an embedding:

```text
"What is Python?"
       ↓
Embedding model
       ↓
[0.12, -0.32, 0.45, ...]
```

Then Qdrant compares that vector against the vectors stored in the collection.

```text
Query Vector
     ↓
   Qdrant
     ↓
Similarity comparison
     ↓
Most similar vectors
```

Points to Remember:

```python
with_payload = True
with_vectors = False
```

It means that Qdrant returns:

```text
text
source
chunk_id
```

and means we don't return the 2048-dimensional vectors because we don't need to print them from stored payload.

What we do in Day 3:

```text
"What is Python used for?"
             ↓
       EmbeddingService
             ↓
       Query Vector
             ↓
         Qdrant
             ↓
   Compare with stored vectors
             ↓
      Sort by similarity
             ↓
       Top matching points
```

You are no longer calculating cosine similarity manually with what we have done in Week5 tasks.

Conceptually:

```text
Point
│
├── ID
│   └── 0
│
├── Vector
│   └── [2048 numbers]
│
└── Payload
    ├── text
    ├── source
    └── chunk_id
```

**Why score matters**

Because Qdrant is using:

```python
Distance.COSINE
```

the score represents how similar the query vector is to the stored vector.

Conceptually:

```text
Higher score
↓
More semantically similar
Lower score
↓
Less semantically similar
```

For example:

```text
Query:
"What is Python used for?"
python.txt → 0.86
react.txt → 0.29
```

Python is more semantically related to the query.

Don't treat a score like:

```text
0.86 = 86% correct
```

That's not what it means.

It is a similarity score, not a correctness percentage.

About **Top-K Search**, Now we make the search configurable.

Instead of always doing:

```python
limit = 5
```

we want:

```text
Top 1
Top 3
Top 5
Top 10
```

This is called **Top-K retrieval**.

---

## Week 6 Overall Architecture

The complete Week 6 workflow will gradually build toward:

```text
Documents
│
▼
Load Documents
│
▼
Chunk Documents
│
├── Chunk 1
├── Chunk 2
├── Chunk 3
└── Chunk N
│
▼
Generate Embeddings
│
▼
Store in Qdrant
│
├── Vector
├── Text
├── Source
└── Metadata
│
▼
User Query
│
▼
Generate Query Embedding
│
▼
Qdrant Similarity Search
│
▼
Return Most Relevant Chunks
```
