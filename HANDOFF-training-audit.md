# Handoff — running `training-audit` as a scheduled job on another machine

Everything needed to stand this up somewhere else. Written 2026-09-09 against branch
`feat/training-audit-skill`.

Read the two **Blockers** first. Both are things that look like they work and quietly don't.

---

## Blockers

### 1. It must run as the same Claude account, or the dashboard forks

The rolling dashboard is an Artifact at a fixed URL, recorded in
`.claude/skills/training-audit/references/dashboard.md`. **Only the artifact's owner can
republish to that URL.** A run from a different Claude identity cannot update it — it silently
publishes a *second* page, and the team keeps reading the stale one.

So: the scheduled machine must be signed into Claude as **bdm@oktorocket.com**, the account that
owns the existing pages. If that is not possible, decide deliberately to start a new dashboard,
publish once, and overwrite the `url:` in `dashboard.md` — do not let it fork by accident.

Per-session reports are new artifacts each run, so they are unaffected.

### 2. Credentials must not go in `~/.zshrc`

`.zshrc` is sourced only by **interactive** zsh. Every Bash call a scheduled run makes is
non-interactive, so credentials exported there are invisible and the job fails weekly with
"missing credentials" while looking perfectly set to a human. This already happened once here.

Put them in `~/.config/okto/zoom.env`, mode `600`. `zoom_client.py` loads that file directly
(override the path with `OKTO_ZOOM_ENV`).

---

## Prerequisites

| need | why | check |
|---|---|---|
| Claude Code, signed in as the artifact owner | publishes the dashboard | see Blocker 1 |
| `python3` ≥ 3.9 | all scripts, stdlib only | `python3 -V` |
| A clone of `oktorocket` | claims are graded against its code | `git -C <path> log -1` |
| `gh` CLI, authenticated | fetches `origin/development` over HTTPS | `gh auth status` |
| Google Chrome | PDF export only, optional | `ls "/Applications/Google Chrome.app"` |
| Zoom S2S credentials | reads recordings + participants | below |
| Slack MCP connector | posts the summary | below |

### Zoom

The app already exists — **"training audit"**, Server-to-Server OAuth, account-level, activated,
in the OktoRocket Zoom account (owner `rick@oktorocket.com`). Do **not** create a second one.
Marketplace → Develop → Created apps.

Scopes it holds, and no others:

```
cloud_recording:read:list_user_recordings:admin
user:read:list_users:admin
meeting:read:list_past_participants:admin
```

Copy the three credentials to the new machine **out of band** — not through git, not through
chat. Then:

```bash
mkdir -p ~/.config/okto && chmod 700 ~/.config/okto
cat > ~/.config/okto/zoom.env <<'EOF'
export ZOOM_ACCOUNT_ID="…"
export ZOOM_CLIENT_ID="…"
export ZOOM_CLIENT_SECRET="…"
EOF
chmod 600 ~/.config/okto/zoom.env
```

### Slack

The Slack MCP connector must be authorised on the new machine as a user who is a **member of the
private channel** `#team-training-audits` (`C0C1HH5P0RW`). A non-member gets `not_in_channel`,
which surfaces only at the very end of a run after every transcript has been read and graded.

Channel id lives in `references/sources.md`. Prefer the id over the name — a rename breaks
name-based posting.

---

## Install

```bash
git clone https://github.com/bdm1981/okto-mgmt-agents.git
cd okto-mgmt-agents
git checkout feat/training-audit-skill        # until it merges to main

# the code baseline the audit grades against
git clone https://github.com/ShopRocket-LLC/oktorocket.git ~/Documents/DEV/oktorocket
```

If the oktorocket clone lives elsewhere, export `OKTO_REPO=/path/to/oktorocket`. The scripts
default to `~/Documents/DEV/oktorocket`.

Skills are discovered from `.claude/skills/` when Claude Code runs inside this repo. To use it
from anywhere:

```bash
ln -s "$PWD/.claude/skills/training-audit" ~/.claude/skills/training-audit
```

---

## Verify before scheduling

Run these in order. Each one fails loudly and specifically.

```bash
cd .claude/skills/training-audit/scripts

# 1. Zoom auth + scopes. Prints "OK — authenticated, N active users visible".
./zoom_client.py

# 2. Code baseline. Prints the pinned short SHA; warns and falls back if fetch fails.
eval "$(./pin_baseline.sh)" && echo "$OKTO_SHA_SHORT"

# 3. Discovery. Should print sessions and a skipped breakdown, not a traceback.
./discover_sessions.py --from 2026-09-01 --to 2026-09-09 | head -30

# 4. Participants scope (the newest, most likely to be missing).
python3 -c "import zoom_client as zc, json; print(json.dumps(zc.attendees('yLMACd4kQIiCsc4B4HbohA=='), indent=1))"

# 5. Renderers, against the committed ledger.
./build_dashboard.py --baseline "$OKTO_SHA_SHORT" > /tmp/dash.html && wc -c /tmp/dash.html
```

Then one **manual** end-to-end run before you trust the schedule — `/training-audit last 7 days`.
It will ask for tool approvals; granting them during a run stores them on the task, so the first
unattended run does not stall on a permission prompt.

