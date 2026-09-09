# Published pages

## Rolling dashboard — Training QA

```
url: https://claude.ai/code/artifact/1d86f6a7-34f2-4d45-8af5-39b80e1d9eda
```

The first run publishes `dashboard.html` and records the URL here. **Every later run must
republish to that URL** (pass it as `url:` to the Artifact tool). Publishing without it
creates a second page, and the team ends up reading a stale one — this is the single most
common way this kind of skill breaks.

Only the artifact's owner can republish. One identity should run the audit; everyone else
consumes the link.

## Per-session reports

New artifact per session, recorded in the ledger row and linked from the dashboard's
Sessions table. These are not republished — a session's report is a fixed record of what
was said and what the code did on that day's commit.

**Course-level reports.** Where a course has many runs (Foundations ran 15 times in August),
one report grades the *script* and states how many runs carried each claim, and every run's
ledger rows point at it. Fifteen near-identical reports would bury the finding that matters —
that the same feature is described three incompatible ways across runs.

| date | session | url |
|---|---|---|
| 2026-08-25 | CRM & scheduler | https://claude.ai/code/artifact/1c83803b-606c-4f7a-b413-f89ec077f9c2 |
| 2026-08-24…25 | Analytics · Deep Dive · Foundations | https://claude.ai/code/artifact/253dda9e-77ef-4e75-acfc-3fb12e49a195 |
| 2026-08-27 | Deep Dive | https://claude.ai/code/artifact/dd17ce3f-ccf4-4d50-8346-928aa5c41744 |
| 2026-09-03 | Deep Dive (both 27 Aug errors fixed; first Okto Assist audit) | https://claude.ai/code/artifact/8b4e9948-a765-4a68-9058-786be1e73928 |
| 2026-08 (15 runs) | **Foundations, August** — course-level | https://claude.ai/code/artifact/78db82b4-5edc-46e4-a8d4-9215c7998b61 |
