import os
from pathlib import Path
from dotenv import load_dotenv

# Search for backend/.env first, then root .env, then fallback to default search
_backend_dir = Path(__file__).resolve().parent.parent.parent
_backend_env = _backend_dir / ".env"
_root_env = _backend_dir.parent / ".env"

if _backend_env.exists():
    load_dotenv(dotenv_path=_backend_env)
elif _root_env.exists():
    load_dotenv(dotenv_path=_root_env)
else:
    load_dotenv()

class Settings:
    MONGODB_URI: str = os.getenv("MONGODB_URI", "").strip()
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "loopback_db").strip()
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    ENV: str = os.getenv("ENV", "development")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1").strip()
    BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "meta.llama3-8b-instruct-v1:0").strip()
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434").strip()
    OLLAMA_MODEL_ID: str = os.getenv("OLLAMA_MODEL_ID", "llama3.2:latest").strip()
    STRANDS_MODEL_ID: str = os.getenv("STRANDS_MODEL_ID", "gemma:2b").strip()

settings = Settings()
