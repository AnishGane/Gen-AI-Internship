# Overlapping chunking
# This is a more advanced way to chunk text into overlapping chunks.
# It is useful for when you need to chunk text into overlapping chunks.

def chunk_text(text, chunk_size = 50, overlap = 10):
    words = text.split()

    if overlap >= chunk_size:
        raise ValueError("Overlap must be less than chunk size")
    
    chunks = []
    
    step = chunk_size - overlap
    
    for start in range(0, len(words), step):
        end = start + chunk_size

        chunk = " ".join(words[start:end])
        
        if chunk:
            chunks.append(chunk)

    return chunks

if __name__ == "__main__":
    text = """
    Python is a popular programming language.
    It is widely used in web development.
    Python is also used in data science.
    Machine learning libraries are available in Python.
    Deep learning is another important application.
    Python can also be used for automation.
    """
    
    chunks = chunk_text(
        text,
        chunk_size=15,
        overlap=3,
    )

    for index, chunk in enumerate(chunks, start=1):
        print(f"Chunk {index}:")
        print(chunk)
        print()