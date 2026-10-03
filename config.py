import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# LLM
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
API_KEY = os.getenv("API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-120b")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
RATE_LIMIT_WAIT = int(os.getenv("RATE_LIMIT_WAIT", "5"))

# Paths
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"
REQUIREMENTS_DIR = BASE_DIR / "data" / "requirements"
PROMPTS_DIR = BASE_DIR / "prompts"

# Scoring
WARNING_WEIGHT = 0.5

def check_config():
    if not API_KEY:
        raise RuntimeError("API_KEY missing. Copy .env.example to .env and fill it in.") 