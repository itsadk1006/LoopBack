import os
from dotenv import load_dotenv

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

settings = Settings()
