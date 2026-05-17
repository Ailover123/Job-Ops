# Job-Ops - API Contract

This document specifies the REST API contract for the Job-Ops backend services. All endpoints are prefixed by the base path.

**Base Path:** `/api/v1`

---

## 1. Health Checks

### GET `/health`
Returns the status and health metrics of the application database and services.

**Response:** `200 OK`
```json
{
  "status": "healthy"
}
```

---

## 2. Onboarding & Profile Extraction

### POST `/onboarding/resume`
Accepts a PDF resume upload, extracts its raw text, and returns the extracted content.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body:**
  - `file`: Binary PDF file.

**Response:** `200 OK`
```json
{
  "filename": "john_doe_resume.pdf",
  "text": "John Doe\nSoftware Engineer...\nSkills: Python, React, SQL..."
}
```

---

### POST `/onboarding/profile/extract` (Alias: `/profile/extract`)
Given raw resume text, parses and structures it into a structured Profile schema using the LLM parser.

**Request:**
- **Content-Type:** `application/json`
- **Body:**
```json
{
  "resume_text": "John Doe\nSoftware Engineer...\nSkills: Python, React, SQL..."
}
```

**Response:** `200 OK`
```json
{
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1 (555) 0199",
  "location": "San Francisco, CA",
  "skills": ["Python", "React", "SQL", "Git"],
  "education": [
    {
      "institution": "University of Technology",
      "degree": "B.S. Computer Science",
      "graduation_year": "2024"
    }
  ],
  "experience": [
    {
      "company": "Tech Corp",
      "role": "Software Engineering Intern",
      "start_date": "2023-06",
      "end_date": "2023-09",
      "description": "Built reactive web applications using Next.js."
    }
  ],
  "projects": [
    {
      "title": "Portfolio Site",
      "description": "A static portfolio page hosted on Vercel."
    }
  ]
}
```

---

### POST `/profile`
Saves the completed, verified structured profile to the PostgreSQL/SQLite database for persistence.

**Request:**
- **Content-Type:** `application/json`
- **Body:** (Profile object, see structure in `/onboarding/profile/extract`)

**Response:** `200 OK`
```json
{
  "status": "success",
  "message": "Profile saved successfully",
  "profile": { ... }
}
```

---

### GET `/profile/latest`
Fetches the user's latest saved structured profile from the database.

**Response:** `200 OK`
```json
{
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1 (555) 0199",
  "location": "San Francisco, CA",
  "skills": ["Python", "React", "SQL", "Git"],
  "education": [...],
  "experience": [...],
  "projects": [...]
}
```
If no profile exists, returns `null` or a empty placeholder response.

---

## 3. Match Preferences

### POST `/preferences`
Saves the user's refined job search preferences to the database.

**Request:**
- **Content-Type:** `application/json`
- **Body:**
```json
{
  "preferred_roles": ["Frontend Engineer", "Full Stack Developer"],
  "preferred_locations": ["San Francisco, CA", "Remote"],
  "remote_preference": "remote_or_hybrid",
  "job_types": ["Full-time", "Internship"],
  "willing_to_relocate": true,
  "preferred_tech_stack": ["React", "TypeScript", "Node.js"]
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "preferred_roles": ["Frontend Engineer", "Full Stack Developer"],
  "preferred_locations": ["San Francisco, CA", "Remote"],
  "remote_preference": "remote_or_hybrid",
  "job_types": ["Full-time", "Internship"],
  "willing_to_relocate": true,
  "preferred_tech_stack": ["React", "TypeScript", "Node.js"],
  "updated_at": "2026-05-17T14:00:00Z"
}
```

---

### GET `/preferences/latest`
Fetches the user's latest saved match preferences from the database.

**Response:** `200 OK` (or `null` if not configured)
```json
{
  "preferred_roles": ["Frontend Engineer", "Full Stack Developer"],
  "preferred_locations": ["San Francisco, CA", "Remote"],
  "remote_preference": "remote_or_hybrid",
  "job_types": ["Full-time", "Internship"],
  "willing_to_relocate": true,
  "preferred_tech_stack": ["React", "TypeScript", "Node.js"]
}
```

---

## 4. Jobs & Recommendations

### GET `/jobs`
An alias endpoint retrieving the list of job match recommendations for the user based on the database-persisted profile and preferences.

