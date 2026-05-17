# Backend

FastAPI backend for Job-Ops.

## Planned Responsibilities

- Resume upload and parsing
- Profile and preferences APIs
- Job ingestion and normalization
- Matching and recommendation APIs
- Saved/applied job tracking

## Real Jobs & Dev Fallback

- **Real Job Listings**: Ingested directly from public Greenhouse/Lever boards via internal collector endpoints and saved in the PostgreSQL/SQLite `Job` database table.
- **Development Fallback**: When the database is empty of imported jobs, `data/seed_jobs_dev_fallback.json` provides an offline/mock set of seed listings for early testing. Fake `example.com` seed jobs are filtered out in production when real database-backed listings are present.

## Suggested Local Run

After dependencies are installed:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

