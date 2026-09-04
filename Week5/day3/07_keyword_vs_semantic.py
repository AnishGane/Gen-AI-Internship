DOCUMENTS = [
    "Python is a popular programming language used for AI.",
    "Machine learning allows computers to learn patterns from data.",
    "React is used to build interactive web interfaces.",
    "PostgreSQL is a relational database management system.",
    "Docker runs applications inside isolated containers.",
]

def keyword_search(query, documents):
    query_words = set(query.lower().split())

    results = []
    
    for document in documents:
        document_words = set(document.lower().split())

        score = len(query_words & document_words)

        results.append((document, score))

        return sorted(results, key=lambda x: x[1], reverse=True)

if __name__ == "__main__":
    query = "What is the best programming language for AI?"
    
    results = keyword_search(query, DOCUMENTS)
    
    print(f"Keyword search results for '{query}':")
    for rank, (document, score) in enumerate(results, start=1):
        print(f"{rank}. [{score}] {document}")