**Response:** `200 OK`
```json
{
  "items": [
    {
      "job": {
        "external_id": "greenhouse-101",
        "title": "Software Engineer (New Grad)",
        "company_name": "Acme Corp",
        "location": "San Francisco, CA",
        "source_name": "greenhouse",
        "apply_url": "https://boards.greenhouse.io/acme/jobs/101",
        "skills": ["React", "TypeScript", "Node.js"],
        "description": "Join our product team..."
      },
      "skill_score": 0.9,
      "fresher_score": 1.0,
      "location_score": 1.0,
      "experience_score": 0.8,
      "quality_score": 1.0,
      "final_score": 85,
      "score_label": "Strong Match",
      "explanation": "Matches your strong frontend background and React/TypeScript skills."
    }
  ]
}
```

---

### POST `/recommendations`
Runs the compatibility score algorithm dynamically on a raw profile and match preference payload without committing the payload to the database. Primarily used during onboarding previews.

**Request:**
- **Content-Type:** `application/json`
- **Body:**
```json
{
  "profile": { ... },
  "preferences": { ... }
}
```

**Response:** `200 OK`
- Returns an array of recommendation objects with matching metrics.
```json
[
  {
    "job": { ... },
    "skill_score": 0.95,
    "fresher_score": 1.0,
    "location_score": 1.0,
    "experience_score": 0.8,
    "quality_score": 1.0,
    "final_score": 90,
    "score_label": "Excellent Match",
    "explanation": "..."
  }
]
```

---

### GET `/recommendations/latest-profile`
Fetches ranked recommendation listings computed dynamically based on the current persisted profile and preferences.

**Response:** `200 OK`
- Same schema structure as the `GET /jobs` response items.

---

### GET `/jobs/{external_id}`
Fetches the full details of a specific job by its external ID, alongside its dynamic compatibility score card.

**Response:** `200 OK`
```json
{
  "job": {
    "external_id": "greenhouse-101",
    "title": "Software Engineer (New Grad)",
    "company_name": "Acme Corp",
    "location": "San Francisco, CA",
    "source_name": "greenhouse",
    "apply_url": "https://boards.greenhouse.io/acme/jobs/101",
    "skills": ["React", "TypeScript", "Node.js"],
    "description": "..."
  },
  "has_profile": true,
  "match_score": 85,
  "match_label": "Strong Match",
  "match_explanation": "...",
  "skill_score": 0.88,
  "fresher_score": 1.0,
  "location_score": 1.0,
  "experience_score": 0.75
}
```

---

## 5. Saved & Applied Jobs

### POST `/saved-jobs`
Saves a job listing to the user's bookmarks list.

**Request:**
- **Content-Type:** `application/json`
- **Body:**
```json
{
  "job_external_id": "greenhouse-101",
  "job_title": "Software Engineer (New Grad)",
  "company_name": "Acme Corp",
  "location": "San Francisco, CA",
  "source_name": "greenhouse",
  "apply_url": "https://boards.greenhouse.io/acme/jobs/101",
  "skills": ["React", "TypeScript"]
}
```

**Response:** `200 OK`
```json
{
  "status": "success",
  "item": {
    "id": 1,
    "job_external_id": "greenhouse-101",
    "saved_at": "2026-05-17T14:15:00Z"
  }
}
```

---

### GET `/saved-jobs`
Retrieves all bookmarks/saved jobs for the current user.

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "job_external_id": "greenhouse-101",
      "job_title": "Software Engineer (New Grad)",
      "company_name": "Acme Corp",
      "location": "San Francisco, CA",
      "source_name": "greenhouse",
      "apply_url": "https://boards.greenhouse.io/acme/jobs/101",
      "skills": ["React", "TypeScript"],
      "saved_at": "2026-05-17T14:15:00Z"
    }
  ]
}
```

---

### DELETE `/saved-jobs/{job_external_id}`
Removes a job listing from the user's saved bookmarks by its external ID.

**Response:** `200 OK`
```json
{
  "status": "success",
  "message": "Saved job removed successfully"
}
```

---

### POST `/applications`
Tracks that a user has submitted an application for a specific job.

**Request:**
- **Content-Type:** `application/json`
- **Body:** (Same job attributes as `/saved-jobs`)

**Response:** `200 OK`
```json
{
  "status": "success",
  "item": {
    "id": 1,
    "job_external_id": "greenhouse-101",
    "status": "applied",
    "notes": null,
    "applied_at": "2026-05-17T14:20:00Z"
  }
}
```

---

### GET `/applications`
Retrieves the user's full history of tracked job applications, complete with their current progress statuses and custom notes.

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "job_external_id": "greenhouse-101",
      "job_title": "Software Engineer (New Grad)",
      "company_name": "Acme Corp",
      "location": "San Francisco, CA",
      "source_name": "greenhouse",
      "apply_url": "https://boards.greenhouse.io/acme/jobs/101",
      "skills": ["React", "TypeScript"],
      "status": "interviewing",
      "notes": "Spoke to recruiter. Round 1 scheduled for next Tuesday.",
      "applied_at": "2026-05-17T14:20:00Z"
    }
  ]
}
```

