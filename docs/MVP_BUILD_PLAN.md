# AI Fresher Job Matcher - MVP Build Plan

## 1. Build Strategy

Build the system in thin working slices.

The first working version should prove:

```text
resume profile -> preferences -> job data -> match score -> dashboard
```

Avoid starting with the hardest scraping targets.

## 2. Suggested Timeline

## Week 1 - Foundation

Goals:

- Set up repo.
- Choose stack.
- Create frontend shell.
- Create backend shell.
- Set up database.
- Add authentication.

Deliverables:

- User can sign up/login.
- User can access protected dashboard.
- Database migrations exist.

## Week 2 - Resume and Profile

Goals:

- Resume upload.
- PDF text extraction.
- LLM-based structured parsing.
- Editable profile page.

Deliverables:

- User uploads resume.
- System extracts profile.
- User can edit and save profile.

## Week 3 - Job Data and Dashboard

Goals:

- Create job schema.
- Seed jobs manually or via simple ATS collectors.
- Build dashboard.
- Build job detail page.

Deliverables:

- Jobs appear in dashboard.
- User can open job details.
- User can save jobs.

## Week 4 - Matching Engine

Goals:

- Implement hard filters.
- Implement fresher detection.
- Implement skill score.
- Implement basic semantic score.
- Show match explanation.

Deliverables:

- Dashboard shows ranked recommendations.
- Job detail shows why it matched.

## Week 5 - Aggregation and Deduplication

Goals:

- Add Greenhouse collector.
- Add Lever collector.
- Add Ashby or Workable collector.
- Add deduplication.
- Add stale job handling.

Deliverables:

- System refreshes jobs from multiple sources.
- Duplicate listings are reduced.

## Week 6 - Polish and Demo Readiness

Goals:

- Improve UI.
- Add applied jobs.
- Add feedback.
- Add error states.
- Deploy MVP.

Deliverables:

- Usable deployed MVP.
- Demo-ready flow from resume to recommendations.

## 3. Minimum Demo Scope

For a strong demo, you need:

- Auth
- Resume upload
- Profile extraction
- Profile editing
- Preferences
- Job recommendations
- Match score
- Save/apply tracking

You do not need:

- Auto-apply
- Resume rewriting
- All job portals
- Notifications
- Admin panel

## 4. Development Order

1. Database schema
2. Auth
3. Resume upload
4. Profile extraction
5. Profile editor
6. Preferences
7. Job seed/import
8. Matching engine
9. Dashboard
10. Saved/applied jobs
11. Feedback
12. Deployment

## 5. Testing Checklist

- Resume upload accepts valid PDF.
- Resume upload rejects invalid file.
- Parser returns valid JSON.
- User can edit AI-extracted fields.
- Jobs are normalized correctly.
- Duplicate jobs are detected.
- Senior jobs are filtered for fresher users.
- Remote preference works.
- Match score is explainable.
- Saved jobs persist.
- Applied jobs persist.

## 6. Biggest Risks

- Scraping instability
- Poor resume extraction
- Weak recommendation quality
- Duplicate jobs
- Stale listings
- Overcomplicated AI usage

## 7. Risk Reduction

- Start with ATS and manual seed sources.
- Keep profile editable.
- Use rules before embeddings.
- Avoid auto-apply.
- Keep scoring transparent.

