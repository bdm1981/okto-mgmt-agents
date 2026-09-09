---
name: daily-call-review
description: Daily review of OktoRocket support call transcripts via the oktorocket partner MCP, surfacing customers at risk, technician performance, customer success performance, and patterns management should see. Use for "daily call review", "review yesterday's calls", "how did support do today", "which customers are at risk", "call review for a specific date", or any scheduled/routine end-of-day call read. Read-only.
---

# Daily call review

You produce a five-part report for one day: **(1) customers at risk, (2) technician performance, (3) customer success performance, (4) patterns for management, (5) coverage & caveats.**

Data comes from the **oktorocket partner MCP** (`mcp__oktorocket__*`). Do not query MongoDB — the partner API is the supported, tenant-scoped, audited path. The older `call-themes` skill reads Mongo directly for ad-hoc multi-tenant theme analysis; that is a different job, and its Mongo access is legacy.

## Required input

- **Date** — default **yesterday** in the site's timezone. Honor explicit dates or ranges.
- **siteId** — default the only site `list_sites` returns. If it returns more than one, ask which.

## Data shape (memorize, don't re-discover)

Read `references/gotchas.md` once per session — it holds every trap that has produced a wrong number so far.

**`list_calls`** — one cheap page per day (~130 rows on a weekday). Rows carry:
`callId, date, direction, from, to, name, contactId, answeringExtension, callDurationSeconds,
talkTimeSeconds, ringTimeSeconds, recorded, vendor, advisorIqScore, labels[], portalUrl`

- Rows do **not** carry `summary` or `hasTranscript` — those exist only on `get_call`.
- `date` has no `Z` suffix but **is UTC**. `get_call` returns the same instant with `Z`.
- `advisorIqScore` is **-1 / 0 / +1**, not a 0-100 score, and is absent on ~25% of calls.