---

### PUT `/applications/{job_external_id}`
Updates the tracker status or custom progress notes for an active job application.

**Request:**
- **Content-Type:** `application/json`
- **Body:** (One or both properties can be updated)
```json
{
  "status": "interviewing",
  "notes": "Completed initial screening. Preparing for technical challenge."
}
```

**Response:** `200 OK`
```json
{
  "status": "success",
  "item": {
    "job_external_id": "greenhouse-101",
    "status": "interviewing",
    "notes": "Completed initial screening. Preparing for technical challenge.",
    "applied_at": "2026-05-17T14:20:00Z"
  }
}
```

---

## 6. Skill Gap & Roadmap Generation

### POST `/roadmap/skill-gap`
Analyzes the user's latest saved profile skills against a set of target role skills, detects deficiencies, and leverages LLM integration to generate a customized learning roadmap.

**Request:**
- **Content-Type:** `application/json`
- **Body:**
```json
{
  "target_role": "Machine Learning Engineer"
}
```

**Response:** `200 OK`
```json
{
  "target_role": "Machine Learning Engineer",
  "current_skills": ["Python", "SQL"],
  "missing_skills": ["PyTorch", "Scikit-Learn", "Model Deployment"],
  "roadmap_stages": [
    {
      "stage": "Stage 1: Core ML Concepts",
      "duration": "2-3 weeks",
      "learning_goals": ["Master Scikit-Learn pipelines", "Understand bias-variance tradeoffs"],
      "action_items": [
        "Complete introductory ML certification",
        "Implement K-Means and Linear Regression models from scratch"
      ]
    },
    {
      "stage": "Stage 2: Deep Learning Foundations",
      "duration": "3-4 weeks",
      "learning_goals": ["Learn PyTorch tensor arithmetic", "Build fully connected and convolutional nets"],
      "action_items": [
        "Read PyTorch tutorial notebooks",
        "Train an image classifier on CIFAR-10 data"
      ]
    }
  ]
}
```

---

## 7. Internal Collector Endpoints

These endpoints are used to trigger job aggregator crawls. They are secured and require authentication.

### Custom Authorization Headers:
All requests to `/internal/*` routes must include the following header:
- **`X-Internal-API-Key`**: Needs to match the `INTERNAL_API_KEY` defined on the backend server environment. If the header is missing or incorrect, the server immediately rejects the request with a `403 Forbidden` response.

---

### POST `/internal/collect/greenhouse`
Triggers the Greenhouse job aggregator crawl to fetch new listings and persist them to the database.
Ad-hoc endpoint — does **not** update `CollectorSource` audit fields.

**Request Headers:**
- `X-Internal-API-Key`: `<secure-key>`

**Request Body:**
```json
{ "board_token": "cloudflare" }
```

**Response:** `200 OK`
```json
{
  "status": "success",
  "board_token": "cloudflare",
  "fetched_count": 45,
  "new_jobs_added": 12,
  "jobs_updated": 33,
  "source": "greenhouse"
}
```

---

### POST `/internal/collect/lever`
Triggers the Lever job aggregator crawl to fetch new listings and persist them to the database.
Ad-hoc endpoint — does **not** update `CollectorSource` audit fields.

**Request Headers:**
- `X-Internal-API-Key`: `<secure-key>`

**Request Body:**
```json
{ "company_id": "vercel" }
```

**Response:** `200 OK`
```json
{
  "status": "success",
  "company_id": "vercel",
  "fetched_count": 30,
  "new_jobs_added": 8,
  "jobs_updated": 22,
  "source": "lever"
}
```

---

### POST `/internal/collect/all`
Triggers a collection run for **all enabled** `CollectorSource` rows in the database.
This is the primary production collection endpoint and the only endpoint that updates
`CollectorSource` audit fields (`last_run_at`, `last_success_at`, `last_error`, etc.).

**Request Headers:**
- `X-Internal-API-Key`: `<secure-key>`

**Response:** `200 OK`
```json
{
  "status": "completed",
  "sources_attempted": 4,
  "sources_succeeded": 3,
  "sources_failed": 1,
  "total_fetched": 120,
  "total_added": 35,
  "total_updated": 85,
  "results": [
    {
      "company": "Cloudflare",
      "source_type": "greenhouse",
      "status": "success",
      "fetched": 80,
      "added": 20,
      "updated": 60
    },
    {
      "company": "Vercel",
      "source_type": "lever",
      "status": "failed",
      "error": "Connection timeout after 15s"
    }
  ]
}
```
