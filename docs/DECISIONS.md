# Decisions

## 2026-05-08 - Use Synthetic Seed Jobs First

Decision:

Use synthetic seed jobs for initial development instead of live scraped jobs.

Reason:

The dashboard, matching engine, filters, deduplication, and saved/applied flows can be built before dealing with scraping instability.

Alternatives considered:

Start with live scraping immediately.

Impact:

The MVP can progress faster and the system can be tested with controlled edge cases.

