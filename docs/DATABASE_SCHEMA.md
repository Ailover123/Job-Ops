# AI Fresher Job Matcher - Database Schema

## 1. Schema Style

Use PostgreSQL for MVP. Add `pgvector` later if embeddings are stored directly in the database.

This document describes logical tables. Exact SQL can be created after choosing the backend framework and ORM.

## 2. Tables

## users

Stores account-level information.

Fields:

- id
- email
- name
- auth_provider
- created_at
- updated_at

## resumes

Stores uploaded resume metadata and extracted text.

Fields:

- id
- user_id
- file_name
- file_url
- extracted_text
- parse_status
- created_at
- updated_at

## profiles

Stores normalized candidate profile extracted from resume and edited by user.

Fields:

- id
- user_id
- resume_id
- full_name
- phone
- location_city
- location_state
- location_country
- education_summary
- experience_level
- profile_summary
- preferred_domains
- created_at
- updated_at

## profile_skills

Stores user skills as normalized searchable rows.

Fields:

- id
- profile_id
- skill_name
- skill_type
- proficiency
- source
- created_at

Possible `skill_type` values:

- programming
- database
- framework
- cloud
- ai_ml
- tool
- soft_skill

Possible `source` values:

- resume
- user_added
- inferred

## profile_projects

Stores projects extracted from resume.

Fields:

- id
- profile_id
- title
- description
- tech_stack
- project_url
- created_at

## preferences

Stores job preference settings.

Fields:

- id
- user_id
- preferred_roles
- preferred_locations
- remote_preference
- job_types
- willing_to_relocate
- minimum_salary
- preferred_tech_stack
- created_at
- updated_at

## job_sources

Stores source portal configuration.

Fields:

- id
- name
- source_type
- base_url
- is_active
- fetch_method
- created_at
- updated_at

Possible `source_type` values:

- ats
- job_board
- company_page
- api

Possible `fetch_method` values:

- api
- html
- playwright
- manual_seed

## jobs

Stores normalized job listings.

Fields:

- id
- source_id
- external_id
- title
- company_name
- description
- location
- city
- state
- country
- is_remote
- job_type
- experience_min
- experience_max
- apply_url
- source_url
- posted_at
- discovered_at
- expires_at
- is_active
- content_hash
- created_at
- updated_at

## job_skills

Stores skills extracted from job descriptions.

Fields:

- id
- job_id
- skill_name
- confidence
- created_at

## job_matches

Stores recommendation score per user and job.

Fields:

- id
- user_id
- job_id
- skill_score
- semantic_score
- location_score
- experience_score
- freshness_score
- final_score
- explanation
- created_at
- updated_at

## saved_jobs

Stores saved jobs.

Fields:

- id
- user_id
- job_id
- created_at

## applications

Stores jobs marked as applied by the user.

Fields:

- id
- user_id
- job_id
- status
- applied_at
- notes
- created_at
- updated_at

Possible `status` values:

- planned
- applied
- interview
- rejected
- offer
- withdrawn

## job_feedback

Stores feedback used for ranking improvement.

Fields:

- id
- user_id
- job_id
- feedback_type
- comment
- created_at

Possible `feedback_type` values:

- irrelevant
- duplicate
- fake
- not_fresher_friendly
- wrong_location
- good_match

## notifications

Stores notification records.

Fields:

- id
- user_id
- job_id
- notification_type
- channel
- status
- sent_at
- created_at

## 3. Important Indexes

- `jobs(company_name, title, location)`
- `jobs(is_active, discovered_at)`
- `jobs(source_id, external_id)`
- `job_matches(user_id, final_score)`
- `saved_jobs(user_id, job_id)`
- `applications(user_id, job_id)`
- `job_feedback(user_id, job_id)`

## 4. Deduplication Fields

Deduplication should use:

- company_name
- normalized title
- normalized location
- apply_url
- content_hash
- semantic similarity of description

