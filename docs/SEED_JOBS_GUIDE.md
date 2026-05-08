# AI Fresher Job Matcher - Manual Seed Jobs Guide

## 1. Why Seed Jobs Manually First

Manual seed jobs let you build and test the product before solving scraping.

This helps validate:

- Job cards
- Search and filters
- Match scoring
- Fresher detection
- Duplicate detection
- Saved/applied job flows
- Dashboard UX

Do not wait for real scrapers before building the matcher.

## 2. Recommended Seed Size

Start with 40 to 60 jobs.

That is enough to test ranking without becoming hectic.

Suggested split:

- 10 excellent fresher matches
- 10 good junior matches
- 10 internships
- 8 remote roles
- 6 wrong-location roles
- 6 senior roles that should be filtered or downranked
- 5 duplicate or near-duplicate listings
- 5 low-quality/noisy jobs

## 3. Role Categories To Include

For your project, seed these categories:

- Python Developer
- Backend Developer
- AI/ML Intern
- Data Analyst
- SQL Analyst
- Frontend Developer
- Full Stack Developer
- Android Developer
- QA Engineer
- Technical Support Engineer

## 4. Experience Levels To Include

Include variety:

- Internship
- Fresher
- Entry level
- 0-1 years
- 0-2 years
- 1-3 years
- 3-5 years
- 5+ years

The senior listings are useful because they test whether your matcher avoids bad recommendations.

## 5. Locations To Include

For an India-focused fresher product, include:

- Remote
- Bangalore
- Mumbai
- Pune
- Hyderabad
- Chennai
- Delhi NCR
- Mangalore
- Kochi
- Jaipur

Also include a few global remote jobs.

## 6. Source Types To Include

Use multiple source names even if they are synthetic:

- Greenhouse
- Lever
- Ashby
- Workable
- YC Jobs
- RemoteOK
- Remotive
- Internshala
- Naukri
- LinkedIn
- Company Careers

This helps test source filters early.

## 7. Seed Job JSON Shape

Use this shape:

```json
{
  "external_id": "seed-001",
  "title": "Python Developer Intern",
  "company_name": "Example Labs",
  "description": "Work on backend APIs using Python and SQL.",
  "location": "Remote",
  "city": null,
  "state": null,
  "country": "India",
  "is_remote": true,
  "job_type": "internship",
  "experience_min": 0,
  "experience_max": 1,
  "skills": ["Python", "SQL", "FastAPI"],
  "apply_url": "https://example.com/jobs/seed-001",
  "source_name": "Seed",
  "posted_at": "2026-05-01",
  "is_active": true
}
```

## 8. Important Testing Cases

Create seed data that checks:

- Excellent match with Python and MySQL
- AI/ML internship with Python
- Data analyst job with SQL/MySQL
- Android role to support your existing identity
- Remote job
- Same-city job
- Senior job that should be filtered
- Duplicate job from two sources
- Job with vague description
- Job missing posted date

## 9. Synthetic vs Real Jobs

Use synthetic seed jobs for development.

Use real jobs only when:

- You are testing live aggregation.
- You store the original source URL.
- You can refresh or expire stale listings.

