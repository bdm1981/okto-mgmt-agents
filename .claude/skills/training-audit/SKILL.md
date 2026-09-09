---
name: training-audit
description: Audit recorded OktoRocket customer training sessions for factual accuracy against the product source code. Pulls Zoom cloud transcripts, grades every checkable claim a trainer made against dc-user / dc-server / dc-booking / moto-sales-tracker on a pinned commit, publishes a per-session report plus a rolling Training QA dashboard, and posts a summary to Slack. Use for "training audit", "audit the training sessions", "review last week's trainings", "did the trainer say anything wrong", "check training accuracy", "training QA", or any scheduled/routine pass over new training recordings. Read-only against every system.
---

# Training audit

You grade what a trainer **told a customer** against what the code **actually does**, then record it so the same mistake is detectable the next time a different trainer makes it.

Output per run: a **per-session report** for each new session, an updated **rolling dashboard**, an appended **findings ledger**, and a **Slack summary**. Every claim you grade carries a `path:line` citation or is explicitly marked unverifiable.

## Required input

- **Window** — default the last 7 days. Honor explicit dates ("audit 2026-09-07", "last week").
- **Code baseline** — always `origin/development` of the `oktorocket` repo, fetched at the start of the run and pinned for the whole run. Record the commit in every artifact.

## Before you start

Read `references/gotchas.md`, `references/grading.md` and `references/product-bugs.md` once per session. `grading.md` holds the taxonomy and the fairness rules; skipping it produces findings that are technically right and unfair, which is worse than none.

## Procedure

### Step 1 — Pin the code baseline

```bash
scripts/pin_baseline.sh                 # fetches origin/development, prints the commit
```

Every subsequent grep runs against that ref (`git grep <pat> <commit> -- <path>`), never the working tree — a dirty checkout would silently grade against someone's branch. Put the short SHA and its date in every report.

### Step 2 — Discover new sessions

```bash
scripts/discover_sessions.py --from 2026-09-01 --to 2026-09-08 > sessions.json
```

Reads `references/sources.md` for the host allowlist and topic patterns, calls Zoom, and drops anything whose meeting UUID already appears in `references/findings-ledger.md`. **Never re-audit a session** — the ledger is the record and duplicates corrupt repeat detection.

If it returns zero sessions, post nothing and stop. A quiet week is a quiet week.

### Step 3 — Fetch and compact each transcript

```bash
scripts/fetch_transcript.py --session <uuid> --out raw/<uuid>.vtt
scripts/compact_vtt.py raw/<uuid>.vtt > compact/<uuid>.txt
```

`compact_vtt.py` turns 2,000 VTT cues into ~500 `[mm:ss] Speaker: text` lines. Read the compacted file, not the raw VTT.

**Only the host's audio is reliably captured.** In two of the four seed sessions the attendee was never transcribed. When you cannot see the customer's question, say so in the caveats and do not infer what they asked.

### Step 4 — Extract claims, then verify each one

Walk the transcript and pull out every statement that is **checkable against code**: what a toggle does, what a field means, what a report shows, what a limit is, what happens when a setting is off. Ignore pleasantries, pricing, competitor claims and coaching opinion — those go in the unverifiable list.

For each claim, locate the implementation and grade it. Useful entry points:

| Area | Where it lives |
|---|---|
| Campaigns, keyword detection, managed links | `dc-user/src/js/admin/components/campaigns/`, `dc-server/modules/campaigns/` |
| Campaign send/build engine | `dc-server/modules/campaignBuilder.js`, `modules/dispatcher.js` |
| Scheduler / booking settings | `dc-user/src/js/admin/components/sites/booking/`, `dc-booking/src/` |
| Inbox, tasks, calls, reviews | `dc-user/src/js/user/components/inbox/`, `admin/components/calls/`, `dc-server/models/tracker.js` |
| Shop Analytics, goals, Rocket Gauge | `dc-user/src/js/admin/components/reports/sales-analytics/`, `moto-sales-tracker-api/` |
| Users, roles, permissions | `dc-user/src/js/admin/components/users/`, `dc-server/routes/users.js`, `modules/cognitoService.js` |
| SQL-side metrics | `moto-tracker-model/Migrations/Sql/` |

Two habits that pay for themselves:

- **Read the in-app label and help text, not just the behavior.** Several findings are the product contradicting itself, and the trainer merely read it aloud. That is a product bug, not a training error — grade it as such (see `product-bugs.md`).
- **Check the "off" branch.** Trainers reliably describe what a toggle does when on. The costly errors are in what happens when it is off, or when a gate upstream means it never applies.

Append one JSON line per graded claim to `findings.jsonl` as you go — this is what survives context summarisation and what the renderers read:

```json
{"session":"<uuid>","stamp":"15:04","claim_id":"campaigns.explain-delete.is-confirmation",
 "quote":"that particular option is just for an extra screen…","grade":"wrong_high",
 "reality":"explainDelete=true removes the reason picker entirely; the legacy label is inverted",
 "evidence":["dc-user/src/js/common/components/campaigns/DeleteCampaignButton.js:16"],
 "say_instead":"Leave it off — off is what gives advisors Delete w/ Reason.",
 "product_bug":true}
```

`claim_id` is the join key for repeat detection. Use `<area>.<feature>.<assertion>`, reuse an existing id from the ledger whenever the same misconception recurs, and keep it stable — a renamed id breaks the repeat count.

### Step 5 — Detect repeats and update the ledger

```bash
scripts/ledger.py --add findings.jsonl        # appends, returns repeats + product-bug deltas
```

Any `claim_id` that now has findings from **more than one session or more than one trainer** is a **curriculum defect**, not a coaching note, and leads the dashboard. That distinction is the whole point of running this on a schedule.

### Step 6 — Render, publish, post

```bash
scripts/build_report.py --session <uuid> --findings findings.jsonl > report-<uuid>.html
scripts/build_dashboard.py --ledger references/findings-ledger.md > dashboard.html
scripts/export_pdf.sh report-<uuid>.html      # optional, Letter, links preserved
```

Publish each per-session report as a new artifact; republish `dashboard.html` to the **fixed URL** in `references/dashboard.md` (publishing without `url:` creates a second page — the usual way this breaks).

Then post one Slack message to the channel named in `references/sources.md`, using the Slack MCP:

- session, date, trainer, duration
- the tallies (wrong / incomplete / correct / unverifiable)
- **any repeat or new product bug, named** — this is the part people act on
- links to the per-session report and the dashboard

Keep the Slack post to a summary and let the detail live on the page. The channel should be a limited one: these reports assess named employees.

### Step 7 — Feed back what you learned

If a run taught you something structural — a new data trap, a new area of the code, a claim that looked wrong and wasn't — add it to `references/gotchas.md` or `references/grading.md` before you finish. A skill that does not accumulate is worth less every month.

## Guardrails

- **Read-only.** Never write to Zoom, never mutate the oktorocket repo, never touch a customer tenant.
- **No finding without evidence.** Either a `path:line` on the pinned commit, or graded `unverifiable`. "I recall this being true" is not a grade.
- **Tenant configuration is not gradeable.** Whether a shop has a flag on, which DMS they run, what their service durations are — list them as unverifiable rather than guessing. Do not query MongoDB to settle them.
- **Be fair to the trainer.** Apply the fairness rules in `grading.md`. Credit self-corrections, separate transcription noise from error, and credit a trainer who contradicts wrong in-app copy.
- **Never post to a customer-facing channel** and never send a report to the audited trainer automatically. A human decides who sees an assessment of a named person.