---

## Schedule it

The scheduled task is **machine-local** — it lives in `~/.claude/scheduled-tasks/<id>/SKILL.md`
and does not travel with the repo. Recreate it on the new machine.

Current definition on the origin machine: `training-audit-weekly`, cron `23 9 * * 1`
(Mondays 09:27 local), covering the previous 7 days. The full prompt is in that file — copy it
across, or ask Claude to recreate it with the same schedule and prompt.

Two things the prompt already handles, and should keep handling:

- **No credentials → post nothing.** It verifies Zoom auth first and reports the problem in the
  run output rather than to Slack.
- **No new sessions → post nothing.** A quiet week is a quiet week.

Scheduled tasks run while the desktop app is open; a task due while it is closed runs on next
launch. Pick a machine that is actually on Monday mornings.

---

## What state lives where

| state | location | travels with repo? |
|---|---|---|
| Findings ledger (89 rows) | `references/findings-ledger.md` | ✅ |
| Session index — duration, attendance | `references/sessions-index.md` | ✅ |
| Trainer roster + aliases | `references/trainers.md` | ✅ |
| Open product bugs | `references/product-bugs.md` | ✅ |
| Published page URLs | `references/dashboard.md` | ✅ |
| Zoom credentials | `~/.config/okto/zoom.env` | ❌ copy by hand |
| Scheduled task | `~/.claude/scheduled-tasks/` | ❌ recreate |
| Artifact ownership | the Claude account | ❌ see Blocker 1 |
| Run outputs (transcripts, findings.jsonl) | scratch dirs, gitignored | ❌ disposable |

**The ledger is the durable record.** Reports are renderings of it and can be regenerated at any
time; the ledger cannot be reconstructed from them. If a run is interrupted, land the findings in
the ledger before worrying about publishing.

---

## Where the August backlog stands

30 sessions were unscored at the start of 9 Sep. As of this handoff:

| course | runs | state |
|---|---|---|
| Foundations | 15 | ✅ audited, course report published, posted to Slack |
| Deep Dive | 9 | ⚠️ **findings in the ledger, no report published, not posted** |
| CRM | 3 | ❌ not started |
| 1:1 Client | 2 | ❌ not started |
| Sales Analytics | 1 | ❌ not started |

Plus 2 sessions audited individually (27 Aug, 3 Sep Deep Dive) with reports published.

The Deep Dive gap is the thing to pick up first: 6 findings are in the ledger from the 04 Aug and
11 Aug and 18 Aug runs, but no report was rendered and nothing was posted. Because those sessions
are now in the ledger, discovery will **not** re-offer them — render the report from the ledger
rather than re-auditing.

Its headline finding is already recorded: the invite-expiry error is **intermittent, not
scripted**. Across nine August runs the wrong "1 hour" figure appears once (18 Aug), with four
runs stating it correctly, and it recurs 25 and 27 Aug before disappearing by 3 Sep.

---

## Open decisions

Neither blocks a run.

1. **Delivery format.** Artifacts are private and cannot be auto-shared — there is no share
   action on the tool. Two alternatives were scoped but not built: a Slack **canvas** (natively
   readable, `canvas_add_file_collaborators` shares it programmatically, but loses the HTML
   design), or **PDF → Google Drive → `share_file` → link in Slack** (keeps the design, needs a
   Google Group address; `share_file` is per-address with no anyone-with-link role). Slack has no
   file-upload tool, so a PDF cannot be attached to a message directly.
2. **Per-course vs per-session reports.** Currently course-level where a course has many runs,
   because 15 near-identical Foundations reports would bury the finding that mattered. Revisit if
   individual reports are wanted.

---

## Things that will bite

Everything below has already happened once.

- **`~/.zshrc` credentials are invisible to scheduled runs.** Blocker 2.
- **SSH to github.com fails on the origin machine** (`sign_and_send_pubkey: signing failed`).
  Pushes use an explicit HTTPS URL plus `-c credential.helper='!gh auth git-credential'`. May not
  apply on the new machine; if pushes fail, that is the fix.
- **A meeting UUID containing `/` or `==` must be double URL-encoded.** Single-encoded it returns
  400 and reads like a malformed request.
- **Zoom participant records are per-join, not per-person.** `total_records` overcounts. Use
  `zoom_client.attendees()`.
- **Transcript speaker count is not attendance.** It reads 0 for sessions that had three people
  present for an hour. Never label it "attendees".
- **The Zoom host is always the shared training account,** so the host name is not the trainer.
  Identify the trainer from the transcript and canonicalise through `references/trainers.md` —
  Zoom rendered one trainer's name four ways, none of them correct.
- **Validate a probe regex against a loose word match** before treating its absence as a coverage
  finding. Tight patterns reported 0/9 for two topics that appear in 9/9 and 6/9.
- **Never re-audit a session.** `ledger.py` refuses, and duplicates would manufacture a repeat out
  of a single mistake.
- **`references/gotchas.md` is the living version of this list.** Read it before trusting a
  finding; add to it when something new bites.
