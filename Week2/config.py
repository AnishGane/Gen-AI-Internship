import os
from dotenv import load_dotenv
from pathlib import Path

# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from the project root
load_dotenv(BASE_DIR / ".env")

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("OPENROUTER_API_KEY")
MAX_TOKENS = os.getenv("MAX_TOKENS")
MODEL = os.getenv("MODEL")