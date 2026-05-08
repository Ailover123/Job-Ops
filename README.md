# Job-Ops

AI Fresher Job Matcher is a fresher-focused job discovery platform. It builds a structured profile from a resume, gathers jobs from public and ATS-style sources, and recommends roles by skill, location, work mode, and fresher suitability.

This project intentionally avoids making resume rewriting or auto-apply the core flow.

### 🚀 Current Status: MVP persistent slice
- [x] **Backend**: FastAPI + SQLModel + PostgreSQL (Supabase/Local).
- [x] **Persistence**: Candidates can save their extracted/reviewed profiles.
- [x] **Personalization**: Dashboard job recommendations are ranked based on the latest saved profile.
- [x] **Demo Mode**: Graceful fallback to seed data if no profile is saved.

### 🛠️ Core Stack
- **Frontend**: Next.js 15, TypeScript, Vanilla CSS (Premium Glassmorphism).
- **Backend**: FastAPI, SQLModel (PostgreSQL), Pydantic v2.
- **AI**: Google Gemini (Flash 1.5) for resume parsing.

---

### 📡 Application Flow

1. **Onboarding**: User uploads a PDF resume.
2. **Extraction**: Backend uses Gemini to parse technical skills, roles, and experience.
3. **Review**: User confirms or edits the extracted data.
4. **Persistence**: Profile is saved to PostgreSQL.
5. **Dashboard**: 
   - Backend fetches the latest profile.
   - Matching engine ranks seed jobs against user's specific skills and roles.
   - Dashboard displays personalized matches with "Strong", "Good", or "Possible" labels.

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
