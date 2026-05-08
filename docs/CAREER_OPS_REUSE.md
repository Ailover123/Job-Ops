# Reusability Analysis - santifer/career-ops

Reference repository:

- https://github.com/santifer/career-ops

## 1. Short Answer

Do not reuse `career-ops` as the base application.

Reuse its ideas around portal configuration, ATS discovery, scoring discipline, deduplication mindset, and tracking. Avoid its Claude Code dependency, resume rewriting flow, senior-role assumptions, and agentic application workflow.

## 2. What Can Be Reused Conceptually

### Portal Configuration Pattern

`career-ops` uses a portal configuration file for:

- Tracked companies
- Career URLs
- Search queries
- Enabled/disabled sources
- Source-specific scan methods
- Title filters

This is highly reusable.

Recommended adaptation:

- Create your own `job_sources` table or `sources.yml`.
- Store source name, base URL, fetch method, and enabled flag.
- Keep fresher-specific role filters separately.

### ATS Portal Focus

The repository focuses on lesser-known but useful ATS systems and startup job portals:

- Ashby
- Greenhouse
- Lever
- Workable
- Wellfound
- RemoteOK / remote boards
- YC Work at a Startup

This is one of the best ideas to reuse because freshers often ignore these portals.

### Source Priority Strategy

The repo favors:

1. Branded company career pages.
2. ATS-hosted pages or APIs.
3. Search fallback.

This pattern is reusable because it reduces stale or broken links.

### Deduplication Mindset

The repo treats job tracking as a clean pipeline, not a random scrape dump.

Reusable ideas:

- Normalize jobs.
- Remove duplicates.
- Track discovered jobs.
- Track status.
- Avoid repeated processing.

### Scoring Discipline

`career-ops` evaluates jobs through structured dimensions instead of blindly applying.

Reusable idea:

- Use a transparent match score.
- Break score into skills, location, experience, freshness, and semantic similarity.

## 3. What Might Be Adapted With Changes

### `portals.example.yml`

Can be used as inspiration, not copied directly.

Why not copy directly:

- It is senior and AI/automation role heavy.
- It excludes junior and intern roles in the negative filters.
- Many companies listed target experienced candidates.
- It has Europe/Spain/DACH-specific assumptions.

How to adapt:

- Replace senior keywords with fresher keywords.
- Add India-focused and global fresher portals.
- Keep ATS portal structure.
- Keep enabled flags.
- Keep scan method fields.

Example fresher-positive title filters:

```yaml
positive:
  - fresher
  - graduate
  - new grad
  - junior
  - trainee
  - intern
  - internship
  - associate software engineer
  - entry level
  - python developer
  - data analyst
  - ai intern
  - machine learning intern
```

Example fresher-negative title filters:

```yaml
negative:
  - senior
  - staff
  - principal
  - lead
  - manager
  - architect
  - 5+ years
  - 7+ years
```

### Dashboard Tracking Idea

The tracking concept is useful, but the Go terminal UI is not ideal for your product.

Adapt it into a web dashboard:

- Recommended
- Saved
- Applied
- Rejected
- Duplicate reports

### Report Generation

`career-ops` generates evaluation reports. For your app, this can become a compact job explanation:

- Why this matched
- Missing skills
- Location fit
- Experience fit
- Apply link

Do not generate long reports in MVP.

## 4. What Should Not Be Reused

### Claude Code Dependency

Your app should work as a normal web app. Users should not need Claude Code or any coding CLI.

### Resume Rewriting Pipeline

This conflicts with your product direction.

Avoid:

- Generating tailored CVs per job by default.
- Modifying resume content automatically.
- Making resume edits the core feature.

Optional later:

- Provide suggestions only.
- Let the user approve every change.

### Agentic Auto-Apply Flow

Avoid auto-apply in MVP.

Risks:

- Incorrect form filling
- User trust issues
- Portal restrictions
- Spam behavior
- Hard debugging

### Senior-Focused Filters

The original repo is optimized for a senior AI/automation job search. Your filters should be fresher-first.

## 5. Files or System Points Worth Studying

Study these areas from the repo:

- `templates/portals.example.yml`
- Scanner strategy described in the README
- Pipeline tracking idea
- Dedup/status normalization ideas
- Dashboard status categories

Do not treat these as drop-in files. Treat them as design references.

## 6. Freshers-First Source List

### Phase 1 Sources

Use these first because they are practical for MVP:

- Greenhouse
- Ashby
- Lever
- Workable
- YC Work at a Startup
- RemoteOK
- Remotive
- Wellfound, if feasible
- Manual company career page seeds

### Phase 2 Sources

Add after the core engine works:

- Internshala
- Naukri
- LinkedIn
- Indeed
- Unstop
- Freshersworld
- Cutshort
- Hirist

These are valuable but may involve more scraping, anti-bot, or data quality problems.

## 7. Recommended Project Interpretation

Your project should be:

```text
Resume profile builder + hidden job source aggregator + fresher matching engine
```

It should not be:

```text
Claude-driven resume rewriting and application automation system
```

## 8. Practical Reuse Decision

Reusable as-is:

- Nothing should be copied as-is into the product without review.

Reusable after adaptation:

- Portal configuration structure
- ATS source list
- Scan method idea
- Tracking states
- Deduplication strategy
- Structured scoring approach

Not reusable:

- Claude Code command system
- Resume PDF generation
- Senior-focused filters
- Auto-apply mode
- Personal career archetypes

