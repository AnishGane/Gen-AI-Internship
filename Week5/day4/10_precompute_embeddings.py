import json
from openai import OpenAI
from Week5.config import BASE_URL,API_KEY, EMBEDDING_MODEL

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
)

DOCUMENTS = [
    "Python is a popular programming language used for AI.",
    "Machine learning allows computers to learn patterns from data.",
    "React is used to build interactive web interfaces.",
    "PostgreSQL is a relational database management system.",
    "Docker runs applications inside isolated containers.",
    "Deep learning uses neural networks to learn complex patterns.",
    "Git tracks changes in source code.",
]

def get_embeddings(texts):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
        encoding_format="float",
    )
    
    return [item.embedding for item in response.data]

vectors = get_embeddings(DOCUMENTS)

records = []

for document, vector in zip(DOCUMENTS, vectors):
    records.append({
        "text": document,
        "embedding": vector,
    })

with open(
    "Week5/day4/embeddings.json",
    "w",
    encoding="utf-8",
) as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print(f"Saved {len(records)} document embeddings.")