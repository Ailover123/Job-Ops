# Backend

FastAPI backend for Job-Ops.

## Planned Responsibilities

- Resume upload and parsing
- Profile and preferences APIs
- Job ingestion and normalization
- Matching and recommendation APIs
- Saved/applied job tracking

## First Backend Goal

Serve recommendations from `data/seed_jobs.json` using the rule-based matching starter.

## Suggested Local Run

After dependencies are installed:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

