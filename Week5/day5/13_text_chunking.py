# Fixed-size chunking
# This is a simple way to chunk text into fixed-size chunks.
# It is useful for when you need to chunk text into a fixed-size chunks.

def chunk_text(text, chunk_size = 50):
    words = text.split()
    
    chunks = []

    for start in range(0, len(words), chunk_size):
        end = start + chunk_size
        
        chunk = " ".join(words[start:end])

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
    )

    for index, chunk in enumerate(chunks, start=1):
        print(f"Chunk {index}:")
        print(chunk)
        print()