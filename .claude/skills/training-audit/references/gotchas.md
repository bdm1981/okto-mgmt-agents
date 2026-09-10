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
- **RESOLVED 9 Sep 2026: the training sessions are Zoho WEBINARS, not Zoho Meetings.**
  Confirmed by Brad after two wrong guesses on this point — record the reasoning so it is not
  re-litigated. The Meeting API cannot see them at all: `listMeetings` returns 28 sessions with
  the newest at 26 Aug 2026, `listtype=upcoming` returns **zero** while a ~16-session-per-week
  schedule is running, and `getAllRecordings` returns 13 recordings, newest 26 Aug. None of that
  changed after adding the audit identity to the "OktoRocket Training" department, which
  **ruled department scoping out** — the department was a red herring, and the sessions being
  *filed* under a department name says nothing about which product they live in.
- **The connected Zoho Meeting MCP server is useless for this audit.** It exposes only
  meeting-scoped operations (listMeetings, getAllRecordings, getSpecificRecording,
  getParticipantReport, user/department reads). A search across every connected MCP server for
  `webinar` returns **nothing**. No amount of permission granting will surface webinars through it.
- **Webinars do carry transcripts.** The org feature set includes `webinarRecording`,
  `webinarRecordingTranscription`, `webinarLiveTranscript` and `revAI`, so the no-speech-to-text
  conclusion still holds — but it must be re-verified against a real webinar recording, since it
  was originally confirmed against *meeting* recordings.
- **Path forward: direct Zoho Webinar REST, not the MCP.** One Self Client credential solves both
  open problems at once — webinar discovery *and* transcript download (the MCP only ever returned
  a transcript URL, which 403s unauthenticated). Org `zsoid` is already known: **796393835**.
  Scope names are in the `ZohoMeeting.*` family and were not verified; Zoho rejects the whole
  list if one entry is wrong, so use the halving workaround documented in
  `dc-manager/dc-nervecenter/modules/integrations/zoho/README.md`.
- **Webinar attendance is a different endpoint from `getParticipantReport`.** Do not assume the
  Zoom `attendees()` helper ports across unchanged. Webinars distinguish *registrants* from
  *attendees*, which is richer than anything Zoom gave us — the old transcripts' "you're the only
  one registered" line was registration data all along.
- **CORRECTION — attribution is NOT solved by the move.** An earlier note here claimed trainers
  host under their own logins so the host is the trainer. That is wrong. Every training webinar
  recording is owned by **Jada Baker**, who is not the trainer — the same shared-host problem as
  Zoom's `training@oktorocket.com`, wearing a different name. Keep identifying the trainer from
  the transcript and canonicalising through `references/trainers.md`.
- **Webinar recordings live in the UI at** `/meeting/{zsoid}/{deptId}/files/my-recordings`,
  under the **Webinar** tab of the Meeting/Webinar toggle (Files → Recordings). The Meeting tab
  there shows exactly the 13 records `getAllRecordings` returns, which also **disproves the
  truncation theory** — `meta.count: 40` is not a total, and the Meeting API is complete for
  meetings. Webinars are simply a separate list it cannot reach.
- **Department is not a usable filter.** Training webinars are split across both "My Department"
  and "OktoRocket Training" with no obvious rule — today's 3 pm Admin Part 2 sits in
  "My Department" while the 9 am, 11 am and 1 pm sessions sit in "OktoRocket Training".
- **Mock/rehearsal webinars are recorded alongside real ones** and must be excluded: "Admin 2
  Mock Training - Aaron Viratos" (4 Sep), "Allie's Mock Training (1on1 w/Aaron)" (4 Sep),
  "Admin 1 Mock Training - TeDarrell Cantrell" (2 Sep), "Mock Advisor Training - Allie Gratton"
  (31 Aug). Add `mock` to the topic excludes in `references/sources.md` when discovery is rebuilt.
- **The transcript UI gives Summary / Transcript / Chapters tabs.** The transcript is timestamped
  `MM:SS` and complete — but carries **no speaker labels**, unlike Zoom's VTT. Speaker separation
  must be inferred from turn-taking, so `compact_vtt.py`'s `[mm:ss] Speaker: text` shape does not
  port directly and the "only the host is transcribed" gotcha no longer applies — the attendee is
  captured, just unlabelled.
- **Backlog as of 9 Sep 2026: six customer sessions since the Zoom cutover (3 Sep).**
  9 Sep — Admin Part 1 (9:00, 1:10), CRM Overview (10:58, 1:06), Advisor (12:57, 1:06),
  Admin Part 2 (14:58, 1:24). 8 Sep — Shop Analytics (11:25, 1:18), Admin Part 1 (14:57, 1:00).

