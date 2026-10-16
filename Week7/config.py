import os
from dotenv import load_dotenv
from pathlib import Path

# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from the project root
load_dotenv(BASE_DIR / ".env")

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("OPENROUTER_API_KEY")
CHAT_MODEL = os.getenv("MODEL") 

if not API_KEY:
    raise ValueError("API_KEY is missing from .env")

if not BASE_URL:
    raise ValueError("BASE_URL is missing from .env")

if not CHAT_MODEL:
    raise ValueError("CHAT_MODEL is missing from .env")