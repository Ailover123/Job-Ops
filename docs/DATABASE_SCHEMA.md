# Job-Ops - Database Schema

This document details the database schema and model structures used by the Job-Ops system. The models are declared using SQLModel and managed with Alembic migrations.

---

## 1. Entity-Relationship Summary

The schema consists of six core tables:
- **`Profile`**: Candidates' parsed and structured information.
- **`Preferences`**: Search parameters (locations, roles, job types, remote).
- **`Job`**: Aggregated job listings from Greenhouse, Lever, and static seed data.
- **`CollectorSource`**: Target company and board configurations for the automatic scrapers.
- **`SavedJob`**: User-saved bookmarks pointing to jobs.
- **`Application`**: Application status and custom notes tracking.

---

## 2. Table Schemas

### `profile`
Stores normalized candidate details extracted from resumes and refined during onboarding.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto-increment | Internal unique profile identifier. |
| `full_name` | `VARCHAR` | Non-Null | Full name of the candidate. |
| `email` | `VARCHAR` | Non-Null | Email address. |
| `phone` | `VARCHAR` | Non-Null | Phone number. |
| `location` | `JSON` | Default: `{}` | Dictionary containing city, state, and country. |
| `education` | `JSON` | Default: `[]` | List of education entities (institution, degree, year). |
| `skills` | `JSON` | Default: `[]` | List of parsed skills and proficiencies. |
| `projects` | `JSON` | Default: `[]` | List of personal/academic projects and stack details. |
| `certifications`| `JSON` | Default: `[]` | List of certification strings. |
| `suggested_roles`| `JSON` | Default: `[]` | AI-inferred suitable job roles. |
| `preferred_domains`| `JSON` | Default: `[]` | Industry/domain preferences. |
| `created_at` | `DATETIME` | Default: UTC Now | Row creation timestamp. |
| `updated_at` | `DATETIME` | Default: UTC Now | Row update timestamp. |

---

### `preferences`
User preferences for job recommendations and score tuning.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto-increment | Internal unique preferences identifier. |
| `preferred_roles` | `JSON` | Default: `[]` | Desired position titles (e.g. `["Frontend Engineer"]`). |
| `preferred_locations`| `JSON` | Default: `[]` | Allowed cities or regions. |
| `remote_preference` | `VARCHAR` | Default: `"remote_or_hybrid"`| `remote`, `hybrid`, `onsite`, or `remote_or_hybrid`. |
| `job_types` | `JSON` | Default: `[]` | Full-time, Part-time, Internship, Contract, etc. |
| `preferred_tech_stack`| `JSON` | Default: `[]` | Primary languages, frameworks, or database keywords. |
| `willing_to_relocate`| `BOOLEAN` | Default: `FALSE` | Willingness to relocate for on-site/hybrid positions. |
| `created_at` | `DATETIME` | Default: UTC Now | Row creation timestamp. |
| `updated_at` | `DATETIME` | Default: UTC Now | Row update timestamp. |

---

### `job`
Unified and deduplicated job listings aggregated from automated crawls and seed files.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto-increment | Internal unique job identifier. |
| `external_id` | `VARCHAR` | Unique, Indexed, Non-Null | Portal source identifier (e.g. `greenhouse-101`). |
| `title` | `VARCHAR` | Non-Null | Role title. |
| `company_name` | `VARCHAR` | Non-Null | Employing company. |
| `description` | `VARCHAR` | Non-Null | Complete text details of the job listing. |
| `location` | `VARCHAR` | Non-Null | Raw location string (e.g. `San Francisco, CA`). |
| `city` | `VARCHAR` | Nullable | Extracted/normalized city name. |
| `state` | `VARCHAR` | Nullable | Extracted/normalized state abbreviation. |
| `country` | `VARCHAR` | Nullable | Extracted/normalized country. |
| `is_remote` | `BOOLEAN` | Default: `FALSE` | Flat flag identifying remote-eligible roles. |
| `job_type` | `VARCHAR` | Non-Null | Standard classification (e.g. `Full-time`, `Internship`). |
| `experience_min` | `INTEGER` | Nullable | Minimum years of experience requested by description. |
| `experience_max` | `INTEGER` | Nullable | Maximum years of experience requested. |
| `skills` | `JSON` | Default: `[]` | Extracted list of technology/skill tags. |
| `apply_url` | `VARCHAR` | Non-Null | Direct link to submit applications. |
| `source_name` | `VARCHAR` | Non-Null | Name of crawler source (e.g. `greenhouse`, `lever`). |
| `posted_at` | `VARCHAR` | Nullable | Source date string. |
| `is_active` | `BOOLEAN` | Default: `TRUE` | Identifies active vs archived listings. |
| `created_at` | `DATETIME` | Default: UTC Now | System discovery timestamp. |

