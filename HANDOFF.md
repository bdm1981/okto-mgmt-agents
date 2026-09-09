# Handoff — running Support Desk Daily from an always-on machine

Goal: one machine, signed in as the account that owns the dashboard, runs `/daily-call-review` every weekday
evening, republishes the same URL, exports the PDF, and posts the link to Slack. The support management team
opens one link each morning and never touches the tooling.

Time to set up: about 45 minutes. Everything below is read-only against production systems.

**Where things run.** The desktop app has two tabs and they are different products:
- **Code** tab — this is Claude Code. The `/daily-call-review` skill, the MCP servers in `~/.claude.json`, and the
  scheduled task all live here. Every `/…` command in this document goes in the **Code** tab's message box.
- **Chat** tab — has its own slash menu and connectors; it does not see Claude Code skills. If `/daily-call-review`
  autocompletes in Chat but not in Code, you are looking at a different `/` item — the skill is not installed for Code yet.
- Shell commands (`git`, `ln`, `claude mcp add`, `python3`) go in a **terminal** — the Terminal panel inside the Code
  tab, or Terminal.app. Never paste them into a chat box.
Skills are loaded when a Code session starts: after installing or symlinking, start a **new** session.

---

## 0. Before you start — what has to be true

| | Why it matters |
|---|---|
| **Same Claude account** (bdm@oktorocket.com) signed in on the new machine | Only the artifact's owner can republish to the fixed URL. A different account would create a second page. |
| **Partner API key** for `okto-partner-api.oktorocket.io` with scopes `read:calls` **and** `read:users` | `read:users` is what maps extensions to people. Without it the review still runs, but by extension number only. Use a *new* key for this machine so it can be rotated independently. |
| **Zoho Desk connector** authorised for that account | Per-user OAuth; done in the desktop app's Connectors screen, not in a file. |
| **Google Chrome** installed | Headless Chrome renders the PDF. |
| **Machine stays awake with the desktop app open** | Scheduled tasks run inside the app. Set Energy → "Prevent automatic sleeping" (or run `caffeinate -dis` at login). |
| GitHub SSH access to `bdm1981/okto-mgmt-agents` | To pull the skill and future fixes. |

---

## 1. Install the skill (10 min)

```bash
git clone git@github.com:bdm1981/okto-mgmt-agents.git ~/Documents/DEV/okto-mgmt-agents
ln -s ~/Documents/DEV/okto-mgmt-agents/.claude/skills/daily-call-review ~/.claude/skills/daily-call-review
python3 --version            # 3.9+ ; standard library only
ls "/Applications/Google Chrome.app" && echo chrome ok
```

The symlink makes `/daily-call-review` available from any directory. `git pull` in the repo later picks up fixes.

## 2. Connect the data sources (15 min)

**Partner MCP** — in a terminal (create the key in the partner API admin first; never commit it anywhere):

```bash
claude mcp add --transport http --scope user oktorocket https://okto-partner-api.oktorocket.io/mcp --header "x-api-key: PASTE_KEY_HERE"
```

That writes the following into `~/.claude.json` under `mcpServers`; add it by hand if the CLI is unavailable:

```json
"oktorocket": {
  "type": "http",
  "url": "https://okto-partner-api.oktorocket.io/mcp",
  "headers": { "x-api-key": "<the new key>" }
}
```

**Zoho Desk** — desktop app → Connectors → Zoho Desk → authorise. Org `841585781`, department `943174000000006907`.

Quit and reopen the desktop app (MCP servers load at startup), open a **Code** session, and verify all three in one go by asking:

> Call oktorocket list_sites, oktorocket list_users for site 634c8538a3be38fc4c8ed28c with pageSize 5, and Zoho Desk searchTickets for org 841585781 limit 1. Just confirm each returns data.

Expected: one site (OktoRocket), a page of users **with names** (if you get `forbidden — lacks read:users`, the key is missing the scope), and one ticket.

## 3. Prove the whole pipeline once, by hand (15 min)

In a session on the new machine:

```
/daily-call-review yesterday
```

Watch for these four things. Each one has bitten before:

1. The `list_calls` result "exceeds maximum tokens" and is saved to a file — **that is expected**, the scripts read the file.
2. It reads **every** Support transcript (54–90 on a weekday), appending to `notes.jsonl` as it goes. If it offers a "top 20" sample, tell it to read all of them.
3. Before publishing it runs `Artifact read` on the URL in `references/dashboard.md`, then publishes **with `url:`**. If the result says "Published … at" a *new* URL, it forgot `url:` — the fix is to republish with the URL passed; delete the accidental page from the gallery.
4. The PDF lands beside the HTML (`scripts/export_pdf.sh`).

