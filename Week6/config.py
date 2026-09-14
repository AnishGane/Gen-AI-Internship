import os
from dotenv import load_dotenv
from pathlib import Path

# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from the project root
load_dotenv(BASE_DIR / ".env")

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("OPENROUTER_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

# Vector database configuration
COLLECTION_NAME = os.getenv(
    "COLLECTION_NAME",
    "week6_documents"
)

QDRANT_PATH = os.getenv(
    "QDRANT_NAME",
    "storage/qdrant"
)

# Search configuration
TOP_K = int(   
    os.getenv(
        "TOP_K", "5"
    )
)

# Chunking configuration
CHUNK_SIZE = int(
    os.getenv(
    "CHUNK_SIZE", "100"
    )
)

CHUNK_OVERLAP = int(
    os.getenv(
        "CHUNK_OVERLAP", "20"
    )
) 