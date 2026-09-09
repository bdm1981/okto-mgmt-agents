# okto-mgmt-agents

Claude Code skills that turn OktoRocket's operational data into management reviews.

| skill | reads | produces |
|---|---|---|
| **`daily-call-review`** | every Support call transcript for a day, joined to Zoho Desk | **Support Desk Daily** — one fixed dashboard page, republished each morning |
| **`training-audit`** | recorded customer training sessions from Zoom, graded against product source | a per-session report, the rolling **Training QA** dashboard, and a Slack summary |

## What `daily-call-review` produces

One page, same URL every day — **Support Desk Daily**:

| Section | Source |
|---|---|
| Department scoreboard — calls, talk-hours, missed-and-waited, tickets opened/closed, open-overdue | partner MCP + Desk |
| Calls by hour with negative-AdvisorIQ overlay | partner MCP |
| Inbound calls ≥3 min without the rep's own ticket | partner MCP × Desk |
| **Needs an owner tomorrow** — accounts where phones and Desk disagree or nobody's name is on it | reviewer, from transcripts |
| **Per technician** — volume, own-ticket rate, Desk load, remote sessions (needed / partial / not needed), one quoted thing done well, one quoted thing to address | transcripts + Desk |
| Remote sessions today, with a verdict each | transcripts |
| Patterns for the department | reviewer |
| Method & caveats | always |

Every call ID links to `app.digitalconcierge.io/userPortal/admin/calls?callId=…`; every `#NNNNN` links to the ticket in Desk.
A Letter-size PDF with the links intact can be exported from the same HTML.

The review reads **every** recorded Support transcript ≥45 s (60–90 on a weekday), not a sample.

## Requirements

**Runtime**
- Claude Code (desktop app or CLI) with the Artifact tool — the dashboard is a published artifact.
- `python3` ≥ 3.9 (standard library only).
- Google Chrome, for the optional PDF export (`scripts/export_pdf.sh`).

