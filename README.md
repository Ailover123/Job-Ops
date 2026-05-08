# Job-Ops

AI Fresher Job Matcher is a fresher-focused job discovery platform. It builds a structured profile from one resume, gathers jobs from public and ATS-style sources, and recommends roles by skill, location, work mode, and fresher suitability.

This project intentionally avoids making resume rewriting or auto-apply the core flow.

## Current Status

Planning docs and seed data are ready. The codebase is scaffolded and the first vertical slice (Backend + Frontend) is running with seed data.

- `frontend/` - Next.js app
- `backend/` - FastAPI app
- `data/seed_jobs.json` - synthetic seed listings for development
- `docs/` - product, architecture, API, database, matching, and handoff docs

## Local Development Setup

### Prerequisites
- Python 3.13+
- Node.js v22+
- npm (on Windows, use `npm.cmd` if blocked by execution policy)

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run tests:
   ```bash
   python -m pytest
   ```
6. Start the FastAPI server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm.cmd install
   ```
3. Start the Next.js dev server:
   ```bash
   npm.cmd run dev
   ```
   The dashboard will be available at `http://localhost:3000`.

## Architecture
- **Frontend**: Next.js (App Router), Tailwind CSS.
- **Backend**: FastAPI, Pydantic, Rule-based matching engine.
- **Data**: Seed jobs available in `data/seed_jobs.json`.

## Documentation
For more details, see the `docs/` directory:
- `ARCHITECTURE.md` - Technical overview
- `API_CONTRACT.md` - Endpoint specifications
- `DATABASE_SCHEMA.md` - Data models
- `MATCHING_LOGIC.md` - How jobs are ranked
- `AI_WORKFLOW.md` - How LLMs are integrated
