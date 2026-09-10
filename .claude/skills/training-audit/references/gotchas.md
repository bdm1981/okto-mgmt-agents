# Gotchas

Every trap that has produced a wrong or unfair finding. Read before trusting a grade; add
to it when you hit a new one.

## Platform — READ THIS FIRST (9 Sep 2026)

- **Training moved off Zoom to Zoho Meeting.** The last training recording on
  `training@oktorocket.com` is 3 Sep 2026. Everything from ~8 Sep runs in Zoho Meeting, on the
  revamped weekly schedule (Advisor / Admin Part 1 / Admin Part 2 / CRM / Shop Analytics,
  ~16 sessions a week, all Central).
- **This skill is Zoom-only end to end and currently audits nothing.** Discovery returns zero
  and the run reports "no new sessions found" — a false all-clear, not a quiet day. Treat a
  zero-session run as a failure until Zoho access exists.
- **Zoho Meeting MCP connector is live** (org `zsoid` 796393835, authenticated as
  bdm@oktorocket.com, org Administrator, 12 licensed users). It exposes listMeetings,
  getAllRecordings, getSpecificRecording, getParticipantReport (real attendance, replaces the
  Zoom `attendees()` helper) and user/department reads.
- **RESOLVED: Zoho Meeting does produce transcripts.** The plan carries
  `meetingRecordingTranscription` and `revAI`; recordings return `isTranscriptGenerated: true`
  plus `transcriptionDownloadUrl`. No speech-to-text stage is needed. But transcription is
  **per-meeting, not account-wide** — several recordings show `isTranscriptionEnabled: false`,
  the same "must be on at meeting time" trap as Zoom.
- **The connector returns the transcript URL, not the text.** Fetching
  `transcriptionPublicDownloadUrl` unauthenticated returns 403, so downloading still needs a
  Zoho OAuth credential (Self Client, meeting + recording read scopes, `~/.config/okto/zoho.env`)
  driving a `zoho_client.py` alongside the MCP.
- **BLOCKER: no September 2026 sessions are visible.** Newest meeting *and* newest recording are
  both 26 Aug 2026 — not even unrecorded past meetings from September appear. An **"OktoRocket
  Training" department** exists (created by Jada, 24 Jun 2026) and everything visible has
  `departmentId: ""`, while Brad reads `departmentAdmin: false` / `isPrivilegedUser: false`
  despite being an org Administrator. The other candidate is that the sessions run as **Zoho
  Webinars** rather than Meetings — the org is webinar-licensed, the training uses registration
  language, and this connector exposes no webinar endpoints at all. Settle which before building.
- **No shared training account in Zoho.** Unlike Zoom's `training@oktorocket.com`, trainers host
  under their own logins, so the host *is* the trainer. Attribution should stop producing
  `unidentified` sessions once discovery moves over.

## Transcripts

- **Only the host is reliably transcribed.** In two of the four seed sessions the attendee
  never appears. You cannot see what the customer asked, so do not infer it — say so in the
  caveats. `compact_vtt.py` warns when it sees one speaker.
- **Attendee lines can be ambient noise.** One session transcribed a customer's shop-floor
  conversation ("It doesn't lose glass", "Same with her ABS system") as dialogue. Not a
  question, not a claim, not gradeable.
- **Timestamps drift from the recording.** VTT stamps are relative to recording start, not
  meeting start. Fine for citation, not for "N minutes in".
- **No VTT means no audit.** Transcription must have been enabled *at meeting time*.
  Retro-enabling does not backfill. Skip and note it.

## Attribution

- **The Zoom host is a shared account, so the host name is NOT the trainer.** Every session runs
  through `training@oktorocket.com`, which Zoom reports as "OktoRocket Training";
  `aaron@oktorocket.com` has no recordings of his own. Identify the trainer from the transcript
  ("My name is Aaron", usually in the first two minutes) and put *that* in the ledger.
  Attributing a session to the host name splits one person across two identities and manufactures
  a false curriculum defect the first time a claim repeats.

## Code baseline

