# AI Fresher Job Matcher - API Contract

## 1. API Style

Use REST for MVP. Keep endpoints predictable and easy to test.

Base path:

```text
/api/v1
```

## 2. Auth

### GET /me

Returns current authenticated user.

Response:

```json
{
  "id": "user_id",
  "email": "user@example.com",
  "name": "User Name"
}
```

## 3. Resume

### POST /resumes

Uploads a resume.

Request:

- multipart form
- field: `file`

Response:

```json
{
  "resume_id": "resume_id",
  "parse_status": "pending"
}
```

### GET /resumes/{resume_id}

Returns resume metadata and parse status.

### POST /resumes/{resume_id}/parse

Runs resume parsing.

Response:

```json
{
  "profile_id": "profile_id",
  "parse_status": "completed"
}
```

## 4. Profile

### GET /profile

Returns current user profile.

### PUT /profile

Updates editable profile fields.

### POST /profile/skills

Adds a skill.

### DELETE /profile/skills/{skill_id}

Removes a skill.

## 5. Preferences

### GET /preferences

Returns user job preferences.

### PUT /preferences

Updates job preferences.

Example request:

```json
{
  "preferred_roles": ["Python Developer", "AI Intern"],
  "preferred_locations": ["Bangalore", "Remote"],
  "remote_preference": "remote_or_hybrid",
  "job_types": ["internship", "full_time"],
  "willing_to_relocate": true,
  "preferred_tech_stack": ["Python", "MySQL"]
}
```

## 6. Jobs

### GET /jobs

Returns searchable jobs.

Query params:

- `q`
- `location`
- `remote`
- `job_type`
- `source`
- `page`
- `limit`

### GET /jobs/{job_id}

Returns job detail.

## 7. Recommendations

### GET /recommendations

Returns ranked jobs for the current user.

Response:

```json
{
  "items": [
    {
      "job_id": "job_id",
      "title": "AI Intern",
      "company_name": "Example AI",
      "location": "Remote",
      "final_score": 87,
      "score_label": "Excellent match",
      "explanation": "Matched because your Python and ML project experience aligns with this internship."
    }
  ]
}
```

## 8. Saved Jobs

### POST /saved-jobs

Saves a job.

Request:

```json
{
  "job_id": "job_id"
}
```

### GET /saved-jobs

Returns saved jobs.

### DELETE /saved-jobs/{job_id}

Removes saved job.

## 9. Applications

### POST /applications

Marks a job as applied.

### GET /applications

Returns application history.

### PUT /applications/{application_id}

Updates application status.

## 10. Feedback

### POST /job-feedback

Submits recommendation feedback.

Request:

```json
{
  "job_id": "job_id",
  "feedback_type": "irrelevant",
  "comment": "Requires 5 years experience"
}
```

## 11. Admin or Internal Collector Endpoints

These should be protected.

### POST /internal/job-sources/{source_id}/run

Runs one source collector.

### POST /internal/recommendations/recompute

Recomputes match scores.

