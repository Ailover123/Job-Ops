# UI Audit — Job-Ops (2026-05-08)

## Pages Reviewed
- `/` (Dashboard)
- `/onboarding/resume` (Resume Upload)
- `/onboarding/profile` (Profile Review)
- `/saved` (Saved Jobs)
- `/applications` (Applications)

---

## Visual Issues

| Issue | Location | Severity |
|-------|----------|----------|
| Body font is Arial/Helvetica — looks generic | `globals.css` | Medium |
| Score badge is hard black (#0f172a) — clashes with teal palette | `.score-badge` | Low |
| `.card` uses 12px radius, `.job-card` uses 8px — inconsistent | `globals.css` | Medium |
| Tag pills have 6px padding + 6px radius — blobby for dense layout | `.tag-row span` | Low |
| Empty states use dashed borders — looks like placeholder/draft | `.empty-state` | Medium |
| Profile snapshot always shows hardcoded demo data | `page.tsx` | Medium |

## Consistency Issues

| Issue | Location | Severity |
|-------|----------|----------|
| Topbar header markup duplicated across 4 page files | All pages | Low |
| No `.input-field` class defined — profile form inputs are unstyled browser defaults | `globals.css` | **High** |
| No `.button-secondary` class defined — "Add Education" button is unstyled | `globals.css` | **High** |
| No `@keyframes spin` / `.animate-spin` — Loader2 spinners don't spin | `globals.css` | **High** |
| Navigation uses only text links — no icons for quick recognition | `Navigation.tsx` | Low |

## Responsive Issues

| Issue | Location | Severity |
|-------|----------|----------|
| 40px gap between brand and nav is too wide on mobile | `page.tsx` topbar | Medium |
| `h1` at 26px is too large for inner pages (Saved, Applications) | `globals.css` | Low |
| Profile form grid `minmax(250px, 1fr)` can overflow narrow screens | `profile/page.tsx` | Medium |
| Nav links stack poorly under 400px | `.nav-links` | Medium |

## Empty State Issues

| Issue | Location | Severity |
|-------|----------|----------|
| No icon in empty states — text-only feels flat | `saved/page.tsx`, `applications/page.tsx` | Medium |
| Generic copy ("No saved jobs yet") could be warmer | Both pages | Low |
| Dashed border looks unfinished | `.empty-state` | Medium |

## Accessibility Issues

| Issue | Location | Severity |
|-------|----------|----------|
| No `:focus-visible` styles on icon buttons | `.icon-actions button` | **High** |
| Upload zone has no keyboard activation cue | `resume/page.tsx` | Medium |
| Form inputs on profile page have no visible border | Profile page | **High** |
| Icon buttons have no title/tooltip text | `JobCard.tsx` | Medium |

## Bugs

| Issue | Location | Severity |
|-------|----------|----------|
| Profile page "Go to Dashboard" links to `/dashboard` — **route does not exist** | `profile/page.tsx` line 283 | **Critical** |
| Applications footer uses `marginTop: -8px` causing overlapping borders | `applications/page.tsx` line 98 | Medium |

---

## Priority Fixes (in order)

1. Define `.input-field`, `.button-secondary`, `.animate-spin` (currently broken)
2. Fix `/dashboard` → `/` link
3. Add Inter font
4. Add `:focus-visible` on all interactive elements
5. Standardize card radius (8px) and small element radius (4-6px)
6. Improve empty states with icons and solid borders
7. Fix applications footer overlap
8. Responsive nav and typography fixes
