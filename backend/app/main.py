from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, recommendations, onboarding

app = FastAPI(
    title="Job-Ops API",
    description="Fresher-first job matching API.",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(onboarding.router, prefix="/api/v1")

