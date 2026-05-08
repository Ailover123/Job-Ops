# AI Fresher Job Matcher - Product Requirements Document

## 1. Product Summary

AI Fresher Job Matcher is a job discovery and recommendation platform for freshers, final-year students, interns, and early-career candidates.

The system parses a resume once, builds a structured candidate profile, asks for job preferences, aggregates relevant jobs from public sources and ATS portals, then ranks jobs by profile fit.

The product is not an auto-apply bot and does not rewrite resumes by default. Its main job is to reduce irrelevant search effort.

## 2. Problem Statement

Freshers spend too much time searching across LinkedIn, Internshala, Naukri, Indeed, company career pages, and lesser-known startup hiring portals. Most listings are duplicated, stale, senior-focused, spammy, or poorly matched.

Existing AI job tools often focus on autonomous application agents or resume rewriting. That creates cost, reliability, hallucination, and trust issues.

## 3. Target Users

- Freshers
- Final-year students
- Early-career developers
- Internship seekers
- Remote job seekers
- Candidates looking for entry-level AI, software, data, and web development roles

## 4. Core Value Proposition

Find relevant fresher-friendly jobs from mainstream and hidden hiring sources without forcing the user to repeatedly edit resumes or manually search many portals.

## 5. MVP Goals

- Allow one-time resume upload.
- Extract structured candidate profile.
- Let users edit profile and preferences.
- Aggregate jobs from selected public/ATS sources.
- Filter jobs by fresher suitability, skills, location, and remote preference.
- Rank jobs using rules plus semantic similarity.
- Provide a dashboard with recommended, saved, and applied jobs.

## 6. Non-Goals for MVP

- No auto-apply workflow.
- No automatic resume rewriting.
- No scraping of heavily protected portals as the first dependency.
- No complex multi-agent system.
- No recruiter-facing product.
- No salary prediction in MVP.
- No full interview preparation module in MVP.

## 7. Main User Journey

1. User signs up.
2. User uploads resume.
3. System extracts skills, education, projects, certifications, roles, and preferred domains.
4. User reviews and edits extracted profile.
5. User selects preferences such as location, remote/on-site, role type, tech stack, and job type.
6. System aggregates jobs from configured sources.
7. Matching engine scores and ranks jobs.
8. User views recommended jobs in dashboard.
9. User saves, applies externally, or marks jobs as irrelevant.
10. System uses feedback to improve recommendations.

## 8. Success Metrics

- Match relevance accuracy
- Job click-through rate
- Saved job rate
- Application conversion rate
- Duplicate reduction percentage
- Notification engagement
- Weekly active users
- User retention after first week

## 9. MVP Feature List

### Resume Upload

- PDF upload.
- Resume text extraction.
- Basic validation for file size and file type.

### Profile Extraction

- Skills
- Education
- Projects
- Certifications
- Experience level
- Suggested role categories
- Preferred domains inferred from resume

### Profile Editor

- Add/remove skills.
- Edit education.
- Edit preferred roles.
- Edit location and work mode.

### Job Aggregation

- Initial sources should prioritize ATS and public startup boards:
  - Greenhouse
  - Ashby
  - Lever
  - Workable
  - YC Work at a Startup
  - Wellfound where feasible
  - RemoteOK
  - Remotive

### Matching

- Rule-based filters for location, experience, freshness, and job type.
- Embedding similarity for job description vs user profile.
- Final match score shown to user.

### Dashboard

- Recommended jobs
- Saved jobs
- Applied jobs
- Match score
- Source portal
- Posted date or discovered date

## 10. Future Features

- Email and WhatsApp alerts.
- AI interview preparation.
- ATS resume scoring.
- Resume enhancement as optional assistive feature.
- Skill-gap analysis.
- Portfolio analyzer.
- Recruiter/company insights.
- One-click apply after legal and reliability review.