Open the live page in a browser and check the date in the header changed.

## 4. Schedule it (5 min)

In the same session, on the always-on machine:

```
/schedule
```

and give it this, verbatim (adjust channel and time if needed):

> Every Monday–Friday at 7:30 PM America/Chicago, run `/daily-call-review` for today. Read every Support
> transcript. Republish the dashboard to the URL in references/dashboard.md (read it first, pass url:).
> Export the PDF with scripts/export_pdf.sh. Then post to Slack `#support-leads`: the one-line headline from
> narrative.json, the three "Needs an owner tomorrow" names, and the dashboard link; attach the PDF. If any
> data source fails, post what failed instead of a partial dashboard.

Confirm the task appears in the app's scheduled-tasks list. Leave the app open. The first automatic run is the
next weekday evening; check the page the following morning.

Notes on the run itself:
- A full day is ~60–90 transcript reads and takes 15–30 minutes. That is normal.
- Holidays: the queue empties on the next working day (we saw campaign bursts and no calls on Labor Day). A
  weekday holiday produces a near-empty dashboard — harmless.
- If the machine was asleep at 7:30, the task runs when the app wakes; the date is computed from "today" so
  a run after midnight reviews the wrong day. Keep it awake.

## 5. Share with the support management team (10 min)

**The page.** Open the dashboard → **Share** → share with the OktoRocket workspace (or the specific managers).
Do this once; the URL never changes. Point them at it with:

> Support Desk Daily — https://claude.ai/code/artifact/13933200-0424-4f9b-9b3f-f58c5897d6bf
> Updated each weekday around 8 pm Central. Every call ID and ticket number is a link. Comment on anything;
> if you hit "Send to Claude" on the comment it reaches the session that maintains the page.

**The Slack post** does the daily nudge (step 4). If leads prefer email, forward the PDF from the Slack post.

**The weekly view.** The week-36 page (`references/dashboard.md`) shows the same design over five days. If they
want a weekly rollup as well, ask for `/daily-call-review last week` on Friday evenings and publish to that URL.

**What to tell them about the numbers** — put this in the first message, it prevents most misreads:
- AdvisorIQ −1 means the *customer* was frustrated, not that the rep did badly. Every −1 read so far was competent work.
- "Own ticket" = the rep who answered opened a phone ticket within 2 hours. It is a discipline metric, not a quality one.
- Remote-session verdicts come from the transcript. *Not needed* means the answer was on our side (registration, routing, ring group). *Partial* means it found something but a server-side check would have skipped it.
- "Missed & waited" counts callers who rang 15 s or more and reached nobody; 0-second legs are ring-group artefacts and excluded.

## 6. Keep it honest

| When | Do |
|---|---|
| Someone joins / leaves / changes extension | Edit `references/team-roles.md`, commit, `git pull` on the runner. The API's `roleId` does **not** give the team split; this file does. |
| A shared phone is used by someone else (e.g. 8021 answered "Shawn speaking") | The review flags it; confirm and note it in `team-roles.md` → Ambiguous extensions. |
| You find a new data trap | Add it to `references/gotchas.md`. That file is why the numbers are trustworthy. |
| Rotating the partner key | Replace in `~/.claude.json`, restart the app, re-run step 2's check. |
| The dashboard URL ever changes | Update `references/dashboard.md` and re-share. Avoid this — everyone has the old link. |

## 7. If something breaks

| Symptom | Cause / fix |
|---|---|
| `forbidden — This key lacks the 'read:users' scope` | Key is missing the scope. Review runs by extension only until fixed. |
| Ticket counts look low | `searchTickets` caps at 100 per page; `count` is the real total. The skill pages with `from:`; check it did. |
| Published to a new URL | `url:` was not passed. Republish with it; delete the stray page. |
| PDF step fails | Chrome path; `CHROME=/path/to/Chrome scripts/export_pdf.sh …`. |
| A tech shows 0 calls | They were out, or worked from another extension — check the greeting on that extension's first transcript. |
| Summary text looks like a prompt ("A well-written narrative summary…") | Known summariser defect; the review reads transcripts, not summaries, so it is unaffected. Report to dev. |

---

Repo: `git@github.com:bdm1981/okto-mgmt-agents.git` · Skill: `.claude/skills/daily-call-review/` · Read-only everywhere.
