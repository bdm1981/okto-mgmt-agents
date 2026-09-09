# okto-mgmt-agents

Claude Code skills that turn OktoRocket's operational data into management reviews.
Today there is one: **`daily-call-review`**, which reads every Support call transcript from a day,
joins it to Zoho Desk, and republishes a fixed dashboard page the support manager opens each morning.

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

## Scheduling

Intended to run each weekday after support closes (7:30 pm Central) from one account, republishing the same URL.
Not yet scheduled — the skill has to be invoked.
