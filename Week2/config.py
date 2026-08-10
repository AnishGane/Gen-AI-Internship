import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://openrouter.ai/api/v1"
API_KEY = os.getenv("OPENROUTER_API_KEY")
MAX_TOKENS = 400
MODEL = "openrouter/free"

if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable not set")