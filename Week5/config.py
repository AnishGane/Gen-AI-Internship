import os
from dotenv import load_dotenv
from pathlib import Path

# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from the project root
load_dotenv(BASE_DIR / ".env")

BASE_URL = "https://openrouter.ai/api/v1"
API_KEY = os.getenv("OPENROUTER_API_KEY")
EMBEDDING_MODEL = "nvidia/llama-nemotron-embed-vl-1b-v2:free"

if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable not set")