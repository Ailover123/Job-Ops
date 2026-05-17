# Job-Ops - Frontend Page Map

This document maps out the Next.js routes, structures, state parameters, and component dependencies implemented in the Job-Ops client interface.

---

## 1. Directory & Route Hierarchy

The client application is built under the Next.js App Router paradigm inside `frontend/app/`.

```text
frontend/app/
├── page.tsx                    # Route: / (Personalized Dashboard)
├── layout.tsx                  # Global HTML Shell & Fonts
├── globals.css                 # Unified Style Tokens & Animations
├── applications/
│   └── page.tsx                # Route: /applications (Application Tracker)
├── jobs/
│   └── [external_id]/
│       └── page.tsx            # Route: /jobs/[external_id] (Opportunity Details)
├── onboarding/
│   ├── resume/
│   │   └── page.tsx            # Route: /onboarding/resume (Resume Extractor)
│   └── profile/
│       └── page.tsx            # Route: /onboarding/profile (Profile Editor)
├── preferences/
│   └── page.tsx                # Route: /preferences (Match Tuner)
├── roadmap/
│   └── page.tsx                # Route: /roadmap (Skill Gap & AI Learning Roadmap)
├── saved/
│   └── page.tsx                # Route: /saved (Job Bookmarks)
├── internal/
│   └── sources/
│       └── page.tsx            # Route: /internal/sources (Admin Job Source Management)
├── components/                 # Global UI Shared Components
│   ├── Navigation.tsx          # Shared Tab Navigation Bar
│   └── JobCard.tsx             # Interactive Job Listing Card
└── lib/
    └── api.ts                  # Central API Base URL & Network Settings
```

---

## 2. Page Specifications & Features

### 1. Root / Personalized Dashboard (`/`)
Serves as the main workspace. Displays matching job listings and summarizes current profile status.

- **Main Elements:**
  - Recommended Jobs List (calculates compatibility rankings dynamically).
  - Quick Profile Snapshot sidebar (indicates missing resume or preference configuration).
  - Empty state guiding users to upload a resume when database profile is blank.
- **State Parameters:**
  - `loading`: Shows beautiful Tailwind/CSS skeleton rows.
  - `jobs`: List of processed recommended opportunities.
  - `hasProfile`: Toggle controlling profile onboarding call-to-actions.

---

### 2. Resume Extractor (`/onboarding/resume`)
First stage of the candidate onboarding lifecycle. Allows PDF uploads for deep processing.

- **Main Elements:**
  - Drag-and-drop region accepting PDF files.
  - Live progress feedback tracker indicating LLM analysis status.
  - Success screen showing snippet preview and routing buttons to next stage.
- **Network Actions:**
  - `POST /onboarding/resume` for text extraction.

---

### 3. Profile Editor (`/onboarding/profile`)
Allows review and modification of candidate skills, work history, and school details extracted from the upload.

- **Main Elements:**
  - Structured fields for Full Name, Email, and Phone.
  - Interactive lists for Education history and Personal projects.
  - Skills and Certifications list editor.
  - Inline forms to modify or save candidate records to database.
- **Network Actions:**
  - `POST /profile` to commit verified schema inputs.

---

### 4. Match Tuner (`/preferences`)
Allows candidates to refine their job preferences to improve recommendations.

- **Main Elements:**
  - List of preferred job titles (chips).
  - Location exclusions and preferences lists.
  - Remote/Hybrid/Onsite drop-down toggle.
  - Minimum salary slider and desired tech stack words.
- **Network Actions:**
  - `POST /preferences` and `GET /preferences/latest`.

---

### 5. Skill Gap & AI Learning Roadmap (`/roadmap`)
Generates clear technical gap charts comparing candidate skills against desired job profiles, and builds a customized weekly learning timeline.

- **Main Elements:**
  - Desired Target Role inputs (e.g. `Machine Learning Engineer`).
  - Comparative skills check (highlights matching vs missing technology tags).
  - Weekly milestone timeline diagram with specific courses and action items.
- **Network Actions:**
  - `POST /roadmap/skill-gap` with custom OpenAI/Gemini JSON mapping output.

---

### 6. Opportunity Details (`/jobs/[external_id]`)
Provides in-depth description, job terms, and a deep compatibility breakdown.

- **Main Elements:**
  - Comprehensive job description.
  - Dynamic score breakdown metrics banner (Skill Match, Location, Experience, Fresher suitability).
  - Action buttons: "Apply Now" (opens job portal), "Save for Later" (bookmarks), "Mark as Applied" (tracks application).
- **Network Actions:**
  - `GET /jobs/[external_id]` to retrieve details.

---

### 7. Job Bookmarks (`/saved`)
Simple tracking view showing saved/saved jobs list.

- **Main Elements:**
  - Grid of saved opportunities.
  - Quick buttons to unsave or mark as applied.

---

### 8. Application Tracker (`/applications`)
Central tracking workspace monitoring active job pipelines.

- **Main Elements:**
  - Application cards displaying company, position, and status.
  - Progress stage dropdown (Applied, Interviewing, Offer Received, Rejected, Withdrawn).
  - Custom notepad tracking interviews, feedback, and calendar milestones per job.
- **Network Actions:**
  - `PUT /applications/{job_external_id}` for editing status and notes.

---

### 9. Admin Job Source Management (`/internal/sources`)
Internal tooling workspace to manage collector sources for aggregator scripts.

- **Main Elements:**
  - Secure authentication input requiring `X-Internal-API-Key`.
  - Configured list of sources, displaying enablement and last execution states.
  - Input form to define new Greenhouse or Lever collector sources.
  - "Run Collect All" button to manually trigger a sync across all enabled sources.
- **State Parameters:**
  - `apiKey`: Stored and restored from browser `sessionStorage`.
- **Network Actions:**
  - `GET`, `POST`, `PATCH`, `DELETE` at `/internal/sources`
  - `POST /internal/collect/all`

---

## 3. Key UI Shared Components

- **`Navigation` ([Navigation.tsx](file:///d:/academic/Job-Ops/frontend/app/components/Navigation.tsx)):**
  Unified responsive header tab containing links to Dashboard (`/`), Bookmarks (`/saved`), Applications (`/applications`), Profile (`/onboarding/profile`), and Roadmap (`/roadmap`). Indicates current active route gracefully using CSS transitions.
- **`JobCard` ([JobCard.tsx](file:///d:/academic/Job-Ops/frontend/app/components/JobCard.tsx)):**
  Standard card structure displaying job headers, matching label tags, and score meters. Equipped with inline hooks to bookmark or log job applications immediately.
