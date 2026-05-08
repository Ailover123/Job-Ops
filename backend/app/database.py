import os
from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import SQLModel, Field, JSON, Column, create_engine, Session
from typing import Generator
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# DATABASE_URL should be in .env, e.g., postgresql://user:pass@host:5432/db
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback to local postgres if not set (for dev convenience if they have one)
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/job_ops"

engine = create_engine(DATABASE_URL)

def init_db():
    # Import models to ensure they are registered
    from app import db_models
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
