import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routers import health, recommendations, onboarding, jobs, preferences, roadmap, internal
from app.database import init_db

from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    init_db()
    yield

app = FastAPI(
    title="Job-Ops API",
    description="Fresher-first job matching API.",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
backend_cors_origins_raw = os.getenv("BACKEND_CORS_ORIGINS")
origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

if backend_cors_origins_raw:
    try:
        # Try to parse as JSON list
        parsed = json.loads(backend_cors_origins_raw)
        if isinstance(parsed, list):
            origins = parsed
    except Exception:
        # Fallback to comma-separated list
        origins = [o.strip() for o in backend_cors_origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(onboarding.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(preferences.router, prefix="/api/v1")
app.include_router(roadmap.router, prefix="/api/v1")
app.include_router(internal.router, prefix="/api/v1")



