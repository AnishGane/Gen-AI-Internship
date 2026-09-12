import json

def save_embeddings(embeddings, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(embeddings, f, ensure_ascii=False, indent=2)

def load_embeddings(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    data = [
        {
            "text": "Python is a popular programming language used for AI.",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        },
        {
            "text": "Machine learning allows computers to learn patterns from data.",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        },
        {
            "text": "React is used to build interactive web interfaces.",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        },
        {
            "text": "PostgreSQL is a relational database management system.",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        }
    ]
    
    filename = "Week5/day4/test_embeddings.json"

    save_embeddings(data, filename)

    loaded_data = load_embeddings(filename)

    print("Saved embeddings:")
    for item in data:
        print(f"Text: {item['text']}")
        print(f"Embedding: {item['embedding']}")
        print("-" * 30)

    print("\nLoaded embeddings:")
    for item in loaded_data:
        print(f"Text: {item['text']}")