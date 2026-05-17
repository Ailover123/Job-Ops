# Job-Ops

AI Fresher Job Matcher is a fresher-focused job discovery platform. It builds a structured profile from a resume, gathers jobs from public and ATS-style sources, and recommends roles by skill, location, work mode, and fresher suitability.

This project intentionally avoids making resume rewriting or auto-apply the core flow.

### Core Features (v0.1.0 MVP)
- **AI-Powered Matching**: Personalized job ranking based on skills and preferences.
- **Resume Parsing**: Direct extraction of profile data from PDF resumes.
- **Job Persistence**: Full PostgreSQL storage for user profiles.
- **Saved & Applied Tracking**: Bookmarking and application history with live backend updates.
- **Intelligent Fallbacks**: Robust dashboard that works even when offline or without a profile.

### Current Tech Stack
- **Backend**: FastAPI, SQLModel (PostgreSQL), Pydantic v2.
- **Frontend**: Next.js 15 (App Router), Lucide Icons, Vanilla CSS.
- **Testing**: Pytest with in-memory SQLite isolation.

---

### Application Flow

1. **Onboarding**: User uploads a PDF resume.
2. **Extraction**: Backend uses Gemini to parse technical skills, roles, and experience.
3. **Review**: User confirms or edits the extracted data.
4. **Persistence**: Profile is saved to PostgreSQL.
5. **Dashboard**: 
   - Backend fetches the latest profile.
   - Matching engine ranks seed jobs against user's specific skills and roles.
   - Dashboard displays personalized matches with "Strong", "Good", or "Possible" labels.

## Screenshots

| Dashboard | Resume Upload | Saved Jobs | Applications |
| :---: | :---: | :---: | :---: |
| ![Dashboard](docs/assets/home.png) | ![Upload](docs/assets/upload.png) | ![Saved](docs/assets/saved.png) | ![Applications](docs/assets/applications.png) |

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
   BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000", "http://192.168.0.105:3000"]
   ```
5. Run migrations (initializes schema): `alembic upgrade head`.
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
