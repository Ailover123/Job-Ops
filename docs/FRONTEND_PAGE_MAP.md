# AI Fresher Job Matcher - Frontend Page Map

## 1. Page List

## /login

Purpose:

- User login and signup.

Main elements:

- Email/social auth
- Error state
- Loading state

## /onboarding/resume

Purpose:

- Upload resume.

Main elements:

- File upload
- Upload progress
- Parse status
- Retry option

## /onboarding/profile

Purpose:

- Review and edit extracted profile.

Main elements:

- Personal details
- Education
- Skills editor
- Projects editor
- Certifications
- Suggested roles

## /onboarding/preferences

Purpose:

- Capture job preferences.

Main elements:

- Role type selector
- Location selector
- Remote/on-site selector
- Job type selector
- Tech stack selector
- Relocation preference

## /dashboard

Purpose:

- Main recommendation screen.

Main elements:

- Recommended jobs list
- Match score
- Filters
- Sort
- Quick actions

Job card fields:

- Job title
- Company
- Location
- Source
- Match score
- Fresher suitability label
- Save button
- Mark applied button

## /jobs/{job_id}

Purpose:

- Job detail view.

Main elements:

- Full job description
- Match explanation
- Required skills
- Missing skills
- Apply link
- Save/apply actions
- Feedback actions

## /saved

Purpose:

- Saved jobs list.

Main elements:

- Saved jobs
- Remove from saved
- Mark applied
- Apply link

## /applications

Purpose:

- Track applied jobs.

Main elements:

- Application status
- Notes
- Status update
- Applied date

## /settings

Purpose:

- Manage profile and preferences.

Main elements:

- Profile edit
- Preferences edit
- Notification settings
- Delete account option

## 2. MVP Navigation

Primary nav:

- Dashboard
- Saved
- Applied
- Profile

Secondary:

- Settings

## 3. Key UI States

Every page should support:

- Loading
- Empty
- Error
- Success

Important empty states:

- No recommendations yet
- No saved jobs
- No applied jobs
- Resume parsing failed

## 4. Dashboard Filters

Filters:

- Role
- Location
- Remote/on-site
- Job type
- Source
- Match score
- Posted/discovered date

Sort options:

- Best match
- Newest
- Closest location
- Fresher-friendly first

