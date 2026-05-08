# Job-Ops

AI Fresher Job Matcher is a fresher-focused job discovery platform. It builds a structured profile from a resume, gathers jobs from public and ATS-style sources, and recommends roles by skill, location, work mode, and fresher suitability.

This project intentionally avoids making resume rewriting or auto-apply the core flow.

## Current Status

The application now supports **PostgreSQL persistence** for user profiles. The initial onboarding flow is functional, from resume upload to profile saving.

- **Backend**: FastAPI with SQLModel (SQLAlchemy + Pydantic v2).
- **Frontend**: Next.js (App Router) with persistent state management.
- **Database**: PostgreSQL (Supabase recommended for dev).

## Application Flow

1. **Resume Upload**: User uploads a PDF resume.
2. **Text Extraction**: System extracts raw text using `pypdf`.
3. **Profile Extraction**: AI (Gemini) structures the text into a detailed profile.
4. **Profile Review**: User reviews and edits the extracted details.
5. **Save Profile**: Profile is persisted in PostgreSQL.
6. **Dashboard**: User receives personalized job recommendations.

## Screenshots

| Home Page | Resume Upload | Profile Review |
| :---: | :---: | :---: |
| ![Home](docs/assets/home.png) | ![Upload](docs/assets/upload.png) | ![Review](docs/assets/review.png) |

## Local Development Setup

### Prerequisites
- Python 3.13+
- Node.js v22+
- PostgreSQL instance (Local or Supabase)

### Backend Setup
1. Navigate to `backend/`.
2. Create and activate a virtual environment.
3. Install dependencies: `pip install -r requirements.txt`.
4. Create a `.env` file based on `.env.example`:
   ```env
   GEMINI_API_KEY=your_key_here
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   ```
5. Run migrations (initializes schema): `python -m app.main`.
6. Start server: `python -m uvicorn app.main:app --reload`.

### Frontend Setup
1. Navigate to `frontend/`.
2. Install dependencies: `npm.cmd install`.
3. Start dev server: `npm.cmd run dev`.

## Documentation
For more details, see the `docs/` directory:
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical overview
- [API_CONTRACT.md](docs/API_CONTRACT.md) - Endpoint specifications
- [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) - Data models
- [MATCHING_LOGIC.md](docs/MATCHING_LOGIC.md) - How jobs are ranked
