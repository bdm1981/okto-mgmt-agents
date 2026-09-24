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
| 2026-09-02 | Foundations (On Deck fixed; last-login hedge) | https://claude.ai/code/artifact/e1d1b737-88c8-4490-ad49-7c2abe84566e |
| 2026-09-03 | Deep Dive (disable-user private-task gap) | https://claude.ai/code/artifact/c0f57918-6b71-4d38-b833-84173f7ce919 |
| 2026-09-08 | Shop Analytics (goal formula; Rocket Gauge gap) | https://claude.ai/code/artifact/3eb616fa-5637-4e7c-934a-d69cec0a11f3 |
| 2026-09-08 | Admin Part 1 (inverted Require Delete Reason) | https://claude.ai/code/artifact/5e30a542-2607-4c09-b981-b32450b24142 |
| 2026-09-09 | Admin Part 1 — Aaron (**translate defect closed**) | https://claude.ai/code/artifact/da58725d-412e-458c-aa56-3f25730f33af |
| 2026-09-09 | CRM Overview (two Aug errors taught right) | https://claude.ai/code/artifact/8fa59e6a-574a-4109-82fa-759d14c04508 |
| 2026-09-09 | Admin Part 2 (live tenant change flagged) | https://claude.ai/code/artifact/85d76d26-0f6e-4072-afba-543cc1075474 |
| 2026-09-14 | Admin Part 1 — Aaron (8 attendees; all checkable claims correct) | https://claude.ai/artifact/MXM5PWMeEbhpmGi8DMZWZh |
| 2026-09-14 | Admin Part 2 — TeDarrell (**block-customer permission inverted**) | https://claude.ai/artifact/7jsXWm3vnTT5ZCwjvJw9CN |
| 2026-09-15 | Admin Part 1 — TeDarrell? (**block-customer inverted again**; Require Delete Reason) | https://claude.ai/artifact/TDUauToxAN91qyM9Vy1yuk |
| 2026-09-15 | Shop Analytics (trainer caught Outrunning Overhead colour bug live) | https://claude.ai/artifact/J7Ttwhd6bLFLskNDb7kRq5 |
| 2026-09-16 | Admin Part 1 — Aaron (role-vs-permission theme; 10 of 13 correct) | https://claude.ai/artifact/XDsbHzEGuCYaAL8iwtu4Vu |
| 2026-09-17 | **Advisor Training — Allie** (first Advisor audit; block-customer taught right) | https://claude.ai/artifact/D7xW1RbY5LJcjXdGbRMvwx |
| 2026-09-21 | Admin Part 1 — unidentified (role-vs-permission again; demo lost admin scope) | https://claude.ai/artifact/XXkFEtoaVcY2kQekmtNTaD |
| 2026-09-21 | **Advisor Training — Allie** (closes the `calls.role-access` gap; new SMS-label product bug) | https://claude.ai/artifact/Cg88XUMmSpFnWsMjNWjr7w |
| 2026-09-21 | Admin Part 2 — TeDarrell (**All Recordings taught as a recording switch**; block-customer corrected) | https://claude.ai/artifact/4hefXCQjiyjRhYHR9EALdD |
| 2026-09-22 | Admin Part 2 — unidentified (**auto-reply gate**; directly-assigned campaign tasks widen to admins) | https://claude.ai/artifact/CoG64ixqBeuyUZzt5cQmcY |
| 2026-09-22 | **Advisor Training — Allie** (pinned-reports + SMS-label findings closed; **block-customer regressed**) | https://claude.ai/artifact/PfjhzMnwgLWPRaX3DCcGcw |
| 2026-09-22 | Admin Part 1 — TeDarrell? (11 of 14 correct; **Require Delete Reason label hits a 4th run**) | https://claude.ai/artifact/EFid33mck3htFEn9mNtK15 |
| 2026-09-23 | Advisor Training — unidentified (substitute trainer; service-description targeting) | https://claude.ai/artifact/LoPDr6QJNLa1AM4iC4Rt47 |
| 2026-09-23 | CRM Overview — unidentified (outcome-prompt repeat; third write path for the campaigns flag) | https://claude.ai/artifact/BzWCER7vmkRgVSGtmovS5W |
| 2026-09-24 | **Admin Part 1 — Aaron** (**Manage Campaigns contradiction**; new dead `/bookings/capture` bug) | https://claude.ai/artifact/BdVb8mLw4Cnq2mthsEKyzm |
