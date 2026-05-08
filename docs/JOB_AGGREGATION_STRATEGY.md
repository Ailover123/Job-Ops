# AI Fresher Job Matcher - Job Aggregation Strategy

## 1. Goal

Collect fresher-friendly jobs from mainstream and hidden sources, normalize them into one schema, remove duplicates, and keep listings fresh.

## 2. Source Priority

Start with sources that are practical and less dependent on aggressive scraping.

Priority order:

1. ATS portals with public job pages or APIs.
2. Company career pages.
3. Remote/startup job boards.
4. Mainstream portals after the MVP works.

## 3. Phase 1 Sources

- Greenhouse
- Ashby
- Lever
- Workable
- YC Work at a Startup
- RemoteOK
- Remotive
- Wellfound, if feasible
- Manually seeded company career pages

## 4. Phase 2 Sources

- Internshala
- Naukri
- LinkedIn
- Indeed
- Unstop
- Freshersworld
- Cutshort
- Hirist

These are useful for Indian freshers but may involve anti-bot protection, unstable HTML, or stricter terms.

## 5. Normalized Job Fields

Every source should become this shape:

```json
{
  "title": "",
  "company_name": "",
  "description": "",
  "location": "",
  "is_remote": false,
  "job_type": "",
  "experience_min": null,
  "experience_max": null,
  "apply_url": "",
  "source_url": "",
  "posted_at": null,
  "discovered_at": "",
  "source_name": ""
}
```

## 6. Fetch Methods

### API

Use where available. Best option.

Examples:

- Some Greenhouse boards expose structured job data.
- Some job boards provide public feeds or APIs.

### HTML Fetch

Use for simple public pages that do not require JavaScript rendering.

### Playwright

Use only when needed for JavaScript-rendered pages.

### Manual Seed

For MVP, manually seed important company career pages and run simple checks against them.

## 7. Freshness Policy

- Run collectors daily for MVP.
- Mark jobs stale if not seen for 14-30 days.
- Prefer discovered date when posted date is unavailable.
- Do not notify users about stale jobs.

## 8. Deduplication Rules

Strong duplicate:

- Same apply URL.
- Same source external ID.
- Same company, normalized title, and normalized location.

Possible duplicate:

- Similar title.
- Same company.
- Similar description.
- Same city or remote status.

Use content hash plus fuzzy matching.

## 9. Data Quality Checks

Reject or downrank jobs if:

- Title is empty.
- Company is empty.
- Apply URL is missing.
- Description is too short.
- Job looks senior-only.
- Source is known for low-quality listings.

## 10. Legal and Reliability Notes

- Prefer public APIs and public career pages.
- Respect robots and terms where applicable.
- Avoid login-required scraping in MVP.
- Avoid auto-apply flows.
- Cache results to reduce repeated requests.

