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
        from app.db_models import CollectorSource
        from sqlmodel import select
        
        try:
            source_count = session.exec(select(CollectorSource)).first()
            if not source_count:
                print("Seeding database with default collector sources...")
                sources = [
                    CollectorSource(company_name="Cloudflare", board_token="cloudflare", source_type="greenhouse", enabled=True),
                    CollectorSource(company_name="Stripe", board_token="stripe", source_type="greenhouse", enabled=True),
                    CollectorSource(company_name="Lever", company_id="lever", source_type="lever", enabled=True),
                    CollectorSource(company_name="Vercel", company_id="vercel", source_type="lever", enabled=True)
                ]
                for src in sources:
                    session.add(src)
                session.commit()
        except Exception as e:
            print(f"Error seeding database with collector sources: {e}")
            session.rollback()

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