**`get_call(callId)`** — adds `summary` (bulleted AI summary), `tags`, `hasTranscript`, `callSid`,
and renames the duration field to `durationSeconds`. When a scorecard has run it also carries
**`scorecardScore`, `scorecardMaxScore`, `scorecardTemplate`** (e.g. 115/115, "OktoRocket Inbound
Support") — the only objective quality number available; prefer it over AdvisorIQ every time.

**`get_transcript(callId, format=text|utterances|both)`** — full transcript, speaker-prefixed
`Advisor:` / `Customer:`, plus **`talkMetrics`**: `advisorSeconds`, `customerSeconds`,
`advisorWords`, `customerWords`, `advisorTalkRatio`, `advisorWordsPerMinute`.
Returns `available: false` when there is no transcript.

**`list_users(siteId, pageSize=200)`** — roster with `firstName, lastName, email, role, roleId,
status, extension, lastLogin`. Requires the `read:users` scope.

## Procedure

### Step 1 — Resolve the day and the roster
Call `list_sites` and `list_users` (parallel). Convert the target date to a UTC window using the
site timezone — America/Chicago is **UTC-5 in CDT (Mar-Nov)** and **UTC-6 in CST**. Getting this
wrong shifts the whole day by an hour and silently drops evening calls.

Build an extension -> person map, applying these rules:
- **`status` is inverted: `"0"` = active, `"1"` = disabled.** Confirm against `lastLogin` when unsure.
- **Extensions are not unique.** 8013, 8021, 8025, 8031, 8036 and 8043 have each mapped to two
  users. Pick the active user with the most recent `lastLogin`, and say in the caveats that you did.
- **`roleId` does NOT give you the technician / customer-success split** at this site — nearly
  everyone is `Advisor` (roleId 1), which is the shop-facing role name, not OktoRocket's internal
  org. Take the split from `references/team-roles.md`. Anyone missing from that file is
  `unclassified`; report them in their own row rather than guessing.

### Step 2 — Pull the day's calls
`list_calls` with the UTC window and `pageSize: 200`. The response **will exceed the token limit and
spill to a file** — that is expected and useful. Do not try to read it inline; note the path.
Page with the returned cursor until `hasMore` is false; each page spills to its own file.

### Step 3 — Compute, then list every transcript to read
Write the extension map to `map.json` (parse the first table of `references/team-roles.md`), then:

```
scripts/triage_calls.py --calls <spilled files> --map map.json --exclude-ext 8000,8008,8083,8097,8098,8765,9001,8002,8054
scripts/select_transcripts.py --calls <spilled files> --map map.json --teams Support > reads.txt
```

`triage_calls.py` gives coverage, per-team tables, at-risk contacts, dial storms — all from rows.
`select_transcripts.py` lists **every** recorded Support call with talk >= 45 s (internal, vendor and
test extensions removed). On a weekday that is 60–90 calls.

### Step 4 — Read every transcript, note each one as you go
**The daily review reads all of `reads.txt`, not a ranked sample.** Fetch `get_transcript`
(format `text`) six to eight at a time in parallel; it returns `summary`, `tags`, `advisorIqScore`
and `talkMetrics` too, so one call per transcript. After each batch, append one JSON line per call
to `notes.jsonl` before fetching the next batch — the notes are what survive when context is
summarised, and the dashboard builder reads them:

```
{"callId":"…","ext":"8039","customer":"North Roswell Automotive","issue":"new W56H handset won't register",
 "outcome":"base station ordered Aug 18 not yet delivered; call back when it arrives",
 "remote":"none|needed|partial|not_needed","ticket":"#21667|none|unknown",
 "flags":["dial-loop","no-history","dropped-request","rushing","dominating","misidentified","slow-sequencing"],
 "quote":"one verbatim line worth showing a manager, or empty"}
```

Remote verdicts: `needed` = guided install/training or a local-network fault after our own logs were
clean; `partial` = it found something but a server-side or sister-site check would have skipped it;
`not_needed` = the symptom lives on our side (ring group, registration, routing, porting config,
multi-location outage). Also flag a session started before confirming the customer had credentials.

Interpreting `talkMetrics`:
- `advisorTalkRatio` **> 0.65** — advisor dominating; **< 0.35** on a long call — passive
- `advisorWordsPerMinute` **> 180** — rushing, common on calls that end unresolved
- Prompts to read closely, never findings on their own.

### Step 4b — Match calls to Zoho Desk tickets
Desk org `841585781`, department `943174000000006907` (tools prefixed
`mcp__3a249e78-0634-4036-918c-18a7d3af06b3__`). Pull the day's tickets with `searchTickets`
using `createdTimeRange` for the same UTC window, `limit: 100`, `sortBy: -createdTime`.
**`limit` caps at 100 and `count` tells you the true total — page with `from: 100`, `200`, ...**
until you have them all. Each page spills to a file; that is fine. Then run:

```
scripts/match_tickets.py --tickets <ticket files> --calls <call files> --map map.json --teams Support
```

It prints per-rep ticketing discipline (phone tickets created vs substantive calls, and how many
inbound calls have the rep's own ticket within 2h) and the list of inbound calls nobody ticketed.

Account-name matching is unreliable: contacts are often filed under a parent org (Arch Automotive
-> "Cataca LLC (Org)", TransMedics has **no** account) or a variant spelling ("Home Town" vs
"Hometown"). Match on time + rep first; use `accountName` wildcards (`*Medics*`) or `_all` only to
confirm a specific case. Ticket text almost never records that a remote session happened (3 of 289
last week), so remote-session rate can only come from transcripts.

### Step 5 — Write the report

**1. Customers at risk** — table: `Customer | Signal | What happened | Call IDs`. Order by
severity. Ground every row in what was actually said, not just the label. A shop that called six
times, a call tagged `escalation` or `lost`, a negative-AdvisorIQ call, and a day that ended on an
unanswered callback are all different kinds of risk — say which. Name the next action.

**2. Technician performance** and **3. Customer success performance** — same structure, one section
per team from `team-roles.md`: a volume/handle-time table, then **specific** coaching observations
tied to call IDs and quoted moments. Praise what went well by name — the report is read by the
people in it. Never coach off a call under 45 seconds or off `talkMetrics` alone.

**4. Patterns for management** — the section that earns the report. Recurring product issues,
process gaps, integration or partner friction that shows up across multiple customers, staffing or
coverage gaps visible in missed-call timing. Each pattern needs at least two supporting call IDs
and a suggested owner or fix. Rank by volume x fixability, not by how alarming it sounds.

**5. Coverage & caveats** — calls analysed vs excluded, transcript and AdvisorIQ coverage,
ambiguous extension attributions, and anything that looks like test traffic.

### Step 6 — Build and republish the dashboard
Write `narrative.json` (headline; owners; per-ext `well`/`fix` with text, quote, ref; patterns;
caveats — words only, the builder computes every number), then:

```
scripts/build_dashboard.py --date YYYY-MM-DD --calls <files> --tickets <files> --map map.json \
  --notes notes.jsonl --narrative narrative.json --out daily.html
```

Optionally `scripts/export_pdf.sh daily.html Support-Desk-Daily-YYYY-MM-DD.pdf` (headless Chrome, Letter, links preserved).

Publish with the Artifact tool **to the URL in `references/dashboard.md`** (`action: read` it first,
then publish with `url:`). Same link every day; a publish without `url` makes a second page.

### Support-manager daily summary (what the dashboard contains)
One page, same day, two halves:

**Department** — calls, inbound/outbound, talk hours, missed customers who waited >=15s, tickets
opened vs closed (from Desk), open-overdue count, top 3 categories, remote-session rate, and the
two or three account arcs that need an owner tomorrow (3+ calls / 3+ people / open ticket).

**Per tech** — one block each: calls and talk time, own-ticket rate and tickets/call, Desk load,
remote sessions used / not needed, one thing they did well quoted from a transcript, one thing to
address quoted from a transcript. No block without at least one quote; no criticism without a call ID.
On a quiet day for a rep, say so rather than manufacturing a finding.

## Defaults & guardrails

- **Read-only.** Never write, amend, or resolve anything.
- Cite the **`callId` in backticks** for every claim, and the Desk **`#ticketNumber`** when one exists. Portal link:
  `https://app.digitalconcierge.io/userPortal/admin/calls?callId=<callId>` — the dashboard builder
  links every 24-hex id to it and every `#NNNNN` to the ticket's Desk `webUrl`.
- Unattributed calls (no `answeringExtension`, ~5%) get their own row — never fold them into
  someone's numbers.
- A single bad call is not a performance finding. Look for repetition across the day, or across
  several days if asked, before naming a person as a problem.
- AdvisorIQ is a weak signal with partial coverage. Use it to rank what to read, not as a score.
- If the user asks for only one section, produce only that section.
- If `list_users` returns `forbidden`, the key lost the `read:users` scope — report by extension
  number and say so, rather than silently dropping sections 2 and 3.