---

### `collectorsource`
Configures the targets parsed by automatic Greenhouse and Lever crawler scripts.
Audit fields are updated exclusively by `POST /internal/collect/all`.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto-increment | Internal source configuration identifier. |
| `company_name` | `VARCHAR` | Non-Null | Target organization title. |
| `board_token` | `VARCHAR` | Nullable | Greenhouse token matching board identifier. |
| `company_id` | `VARCHAR` | Nullable | Lever company unique identifier. |
| `source_type` | `VARCHAR` | Non-Null | Aggregation protocol type: `greenhouse` or `lever`. |
| `enabled` | `BOOLEAN` | Default: `TRUE` | Toggle enabling or skipping this source in standard runs. |
| `created_at` | `DATETIME` | Default: UTC Now | Creation timestamp. |
| `updated_at` | `DATETIME` | Default: UTC Now | Last configuration change timestamp. |
| `last_run_at` | `DATETIME` | Nullable | Timestamp of the most recent `/collect/all` attempt (regardless of outcome). |
| `last_success_at` | `DATETIME` | Nullable | Timestamp of the most recent **successful** collection run. |
| `last_error` | `VARCHAR` | Nullable | Error message from the most recent **failed** run. `NULL` when the last run succeeded. |
| `last_fetched_count` | `INTEGER` | Nullable | Number of jobs returned by the ATS on the last successful run. |
| `last_saved_count` | `INTEGER` | Nullable | Number of **new** jobs inserted into the `job` table on the last successful run. |

---


### `savedjob`
Candidate's bookmarked job listings.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto-increment | Internal bookmark identifier. |
| `job_external_id` | `VARCHAR` | Unique, Indexed, Non-Null | External identifier of the bookmarked job. |
| `job_title` | `VARCHAR` | Non-Null | Cached job title. |
| `company_name` | `VARCHAR` | Non-Null | Cached company name. |
| `location` | `VARCHAR` | Default: `"Unknown"` | Cached location text. |
| `source_name` | `VARCHAR` | Non-Null | Source crawl platform. |
| `apply_url` | `VARCHAR` | Non-Null | Direct application link. |
| `skills` | `JSON` | Default: `[]` | Cached job skill tags. |
| `saved_at` | `DATETIME` | Default: UTC Now | Saved timestamp. |

---

### `application`
Submissions tracking, custom logs, notes, and stages.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto-increment | Internal unique application tracker identifier. |
| `job_external_id` | `VARCHAR` | Unique, Indexed, Non-Null | External identifier of the applied job. |
| `job_title` | `VARCHAR` | Non-Null | Cached job title. |
| `company_name` | `VARCHAR` | Non-Null | Cached company name. |
| `location` | `VARCHAR` | Default: `"Unknown"` | Cached location. |
| `source_name` | `VARCHAR` | Non-Null | Platform source. |
| `apply_url` | `VARCHAR` | Non-Null | Direct application submission link. |
| `skills` | `JSON` | Default: `[]` | Cached job skill tags. |
| `status` | `VARCHAR` | Default: `"applied"` | Tracked stage: `applied`, `interviewing`, `offer`, `rejected`, `withdrawn`. |
| `notes` | `VARCHAR` | Default: `""` | User's custom comments and progress notes. |
| `applied_at` | `DATETIME` | Default: UTC Now | Initial record/submission date. |

---

## 3. Database Indexes

Alembic configures automatic indexing on critical search parameters to sustain performance as listing sizes scale:
1. **`ix_job_external_id`**: Speed up individual job details and deduplication looks.
2. **`ix_savedjob_job_external_id`**: Bookmarks toggle checking.
3. **`ix_application_job_external_id`**: Syncing application badges in job grids.

---

## 4. Alembic Migration Structure

All schema revisions are auto-generated under `backend/alembic/versions`. The environment relies on import bindings to dynamically inject SQLModel tables and auto-injects `import sqlmodel` on file generations to support specialized structures seamlessly.
