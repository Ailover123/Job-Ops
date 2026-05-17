from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, recommendations, onboarding, jobs, preferences, roadmap, internal
from app.database import init_db

from app.config import settings

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
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



