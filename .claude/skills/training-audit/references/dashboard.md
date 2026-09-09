# Published pages

## Rolling dashboard — Training QA

```
url: (not yet published)
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

| date | session | url |
|---|---|---|
| 2026-08-25 | CRM & scheduler | https://claude.ai/code/artifact/1c83803b-606c-4f7a-b413-f89ec077f9c2 |
| 2026-08-24…25 | Analytics · Deep Dive · Foundations | https://claude.ai/code/artifact/253dda9e-77ef-4e75-acfc-3fb12e49a195 |