**MCP servers** (configured in the runner's Claude Code — see `~/.claude.json` → `mcpServers`)
- **OktoRocket partner MCP** — `https://okto-partner-api.oktorocket.io/mcp`, header `x-api-key`. The key needs
  `read:calls` (list/get calls + `get_transcript`) and **`read:users`** (`list_users`, `get_site_employee_map`).
  Without `read:users` the review still runs but reports by extension number only.
- **Zoho Desk MCP** (Zoho connector, per-user OAuth). Org `841585781`, department `943174000000006907`.
  Needs ticket read access; nothing is ever written.

**Ownership**
- Only the artifact's owner can republish to its URL. The page in `references/dashboard.md` is owned by the
  account that first published it. One identity should run the review; everyone else consumes the link.
- The review is **read-only** against every system it touches.

## Install

Skills are discovered from `.claude/skills/` when Claude Code runs inside this repo:

```bash
git clone git@github.com:bdm1981/okto-mgmt-agents.git
cd okto-mgmt-agents
claude          # or open the folder in the desktop app
```

To make the skill available from any directory, symlink it into your user skills:

```bash
ln -s "$PWD/.claude/skills/daily-call-review" ~/.claude/skills/daily-call-review
```

## Run

```
/daily-call-review yesterday
/daily-call-review 2026-09-08
/daily-call-review last week (Mon 2026-08-31 through Fri 2026-09-04)
```

The skill walks these steps (all in `SKILL.md`):

1. Roster (`list_users`) → extension map, using `references/team-roles.md` for the team split.
2. Day's calls (`list_calls`, spills to a file — expected) → `scripts/triage_calls.py` for coverage, at-risk contacts, dial storms; `scripts/select_transcripts.py` for the full read list.
3. Read **every** transcript, appending one JSON line per call to `notes.jsonl` as you go.
4. Day's Desk tickets (`searchTickets`, paged at 100) → `scripts/match_tickets.py`.
5. Author `narrative.json` (words only — owners, per-tech quotes, patterns, caveats).
6. `scripts/build_dashboard.py` computes every number and renders `daily.html`; publish to the URL in `references/dashboard.md`; optionally `scripts/export_pdf.sh`.

## Maintain

- **`references/team-roles.md`** — extension → name → team. `roleId` from the API does not describe internal teams; this file does. Update it when someone joins, leaves, or changes extension. Also records how shared extensions are resolved.
- **`references/dashboard.md`** — the fixed artifact URL(s). Publishing without `url:` creates a second page.
- **`references/gotchas.md`** — every data trap that has produced a wrong number so far (inverted `status`, Desk's 100-row cap, ring-group artefacts, broken summaries…). Read it before trusting a metric; add to it when you find a new one.

## Layout

```
.claude/skills/daily-call-review/
├── SKILL.md                      procedure, data shape, guardrails, report contract
├── scripts/
│   ├── triage_calls.py           coverage, per-team tables, at-risk contacts, dial storms
│   ├── select_transcripts.py     every recorded Support call worth reading
│   ├── match_tickets.py          Desk × calls: ticketing discipline, unticketed calls
│   ├── build_dashboard.py        renders the dashboard from stats + notes + narrative
│   └── export_pdf.sh             headless-Chrome PDF with links preserved
├── assets/
│   ├── dashboard.css             the page design (both themes)
│   └── print.css                 Letter-size print overrides
└── references/
    ├── team-roles.md             extension → person → team
    ├── dashboard.md              fixed artifact URL(s)
    └── gotchas.md                data traps
```

## `training-audit`

Grades what a trainer **told a customer** against what the code **actually does**, then records it
so the same mistake is detectable when a different trainer makes it.

Three things come out of a run:

- **A per-session report** — every checkable claim graded `wrong_high` / `wrong_contained` /
  `incomplete` / `correct` / `unverifiable`, each with a `path:line` citation on a pinned commit,
  the trainer's own words quoted, and a "say instead" line.
- **The rolling Training QA dashboard** — the part a schedule buys you:
  - **repeats** — the same misconception in more than one session. More than one trainer means a
    curriculum defect, not a coaching note.
  - **contradictions** — taught *wrong* in one session and *correctly* in another. Nobody is
    consistently wrong so it never shows as a repeat, yet the curriculum is inconsistent and the
    fix is free, because a correct script already exists in a recording.
  - **open product bugs** found while auditing, several of which are the product contradicting
    itself in its own labels.
- **A Slack summary** to the limited channel in `references/sources.md`.

### Requirements

**Zoom Server-to-Server OAuth** — the Zoom *connector* cannot do this job. It is per-user OAuth and
only returns the authenticated user's own recordings, so a run driven by anyone but the training
account sees nothing. Verified against 20–31 Aug 2026: 10 recordings returned, all one host, none of
them training. Create an S2S app with `cloud_recording:read:list_user_recordings:admin` + `user:read:list_users:admin` (the granular scopes — Zoom retired the coarse `recording:read:admin`) and export
`ZOOM_ACCOUNT_ID`, `ZOOM_CLIENT_ID`, `ZOOM_CLIENT_SECRET`. Full steps in
`references/sources.md`; verify with `scripts/zoom_client.py`.

Also needs a clone of `oktorocket` (default `~/Documents/DEV/oktorocket`, override with
`OKTO_REPO`) — claims are graded against `origin/development` at a commit pinned per run, never
against the working tree.

### Run

```
/training-audit                       # the last 7 days
/training-audit 2026-09-07            # one day
/training-audit last two weeks
```

### Maintain

- **`references/grading.md`** — the taxonomy and the **fairness rules**. Read before grading:
  separate transcription noise from error, credit self-corrections, and credit a trainer who
  contradicts wrong in-app copy. Breaking these produces findings that are technically right and
  unfair, which is worse than reporting nothing.
- **`references/findings-ledger.md`** — append-only, one row per graded claim. `claim_id` is the
  join key for repeat and contradiction detection. Written by `scripts/ledger.py`; never hand-edit
  rows, never re-audit a session, never rename an id.
- **`references/sources.md`** — Zoom host allowlist, topic patterns, minimum duration, Slack channel.
- **`references/product-bugs.md`** — bugs found while auditing. A bug that keeps appearing across
  sessions is evidence for prioritising it.
- **`references/gotchas.md`** — every trap that has produced a wrong or unfair finding.

### Layout

```
.claude/skills/training-audit/
├── SKILL.md                      procedure, grading contract, guardrails
├── scripts/
│   ├── zoom_client.py            S2S OAuth; list recordings, download VTT (stdlib only)
│   ├── discover_sessions.py      new training sessions in a window, minus anything already audited
│   ├── fetch_transcript.py       download one session's VTT
│   ├── compact_vtt.py            2,000 cues -> ~500 readable "[mm:ss] Speaker: text" lines
│   ├── pin_baseline.sh           fetch + pin origin/development for the run
│   ├── ledger.py                 append findings; detect repeats and contradictions
│   ├── render.py                 shared HTML helpers (numbers computed, words authored)
│   ├── build_report.py           per-session report
│   ├── build_dashboard.py        rolling Training QA dashboard
│   └── export_pdf.sh             Letter PDF, findings never split across pages
├── assets/
│   ├── report.css                page design, both themes
│   └── print.css                 print overrides
└── references/
    ├── sources.md                hosts, topic patterns, Zoom S2S setup, Slack channel
    ├── grading.md                taxonomy + fairness rules + claim_id conventions
    ├── findings-ledger.md        append-only graded claims
    ├── product-bugs.md           open bugs found while auditing
    ├── dashboard.md              fixed artifact URLs
    └── gotchas.md                data traps
```

## Handoff

Setting this up on another machine: **[HANDOFF-training-audit.md](HANDOFF-training-audit.md)**.
Read its two Blockers first — artifact ownership (a different Claude account silently forks the
dashboard instead of updating it) and credential placement (`~/.zshrc` is invisible to scheduled
runs).

## Scheduling

| skill | when | how |
|---|---|---|
| `daily-call-review` | weekdays after support closes (7:30 pm Central) | not yet scheduled — invoke it |
| `training-audit` | Mondays 09:27 local, covering the previous 7 days | scheduled task `training-audit-weekly` |

Scheduled tasks live in `~/.claude/scheduled-tasks/<id>/SKILL.md` and run while the desktop app is
open; a task due while it is closed runs on next launch. Both reviews republish to a **fixed**
artifact URL — publishing without `url:` creates a second page and the team ends up reading a stale
one.

`training-audit-weekly` checks its Zoom credentials first and posts nothing if they are missing, so
it is safe to leave scheduled before the S2S app exists.