- **Never grade against the working tree.** Always `git grep <pat> $OKTO_SHA -- <path>`.
  A feature branch checked out locally will silently grade a trainer against code that
  never shipped. `pin_baseline.sh` exists for this.
- **A claim can be right on the session date and wrong now.** The reports grade against
  current `development` and say so. When the gap matters, check both and state which.
- **SSH to github is dead on this host.** Fetch via the `gh auth git-credential` helper
  over HTTPS; `pin_baseline.sh` already does.

## The product

- **`status` on Tracker is inverted** in places, and `unread` exists but is ignored by
  `closeStaleTasks`. Read the query, not the field name.
- **`explainDelete` is inverted relative to its legacy label.** See `product-bugs.md`.
- **"On Deck" is two different things.** The approval queue, and a campaign card counter
  that is `recipients − built` (a *skip* count). Check which surface a claim is about.
  Both surfaces are live at once: `OnDeckTile.js:56` renders `approved/total` under the label
  "Messages on Deck", while `CampaignHistory.js:101` renders the skip count under "On Deck".
  A trainer describing the tile as approved-over-total is **right** — check which one is on
  screen before reusing `campaigns.on-deck.card-vs-queue`.
- **A safety toggle may not cover every task class.** Disabling a user with "close their open
  tasks" off spares shared tasks but still force-completes private ones
  (`dc-server/routes/users.js:482`). When a trainer teaches a toggle as a safeguard, check
  whether a later unconditional write undoes it — this is the "off branch" trap one level down.
- **Many features are gated to one trigger, channel or DMS.** Campaign-level scheduling is
  trigger 5 only; structured waiter/drop-off messages need SMS + trigger 5 + Tekmetric or
  Shop-Ware; review de-dup belongs to trigger 16. A generic-sounding claim usually isn't.
- **Commented-out code changes behavior.** The Rocket Gauge has 56 commented recommendation
  entries; the metrics they cover silently return "No recommendation available" and get
  filtered out of the UI. Grep for the key, then check it isn't behind `//`.
- **Feature flags look like unreleased features.** Campaign attribution and the DNI report
  ship today and are per-tenant flagged. "Not released yet" is almost always "not enabled".

## Probes and counting

- **Validate a probe regex against a loose word match before treating its absence as a finding.**
  Scanning 9 Deep Dive runs, tight patterns reported 0/9 for "holidays block booking" and
  "directly assigned tasks" — both topics actually appear in 9/9 and 6/9. A tight regex reads
  exactly like a coverage gap and would have produced a confident, wrong finding. Loose-match
  first, then tighten.
- **Zoom participant records are per-join, not per-person.** See `references/sources.md`; use
  `zoom_client.attendees()` rather than `total_records`.
- **Transcript speaker count is not attendance.** It reads 0 for sessions that had three people
  present for over an hour. Never label it "attendees".

## Ledger

- **Never re-audit a session.** Duplicate rows inflate repeat counts and turn a single
  mistake into a fake curriculum defect. `ledger.py` refuses a session it has already seen.
- **The seed rows use `seed-*` ids**, not Zoom UUIDs — the first four sessions were audited
  from local VTT files before S2S access existed. They will never collide with a real UUID.

## Scripts

- **`session_index.py --add` writes six columns into a seven-column table.** It emits
  date/uuid/course/minutes/spoke/trainer and omits `att`, so every row it appends shifts the
  trainer into the attendance column. Both 9 Sep rows had to be repaired by hand. Check the
  appended rows against the header until the script is fixed; the real attendance comes from
  `zoom_client.attendees()`, which the script never calls.
- **`fetch_transcript.py` takes `--sessions <file> --uuid <uuid>`, not `--session`.** The
  SKILL.md procedure and the scheduled-task file both write `--session <uuid>`, which exits 1
  with "give --url, or --sessions with --uuid".
- **`build_report.py` needs `--fragment` for anything going to the Artifact tool.** Without it
  the renderer emits a full `<!doctype html>` document, which the publisher wraps in a second
  head/body skeleton.
