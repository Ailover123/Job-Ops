from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

# Setup engine with centralized normalizations
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(settings.DATABASE_URL)

def init_db():
    # Import models to ensure they are registered
    from app import db_models
    SQLModel.metadata.create_all(engine)
    
    # Seeding database configurations inside execution in Phase 3
    with Session(engine) as session:
        # Check and seed default CollectorSource values if empty
        from app.seed_loader import seed_collector_sources
        try:
            seed_collector_sources(session)
        except Exception as e:
            print(f"Error seeding database with collector sources: {e}")
            session.rollback()

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