## Zoho session identifiers and `spoke`

- **Zoho sessions are keyed by `meetingKey`** (a plain 10-digit number), recorded in the ledger's
  uuid column. Zoom UUIDs contain `/` and `==`, so the two namespaces cannot collide.
- **`spoke` is not derivable from a Zoho transcript** — there are no speaker labels, so distinct
  non-trainer speakers cannot be counted. Record `—`, and rely on `att` from
  `ZohoWebinar_getAttendeeReport`, which is richer than Zoom's anyway.
- **`session_index.py` is Zoom-shaped** (it wants `sessions.json` plus `<date>-<HHMM>.txt`
  transcripts and omits the `att` column). For Zoho runs, append index rows directly until it is
  rewritten.
- **Extracting a Zoho transcript:** open the recording page, click the Transcript tab, then
  `get_page_text` with `max_chars` well above 60000 — the default truncates a 78-minute session
  around the 60-minute mark, which looks like a complete transcript and is not. Collapse the
  `MM:SS`-then-text layout into `[mm:ss] text` cues.

## Zoho Webinar API — verified 10 Sep 2026

Connector `76bf9a32…` with Meeting + Webinar + Workdrive apps, "Authorization on Demand".
Adding tools does NOT widen an existing OAuth grant — the connector must be reconnected in
Claude so a fresh consent runs. `zsoid` **796393835**.

**Works:**
- `ZohoWebinar_getAllRecordings` — the discovery call. Returns topic, `sDate`/`startTimeinMs`,
  `durationInMins`, `meetingKey`, `isTranscriptGenerated`, `transcriptionDownloadUrl`.
  Returns 20 rows with `moreRecords: true` and **no pagination parameter** — a hard ceiling,
  fine for a 7-day window but it cannot walk history.
- `ZohoWebinar_getWebinarRecording` — per-recording detail, same URLs.
- `ZohoWebinar_getAttendeeReport` — **richer than Zoom ever was**: registered/joined/left times,
  duration, polls answered, questions asked, email, country. Replaces `zoom_client.attendees()`
  outright; no per-join dedup needed.

**Does NOT work — the one remaining gap:**
- **Transcript content is unreachable via the connector.** `ZohoWebinar_downloadRecording`
  resolves to `webinar.zoho.com` and returns a 404 HTML page; the transcript actually lives at
  `download.zoho.com/download?x-service=webinar&event-id=…`. That looks like a wrong base URL in
  the connector's spec, not a config error. The `transcriptionPublicDownloadUrl` variant on
  `files-accl.zohopublic.com` returns **403** unauthenticated (tested for both a meeting and a
  webinar recording). `workdriveResourceId` is the **MP4**, not the transcript, and the parent
  is the org-wide "General" workspace — so the transcript is not addressable as a WorkDrive file
  either. Closing this needs an OAuth bearer able to GET that URL.
- `ZohoWebinar_listWebinars` returns an empty `session` array for every listtype/index/department
  combination tried, despite recordings existing. Use `getAllRecordings` for discovery instead.

**Transcription is per-session and silently absent — but IS recoverable.** Of the six customer
sessions since the Zoom cutover, five have `isTranscriptGenerated: true` and one does **not**:
Advisor Training Wednesday 1 pm cst, 9 Sep, 66 min. **Correction to an earlier note here: this
can be backfilled.** The recording page offers a **"Generate transcript"** button when none
exists (verified 10 Sep). Zoom's "transcription must be on at meeting time, no backfill" rule
does NOT carry over to Zoho — do not write a session off as unauditable. Check the flag during
discovery and surface missing transcripts as an action, not a loss.

**Org defaults are already correct**, so a missing transcript is a per-webinar setting, not a
global one: Settings → Organization → Recording has both *Auto-record webinars* and *AI-generated
transcripts for webinar recordings* enabled. `Advisor Training Wednesday 1 pm cst` is a recurring
series with ~41 instances through 23 Jun 2027, each with its own `meetingKey`; the transcription
setting rides on the series, so one bad series silently loses a year of sessions. The API exposes
no transcription flag on the webinar record — only on recordings after the fact — so future
instances can only be checked in the UI.

**The `.txt` transcript export drops timestamps.** The in-page transcript is timestamped
(`00:23`, `00:29`, …); the downloaded file is plain prose with none. Ledger rows cite a `stamp`,
so grade from the page transcript, not the export. Neither carries speaker labels.

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
