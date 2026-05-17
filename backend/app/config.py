import os
import json
from dotenv import load_dotenv

# Ensure environment is loaded
load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL") or ""
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    BACKEND_CORS_ORIGINS: list[str] = []
    INTERNAL_API_KEY: str | None = os.getenv("INTERNAL_API_KEY")

    def __init__(self):
        # 1. Fallback for DATABASE_URL
        if not self.DATABASE_URL:
            self.DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/job_ops"
        
        # 2. Driver mismatch normalization
        # Rewrite to postgresql+psycopg2 (psycopg2-binary) to prevent driver not found errors
        if self.DATABASE_URL.startswith("postgresql://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
        elif self.DATABASE_URL.startswith("postgresql+psycopg://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)

        # 3. Parse CORS origins
        cors_raw = os.getenv("BACKEND_CORS_ORIGINS")
        if cors_raw:
            try:
                parsed = json.loads(cors_raw)
                if isinstance(parsed, list):
                    self.BACKEND_CORS_ORIGINS = parsed
            except Exception:
                self.BACKEND_CORS_ORIGINS = [o.strip() for o in cors_raw.split(",") if o.strip()]
        else:
            self.BACKEND_CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

settings = Settings()
