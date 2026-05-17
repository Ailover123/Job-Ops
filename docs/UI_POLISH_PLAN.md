# UI Polish Plan — Session 8

## Audit Findings

### Missing CSS (broken right now)
- `.input-field` used in profile page but **never defined** → form inputs are unstyled browser defaults
- `.button-secondary` used in profile page but **never defined** → "Add Education" button is unstyled
- `.animate-spin` keyframes missing → Loader2 spinners don't actually spin
- No focus-visible styles on any interactive element

### Bugs
- Profile page "Go to Dashboard" links to `/dashboard` which **doesn't exist** → should be `/`
- Applications page footer has `marginTop: -8px` hack causing overlapping borders

### Visual Issues
- **Font**: body uses `Arial, Helvetica, sans-serif` — looks generic
- **Border-radius inconsistency**: `.card` = 12px, `.job-card` = 8px, `.match-label` = 6px
- **Score badge**: hard black (#0f172a) clashes with teal palette
- **Empty states**: dashed borders look draft-like, no icons
- **Tag pills**: 6px padding + 6px radius feels blobby for a dense dashboard
- **Profile snapshot**: always shows hardcoded demo data even when personalized

### Responsive Issues
- Navigation 40px gap between brand and nav is too wide on mobile
- `h1` at 26px is too large for inner pages (Saved, Applications)
- Profile form grid can overflow on narrow screens
- Nav links stack poorly under 400px

### Accessibility
- Icon buttons (save, apply) have no focus ring
- Upload zone has no keyboard activation beyond click
- Form inputs on profile page have no visible border

---

## Proposed Changes

### 1. layout.tsx
- Import Inter from `next/font/google`
- Apply to `<body>`

### 2. globals.css (bulk of the work)
- Add `.input-field` with border, padding, focus ring
- Add `.button-secondary` with outline style
- Add `@keyframes spin` and `.animate-spin`
- Standardize border-radius to 6px on cards
- Add `:focus-visible` outlines on buttons
- Score badge: teal instead of black
- Empty state: solid border, icon slot, warmer styling
- Tag pills: tighter, 4px radius
- Icon button hover transitions
- Nav mobile responsive fix
- Inner page h1 size reduction
- Application footer proper class

### 3. Navigation.tsx
- Add lucide icons next to link text (LayoutDashboard, Bookmark, ClipboardList)

### 4. JobCard.tsx
- Card hover state (border color shift)
- Title attributes on icon buttons
- Clean up inline styles → CSS classes

### 5. page.tsx (Dashboard)
- Replace inline styles with classes
- Tighten status message area

### 6. resume/page.tsx
- Add drag-and-drop visual states
- Clean up inline styles

### 7. profile/page.tsx
- Fix broken `/dashboard` link → `/`
- Style inputs with `.input-field`
- Visual distinction on readonly location field
- Reduce inline styles

### 8. saved/page.tsx
- Better empty state with Bookmark icon
- Remove redundant "Back to Dashboard" (nav handles it)

### 9. applications/page.tsx
- Better empty state with icon
- Fix applied-on footer (remove -8px hack, use proper class)

---

## NOT doing
- No backend changes
- No new dependencies
- No auth
- No scraping
- No new pages or routes
- No Tailwind

## Font
Using **Inter** via `next/font/google` (built into Next.js, zero dependency).

## Verification
1. `cd frontend && npm.cmd run build`
2. Playwright screenshots at 1280x800 for all pages
3. Mobile screenshot at 390x844

## Git
- Commit: `style: polish core app UI`
- Exclude: `docs/LOCAL_HANDOFF.md`, `backend/.env`, node_modules, .next, .venv, __pycache__
