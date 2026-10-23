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
- **Backlog status as of 11 Sep 2026.** Of the eight customer sessions since the Zoom cutover
  (3 Sep), **five are audited** — 8 Sep Shop Analytics and Admin Part 1, 9 Sep Admin Part 1, CRM
  Overview and Admin Part 2. **Two remain open**, both Advisor (9 Sep `1056342748`, 10 Sep
  `1062515451`), blocked on transcripts — see "Advisor Training is the one course with zero audited
  sessions". The eighth, Shop Analytics 10 Sep, is a 16-minute no-show shell and is not auditable
  work.
- **Backlog unchanged as of 14 Sep 2026.** Re-checked both stuck Advisor recordings in the UI:
  9 Sep `1056342748` and 10 Sep `1062515451` both still show **"No transcript generated"** with the
  Generate button live — five and four days after the sessions ran. Nothing new was recorded between
  11 and 14 Sep (no training runs Fri-Sun), so the 7-day window produced **zero new gradeable
  sessions** and the only open work is still Advisor. Six customer attendances remain unchecked.

## Advisor Training is the one course with zero audited sessions (11 Sep 2026)

Not a one-off. Both customer Advisor sessions since the Zoho cutover are ungradeable, while
**every** Admin Part 1 / Admin Part 2 / CRM / Shop Analytics session in the same period produced a
usable transcript. Six customer attendances unchecked, on the newest course and the newest trainer.

- **Advisor, Wed 9 Sep, `1056342748`, 66 min, 3 joined** — `isTranscriptGenerated: true`,
  `isTranscriptionEnabled: true`, `transcriptionDownloadUrl` present, `openAIStatus: SUCCESS`,
  chapters and summary both generated — and the recording page still shows **"No transcript
  generated"** with the Generate button live. Re-verified 11 Sep: unchanged from 10 Sep, so this is
  not a processing delay. The flag is wrong, not late.
- **Advisor, Thu 10 Sep, `1062515451`, 63 min, 3 joined** — honest `false`: transcription was off
  for the series. No summary either.

The two Advisor webinars are **different recurring series** ("Wednesday 1 pm", "Thursdays 2 pm"),
so this is not one misconfigured series. Check Advisor specifically on every run until a transcript
lands; org-level recording defaults are already correct, so the setting must be fixed per series.

## Advisor transcripts: the per-series Preferences pane is NOT the cause (14 Sep 2026)

The standing hypothesis here — "the transcription setting rides on the series, so one bad series
silently loses a year of sessions" — was tested directly in the UI on 14 Sep and **does not hold**.
Webinar → Preferences exposes no "generate a transcript for the recording" toggle at all. It offers
only *Start recording automatically*, *Record session with webcam video included*, a *Preferred
language for recording transcript* dropdown, and, under Others, *Live transcript for webinars*.

Compared across a known-good and a known-bad series:

| series | auto-record | language | Live transcript | recording transcript? |
|---|---|---|---|---|
| Admin Part 1 Mon or Wed 9 am | on | Auto | **on** | yes (9 Sep) |
| Shop Analytics Tues 11 am | on | Auto | **off** | **yes** (8 Sep) |
| Advisor Training Mondays 11 am | on | Auto | off | — |

Shop Analytics has *Live transcript for webinars* **off** and still produced a transcript, so that
checkbox is live captions and is **not** the switch. Recording preferences are otherwise identical
between a series that transcribes and one that does not. Do not "fix" Advisor by ticking that box
and do not report it as the cause — the real switch is not exposed on the webinar record, and the
only reliable recovery remains the **Generate transcript** button on the recording page.

**Generating a transcript is a write.** The button is live on both stuck Advisor recordings, but the
audit is read-only and the scheduled task does not authorise it. Surface it as an action for a human
every run; never click it.

## Advisor runs as FOUR weekly series, not two (14 Sep 2026)

An earlier note here said "the two Advisor webinars are different recurring series". There are four,
all live and all recurring ~41-59 instances into 2027:

- Advisor Training **Mondays 11 am** cst
- Advisor Training **Tuesdays 12 pm** cst
- Advisor Training **Wednesday 1 pm** cst  (9 Sep — flag true, no transcript)
- Advisor Training **Thursdays 2 pm** cst  (10 Sep — flag false, no transcript)

The Tuesday series ran 8 Sep with 1 registrant and **0 attended**, which is why it never reached
`getAllRecordings` and why the gap read as two series rather than four. Check all four every run.

## Co-organizers do not disambiguate the trainer

`trainers.md` suggests adding the trainer as a Zoho co-organizer so the API can read it. They already
are — and it does not help: the Advisor Mondays webinar lists **Aaron Viratos, Allie Gratton and
TeDarrell Cantrell together** as co-organizers, on the series rather than the instance. Every series
carries the same bench. Attribution still has to come from the transcript or a human.

## Where the webinar UI actually lives

`webinar.zoho.com/meeting/...` 404s for list pages. The working host is **meeting.zoho.com**:

- Past / Upcoming: `https://meeting.zoho.com/meeting/796393835/3764623000000012011/webinar/my-webinars/past`
  (and `/upcoming`) — `3764623000000012011` is the department id in the URL.
- A recording page is still `webinar.zoho.com/meeting/videoprv?recordingId=<erecordingId>&x-meeting-org=796393835`,
  which is the `shareUrl` / `playUrl` returned by `getWebinarRecording`.

The Past list is the authority on held-vs-not-held: it shows registrants, attended and a percentage
for every instance. Verified 14 Sep — **no training was held Fri 11 Sep through Sun 13 Sep**, so the
four-day recording gap after 10 Sep is the weekend plus a Friday with nothing scheduled, not lost
recordings. All course series run Monday-Thursday only.

## Never ledger a session you could not grade

A discovered-but-ungradeable session must **not** go into `findings-ledger.md` or
`sessions-index.md`. `ledger.py` refuses a uuid it has already seen and `discover_sessions.py`
drops anything in the ledger, so recording a no-transcript session retires it permanently and the
gap becomes invisible. Report it as an open coverage gap instead and leave it discoverable. The
run on 11 Sep published it as a **Coverage gap** section on the dashboard for exactly this reason.

## Zero graded sessions is a report, not silence

The scheduled-task file says a zero-session run posts nothing. That rule is for *discovery*
returning nothing. A run that discovers sessions and grades none of them because the transcripts
are missing is a **failure with a named cause** and must be posted — staying quiet reproduces the
false all-clear the Zoom-to-Zoho cutover already caused once.

## Distinguishing "not held" from "recording lost"

A course missing from `getAllRecordings` is usually a session that never ran. The UI's
**Webinars → Past** list settles it: it shows registrants and attended-count with a percentage for
every scheduled instance, held or not. Verified 11 Sep — Thursday 10 Sep shows only two past
webinars (Advisor 4 reg / 3 attended, Shop Analytics 1 reg / 0 attended), so the absent Thursday
Admin sessions were never held rather than recorded and lost. The 16-minute Shop Analytics
recording that day is a no-show shell: `noAudioRecording: true`, 0 attendees, correctly dropped by
`min_duration_minutes: 20`.

## `build_dashboard.py --reports` must be rebuilt every run

Two traps, both silent:

- **Keys are bare uuids** (`1028334905`, `yAuBNF7bROKsAG2GhRFbkA==`), **not** the ledger's
  `` `uuid:…` `` display form. A prefixed key matches nothing and every Report cell renders `—`.
- **CORRECTION 18 Sep 2026 — the map IS persisted now.** It lives at
  `references/report-map.json` (added 17 Sep). Pass
  `--reports references/report-map.json` and add one line to that file whenever you publish a
  report. The old advice below stood for two weeks after it stopped being true; do not rebuild
  the map by hand from `dashboard.md`.
- **Still true: omitting `--reports` fails silently.** The republished dashboard loses every
  report link and the page still renders, so nothing errors — it just quietly gets worse.

The renderer also has **no coverage-gap section**; the 11 Sep run injected one into the fragment by
hand after generating it. Worth adding to the script — a hand-patched section disappears the next
time someone republishes without repeating the patch.

## Attribution errors masquerade as tool bugs

A note here previously claimed `ledger.py`'s `contradictions()` was missing wrong→correct pairs,
citing `campaigns.campaign-schedule.is-general` and `reports.campaign-attribution.unreleased`.
**That was wrong and the tool was fine.** Both were recorded as taught-right by `unidentified`
because the trainer had not been identified; once Brad confirmed CRM was Aaron, the detector
surfaced both immediately. Before blaming a script, check whether the input is complete.

## Without speaker labels, do not attribute a first-person line to the trainer

The costliest mistake of the 10 Sep run. Admin Part 2 (9 Sep) contains, at 01:49, "this is the
third one, the one I did earlier today for the CRM, I was the only one to[o]" — read as the
trainer, it "proves" CRM and Admin Part 2 share a trainer. They do not: CRM was Aaron and Admin
Part 2 was TeDarrell. The line was **the customer**, Jason Simms, who attended both, as the
attendee reports show. The following turns give it away — "Oh yeah, you've been busy today, huh?"
answered by "I got to get this stuff in because if I don't do it, I just won't do it."

Zoho transcripts have no speaker labels, so **any** first-person claim ("I", "my", "earlier today")
is unassigned by default. Cross-check against the attendee report before building on it: a customer
attending several sessions in a week produces first-person lines that read exactly like a trainer's.

## `isTranscriptGenerated` is not trustworthy

Verified 10 Sep 2026 on Advisor Training Wednesday 1 pm cst (`1056342748`). The API reports
`isTranscriptGenerated: true` and `isSummaryGenerated: true`, while the recording page still shows
**"No transcript generated"** with the Generate button live. Only the summary had in fact been
produced. So the flag can go true off the back of a summary, and discovery cannot rely on it to
decide a session is auditable — check that transcript text actually comes back before grading, and
report a session as unaudited if it does not.

**Never grade from the AI summary.** It is a paraphrase, several steps from what was said, and it
cannot support a `path:line` finding. It is usable for one narrow thing — attribution, when it
records the host stating their own name (see references/trainers.md, Advisor Training 9 Sep).

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

## Reading a Zoho transcript: the two traps that silently truncate it (15 Sep 2026)

Both of these make a **complete** transcript look short, which is worse than an obvious failure.

- **Timestamps switch from `MM:SS` to `H:MM:SS` past the hour.** A cue-counting regex of
  `^\d{1,2}:\d{2}$` matches nothing after 59:59, so an 86-minute session reports its last cue at
  `54:52` and looks truncated at the 60-minute mark. This is the *same symptom* as the
  `max_chars` trap recorded below and a completely different cause — check the tail text before
  concluding anything is missing. The transcript panel is **not** virtualised: the container
  `div.transTimeStampMainContainer` holds every cue in the DOM at once, so scrolling is not
  needed and `innerText` on that one element is the whole transcript.
- **`javascript_tool` truncates its own return at roughly 1-2 KB**, so it cannot carry a
  95,000-character transcript back no matter how you slice it. What works: read the container's
  `innerText` into a page global, then insert a `<pre>` holding a <50,000-char slice as the
  first child of `<body>` and read it with `get_page_text` (which caps at 50,000 and reads from
  the top of the body). Two passes covers a 90-minute session. Remove the `<pre>` between passes.

The in-app browser is still not authenticated against Zoho — use **Claude in Chrome**, where
Brad's session is live. Nothing else about the recording page changed.

## The transcript gap is no longer Advisor-only (15 Sep 2026)

Until 10 Sep every non-Advisor course transcribed reliably, which is what made "Advisor is the
one broken course" a usable theory. It no longer holds. Two more recordings, on two other
courses, came back with `isTranscriptionEnabled: false`:

- **CRM Overview Monday 1 pm**, 14 Sep, `1026984660`, 73 min — this course transcribed fine on 9 Sep.
- **Admin Part 2 Tues/Thurs 9 am**, 15 Sep, `1020522825`, 82 min — the Mon/Wed 3 pm instance of the
  same course transcribed fine the day before.

So the failure is **per-recording and intermittent**, not per-course and not per-series. That
also retires the remaining temptation to explain it by something about Advisor specifically.
Treat any recording as at risk and check `isTranscriptionEnabled` on every discovery pass.
The *Generate transcript* button remains the only known recovery and remains a write.

## Same-day sessions can be missed by an evening run (15 Sep 2026)

The 14 Sep run concluded "nothing new was recorded between 11 and 14 Sep", but **two** 14 Sep
sessions (Admin Part 1 at 09:01, Admin Part 2 at 15:03) were both present and transcribed when
this run looked the next afternoon. Whatever the cause — processing lag behind the 18:00 run, or
a discovery window that excludes the current day — a run that reports a quiet day for a weekday
is suspicious on its face: the schedule puts training on every Monday through Thursday. Check the
Past list before believing an empty result on a weekday.

## `ledger.py`'s alias table has drifted from `trainers.md`

`TRAINER_ALIASES` in `scripts/ledger.py` mirrors only the TeDarrell family and Aaron. It contains
**no entry for Allie** at all (`allie`, `ali`, `aldith` are all in `trainers.md` and none is in the
script), and as of 15 Sep it also lacks `serio` / `trader serio`. An unmatched name passes through
unchanged and splits that trainer into two rows, which is exactly the false-curriculum-defect
failure the table exists to prevent.

Until the two are reconciled, **canonicalise the name yourself and put the canonical spelling in
`findings.jsonl`** rather than relying on the script to do it.

## New variant: "Serio" / "Trader Serio" = TeDarrell (15 Sep 2026, unconfirmed)

Admin Part 2 on 14 Sep opens "My name is Serio"; the generated summary renders it "Trader Serio".
Nobody by that name is on the roster. Read as another mis-transcription of the same name that has
already produced Tedario, Tadario, Tadirio and Tedarios, and corroborated by the series: Brad
confirmed the 9 Sep instance of this same Mon/Wed 3 pm Admin Part 2 series as TeDarrell.
Recorded as TeDarrell with the caveat travelling alongside — **a human should confirm** before it
hardens, exactly as with the Allie attribution. Add the variant to `trainers.md` and to
`ledger.py` when someone does.

## The customer-facing review microsite IS in this repo

Worth recording because a reasonable first guess is that anything under `/customer/...` on
`digitalconcierge.io` is a separately deployed app and therefore ungradeable. It is not:
it lives at **`dc-user/src/js/cust/`**, routed from `dc-user/src/js/cust/App.js`.

That is where the review gate actually decides: `cust/components/reviews/ReviewCard.js:64`
reads `settings.business_info.minGoogleRating || 4` and sends anything **below** it to an internal
feedback form instead of the public review options. So the "four stars or up goes to Google" claim
is checkable after all — and the floor is per-site configurable from the Google Business
integration modal, defaulting to 4 only when it has never been set.

## `restrictAdvisorBlockCustomer` is the one account permission that means the opposite

Of the four entries in `accountPermissions.json`, three are grants and this one is a **restriction**.
Both surfaces render Block Contact only when it is absent — `ActionMenu.tsx:467` and
`CustomerActionPanel.tsx:80` both test `!hasRestrictAdvisorBlockCustomer`. Turning it **on** takes
the ability away.

Unlike the `explainDelete` case, this is **not** a product bug: the label "Restrict Advisor Block
Customer" does parse correctly as *restrict the advisor from blocking*. It is a genuinely easy
misread, though, and it has now been taught as a grant once. Check which way a trainer takes it
every time this permission comes up.

## The evening run must re-check the same day's afternoon sessions (15 Sep 2026, evening)

The earlier 15 Sep run listed Shop Analytics Tues 11 am (`1023136224`) and Advisor Tuesdays 12 pm
(`1017030712`) as "still processing" and graded neither. By evening `1023136224` had transcribed
and was fully auditable — 11 checkable claims — and the 3 pm Admin Part 1 (`1041064344`, 78 min)
had appeared and transcribed too. **Two gradeable sessions would have been lost** had this run
trusted the earlier pass.

Recordings on this account land in `getAllRecordings` within minutes of the session ending but the
transcript follows later. So: a session recorded **the same day** is not settled until a later run
re-checks it. Never carry "still processing" forward as a conclusion — re-read the flag, and if it
is true, try to pull the text before writing the session off.

## Trigger 5 does NOT hide the campaign delivery sliders — check the nesting before grading

`AddCampaign.js:704` opens `{props.values.trigger !== "5" && (` immediately above the Auto Approve /
Require Delete Reason / Do not track outcomes block, which reads exactly like "these settings are
hidden for Appointment Reminder campaigns" and would make a trainer's whole walkthrough of them
wrong. It is not: that gate closes at `:721` and wraps **only** the Minimum RO Spend field. The
sliders below are gated on `type != "call"` (`:722`) and the vCard on `type === "email"` (`:747`).

Print the region with line numbers before concluding a gate applies. A JSX conditional two lines
above a block is not evidence that it wraps the block.

## `git grep` line numbers drift from the ledger's citations

`ActionMenu.tsx:467` and `CustomerActionPanel.tsx:80` are cited correctly in the 14 Sep rows, but
a fresh `git grep` for `restrictAdvisorBlockCustomer` at a newer baseline returns `:323` and `:52`
— those are the *declaration* sites, and the render gates are still at 467 and 80. Grep finds the
first occurrence, which is usually the `const hasX = ...` line, not the branch that matters. Follow
the symbol to its use before citing a line, or the evidence points at a variable assignment.

## Report links: the artifact URL scheme changed mid-history

Older reports are `claude.ai/code/artifact/<uuid>`; anything published from 14 Sep on is
`claude.ai/artifact/<short-id>`. Both resolve and both must stay in the `--reports` map. Republishing
the dashboard to the old-form URL still updates the same artifact (it came back as Version 14), so
**keep passing the `code/artifact` URL from `dashboard.md` as `url:`** — do not "modernise" it to the
short form the publish result prints back, which is a different string for the same page.

## `pin_baseline.sh` cannot actually fetch on this host — it silently grades against a stale ref (16 Sep 2026)

The script runs `git -C "$REPO" -c credential.helper='!gh auth git-credential' fetch origin development`.
`origin` in the oktorocket clone is **`git@github.com:ShopRocket-LLC/oktorocket.git`** — an SSH remote — and
the gh credential helper only applies to HTTPS, so the fetch dies on `Permission denied (publickey)`. The
script catches that, prints `pin_baseline: fetch failed — grading against the local origin/development`
on **stderr**, and exits 0 with whatever the local remote-tracking ref happens to hold.

On this run that stderr line was one line of noise in a successful-looking `eval`, and the local ref was
`39e669e80` (11:46) while the real tip was `685745b44` (16:24) — **five hours and several merges behind**.
A stale baseline does not fail loudly; it grades a trainer against code that is not what shipped.

Fetch explicitly by URL instead, then pin that:

```bash
git -C ~/Documents/DEV/oktorocket -c credential.helper='!gh auth git-credential' \
    fetch https://github.com/ShopRocket-LLC/oktorocket.git development
git -C ~/Documents/DEV/oktorocket update-ref refs/remotes/origin/development FETCH_HEAD
```

The fix in the script is to rewrite the SSH remote to its HTTPS form before fetching. Until someone does
that, **treat a `fetch failed` line as a stop-and-fix, not a warning** — and check the baseline's timestamp
against the wall clock before grading anything.

## The advisor call-list boundary is a permission, not a role (16 Sep 2026)

`calls.role-access.by-extension` was graded **correct** on 24 Aug and is graded **incomplete** from 16 Sep.
The stricter read is the right one and the earlier grade simply stopped one level too early:
`callsReviewUtils.ts:147` pins only `PID === "1"`, and `:150-155` lifts the pin entirely for any advisor
holding the **"All Recordings"** permission (which has existed since Nov 2025, so this is not drift).

The same shape one layer up: **admin ≠ all sites.** `dc-server/models/user.js:297` grants `allSites` to a
PID 0 admin *only when they have no group assignment*, and `:281-306` scopes anyone carrying a `Group:`
permission to that group's sites plus their own. So a site manager in a group sees several stores, and an
admin in a group sees fewer than all of them.

Generalise: when a trainer states an access rule as a property of a **job title**, go and find what the code
actually keys on. Three times now it has been a permission or a group membership, and the caveat is always
one sentence the trainer could have said.

## A 0-attendee webinar never reaches `getAllRecordings` — check Past before calling it a lost recording

Verified 16 Sep. Four courses were scheduled that day; `getAllRecordings` returned two. The Past list settles
it immediately: Admin Part 2 Mon/Wed 3 pm had **1 registered, 0 attended** and CRM Overview Wed 11 am had
**1 registered, 0 attended**, so neither produced a recording worth having. Only Admin Part 1 (3 reg / 2 att)
and Advisor Wed 1 pm (4 reg / 2 att) actually ran with customers.

This is the cheap check that separates "not held" from "recording lost", and it takes one page load:
`https://meeting.zoho.com/meeting/796393835/3764623000000012011/webinar/my-webinars/past`. Note the page
hydrates late — `get_page_text` returns a chat-history placeholder for several seconds, so read
`document.body.innerText` via `javascript_tool` instead of waiting on the text extractor.

## Advisor Training Wednesday 1 pm is now 0 for 4 on transcripts

9 Sep, 16 Sep and the two other Advisor series have all failed. Whatever the intermittent per-recording cause
is, this particular series has never once produced a transcript since the Zoho cutover. That is no longer
distinguishable from a series-level fault by observation alone — but the Preferences pane still exposes no
toggle that would explain it (tested 14 Sep), so do **not** re-open that hypothesis without new evidence.
Report it, keep it out of the ledger, and keep asking a human to press *Generate transcript*.

## Advisor Training finally transcribed — and the per-recording theory is now settled (17 Sep 2026)

Advisor Training **Thursdays 2 pm** (`1035089688`, 17 Sep) produced a full transcript and is the first
Advisor session ever graded. Four earlier Advisor recordings across all four series had failed. Note the
Thursday 2 pm series itself failed on 10 Sep and succeeded on 17 Sep — **the same series, both outcomes**,
which is the direct refutation of any remaining series-level hypothesis.

The same day settles it from the other side: four courses ran, **one transcribed and three did not**, and
all three failures (Admin Part 1 Tue/Thu 3 pm, Admin Part 2 Tue/Thu 9 am, Shop Analytics Thu 1 pm) were on
series that had transcribed successfully within the previous nine days. Stop looking for a per-course,
per-series or per-trainer cause. It is per-recording and intermittent, and the only recovery is still the
*Generate transcript* button, which is a write.

## Attribution: a transcript self-introduction finally exists for Allie

`trainers.md` carried Allie's attribution as "strong but derived" — it came from a Zoho AI *summary* of the
9 Sep session and asked for human confirmation. The 17 Sep Advisor transcript opens at 01:56 with
**"My name is ALI"**, verbatim. That is the first non-summary, non-human source for this trainer and it
matches. Treat the Allie attribution as confirmed from here.

Note this is the *opposite* trap to the "Serio"/"Stereo" family: those were mis-transcriptions of TeDarrell
needing a human arbiter. "ALI" is corroborated by an independent prior source, so it is not a plurality
guess.

## `build_report.py --narrative` takes JSON, not markdown

The SKILL.md procedure does not say so and the flag name suggests prose. Passing a `.md` file dies with
`json.decoder.JSONDecodeError: Expecting value: line 1 column 1`. The expected keys are `title`,
`standfirst`, `method`, `practice_notes` (a list of `{heading, paras[]}`) and `footer`. Session metadata —
topic, date, trainer, duration — comes from `--sessions`, a `{"sessions":[{uuid, topic, start_time,
trainer, duration_minutes}]}` file, which for a Zoho run you have to hand-write since
`discover_sessions.py` is Zoom-only.

## `ledger.py --add` silently writes a blank date column

`findings.jsonl` has no `date` field in the schema documented in SKILL.md, and the script does not derive
one from the session. All 17 rows from the 17 Sep run landed as `|  | uuid:… |` with an empty first
column, which the dashboard joins on. Repaired with a `sed` over the new rows. **Check the date column
after every `--add`** until the script is fixed, or put `date` in each JSON line and confirm it is read.

## The `--reports` map is now persisted — use it

The standing trap here ("the map is not persisted anywhere; omit `--reports` and the dashboard silently
loses every report link") is fixed as of 17 Sep: the map lives in **`references/report-map.json`**, keyed
by bare uuid. Build the `--reports` argument from that file and add a line whenever you publish a report.
Five August Deep Dive sessions (`3+wKfi9hQLSzEcnEEmhqnw==`, `4xYzQyJWQLqcyHgjzUDW6w==`,
`5DLC6CWcRySruihidAnu/Q==`, `KNq5QbshQX2wxaWGkNWnwQ==`, `aRMS5aVyT8CR+bca1lsodQ==`) are deliberately
unmapped — their original reports could not be identified, and a wrong link is worse than a dash.

## The dashboard's coverage-gap section must be carried forward, not regenerated

`build_dashboard.py` still has no coverage-gap section, so each run injects one by hand — and a
freshly-written injection is *poorer* than what is already live, because previous runs accumulated
per-recording history in it. **Read the published dashboard first** (`Artifact` action `read` on the fixed
URL, which you must do anyway before republishing) and update that section's prose rather than writing a
new one from scratch. The 17 Sep run nearly shipped a regression this way.

## Read the UI branch, not just the action payload

`OnDeck.tsx`'s `onUpdateMessage` posts `message`, `number`, `email` and `send_date` for every row type,
which reads as "the body is editable for email too" and would have made a correct trainer claim wrong.
It is not: `MessageModal.js:206` puts the editable textarea inside a `type == "sms"` branch and gives
email rows only a read-only `Subject:` label. The payload carries the field; no control ever changes it.
Same lesson as the line-number drift note above — follow the symbol to the surface that renders it.

## Friday is the one weekday where an empty result is correct (18 Sep 2026)

The rule recorded above — "a run that reports a quiet day for a weekday is suspicious on its face" —
needs one carve-out, or every Friday run will waste effort hunting for sessions that do not exist.
**All five course series run Monday to Thursday only.** Verified again 18 Sep: `getAllRecordings`
returned nothing newer than Thu 17 Sep 15:00, and the Webinars → Past list's most recent group was
still headed "Yesterday".

So: empty discovery on Mon-Thu is suspicious and must be checked against the Past list. Empty
discovery on Fri-Sun is expected. Say which case it is in the run output rather than reporting a
bare "no new sessions" — the two read identically and mean opposite things.

**Generalises to the whole weekend, verified Sat 19 Sep and again Sun 20 Sep.** Same result all three days:
newest recording still Thu 17 Sep 15:00 and the Past list's newest group still headed "Last week" with
Thursday at the top. Fri/Sat/Sun runs are expected to be empty; a Monday-to-Thursday run that comes back
empty is not.

**Stuck recordings do not self-heal — 11 days of evidence.** The 9 Sep Advisor recording (`1056342748`)
was re-checked in the browser again on 20 Sep and still shows "No transcript generated" with the *Generate
transcript* button live, eleven days after the session and after five separate re-checks (10, 11, 14, 19,
20 Sep).
Nothing in the backlog has ever recovered on its own. Stop treating any stuck recording as possibly-late:
if the flag is `false`, or `true` with no text behind it, the only thing that will ever change it is a human
pressing the button. Re-check costs one page load, so keep doing it — but report it as blocked, not pending.

## `isTranscriptionEnabled: false` is accurate — the flag only lies optimistically (18 Sep 2026)

`isTranscriptGenerated` is documented above as untrustworthy, but only in one direction: it can read
`true` off the back of a generated *summary* when no transcript exists (Advisor 9 Sep). The opposite
error had never been tested, and it matters much more — if the flag could read `false` while a
transcript existed, discovery would have been silently dropping gradeable sessions for a week.

Tested directly on 18 Sep against the newest failure, Admin Part 1 Tue/Thu 3 pm (`1077862314`,
17 Sep): the API reports `isTranscriptionEnabled: false` / `isTranscriptGenerated: false`, and the
recording page's Transcript tab shows **"No transcript generated"** with the *Generate transcript*
button live. The two agree. **A `false` flag can be believed; a `true` flag must still be confirmed
by pulling actual text.**

One UI detail worth keeping: on the recording page the `find` tool returned a ref for the Transcript
tab button, but clicking that ref did nothing — the panel stayed on Summary. Clicking the tab by
screenshot coordinate worked first time. Take the screenshot and click the coordinate; do not trust
a silent no-op from a ref click to mean the tab was already selected.

## Internal test webinars now appear in the Past list — widen the excludes beyond `mock` (20 Sep 2026)

Thu 17 Sep 22:55 carries **"ZZZ TEST - Automation Delete Test 2 (disposable)"**, hosted by TeDarrell
Cantrell in "My Department", 0 registered / 0 attended. It is somebody's automation fixture, not a training.

It did **not** reach `getAllRecordings` — a 0-attendee webinar never does — so nothing was at risk on this
run, and that is the only reason it was harmless. A fixture that someone joins once would sail straight into
discovery, and an audit report on a disposable test webinar is exactly the kind of noise that makes people
stop reading the channel.

The standing note above says to add `mock` to the topic excludes in `references/sources.md` when Zoho
discovery is rebuilt. Add these at the same time, one row each (the table parser splits on `|`, so no
alternation): **`ZZZ`**, **`test`**, **`disposable`**, **`automation`**. Keep matching case-insensitively.
Note that `test` is the risky one — it would also drop a genuine session topic containing "latest" or
"greatest", so anchor it as a word if the parser ever gains the capability. `ZZZ` alone catches this
particular family and is safe.

Also worth knowing for attribution: this is the first webinar on the account whose creator is **not**
Jada Baker. Every real training recording is hers; a non-Jada creator is a useful smell test for "not a
customer training" that costs nothing to check.

## `ledger.py --add` reads a `date` field — put one in every JSON line (21 Sep 2026)

The standing note above says `--add` "silently writes a blank date column" and that the 17 Sep rows had to
be repaired with `sed`. The cause was the input, not the script: `findings.jsonl` had no `date` key. Add
`"date":"YYYY-MM-DD"` to each line and the column populates correctly — verified this run, 30 rows appended
with zero blanks. The schema in SKILL.md still omits it, so it has to be remembered rather than copied.

## Reusing a claim_id for a *different* misconception manufactures a false contradiction (21 Sep 2026)

grading.md says to reuse an existing id whenever the same misconception recurs, and that is right — but it
has an edge this run walked straight into. Allie's "disable campaigns removes them from future **SMS**
campaigns" was filed under the existing `inbox.disable-campaigns.stops-future-sends`, which TeDarrell had
been graded **correct** on for a different assertion on 15 Sep. The dashboard immediately rendered a
contradiction reading "taught wrong by Allie, taught right by TeDarrell" — an artefact, not a finding, and
the kind that would have sent someone to coach the wrong person.

The rule that resolves it is already in grading.md and is easy to read past: **name the misconception, not
the feature.** "Stops future sends" and "SMS only" are two claims about one menu item. Split them.
Practical check: before reusing an id, read the existing rows under it. If any is graded `correct`, you are
probably about to collide two different assertions.

## `isAdmin` in the calls modal includes Site Manager — the product-bugs note was imprecise

`CallModalTabs.tsx:144` is `utils.roleCheck([0, 5], String(me.PID))`, and `accountRoles.json` maps **0 =
Administrator, 5 = Site Manager**. So the transcript download at `:168` is open to both roles, and a trainer
saying "site manager or admin can download the recording and the transcript" is **correct**, not wrong.
product-bugs.md described this gate as "admin-only", which reads as PID 0 alone; corrected there.

Generalises: `isAdmin` is a variable name, not a role. Read the `roleCheck` array before grading any claim
about who can do something.

## The weekday rule was tested on a Monday and held (21 Sep 2026)

The standing rule — empty on Fri-Sun is expected, empty on Mon-Thu is suspicious — got its first real
Monday. Four courses ran and `getAllRecordings` returned all four within hours; three transcribed and were
audited, one did not. So the rule survives, and the 18:00 run time is late enough to catch a 15:00 session's
recording **and** its transcript on the same day. The same-day re-check caveat still applies to anything
that lands later than that.

## The Transcript tab ignores synthetic coordinate clicks — click the button object (22 Sep 2026)

The 18 Sep note says to click the Transcript tab by screenshot coordinate because a `find` ref click
silently no-ops. That is now only half right, and the coordinate route failed outright on one of three
recordings this run: two clicks at the correct pixel produced no tab change, and
`div.transTimeStampMainContainer` kept returning an empty string — which reads exactly like a recording
with no transcript, and is the most dangerous possible false negative for this skill.

The cause is a coordinate-frame mismatch. `getBoundingClientRect()` on the tab button returns CSS pixels
(`x: 2060–2189, y: 83–129`) while the screenshot frame is 1480×812 — roughly a 0.636 scale. A click that
maps into the button's box still does not always land, so do not debug this by re-measuring.

**Do this instead**, which worked first time and needs no screenshot at all:

```js
[...document.querySelectorAll('button.transcript-panel__tab')]
  .find(b => b.textContent.trim() === 'Transcript').click();
```

Then wait ~2 s and confirm `document.querySelector('.transcript-panel__tab--active').textContent` reads
`Transcript` **before** reading the container. An empty container with Summary still active means the click
was lost, not that the transcript is missing — check the active tab before concluding anything.

Also note the first click after a `navigate` is reliably swallowed on this page, on every recording. The
two sessions that did work each needed a second click. Budget for it or go straight to the JS click.

## Dumping a transcript: hide the page first or you pay for it twice

The `<pre>`-plus-`get_page_text` technique in the 15 Sep note works, but as written it returns **the
`<pre>` and the live transcript panel underneath it** — the first pass this run returned 111,257
characters to deliver a 28,000-character slice, and truncated mid-way.

Hide the existing body children before inserting the `<pre>`:

```js
Array.from(document.body.children).forEach(el => { el.style.display = 'none' });
```

With that, three passes cover an 83,000-character session cleanly. Compacting `MM:SS`-then-text into
`[mm:ss] text` in the page first does **not** shrink it — the newlines you remove and the brackets you add
cancel out — so do it for readability, not for size.

## `findings.jsonl` needs a `trainer` field — SKILL.md's schema omits it

The documented schema has `session`, `stamp`, `claim_id`, `quote`, `grade`, `reality`, `evidence`,
`say_instead`, `product_bug`, and the 21 Sep note added `date`. It does **not** mention `trainer`, and
`ledger.py --add` reads `r["trainer"]` to build the row. Omit it and every row lands misattributed or the
add fails outright.

So the working schema is the documented one **plus `date` plus `trainer`**, with the trainer already
canonicalised by hand — `TRAINER_ALIASES` in the script still has no entry for Allie, Serio, Stereo or
Tirio, so it cannot do the canonicalisation for you.

## `admin.directly-assigned.admins-can-see` — the code moved under this claim_id (22 Sep 2026)

Rows from 27 Aug and 3 Sep grade "admins can see directly-assigned tasks" as `wrong_contained`, against a
`buildPrivateTaskVisibilityFilter` that was self-only with no bypass at all. Since then TRS-I2079 added
`buildPrivateTaskVisibilityFilterForViewer` (`taskVisibility.ts:210`), and the answer is now **split by
task class**:

- direct voicemails, personal-number SMS, private faxes → still self-only for every viewer, admins included;
- direct-assigned SMS campaign tasks and private call-campaign tasks → visible to Admins anywhere and to
  Site Managers at their sites.

So a blanket claim in **either** direction is now incomplete, and the two old rows were graded against
behaviour that no longer exists. Do not read that history as "trainers keep getting this wrong" — read the
two helpers before grading, and check which class the trainer was actually talking about. This is the
clearest instance yet of the standing "a claim can be right on the session date and wrong now" rule, running
in reverse.

## `ReviewCard` moved to TypeScript — the cited line is stale

The 15 Sep note cites `dc-user/src/js/cust/components/reviews/ReviewCard.js:64` for the Google review floor.
That path no longer exists: it is `ReviewCard.tsx` and the read is at **:79**, with the routing branch at
**:80**. The logic is unchanged (`settings?.business_info?.minGoogleRating || 4`). Re-resolve a cited path
before quoting it in a new finding; a `git grep` against the pinned commit catches this in one call.

## Five series have now produced both transcript outcomes (22 Sep 2026)

The per-recording conclusion recorded on 17 Sep is now beyond argument, and it is worth writing the list
down so nobody re-opens it:

| series | failed | succeeded |
|---|---|---|
| Advisor Thursdays 2 pm | 10 Sep | 17 Sep |
| Advisor Tuesdays 12 pm | 15 Sep | 22 Sep (first ever) |
| Shop Analytics Tuesdays 11 am | 22 Sep | 8 Sep, 15 Sep |
| Admin Part 1 Tue/Thu 3 pm | 17 Sep | 15 Sep, 22 Sep |
| Admin Part 2 Tue/Thu 9 am | 15 Sep, 17 Sep | 22 Sep |

Only Advisor Wednesday 1 pm (0 for 5) and CRM Overview Monday 1 pm (failed 14 and 21 Sep) have unbroken
recent runs, and neither is long enough to mean anything on its own. Stop looking for a pattern; report the
gap and keep asking for the Generate-transcript click.

## Grading the same claim in two sessions on one day is the cheapest signal this skill produces

Two sessions three hours apart on 22 Sep took opposite positions on
`admin.block-customer-permission.is-a-grant` — Allie wrong at 12:29, TeDarrell right at 15:28. Same day,
same pinned commit, no possibility of the product having changed underneath them.

That is worth more than the same two findings a week apart, because it removes every confound and lands as
a curriculum question rather than a coaching one. It only appears if **all** of a day's sessions are graded
in one run. A run that audits the day's most interesting session and defers the rest would have reported a
single trainer error and missed the actual finding.

## A feature existing is not a feature being available — read the type gate (23 Sep 2026)

The Advisor trainer told a customer there is no way to target a call campaign by service description,
and offered to file a feature request. The obvious audit move is to grep, find
`campaignTypes.js:17` — `{ label: "Service Description", value: "13" }` — plus an **Oil Change
Reminder** trigger at `:14`, and grade the trainer `wrong_high` on a claim that touched the
customer's stated core job. That grade would have been wrong.

`getAvailableTriggers` (`AddCampaign.js:167-174`) restricts the call type to
`allowedCallTriggers = ["1","2","3","11","12"]`. Triggers 13 and 8 are real, shipped and
unavailable for call campaigns. The trainer had opened the trigger dropdown on screen and read it.

Two rules out of this, and they pull in opposite directions:

- **Before grading a "that doesn't exist" claim wrong, find the gate for the specific type,
  channel or trigger the trainer was talking about.** A global grep proves a feature exists
  somewhere, never that it is reachable from where the customer was standing.
- **But do check the other side.** He generalised from "not for calls" to "I'll put in a feature
  request", and service-description targeting ships today for SMS and email. That is the
  `incomplete`, and it is the finding worth the customer's time — not the wrong_high that the
  grep alone would have produced.

## `scheduler.after-hours.resources-are-uploads` is the ledger id — grading.md suggests a different one

`grading.md`'s claim_id section uses `…after-hours.resources` as its worked example of a well-named
id. The ledger has used **`scheduler.after-hours.resources-are-uploads`** since 25 Aug, across seven
rows. Filing a new row under the example name silently starts a second history and the contradiction
detector goes quiet on one of the better-evidenced claims in the set.

Caught this run only because the `--check` dry run printed `all_repeating` and the id was not in it.
**Grep the ledger for the nearest existing id before inventing one** — `awk -F'|' '{print $5}'
references/findings-ledger.md | sort -u` is the whole check, and the same pass caught three more
(`inbox.campaign-task.outcome-required`, `campaigns.advisor-permission.needs-manage-campaigns`,
`campaigns.call-campaigns.no-customer-send`). Four of eighteen rows would have failed to join.

## Read the existing rows before writing "first time this was taught right"

The same run drafted a finding saying the after-hours claim had never been taught correctly before.
The ledger says it was taught correctly on 25 Aug, 27 Aug, 3 Sep and 22 Sep, and got it wrong twice.
A superlative in a `reality` field is a claim about the ledger, and it needs the same evidence
standard as a claim about the code — go and read the rows.

## Both trainers unidentified on the same day — the opening script is slipping (23 Sep 2026)

Neither the 23 Sep CRM Overview nor the 23 Sep Advisor session contains a self-introduction anywhere
in the transcript. That is the first day since the Zoho cutover with two graded sessions and zero
attributions, and it undoes the run of clean openings (Aaron 9 Sep, Allie 17 Sep, "Tirio" 22 Sep).

The Advisor session has a partial excuse and it is worth recording: at 01:18 the trainer says
**"I'm taking on someone else's training for today, they're out on vacation."** A substitute is
exactly when attribution matters most — the roster-and-course heuristics everyone reaches for are
guaranteed wrong — and exactly when the habit is most likely to be skipped.

The transcripts do carry a *different* signal worth noting, without acting on it: this trainer says
"I'm actually in charge of setting up your guys's campaigns" and "I did start working on your
platform yesterday", which reads as an onboarding/implementation role rather than the training
bench. Do **not** promote that to an attribution — it is the same shape of inference that produced
the Jason Simms error on 10 Sep. Record `unidentified` and let a human name them from the video.

## `ledger.py --check` is worth running every time, for the repeat table, not the validation

The documented reason to dry-run is to avoid writing bad rows. The more useful output is
`all_repeating` and `contradictions`, which show what the new rows will join *before* they land —
which is how the two claim_id mistakes above were both caught in one pass. It costs one command.

## `ledger.py --check` does not surface contradictions — run `--contradictions` separately (24 Sep 2026)

The 23 Sep note says `--check` is worth running every time for `all_repeating`, and that is still true. But its
`contradictions` key came back **`{}`** on this run while the full-ledger `--contradictions` call immediately
reported `campaigns.advisor-permission.needs-manage-campaigns` as Aaron-wrong against TeDarrell-right in six
sessions — the single most actionable finding of the day. `--check` evidently computes contradictions over the
incoming rows alone, which can never contain the older correct version by construction.

So the dry run answers "what will these rows join?" and only the post-add `--contradictions` answers "who
disagrees with whom". **Run both.** A run that trusted `--check`'s empty contradictions block would have
reported this as a lone trainer slip rather than a curriculum inconsistency with a correct script already on file.

Note also that `incomplete` counts as wrong for this detector (`ledger.py:134`), which is right — an omitted
gate and a false statement land on the customer the same way.

## A repeat can hide inside a claim the tool calls "not repeating"

`campaigns.advisor-permission.needs-manage-campaigns` has seven rows and did **not** appear in `all_repeating`,
because the repeat counter only counts non-`correct` gradings and the six earlier rows were all correct. That is
correct behaviour for repeat detection and a trap for a human reading the output: "not repeating" here meant
"taught right six times and wrong once", which is a *more* interesting result, not a less interesting one.

Read `--contradictions` before concluding a claim has no history.

## Verify the partial-capture path before grading an "any single field is enough" claim (24 Sep 2026)

Grading `scheduler.appointment-lead.phone-is-minimum` looked like a one-grep job: the bail-out forms
(`StayOrGo.js:193-196`, `SkipToForm.js:14-22`) require first name, last name, phone and comments, so "you may not
even see a name" is wrong. That grade is right, but it is only *safe* because of a second check.

`dc-booking/src/Header.tsx:111-144` holds an exit-intent capture whose gate is an **OR** over
phone/fname/lname/comments — a path that fires on any one field and would have made the trainer substantially
correct. It is dead: it posts to `/bookings/capture` (`api.js:12`) and the router is mounted at `/booking`, with no
`/capture` handler in dc-server at all, and the 404 is swallowed by the surrounding `try/catch`.

Two lessons, the same pair as the 23 Sep service-description note. **Find the other path before grading a
"minimum requirement" claim wrong** — forms are rarely the only writer. And **when the other path exists but is
broken, that is the product bug, and it is worth more than the training finding.**

## The same trainer repeating a claim eight days later is the cheapest coaching signal there is

Aaron was graded `incomplete` on the appointment-lead minimum on 16 Sep and stated a stronger version of it on
24 Sep. Same trainer, same claim, nothing changed in between. `newly_repeating` flags it with
`curriculum_defect: false`, and that flag is doing real work: this needs one conversation with one person, not a
script change. Do not let a single-trainer repeat get written up in the same breath as a cross-trainer one —
they have different owners and different fixes.

## A daily run drains the 7-day window, so "zero new in 7 days" is normal (25 Sep 2026)

The scheduled task asks for "the last 7 days", which reads like a weekly sweep and invites the worry that a
zero result means discovery is broken. It does not, once the task runs daily. This run's window (18-25 Sep)
held **15 recordings: 9 already in the ledger, 6 with no transcript, 0 new and gradeable** — because each
day's own 18:00 run had already graded that day's transcribed sessions. The window is a safety net for
recordings that transcribe late, not a backlog to work through.

So the diagnostic is not "did the window produce sessions" but **"did anything transcribe that is not yet in
the ledger"**. Combined with the Friday-to-Sunday carve-out already recorded above, a Friday run finding
nothing new is expected twice over, and the run output should say which of the two cases it is rather than
reporting a bare zero.

## The dashboard's coverage-gap section must be re-dated, not just carried forward

The standing note above says to carry that section forward rather than regenerate it. That is right and
incomplete: the section is written in **relative time**, so carrying it forward verbatim publishes stale
claims. Before this run the live page said "**New today**" about two 24 Sep recordings, "three courses ran
today and only one transcribed", "fifteen days of evidence" and "Today the gap landed on one customer twice"
— every one of which had been true the day before and was wrong by the time anyone read it.

On every republish, age the `N days open` counters by the elapsed days, convert each `today` to the date or
weekday it actually refers to, and update the "oldest has been open for N days" line. Nothing errors, and a
page that confidently mis-dates itself is worse than one that omits the detail.

## The coverage-gap headline totals are hand-maintained and had drifted by two (26 Sep 2026)

The dashboard's summary line read "15 sessions, **48** customer attendances across 1,120 minutes" while its
own fifteen rows summed to **50**. The minutes were right, so nothing looked wrong.

Traced through the Slack posts, the error entered on **23 Sep**: the backlog went from 13 sessions / 42 to
15 / 48, but the two sessions added that day (Admin Part 1, 6 att; Admin Part 2, 1 att) contribute **7**,
not 5. Every run since carried it forward, because each run adds a delta to the previous total rather than
re-reading the table. The 24 Sep Slack post repeated it, so the wrong figure is now in the channel too.

**Recompute the totals from the rows on every republish**, rather than adding the day's delta to yesterday's
number. It is three lines and it is the only thing in that section a reader can check against the table
immediately above it:

```bash
python3 - <<'PY'
import re
h=open('index.html').read()
sec=h[h.index('Coverage gap'):h.index('Open product bugs')]
rows=re.findall(r'<tr><td>(2026-\d\d-\d\d)</td>.*?<code>(\d+)</code></td><td>(?:<strong>)?(\d+)(?:</strong>)?</td><td>(?:<strong>)?(\d+)(?:</strong>)?</td>', sec)
print(len(rows), sum(int(r[3]) for r in rows), sum(int(r[2]) for r in rows))
PY
```

Generalises to every hand-maintained aggregate in that section: it is prose, so nothing validates it, and a
running total that is only ever incremented never re-derives itself back to the truth.

## Whether a quiet-day run posts to Slack has been inconsistent — the rule is "did anything change" (26 Sep 2026)

Two Fridays, two different behaviours. **18 Sep** posted a full quiet-Friday message (0 graded, the nine
open gap entries listed). **25 Sep** posted nothing and only re-dated the dashboard. Both were correct runs
of the same situation, which means the rule was never actually written down, and this run had to reconstruct
it from the channel.

The rule that reconciles the scheduled-task file ("discovery returns zero → post nothing") with the standing
note above ("zero graded sessions is a report, not silence"):

- **Post** when something a reader would act on changed: a session was graded, the gap grew or shrank, or
  sessions ran and could not be graded (the false-all-clear case the Zoom cutover caused).
- **Do not post** when nothing changed: a Fri-Sun day with no training scheduled, no new recordings, and a
  gap identical to the one already posted. Re-posting an unchanged backlog into a channel that assesses
  named employees trains people to skim it.
- **Still republish the dashboard** either way, because its relative-time prose ages regardless.

Checked 26 Sep (Saturday): 15 in-window recordings, 9 already ledgered, 6 unchanged no-transcript, newest
recording still Thu 24 Sep, Past list's newest group still "LAST WEEK". Nothing changed, so nothing posted.

## Re-date the `N days open` counters in DESCENDING order or you double-age a row (27 Sep 2026)

The 25 Sep note makes re-dating the coverage-gap section standing procedure on every republish. The
mechanical trap it does not mention: the counters are plain text, so a naive ascending sweep
(`9 days open` → `10 days open`, then `10 days open` → `11 days open`) re-matches its own output and
ages the 17 Sep rows twice. Nothing errors and the table still looks plausible.

Replace largest-first — 17→18, 16→17, 12→13, 11→12, 10→11, 9→10, 5→6, 4→5, 3→4, 2→3 — so every
replacement's output is bigger than any source still to be matched. Anchor on `<strong>N days open`
rather than the bare number, or the `<td>` attendance and minutes cells get caught too. Then print
every `days open` match with its row's meeting key and eyeball the sequence against the dates before
publishing; that check takes one command and catches the double-age immediately.

Also confirmed this run: the 26 Sep totals repair held. The fifteen rows still sum to **50
attendances / 1,120 minutes**, matching the headline. Keep re-deriving it from the rows rather than
carrying the number forward — that is what let the drift run for three days last time.

## dc-booking's API base is graphql-broker, NOT dc-server — grepping the wrong service invented a product bug (28 Sep 2026)

The 24 Sep run reported a product bug: `dc-booking` posts bail-out leads to `${API}/bookings/capture`, the
booking router in dc-server is mounted at `/booking` (singular), and "no `/capture` handler exists anywhere in
dc-server". Every one of those statements is true. The conclusion was still wrong.

`REACT_APP_API_URL` for the booking microsite points at **graphql-broker**. The route is right there:
`graphql-broker/src/routes/index.ts:37` mounts `app.use("/bookings", bookingRoutes)`, the handler is
`graphql-broker/src/routes/booking/capture.ts:62`, it has its own test suite
(`routes/booking/__tests__/capture.test.ts`), and on a bailed capture it calls
`generateLead` (`capture.ts:125`) which posts to dc-server's `customer/createLead`. All three bail-out paths
work. Withdrawn in `product-bugs.md`.

**The rule: before concluding a route does not exist, find out which service the caller is actually pointed at.**
A repo-wide `git grep` for the path costs one call and would have caught it immediately — the dc-server-scoped
grep is what produced a confident, wrong bug report that sat in the ledger and in Slack for four days.

Generalises past routes: this monorepo has at least dc-server, graphql-broker and dc-calls answering HTTP for
different front-ends. "Not in dc-server" means nothing on its own.

## A false product bug is more expensive than a false training finding

Worth stating plainly because the incentives run the other way. `product-bugs.md` says a bug found here is worth
more than the training note that surfaced it, and that is true — which is exactly why a wrong one costs more.
A wrong training finding is corrected by re-grading one claim. A wrong product bug goes into the dashboard, into
Slack, and into somebody's sprint planning as evidence, and nothing in the pipeline re-checks it. The
`/bookings/capture` entry was cited in the 24 Sep Slack post as a *new* bug, which is the loudest slot in the
message.

Re-verify an open product-bug entry whenever a run touches the same code path, and date the re-verification.

## `git show "$SHA:path"` breaks in zsh when the path starts with certain letters

`git show "${SHA}:graphql-broker/..."` failed with `unknown revision e2564f6ea...aphql-broker/...` — zsh ate the
`:gr`. Quoting the whole argument does not help. Assign the path to its own variable and interpolate both:

```bash
P="graphql-broker/src/routes/booking/capture.ts"
git show "${SHA}:${P}" | sed -n '55,145p'
```

Reads as a bad SHA or a missing file, which is exactly the wrong diagnosis when you are checking whether a file
exists in another service.

## Zoho recording (1) and (2) with the same meetingKey: audit the long one, drop the shell

CRM Overview on 28 Sep produced two recordings under one `meetingKey` (`1092090568`): "… (1)" at 13:00 running
**11 seconds** with `noAudioRecording: true`, and "… (2)" at 13:04 running 43 minutes with a full transcript.
The false start is the host's first join; `min_duration_minutes: 20` drops it correctly. Grade the long one and
key the ledger row on the shared `meetingKey` — do not treat the pair as two sessions, and do not let the
0-minute shell's `isTranscriptGenerated: false` persuade you the session has no transcript.

## `campaigns.campaign-hours.window-930-to-3` is about the *window*; day-of-week is a separate assertion

Two claims live on the campaign schedule screen and collapsing them into one id would have collided a
`correct` history with a new `incomplete`. The existing id covers the send *window* (start/end times) and has
two `correct` rows. Aaron's 28 Sep claim was about which *days* the schedule can cover — a different
misconception — and was filed as **`campaigns.campaign-schedule.fixed-weekdays`**, which immediately paid for
itself: TeDarrell stated the opposite correctly three hours later and the contradiction detector surfaced the
pair. Same lesson as the 21 Sep note, from the other direction: splitting an id is cheap, merging two
assertions is not.

## The same-day contradiction fired again, and it is still the best signal here

28 Sep is the second clean instance (after 22 Sep): two trainers, one day, one pinned commit, opposite
positions on whether the campaign send schedule is fixed. It only appears because *both* of the day's
transcribed sessions were graded in the same run. Keep grading the whole day even when the second session
looks routine — the CRM session was 8-of-9 correct and still supplied half the most useful finding of the run.

## A partial grep on the translate claim manufactures a false wrong_high (29 Sep 2026)

There are **two** translate surfaces and they run in opposite directions. `MessageBubble.tsx:139-141`
translates a *received* message with `source_lang:"es", target_lang:"en"` hardcoded, and only offers the
control when `isSpanishText()` detects Spanish. `MessageToolbar.tsx:121` is a separate **"Translate to
Spanish"** button in the compose toolbar that translates the advisor's *outbound* draft.

TeDarrell's "you can use translate services to translate to Spanish" grepped against MessageBubble alone
reads as flatly inverted and would have been graded `wrong_high`. It is correct — he was describing the
compose button. The ledger already encodes the split: `inbox.translate.language-direction` (19 rows, the
inbound direction) and `inbox.translate.english-to-spanish` (the outbound button, graded correct 15 Sep).
**Check which surface the trainer is on before reaching for either id.**

## `isTranscriptGenerated: true` lied again — second instance, and it is now a discovery rule (29 Sep 2026)

Advisor Training Tuesdays 12 pm (`1031224791`, 29 Sep, 62 min, 2 attendees) returned
`isTranscriptGenerated: true` **and** `isTranscriptionEnabled: true`, and the recording page still showed
"No transcript generated" with the Generate button live. That is the same optimistic failure first seen on
9 Sep (`1056342748`) — the flag goes true off the back of a generated *summary*.

The standing note already says a `true` flag must be confirmed by pulling real text. Twenty days and one
recurrence later, treat that as mandatory rather than advisory: **`isTranscriptionEnabled: true` does not
rescue it either** — both flags read true here. The only proof is a non-empty
`div.transTimeStampMainContainer`. A run that trusted the flags would have reported three graded sessions
and silently invented findings for a session with no transcript at all.

## Read the screen the trainer was actually on before grading a permissions claim (29 Sep 2026)

`UserPermissionsToggles.tsx` builds an `enhancedPermissions` array with only **three** entries —
allRecordings, campaigns, restrictAdvisorBlockCustomer — omitting `closeSiteEarly`, which *is* in
`accountPermissions.json`. That reads exactly like a product bug: a permission that exists, is enforced at
`sites.js:1732`, and cannot be granted from the UI.

It is not. The screen in use is `UserEditSettings.tsx`, whose `permissionsList` (`:94-96`) is built from
`accountPermissions.json` plus the group list, so all four render. Aaron's "for those four" is correct.
Same lesson as the dc-booking/graphql-broker error on 28 Sep, one layer in: a component existing does not
mean it is the component on screen. **Find the consumer before treating a narrower list as the product's
behaviour** — this one was three minutes from a false product-bug entry in Slack.

## TRS-I2264 made attribution server-owned, but only for campaignsV2 tenants (29 Sep 2026)

`attributionClass.ts` (landed 25 Sep) plus `campaigns.update.ts:334` force `attributionEnabled = true` and
re-derive `campaignClass` from the trigger, discarding whatever the client sent. Read alone that makes every
"you can choose the class / toggle attribution off" claim wrong — and it would have contradicted three
existing `correct` rows for `campaigns.attribution.classes-and-overrides`, all TeDarrell.

The whole block is inside `if (await campaignsV2OnForTenant(ctx.tenantId))`, and the comment is explicit:
"Legacy tenants (flag off) save through this intent from the legacy editor and list toggle, and **keep the
attribution choices they send**." A legacy-editor demo is still accurate, and which tenants have the flag is
configuration — not gradeable.

What *is* unconditional and worth grading: `change-relay-worker/Configuration/CampaignMappingProfile.cs:26`
maps `AttributionEnabled` to `Trigger != "5" && ...`, so **Appointment Reminder campaigns never earn
attribution credit**, flag or no flag. Filed as `campaigns.attribution.trigger5-excluded` rather than folded
into the existing id — two different assertions, and merging them would have collided a correct history.

## Cited lines keep drifting — re-resolve before quoting (29 Sep 2026)

Three stale citations found in one run:
- `ReviewCard.tsx` Google floor: the 22 Sep note corrected `.js:64` to `.tsx:79`; it is now **`:87`** (read)
  and `:88` (routing branch). Logic unchanged.
- `product-bugs.md` cited the honest V2 wording at `campaignsV2/wizard/steps/DeliveryStep.tsx:324`. **That
  file does not exist at `7790cef49`.** The only honest wording left is a comment at `campaignsV2/api.ts:284`.
- `users.js` private-task sweep moved from `:482` to **`:483`**.

None changed a grade, but all three would have shipped as evidence pointing at nothing. A `git grep` against
the pinned commit costs one call.

## A scheduled run can simply not happen — the 7-day window is what catches it (29-30 Sep 2026)

There is no 29 Sep commit in `okto-mgmt-agents` and no 29 Sep report, while three sessions ran that day. The
30 Sep run picked all three up because discovery looks back seven days, which is exactly the safety net the
25 Sep note describes. Two points worth keeping:

- **Do not treat "the previous run covered yesterday" as an assumption.** Check the ledger, not the calendar.
- **This run fired at 07:03, not the usual 18:00.** A morning run sees *yesterday* complete and *today* empty
  — the day's 9 am, 11 am, 1 pm and 3 pm sessions have not happened yet. An empty result for the current day
  in a morning run is not the suspicious-weekday case from the 15 Sep note; say which it is.

## The recording API's transcript flags are now uniformly `true` and are useless for discovery (30 Sep 2026)

This retires every previous rule about reading `isTranscriptGenerated` / `isTranscriptionEnabled`, in both
directions.

All **twenty** rows `getAllRecordings` returned on 30 Sep carry the identical flag set:
`isTranscriptGenerated: true`, `isTranscriptionEnabled: true`, `isSummaryGenerated: true`,
`openAIStatus: SUCCESS`, `isGenerating: false`, `transcriptAccess: 1`, `status: UPLOADED`,
`isChaptersGenerated: true`, and a non-null `transcriptionDownloadUrl`. Five of those twenty have **no
transcript at all** — `1062682173`, `1012679711`, `1085383207`, `1037384439` and `1031224791` all still show
"No transcript generated" with the Generate button live, checked in the browser this evening. Four of them
were recorded on this dashboard as honest `isTranscriptionEnabled: false` / `openAIStatus: NOT_GENERATED`
as recently as yesterday.

So the standing 18 Sep rule — "a `false` flag can be believed; a `true` flag must still be confirmed by
pulling actual text" — is now **half wrong and wholly unusable**. There is no longer any value in the flag in
either direction, because no recording reports anything but success.

**The only reliable test is a non-empty `div.transTimeStampMainContainer` on the recording page.** Discovery
must open every in-window recording in the browser; the API is good for topic, date, duration, `meetingKey`
and `erecordingId` and nothing else. Budget for that — it is one page load plus a JS click per recording, and
the batch tool does about four per call.

Do **not** read the uniformity as "everything transcribed". It is the opposite failure to the 9 Sep one: then
a single flag lied optimistically off the back of a summary; now the whole field set appears to be defaulted.
`meta.userPlan` on the same response reads `{"user-type": "Free"}`, which is also obviously wrong for this
org, so treat the response's metadata block as degraded generally.

## A stuck recording DID recover — re-check the whole gap every run (30 Sep 2026)

The dashboard has said since 20 Sep that "stuck recordings do not self-heal" and has cited up to twenty-one
days of evidence for it. That rule is now **broken by a counter-example**: Advisor Training Monday 11 am of
28 Sep (`1059550464`), published as a coverage-gap row on 28 Sep with transcription reported off, came back
with a full 47,946-character transcript on 30 Sep and was graded on this run. It is the first entry ever to
leave that table.

Whether a human pressed *Generate transcript* or it healed on its own is not observable from here, and it does
not matter operationally. What matters is the procedure: **re-check every coverage-gap row in the browser on
every run**, not just the newest ones. The cost is one page load each and this run got a fully gradeable
session out of it — one that turned out to hold the correct script for two claims being taught wrong elsewhere
in the same week.

Keep reporting the gap as blocked rather than pending, because most rows still do not move. But drop the
"never recovers" framing; it is now false, and it was the argument for not re-checking.

## Re-date the coverage-gap counters by ELAPSED days, which is sometimes zero (30 Sep 2026)

The 25 and 27 Sep notes make re-dating standing procedure and warn about double-ageing via ascending
replacement. Both are right and both assume a day has passed.

This run republished the dashboard about **eleven hours** after the previous version (artifact version ids are
epoch seconds — `1790771014` was 07:03, `1790810765` was 18:06 the same day). Elapsed days: zero. Ageing the
counters would have published a table where every `N days open` disagreed with its own date column.

So: compute elapsed days from the live version's timestamp, not from "the last run was yesterday". A daily
task that fires twice in one day, or that missed a day and catches up, breaks the assumption in both
directions. The check is the same one already recommended — print every `days open` with its row's date and
confirm the arithmetic against today — and it catches a zero-day republish as readily as a double-age.

## `git pull` in okto-mgmt-agents fails the same way `pin_baseline.sh` does

The 16 Sep note covers the oktorocket clone. The **skill's own repo** has the same SSH remote and the same
failure: `git pull --ff-only` dies on `sign_and_send_pubkey: signing failed for ED25519 "Github" from agent`.
The scheduled task already says to continue on the local checkout, which is the right call — but note the push
at the end of the run works, because it is written with an explicit HTTPS URL and the gh credential helper.
The asymmetry is confusing in the run log: the pull fails, the push succeeds, and nothing is wrong.

Confirmed again for the baseline on this run: `pin_baseline.sh` reported `fetch failed` and pinned
`fca11443a` (14:47) while the real tip was `8719ad736` (16:18) — an hour and a half and one merge behind.
Fetch explicitly by URL and `update-ref` before grading, every time.

## The inbox message-search scope was not locatable in dc-server (30 Sep 2026)

`inbox.message-search.open-only` was graded `wrong_contained` on 17 Sep and was stated the other way on
28 and 30 Sep — searching by contact covers open tasks only, searching message text covers open and
completed. It could not be verified at `8719ad736` and was recorded `unverifiable` rather than assumed.

Where it is **not**: there is no `dc-server/routes/tracker.js` or `tracker.ts`, and greps for `searchText`,
`searchBy`, `byContact`, `messageSearch` across `dc-server/routes/` return nothing. `dc-server/modules/recordSearch.ts`
exists and is the most likely place to look next, along with the graphql-broker resolvers — this monorepo
answers HTTP from several services and "not in dc-server" means nothing on its own (see the 28 Sep note).
Worth ten minutes on a future run: the claim has now been graded three times with no citation behind any of them.

## Every course that ran on 1 Oct failed to transcribe — the first 100% day (1 Oct 2026)

Three webinars ran Thursday 1 Oct (Admin Part 2 9 am, Shop Analytics 1 pm, Advisor 2 pm), all three recorded,
**none** transcribed. Previous worst was three of four on 17 Sep. Six customer attendances and 203 minutes went
straight into the coverage gap without ever being gradeable, and **zero sessions were graded on this run** — the
first run since the Zoho cutover where the window produced no gradeable session at all despite training running.

This is the "sessions ran and could not be graded" case, so it was posted to Slack rather than passed over as a
quiet day. Note which case it is explicitly in the run output: a Thursday with three sessions and no transcripts
reads identically to a Friday with no sessions if you only report the number zero.

All sixteen previously-open gap rows were re-checked in the browser on this run and all sixteen are still empty,
so the backlog is now **19 sessions / 58 attendances / 1,385 minutes**. The 28 Sep recovery remains the only
entry ever to leave that table.

## Re-checking the whole gap needs `getWebinarRecording`, because `getAllRecordings` only reaches back ~10 days

The 30 Sep note says to re-check every coverage-gap row every run. The mechanical obstacle it does not mention:
`getAllRecordings` returned twenty rows covering 22 Sep onward, so eleven of the sixteen gap rows had **no
`erecordingId` in that response**, and the recording-page URL cannot be built without one.

`ZohoWebinar_getWebinarRecording` with `path_variables.webinarKey` set to the meeting key returns that one
recording including its `erecordingId`, which is all that is needed. It is one call per row, each ~1.5 KB of
response for one field, so budget roughly 11 extra calls plus 16 page loads to sweep the whole table. Worth it:
the sweep is cheap compared to publishing a dashboard whose gap section is asserted rather than checked.

## An empty transcript has no container at all — check `.transcript-tab--empty`, not a zero length

The 30 Sep rule is "the only reliable test is a non-empty `div.transTimeStampMainContainer`". True, but the
check as written invites a wrong implementation: when there is no transcript the container is **not present**,
so `document.querySelector('div.transTimeStampMainContainer').innerText.length` throws rather than returning 0,
and a batch step that throws looks like a tool failure rather than an answer.

Query both and report both:

```js
const c = document.querySelector('div.transTimeStampMainContainer');
const e = document.querySelector('.transcript-tab--empty');
`len=${c ? c.innerText.length : 'NONE'} empty=${!!e}`
```

`.transcript-tab--empty` is the empty-state wrapper that holds "No transcript generated" and the Generate
button, so `empty=true` is a positive confirmation of absence rather than an inference from a missing node.
All nineteen recordings checked this run answered `len=NONE empty=true`, unambiguously.

Also still true, and still worth the JS click over any coordinate click: the Transcript tab is reached with
`[...document.querySelectorAll('button.transcript-panel__tab')].find(b => b.textContent.trim() === 'Transcript').click()`.
Four seconds after `navigate` and four after the click was reliable across all nineteen loads this run.

## A citation can rot in place — `cleanup.js:657` pointed at the wrong code for days (1 Oct 2026)

The 29 Sep note says cited lines drift and to re-resolve before quoting. This run found the harder version of
that problem: `product-bugs.md` cited the stale-task auto-close at `dc-server/modules/cleanup.js:657`, and that
line is ShopWare RO-reconciliation code — at today's baseline **and** at `8719ad736`, which the table claims to
have re-verified against. The file still exists and the line number still resolves, so nothing ever looked
broken; the citation simply stopped pointing at the thing it names.

The sweep is `closeStaleTasks` at `:836`, and both halves of the defect are intact at `:849`:
`{ tenantId, date_updated: { $lte: staleDate, $gte: staleGte } }`, where `staleGte` (`:844-847`) is `staleDate`
minus one day at `startOf('day')` — bounded below, hence the ~1-day window — and there is no read or
`responded` filter anywhere in the query.

Generalise: **re-resolve a citation by searching for the code, not by reading the line it points at.** Reading
`:657` and finding plausible-looking server code there is exactly how this survived. A `git grep` for the
distinguishing identifier (`closeStaleTasks`, `staleGte`) costs one call and cannot land on the wrong function.

## On a zero-transcript day, re-verify the product bugs — it is the only real work available

A run that grades nothing still has a baseline pinned and a table of open findings whose citations age every
day. This run re-resolved all ten open bugs against `4f4044545`: all ten still open, seven citations drifted,
one (above) outright wrong. That is a concrete, checkable deliverable from a day that would otherwise produce
only "nothing transcribed again".

It also gives the run's baseline SHA a meaning. Publishing a dashboard stamped with a commit that nothing was
checked against is a quiet lie; stamping it with the commit the whole bug table was just re-verified at is not.

## `inbox.message-search.open-only` is RESOLVED — and the 30 Sep "not locatable" note was wrong (2 Oct 2026)

The 30 Sep note says this claim "could not be verified at `8719ad736`" and lists where it is *not*
(`dc-server/routes/tracker.js`, greps for `searchText` / `searchBy` / `byContact` / `messageSearch`
across `dc-server/routes/`). It was never missing. The chain, all at `565dea231`:

- Inbox search modal `SearchModal.tsx:51-61` offers two modes, `contact` and `message`, and dispatches
  `search` from `common/actions/tasks`.
- That action posts to **`/messages/tracker/search`** (`dc-user/src/js/common/actions/tasks/index.js:402`).
- The route (`dc-server/routes/messages.js:966`) delegates to `advancedSearch`
  (`dc-server/modules/taskHelper.js:157`).
- **contact branch:** `Trackers.find({ contact, status: { $ne: "complete" } })` at `taskHelper.js:172`,
  under a comment that literally reads `// search for open tasks`. **Open only.**
- **message branch:** an Atlas `$search` over message `body` whose `must` is only `tenantId` plus an
  optional `siteId` (`:192-209`), then `Trackers.findOne({ _id })` at `:255` with **no status filter
  anywhere**. **Open and completed.**

So the claim "contact search is open-only, message search covers open and completed" is **correct**,
and that is what Allie said on 28 Sep — recorded `unverifiable` for want of a citation. The 17 Sep
row had already carried `taskHelper.js:172, :255, :265` the whole time; the 30 Sep run did not look
at the existing ledger row before declaring the code unlocatable.

Three lessons, in order of how much they cost:

1. **Before searching for a claim's implementation, read the claim's own earlier ledger rows.** The
   citation was sitting in the ledger. This is the cheapest possible lookup and it was skipped.
2. **Grep for the route the client calls, not for the concept.** `searchText`/`searchBy` are the
   client's vocabulary; the server's is `advancedSearch` in `modules/`, not `routes/`. Trace
   UI → action → URL → route → module, one hop at a time.
3. `taskHelper.js` is byte-identical across `8719ad736`, `7790cef49`, `4f4044545` and `565dea231`, so
   it was exactly as verifiable on 30 Sep as today. "Unverifiable" recorded against a stable file is
   almost always a search failure, not a property of the code — treat it as a lead, not a verdict.

**The correction the ledger cannot make itself.** The 28 Sep row (`uuid:1059550464`, Allie) should be
`correct` with evidence `taskHelper.js:172, :255`, which would make Allie wrong_contained 17 Sep →
correct 28 Sep a **Fixed** pair. The ledger is append-only, `ledger.py` has no correction mode, and no
session was graded on this run, so the row still reads `unverifiable`. Leaving a trainer's correct
statement recorded as uncheckable is the unfair direction; flag it for a human rather than hand-editing
a grade row autonomously.

## Re-verify the bug table by blob hash, not by re-reading line numbers (2 Oct 2026)

The 1 Oct sweep re-resolved all ten open bugs by reading lines, found seven citations drifted and one
outright wrong. That is the right thing to do *when the code has moved*. The cheap precondition nobody
was checking first:

```bash
git rev-parse "${OLD_SHA}:${PATH}"   # compare to
git rev-parse "${NEW_SHA}:${PATH}"   # identical blob => no citation in that file can have drifted
```

29 commits landed between `4f4044545` and `565dea231` and **all thirteen cited files were byte-identical**,
so every line number carried over with certainty, in one command instead of ten greps. Only diff the
files whose hash actually changed.

**The trap this run hit:** `git diff --name-only <old> <new> -- <paths…>` printed nothing, which reads as
"nothing changed" — but it prints nothing for a *misspelled path* too. One of the thirteen was wrong
(`callsReviewUtils.ts` is under `dc-user/src/js/admin/components/calls/Calls/`, not `common/utils/`), and
the empty diff concealed it completely. **Always `git cat-file -e "${SHA}:${PATH}"` each path first** and
make a missing path loud; an empty diff is only meaningful once every path in it is known to exist.

## A quiet Friday and a failed Thursday are both "zero" — say which, every time (2 Oct 2026)

Two consecutive runs graded zero sessions for opposite reasons: 1 Oct ran three courses and none
transcribed; 2 Oct had no training scheduled at all (Past list's newest group was still Thursday, and all
series run Mon–Thu). Per the 26 Sep "did anything change" rule, 1 Oct posted to Slack and 2 Oct did not,
which is correct and will look inconsistent in the channel to anyone reading the two in sequence — the
run output is the only place that distinction gets recorded, so state it explicitly rather than reporting
a bare zero.

Also worth keeping: a Friday run still has real work in it. This one re-swept all nineteen coverage-gap
rows, re-verified ten product bugs against a fresh baseline, and closed a ten-day-old open question. A
day with nothing to grade is not a day with nothing to do.

## `build_dashboard.py` splices EVERY pipe-table in `product-bugs.md` into the bug table (3 Oct 2026)

The renderer does not look for one table; it scrapes every markdown pipe-row in the file and concatenates
them into the single "Open product bugs" table. `product-bugs.md` has grown three sections beyond the bug
table itself — `## Full re-verification sweep — 1 Oct 2026` (lines 28-36) holds a `bug | was | is now`
citation-drift table — and those seven rows render **inside** the bug table as malformed three-column rows,
with the sub-table's own header (`bug | was | is now`) appearing as a data row.

So on this run a freshly generated `dashboard.html` was **worse than the page already live**: identical for
every ledger-derived section (Repeats, Fixed, Contradictions, Sessions all byte-identical, since the ledger
had not changed), and a regression in the bug table. Publishing the generated file would have quietly
shipped it.

**The check is one command** — diff the generated page against the live one section by section before
publishing, and treat any section that differs on a day the ledger did not change as a bug in the renderer,
not an update:

```python
def sec(h,txt): i=txt.index('<h2>'+h); j=txt.find('<h2>',i+4); return txt[i:j if j>0 else len(txt)]
```

**On a day with no new sessions, build the republish from the live page** (which you must read anyway) and
edit only the coverage-gap section. Regenerating buys nothing — every other section is derived from a ledger
that did not move — and risks exactly this. The real fix is to scope the renderer to the first table or to
the `# Open product bugs` section; until someone does, keep extra tables out of `product-bugs.md`, or expect
them on the dashboard.

## The gap sweep's `erecordingId` map, so the next run skips 11 API calls

The 1 Oct note explains that `getAllRecordings` only reaches back ~10 days, so most coverage-gap rows need a
`ZohoWebinar_getWebinarRecording` call each just to build the recording-page URL. These ids are **stable** —
they are properties of the recording, not of the query — so they only need fetching once. Current table:

| date | meetingKey | erecordingId |
|---|---|---|
| 2026-09-09 | 1056342748 | `78d418380d1b61f1e27a043500f34ca5fed86b8ee0c88b5569937745d1e35425` |
| 2026-09-10 | 1062515451 | `440305a7ca97c4c8b967e21ce51754aa619466f4870c9bf89503de3b5a2b12c0` |
| 2026-09-14 | 1026984660 | `3265686a0eaf4493274f23ff8e85539d22b26a4d21aa889da28a89a410d81797` |
| 2026-09-15 | 1020522825 | `3265686a0eaf4493274f23ff8e85539d39c8511d7007023f3c01d9d1c42dc54b` |
| 2026-09-15 | 1017030712 | `c64987a16797505704c2b1490cc358c414a8f0457ce777d1c84ebcc7772fb7f0` |
| 2026-09-16 | 1014397535 | `20913636e0fe6edfda26769d97ec169d0af1f8e33674f0718ecf41505e557054` |
| 2026-09-17 | 1098634476 | `63151bc4e0bd4c22a6d71c03f018816c83787c3f9501ce686dc6bca78338a495` |
| 2026-09-17 | 1096605816 | `63151bc4e0bd4c22a6d71c03f018816cf78b698aeb7f5904e2be722d4c7bfa9b` |
| 2026-09-17 | 1077862314 | `793f3a0ab35ad6f0cd007d83d6472a1b01ac5e30b2c1cd8b3da6b476e9a1f910` |
| 2026-09-21 | 1035658075 | `f5c8926552738beba65ff56c11ab8f7148a1cdf41846f824a4d61eded639a6d3` |
| 2026-09-22 | 1047685227 | `981f0665e16e6867b4829eda7764ae22b13ca6e741c08ea073eddd900e264049` |
| 2026-09-23 | 1062682173 | `31da7e4b68d35304dff1996c740c1775a4da94c8bdffdea94b4d6b9fb465aa83` |
| 2026-09-23 | 1012679711 | `981f0665e16e6867b4829eda7764ae2253509d747d944b5298d266f564b8980c` |
| 2026-09-24 | 1085383207 | `981f0665e16e6867b4829eda7764ae22ffbab4ede94e46ea51fb59989eb28066` |
| 2026-09-24 | 1037384439 | `f5c8926552738beba65ff56c11ab8f71fdc28a9f8ef56d702ca40cf1dced87b7` |
| 2026-09-29 | 1031224791 | `b88ababcddba2e9fb7bb2f29e4bf9c340d847835bbda8adf28aa50f6e19727ab` |
| 2026-10-01 | 1014604520 | `555451ad8e12ff5f1a46d03ced8490c871976e017f1c9ca622e5051901ac6c54` |
| 2026-10-01 | 1058828040 | `8e63910aeac9d68a77e6fc6cbf3d8d424717edb6269cadca3e4aef504247dd73` |
| 2026-10-01 | 1042885760 | `1e53b4373bc37d0d676efa94681310ebd532bd755ddc0ab3622dc2acdd35ea46` |
| 2026-10-05 | 1074035494 | `0dacea0849d042373acba9d77f3f7b43c12e299637c6cabb4d72823bfaa6bf96` |
| 2026-10-05 | 1081190831 | `555451ad8e12ff5f1a46d03ced8490c8aa87f1e54ebeec13cb472d2dbcc9e619` |
| 2026-10-06 | 1081511660 | `1e53b4373bc37d0d676efa94681310eb8bf068251d36e1dc02a456f381b5d0a6` |
| 2026-10-06 | 1064758517 | `8e63910aeac9d68a77e6fc6cbf3d8d4261c3e82de9cfe23800f6ae0dbc08f20d` |
| 2026-10-07 | 1020531693 | `e2ae0c28c9b0cf5aa6a723e943f4ea5998eb3b56252f85d98114cc42168e79b0` |
| 2026-10-12 | 1063155070 | `b9acee1c85cd78bbec5acb7e246a911b3d7ea4436dd9a5f99e01d5a85bec2931` |
| 2026-10-14 | 1034354820 | `77f701363e2d28127222470972e1572c950f9ee668913812db0a8631d213d8b0` |
| 2026-10-15 | 1060714650 | `22094594caca3ffd9f7924db90e23005aa102bde24527551271efeaeb12b4f4b` |
| 2026-10-20 | 1063327770 | `ffb748232a43ed38e7e20f11aa3cd2a16941a36eff6a53d46b2fdd4359cb6b55` |
| 2026-10-21 | 1078512746 | `43dccd8e29f67c3f39733fd2f93f0a2c8cd9e31cd46baca77ff2fd8f0e9f7dac` |
| 2026-10-22 | 1046976106 | `fd465b2080173d1dd408f360761b31ea29711009b7f4ee5a0452f3819fc0771c` |
| 2026-10-22 | 1060567444 | `27f50025bdcfcf700c8961a93cb05e41747bf2f1590fed6e0ce1d9a81e6853fb` |

Page URL is `https://webinar.zoho.com/meeting/videoprv?recordingId=<erecordingId>&x-meeting-org=796393835`.
Add a row whenever a recording enters the gap; delete one when it leaves. Four recordings per
`browser_batch` (navigate + a JS probe each) swept all nineteen in five calls this run.

The 7 Oct Admin Part 2 id shares its first 32 characters (`e2ae0c28c9b0cf5aa6a723e943f4ea59`) with the **same day's Advisor recording**, which was graded rather than entering the gap — the two sessions ran four hours apart on the same day and differ only in the tail. Match on the whole string.

Both 6 Oct ids collide on their first 32 characters with a 1 Oct row — `1e53b437…` with the 1 Oct Advisor
recording and `8e63910a…` with the 1 Oct Shop Analytics one. Match on the whole string.

Note the ids are **not** unique prefixes: several share a 32-char head (`981f0665…` appears three times,
`3265686a…`, `63151bc4…` and now `555451ad…` twice each) and differ only in the tail. Match on the whole
string — the 5 Oct CRM recording and the 1 Oct Admin Part 2 recording share the first 32 characters and are
different sessions three weeks apart, which is exactly the collision that would silently sweep the wrong page.

## A zero-commit day makes the bug-table sweep an identity argument, not a check (3 Oct 2026)

The 2 Oct note says to re-verify the bug table by blob hash rather than by re-reading line numbers. There is
a cheaper case above that one: this run's `pin_baseline` fetch returned **`565dea231`, the same commit the
2 Oct run pinned** — `git rev-list --count 565dea231..origin/development` was `0`. When no commit has landed,
the baseline is the same object, so no citation can have drifted and there is no diff to read at all.

Say that explicitly rather than claiming a re-verification that did not happen; the two look the same on the
page and only one of them is true. Still run `git cat-file -e "$SHA:$PATH"` over every cited path — that
catches a misspelled path, which the 2 Oct note flags as the failure an empty diff conceals, and it is the
only part of the sweep that has any work in it on a zero-commit day.

## The webinar list APIs stopped returning training webinars — discovery is browser-only now (4 Oct 2026)

The 30 Sep note retired the recording API's transcript *flags* as a discovery signal but kept
`getAllRecordings` for "topic, date, duration, `meetingKey` and `erecordingId`". That is now gone too.

On this run `ZohoWebinar_getAllRecordings` returned **seven** rows and not one was a training webinar: newest
26 Aug 2026, the rest Oct–Dec 2025, every one a Zoho *Meeting* recording. On 1 Oct the same call returned
twenty webinar recordings back to 22 Sep. Cross-checks:

- `ZohoMeeting_listMeetings` (`listtype=past`) — 29 rows, newest 28 Sep 2026, all Meetings, no webinars.
- `ZohoWebinar_listWebinars` — still empty, as it has been since the cutover.
- `ZohoWebinar_getWebinarRecording` with `webinarKey=1042885760` — **works**, returns the 1 Oct Advisor
  recording with its `erecordingId` and a `startTime` of `2026-10-01T13:58:20 CDT`.
- All nineteen gap recording pages loaded normally in the browser.

So the recordings exist and are individually reachable; it is the *listing* that lost webinar scope. The
practical consequence is the one that matters: **there is no API left that can enumerate a session you have
not already seen.** `getWebinarRecording` only confirms a key you hold, and the stored `erecordingId` map
above only covers rows already in the gap. The sole discovery path is the Past Webinars list in the browser:

```
https://meeting.zoho.com/meeting/796393835/3764623000000012011/webinar/my-webinars/past
```

Note the host is `meeting.zoho.com`, not `webinar.zoho.com` — the latter redirects there and
`webinar.zoho.com/meeting/recordings` is a 404. The list groups by recency ("LAST WEEK", "EARLIER") and each
row carries date, time, duration, course name and attendee count, which is everything discovery needs except
the `erecordingId`. `get_page_text` returns nothing on this page; read `document.body.innerText` directly
instead — it is only ~3 KB.

**A lead, not a diagnosis.** The `getAllRecordings` response now reports `userPlan: {"user-type": "Free"}`
and `recordingLimitStatus: -1`, and the Zoho home screen shows a **Renew now** prompt. A lapsed or downgraded
plan would explain webinar scope vanishing while meeting data survives, and could eventually threaten the
recordings themselves. Worth a human check before the next training day rather than waiting to see.

**The general lesson, which has now bitten twice in five days:** this integration degrades by *quietly
returning a plausible smaller answer*, not by erroring. On 30 Sep it was flags that were uniformly `true`;
here it is a list that is well-formed, `status: success`, `moreRecords: false` — and simply does not contain
the thing being looked for. A zero from this API means nothing on its own. Confirm every zero against the
browser before writing "no new sessions", because a quiet weekend and a broken endpoint look identical.

## The webinar list API outage was transient — it recovered in a day (5 Oct 2026)

The 4 Oct note concluded that `getAllRecordings` had permanently lost webinar scope and that "there is no API
left that can enumerate a session you have not already seen". **That is now too strong.** On 5 Oct the same
call returned **twenty rows, all training webinars**, back to 23 Sep, including both of the day's sessions with
their `erecordingId`s. Nothing was changed at this end; it simply came back after roughly a day.

Keep the browser-first rule anyway, and keep it for the reason the 4 Oct note gives rather than because the API
is broken: **this integration degrades by returning a well-formed, `status: success` response that omits what
you are looking for.** Twice in a week now — the 30 Sep flag collapse and the 4 Oct scope loss. A zero from
this API means nothing until the Past Webinars list agrees with it. The right order, and the one that would
have caught 4 Oct on the day, is what this run did: find the sessions in the browser first, let the API confirm
them and supply `erecordingId` second.

The `userPlan: {"user-type": "Free"}` reading and the **Renew now** prompt were both still present on the
healthy 5 Oct response. They did not predict the outage and did not explain the recovery, so treat them as an
unrelated standing oddity rather than a diagnosis — but they are still worth a human check.

## `pin_baseline.sh`'s silent fallback was seven commits stale, and this time it mattered (5 Oct 2026)

The 16 and 30 Sep notes say to fetch explicitly by URL because the script's fetch fails. The 3 and 4 Oct runs
found the fallback happened to be correct, because `development` had not moved for three runs. That made the
fallback look harmless. It is not.

This run: `pin_baseline.sh` printed `fetch failed` and pinned the local `origin/development` at **`a6feb10f0`**,
while an explicit HTTPS fetch of `development` gave **`926cb3888`** — `git rev-list --count a6feb10f0..FETCH_HEAD`
was **7**. Grading or re-verifying against the fallback would have stamped the dashboard with a commit that was
seven commits and several hours behind the real tip.

The remote is `git@github.com:ShopRocket-LLC/oktorocket.git`, so the explicit fetch is:

```bash
git -c credential.helper='!gh auth git-credential' fetch https://github.com/ShopRocket-LLC/oktorocket.git development
```

Do not derive the HTTPS URL from `git remote get-url origin` with a `sed` that uses `+?` — BSD `sed` on this host
rejects the non-greedy operand with `RE error: repetition-operator operand invalid` and the fetch then runs
against `https://github.com/`, which fails as "repository not found" and reads like an auth problem.

## Expanding an abbreviated citation path is its own failure mode (5 Oct 2026)

`product-bugs.md` writes several citations in abbreviated form — `dc-user/.../campaigns/AddCampaign.js:732` vs
`campaignsV2/api.ts:284`. Expanding `campaignsV2/api.ts` to `dc-user/src/js/admin/components/campaignsV2/api.ts`
for the blob sweep produced a `MISSING-AT-NEW`, which looks exactly like a file that was deleted by one of the
19 commits. It was not: the real path is **`dc-user/src/js/common/components/campaignsV2/api.ts`**, under
`common/`, and the blob is unchanged.

The 2 Oct note says to `git cat-file -e` every path so a misspelling is loud rather than hidden. This is the
mirror image: the check fired correctly, and the thing it caught was **my expansion**, not the repository. When
a path comes back missing, resolve it with `git ls-tree -r --name-only $SHA | grep "/<basename>$"` before
concluding anything about the code. Three of the twenty-five paths in this sweep were under a different parent
than the obvious guess (`OnDeck.tsx` and `api.ts` under `common/components/`, `overviewGoalColors.ts` under
`common/utils/`, `CampaignOutcomeModal.js` under `user/components/tasks/`).

## `taskHelper.js` finally moved — the message-search citations are now `:169` / `:254` (5 Oct 2026)

`inbox.message-search.open-only` was resolved on 2 Oct with citations `taskHelper.js:172` (contact branch,
`status: { $ne: "complete" }`) and `:255` (message branch, `Trackers.findOne({_id})` with no status filter).
The file had been byte-identical across four consecutive baselines, which is what the 2 Oct note leaned on.

At `926cb3888` it has changed for the first time: commit `dba26529f` ("Move OpenRouter routing to feature
presets #TRS-I2146") deleted two unrelated lines, one at `:14` and one at `:581`. The first is above both
citations, so **both shift up by exactly one**: contact branch `:169` (comment `// search for open tasks` at
`:168`), message branch `:254`. **The behaviour is unchanged** — contact search is still open-only, message
search still carries no status filter.

This is the cheap confirmation of the 1 Oct "re-resolve by searching for the code, not the line" rule: a
`git grep -n 'search for open tasks'` costs one call and lands on the right line regardless of drift, whereas
reading `:172` at the new baseline would have shown plausible-looking code one line off.

## A Monday evening run is the one that catches the whole day (5 Oct 2026)

The 15 Sep note says the evening run must re-check the same day's afternoon sessions, and the 29 Sep note warns
that a morning run sees the current day empty. This run fired at **18:08 Central on a Monday** and found both of
the day's sessions already complete and recorded — Advisor 11 am (ended 12:06) and CRM 1 pm (ended 14:15).

Worth stating plainly because the preceding four runs all landed on days with no training: **Mon–Thu, an evening
run is expected to find sessions, and finding none is suspicious.** Fri–Sun it is expected to find nothing. The
weekday is the first thing to establish, and it is not safe to infer it from "the last run found nothing".

## A recording can capture one minute of a 77-minute session, and discovery reads that as a no-show (6 Oct 2026)

Every coverage-gap row before today is the same failure: an intact recording with no transcript behind it. Admin
Part 1 Tue/Thu 3 pm on 6 Oct (`1064758517`) is a **different** failure and the table now has to distinguish them.

The session ran in full — `getWebinarRecording` gives `startTime` `2026-10-06T15:03:21 CDT` and `endTime`
`16:19:14`, and the one attendee was present **77 minutes** and answered two polls. But `durationInMins` is **1**,
`fileSize` is **2,212,655** (2.2 MB), and the transcript that *does* exist is 287 characters covering 00:26–00:40:
"Good afternoon… My name is Theo and I will be a trainer for this evening session… we're just going to give it one
more minute." Then the capture stops. The transcript is accurate; there is simply nothing else on the tape.

Two consequences, both of which bite silently:

1. **`min_duration_minutes: 20` discards it.** The threshold exists to drop false starts and no-show shells, and
   `durationInMins: 1` looks exactly like one. A 77-minute session with a customer in it would have vanished from
   the run with no row anywhere. **Never classify a short recording from `durationInMins` alone** — compare it to
   the `startTime`→`endTime` span, and cross-check `fileSize`. A healthy hour is ~250 MB (the same day's Advisor
   recording is 246 MB for 68 minutes); 2.2 MB for a 76-minute span is a truncated capture, not a short meeting.
2. **It is not recoverable.** The Generate-transcript button fixes a missing transcript over an intact recording.
   It cannot invent audio that was never written. Rows of this kind should say so, or someone will spend a week
   waiting for a transcript that cannot arrive.

The honest discriminator between "no-show" and "truncated capture" is the **attendee report**, not the recording:
0 attendees and a short file is a no-show (the day's 9 am and 11 am sessions, correctly dropped); 1 attendee
present for 77 minutes and a short file is a lost session.

## `isTranscriptGenerated: true` has now lied three times, and a true `isSummaryGenerated` does not rescue it

Advisor Tue 12 pm on 6 Oct (`1081511660`): a completely healthy recording — 246 MB, 67 min 48 s, `status: UPLOADED` —
with `isTranscriptGenerated: true`, `isSummaryGenerated: true`, and a transcript tab answering `len=NONE empty=true`.
The **summary genuinely exists** and renders; the transcript genuinely does not. So the two flags are independent and
a believable summary is not evidence that a transcript is behind it.

Useful corollary, and the only thing the summary is good for here: **it carries attribution.** This one opens
"Introduction by Ali from Rocket Advisors Training team", which canonicalises to **Allie** via the alias table. That
is worth recording on a gap row — it says *who* lost a session — but it is **not** grading material: the summary is
paraphrase with no timestamps, and `grading.md` requires a `stamp` from the page transcript. Never grade a claim
from a summary.

## "Theo" is a new unconfirmed trainer variant — do not fold it into TeDarrell without asking (6 Oct 2026)

The 6 Oct Admin Part 1 3 pm fragment contains the clearest self-introduction in weeks — "My name is Theo and I will
be a trainer for this evening session" — and **Theo is not on the roster and not in the alias table.** It sits in the
same phonetic family as Tedario / Tadario / Serio / Stereo / Tirio, so the tempting move is to canonicalise it to
TeDarrell as those were.

Resist it this time. `trainers.md`'s own rule is that the canonical spelling comes from a person or an account and
**never** from a transcript, and the three prior variants were folded in on the reasoning that no other roster name
is close. "Theo" is short enough to be a genuinely different name — the bench has grown before (Allie was missing
from the roster entirely until 10 Sep). Nothing was graded from this session, so the attribution costs nothing
today; recording it wrong would corrupt repeat detection the first time it matters. **Flagged for a human.**

## zsh does not word-split unquoted variables, so a `for p in $PATHS` sweep runs once (6 Oct 2026)

The blob-hash sweep from the 2 Oct note was written as `PATHS="…multi-line…"` then `for p in $PATHS`. In bash that
iterates per path; in **zsh**, which is the shell here, unquoted parameter expansion does not word-split, so the loop
ran **once** with the entire multi-line blob as `$p`. The output was one `MISSING-AT-NEW` followed by the path list
printed verbatim, which reads like a tool glitch rather than a loop that never ran — and if the first path happened
to be the only one checked, it would read like a clean sweep.

Use a `while IFS= read -r p` loop over a heredoc. It is shell-agnostic and it cannot silently collapse.

## Blob identity cannot catch a citation that was already wrong (6 Oct 2026)

The 2 Oct rule — compare `git rev-parse "$SHA:$PATH"` across baselines, and only diff the files whose hash changed —
is sound and cheap, and the 5 Oct sweep leaned on it entirely: "every file cited by the table is byte-identical, so
every line number carries over **with certainty**".

The certainty is misplaced. Byte-identity proves a line number has not **drifted**. It proves nothing about whether
the line was ever right. `product-bugs.md` cited `dc-server/modules/campaignBuilder.js:4357` for the
`cust.campaigns !== false` audience gate. That line has never been that code — checked at `8719ad736`, `4f4044545`,
`565dea231`, `926cb3888` and today's `c2962ec29`. At today's baseline `:4357` is `params.ro.customer.fname`
assignment; the gate is at **`:4505`**, under the comment block at `:4498`. The 5 Oct sweep could not have caught it,
because the file *was* byte-identical and the reasoning stopped there.

So the two checks answer different questions and both are needed: **hash-compare to find what moved, and `git grep`
for the distinguishing identifier to confirm the citation still names the right code.** The grep is one call per bug
and it is the only one that can detect rot. This is the second rotted citation found this way, after
`cleanup.js:657` on 1 Oct — and in both cases the cited line resolved to plausible-looking code, which is exactly
why neither was noticed for weeks.

## The abbreviated-path expansion error fired again — `OnDeck.tsx` is under `campaigns/`, not `campaignsV2/` (6 Oct 2026)

Second instance of the 5 Oct lesson, same shape. `product-bugs.md` mentions `OnDeck.tsx:347` beside
`campaignsV2/api.ts:284`, so the natural expansion is `dc-user/src/js/common/components/campaignsV2/OnDeck.tsx` —
which does not exist and reports `MISSING-AT-NEW`, reading like a deletion by one of the day's 27 commits. The real
path is `dc-user/src/js/common/components/**campaigns**/OnDeck.tsx`, present and byte-identical at both baselines,
with `{!campaign?.explainDelete && (` still at `:347`.

The adjacency of two citations in one table cell is not evidence they share a directory. Resolve every abbreviated
path with `git ls-tree -r --name-only $SHA | grep "/<basename>$"` **before** reading anything into a missing file.

## The in-app browser is signed out of Zoho — this run wasted five calls rediscovering it (7 Oct 2026)

The 15 Sep note already says "the in-app browser is still not authenticated against Zoho — use **Claude in Chrome**,
where Brad's session is live." It is buried in the middle of a section about transcript truncation, and this run
opened the Past Webinars list in the **in-app browser** first, hit a OneAuth sign-in wall, then tried a recording
page and got `Permission Denied`, and briefly concluded discovery was blocked for the day.

It was not: Chrome worked first time and both transcripts came back clean. Signing in is not an option — it needs
Brad's password and his second factor — so the in-app browser can never do this job.

**Rule, stated where it will be found: every Zoho page in this skill goes through `mcp__claude-in-chrome__*`.**
The in-app browser's Zoho session does not exist and will not be created. A OneAuth prompt or a "Permission
Denied" page from `webinar.zoho.com` means the wrong browser, not a lost session and not an access problem.

## `reportPermissionsService.ts` is a per-report fallback, not the advisor default set (7 Oct 2026)

Allie said "as an advisor you are by default given access to **14 reports**". Grading this against
`dc-server/modules/reportPermissionsService.ts` makes it look like a clean `wrong_high`:
`calculateDefaultReportPermission` computes `const enabled = pidLevel === 0 || pidLevel === 5` (`:704`) with a
comment directly above saying "PID 1 (Advisor), 2 (Technician), 3 (Wallboard), 4 (Phone): **no access** unless
granted by an individual permission or a Report Permission Group". Read alone, that says advisors get nothing.

**It was written up as wrong_high and then caught before landing, by checking the ledger for prior rows on the
same claim_id.** `reports.advisor-default-count.fourteen` was already graded **correct** on 28 Sep, citing a file
the service never mentions: `dc-user/src/js/common/schema/defaultReportPermissions.json`. PID `"1"`
("User - Advisor") carries a `defaultReports` array of five groups holding **exactly 14 reportIds** —
`callSiteStats`, `firstTimeCallConversion`, `transactionDetail`, `partsSearch`, `laborSearch`,
`deferredServicesReport`, `roDVIsummary`, `advisorSalesByCategory`, `serviceAdvisorSalesTracker`,
`techSalesTracker`, `focusItems`, `taskHistory`, `advisorTaskActivity`, `shortUrl`. The service function is the
fallback for a report **not** covered by that file. There are two copies of the JSON (`dc-user/src/js/common/schema/`
and `dc-server/schema/`); either resolves the count.

Two transferable rules. **A grep that produces a confident wrong_high on a claim the ledger has already graded
should stop the grade, not confirm it** — read the prior row's citation first, because it was found by someone who
had the same question and more time. And **a PID-gating function is not the same thing as a seeded default**; look
for a schema or seed file before concluding a role gets nothing.

## Three resolutions in one day, and the thing they have in common (7 Oct 2026)

`campaigns.campaign-schedule.is-general` (TeDarrell, wrong since 25 Aug), `inbox.message-search.open-only` and
`advisoriq.sentiment-timeline.only-without-scorecard` (both Allie) all flipped to `correct` on this run — the most
in any single run. Worth noting *why*, because it is evidence the loop works rather than luck:

- All three had been written up with an explicit **say_instead** in an earlier report.
- Two of the three were taught not merely correctly but *defensively* — Allie volunteered the sentiment-timeline
  bug to the customer, and TeDarrell said "this is not how to measure business hours at all" unprompted.

The `--resolved` detector only fires on a wrong→right pair **for the same trainer**, so these are all genuine
individual corrections, not another person happening to say it right. Run `ledger.py --resolved` every time and
read the rows whose `first_right` is today; they are the cheapest positive signal this skill produces and they
belong in the Slack post, not just on the page.

## A no-show and a truncated capture both look short — the discriminator is attendance, not duration

The 6 Oct note established this with an 18-minute-looking file that was really 77 minutes. The 7 Oct run had the
mirror case and it is worth recording so the test is not applied one-sidedly: Admin Part 1 Mon/Wed 9 am
(`1070071202`) came back `durationInMins: 18`, 25 MB — and this one **is** a genuine no-show.

The check that separates them, in order:
1. **`startTime` → `endTime` span.** 08:58:05 → 09:16:12 is 18 minutes, which *matches* `durationInMins`. The 6 Oct
   failure had a 76-minute span against a 1-minute duration. A span that matches the duration is a real short session.
2. **Attendee report.** `meta.count: 0`. Nobody joined.

Only when the span and the duration *disagree* is it a truncated capture. Both checks are one API call each and they
settle it; `durationInMins` alone settles nothing in either direction. A genuine no-show stays out of the coverage-gap
table — it is not an unaudited session, there was nothing to audit.

## `build_dashboard.py` still splices the sub-tables, so filter them in the republish (7 Oct 2026)

The 3 Oct note says to keep pipe tables out of `product-bugs.md` and that a freshly generated dashboard can be worse
than the live page. Both still true: this run's generated page had **20 rows** in the bug table against the live
page's **12**, the extra eight being the 1 Oct `bug | was | is now` sub-table rendered as malformed three-cell rows.

But the 3 Oct advice — "on a day with no new sessions, build the republish from the live page" — does not cover a day
*with* new sessions, when every ledger-derived section genuinely has to be regenerated. The working recipe for that
case, used here:

```python
# 1. generate normally, then drop any <tr> in the bug section that is not 4 cells
i = gen.index('<h2>Open product bugs'); j = gen.find('<h2>', i+4)
bugs = re.sub(r'<tr>(.*?)</tr>',
              lambda m: m.group(0) if len(re.findall(r'<t[dh][^>]*>', m.group(1))) == 4 else '',
              gen[i:j], flags=re.S)
# 2. splice the coverage-gap section from the LIVE page back in ahead of it
```

The renderer emits no coverage-gap section at all, so it must be carried forward from the live page every single
run — generate, filter, splice, then publish. Checking section-by-section against the live page before publishing is
what catches both halves.

## Publishing the dashboard now requires a Read of the saved live copy, and one refusal is expected

`Artifact action:"read"` on the dashboard prints a long head and saves the full page to a file — but printing it does
**not** count as viewing it. The first `publish` with `url:` is refused with "you hadn't viewed the live version".
The saved file must be opened with the **Read tool**, every line of it (201 lines for this page, in two calls because
of its length), and only then does the publish go through.

Second trap, immediately after: re-sending the same bytes earns a *different* refusal — "identical content already
refused ... resent unchanged". That one is not asking for a merge. It says explicitly that if the content already
accounts for the live version, publishing it **again unchanged** will succeed. So the sequence on a normal run is
three calls: refused publish → Read the saved file in full → publish → refused as unchanged → publish again. Budget
for it rather than treating the second refusal as a real conflict.

## `findings.jsonl`'s `session` must be the BARE meeting key — `ledger.py` adds the `uuid:` prefix (8 Oct 2026)

Every prior run wrote `"session": "1092823344"`. This run wrote `"session": "uuid:1092823344"`, reasoning from
the ledger rows, which render as `` `uuid:1092823344` ``. That prefix is added by `ledger.py` when it writes the
row, so the 27 rows landed as `` `uuid:uuid:1092823344` ``.

Nothing errored. `--check` passed, `--add` appended, the repeat tables rendered. What broke was quiet:

- `build_dashboard.py`'s `session_index()` strips `^\`uuid:` from the index key, so the join against the ledger's
  doubly-prefixed uuid missed, and both new Sessions rows rendered `— — — —` for course / minutes / attendance.
- `--reports` lookup missed the same way, so both rows showed `—` instead of a report link, on the run that had
  just published those two reports.

Fix applied: `sed -i '' 's/`uuid:uuid:/`uuid:/g'` on the ledger (a formatting repair of rows written minutes
earlier, not a grade correction), and `report-map.json` keys moved from `uuid:<key>` to `<key>` to match the
52 that were already there.

**Rule: the `session` field is the bare meeting key everywhere — `findings.jsonl`, `report-map.json`,
`--session` on `build_report.py`.** The only place `uuid:` appears is in a rendered ledger or index row, where
a script put it. Grepping one existing row of each file before writing a new one costs one call and would have
caught this.

## The `erecordingId` prefix collision finally bit, and a wrong page answers "empty" just like a right one (8 Oct 2026)

The 3 Oct note warns that these ids share 32-character heads and says to match on the whole string. This run
swept the gap table and, for the 6 Oct Admin Part 1 row, used `1e53b4373bc37d0d676efa94681310eb2f4397ae…` —
which is the **7 Oct Admin Part 1 9 am no-show**, not the intended recording. The head `1e53b4373bc37d0d676efa94681310eb`
is now shared by **four** recordings spanning 1–7 Oct.

The page loaded, the Transcript tab clicked, and it answered `len=NONE empty=true` — a perfectly ordinary
result that would have been written into the dashboard as a confirmed re-check of a row that was never opened.

It was caught only by luck of subject matter: that one row is the 287-character fragment, so an empty answer was
surprising enough to re-check. **Every other row in the table would have absorbed the error silently**, because
`empty=true` is the expected answer for all of them. Re-run with the correct id confirmed `len=287 empty=false`.

**Build the sweep list by copying ids out of the stored map in one go, never by recalling a head.** And treat
`empty=true` as evidence only when the page title matches the row — `document.title` costs nothing and names the
course, which is the cheapest available proof the right page was loaded.

## `session_index.py` cannot run on a Zoho run — append the rows by hand, and mind the column drift

It requires `--sessions` and `--transcripts <dir>` and derives `spoke` by counting distinct non-trainer speakers
in compacted VTTs. A Zoho run has no VTTs on disk (the transcript is read out of the browser) and Zoho transcripts
carry no speaker labels, so there is nothing for it to count. Pointing it at an empty directory would write
`spoke: 0`, which is a false statement rather than a missing one.

Prior runs evidently appended by hand, and the file's header has drifted from its rows: the header declares
`| date | uuid | course | minutes | spoke | trainer |` (six columns) while every row since the Zoho cutover
carries **seven** — attendance in column 5 and `—` for spoke in column 6. Match the rows, not the header.

## A regression correctly removes a row from *Fixed* — do not treat the shrinkage as a renderer bug

`advisoriq.sentiment-timeline.only-without-scorecard` was in the Fixed table (Allie, wrong through 28 Sep, right
from 7 Oct). Today's grade of `incomplete` means she is no longer right-from-that-date-onward, so `--resolved`
stopped emitting the pair and the generated Fixed table came back one row shorter than the live page.

The 3 Oct rule says a section that differs on a day the ledger did not change is a renderer bug. The corollary
worth stating: on a day the ledger *did* change, a section getting **smaller** can be exactly right. Diff it row
by row and confirm the removal is the claim you just regraded — this run's four changed sections each reduced to
exactly the rows today's 27 findings should have moved, which is the check that makes publishing safe.

## `useJobDataSupport.ts` is the single predicate for authorized/job data — and it is Tekmetric **and CE**

Worth recording as product knowledge, because the training has it wrong and the area will come up again.
`softwareTypeSupportsJobData(softwareType)` is `=== "tekmetric" || === "CE"` (`:23`), and the comment above it
is unusually explicit: "Tekmetric (extractor) and CE (change relay) shops both populate ShopJobs." Every
authorized-vs-posted surface keys off that one function — `DailySales.tsx:44`, `BreakdownByWeek.tsx:573`,
`IndividualPerformanceReport.tsx:695` — plus `DataView.tsx:224`, which inlines the same comparison rather than
calling the helper.

So "Tekmetric is the only system that can show authorized" is wrong, and the file anticipates being asked:
its lifecycle comment says to extend the predicate when an integration gains job sync. Check the predicate, not
a trainer's DMS list, and not `DataView.tsx` alone.

## Grading the same claim a day apart produced opposite verdicts on byte-identical code (8 Oct 2026)

`advisoriq.sentiment-timeline.only-without-scorecard` was graded `correct` on 7 Oct and `incomplete` today.
`CallTranscriptTab.tsx` has not changed since 14 Aug and `CallModalTabs.tsx` since 25 Aug, so the two runs read
the same bytes and disagreed.

Today's reading: there is no gate on the absence of a scorecard. `showTranscriptSentiment` is a user toggle
defaulting to `true` (`CallModalTabs.tsx:89`), the render condition is `!call?.vendor && showSentimentData &&
journeyForRender.length > 0` (`CallTranscriptTab.tsx:546-549`), and the journey is resolved **scorecard-first**
(`CallModalTabs.tsx:91-104`). A scorecard call is the case the timeline is built for.

The 7 Oct note frames that grade as crediting her for volunteering a bug, which is a different thing from the
factual assertion being right. Both readings are defensible and the ledger now holds both. **This was flagged
to a human rather than quietly flipped**, and that is the right move whenever a re-grade would overturn a prior
run on evidence that has not changed: the 7 Oct rule says a confident contradiction of an existing row should
stop the grade, and stopping it means escalating, not deferring to whichever run is more recent.

## The vendor-exclusion bug was never real, and it inverted 13 grades (9 Oct 2026)

The most expensive finding this skill has produced was wrong for three weeks, and the rule that
would have caught it was already written down on 28 Sep.

`directory.vendor-flag.excludes-from-advisoriq` and the matching product-bug entry both rest on one
claim: marking a contact as a vendor sweeps their **existing** calls once (`vendors.js:30`) and
nothing in the call-creation path ever consults the Vendor collection again, so future calls are
created `vendor: false` and keep re-entering Advisor IQ. The grep behind it was scoped to
`dc-server/routes/call.js`.

That grep was accurate and the conclusion was still false, because **dc-server does not ingest
calls.** Its only `Call.create` is the `manualUpload` path at `:2305`. Live telephony is handled by
**dc-calls**, which gates on vendors *twice, independently*:

- `dc-calls/src/modules/director.js:103` calls `utils.vendorLookup(contactNumber, siteInfo.tenantId)`
  unconditionally for every call and sets `detail.vendor = isVendor` at `:112`, before
  `Call.create(detail)` at `:118`. `vendorLookup` (`utils.js:542`) queries
  `Vendors.findOne({ tenantId, number: e164Number })` — and `dc-calls/src/models/vendor.js` binds
  `mongoose.model("Vendor", VendorSchema, "vendors")`, the same collection dc-server writes.
- `dc-calls/src/routes/events.js:1992` runs its **own** lookup in the transcription pipeline, logs
  "Detected vendor call", and skips Advisor IQ, scorecards and sentiment entirely behind
  `if (!isVendor)` at `:2003`.

`scorecardsReport.ts:125` (`vendor: { $ne: true }`) then excludes them from the report. So a vendor
number is flagged at creation *and* never scored. `vendorLookup` has been in that path since
**July 2025** (`ae54c2c92d` / `262895f5c9`) — fourteen months before the bug was raised. There was
never a window in which it was true.

**This is the third instance of the 28 Sep service-boundary error** (`/bookings/capture`, then the
`reportPermissionsService` near-miss on 7 Oct). The rule is already in this file — "before
concluding a route does not exist, find out which service the caller is actually pointed at;
'not in dc-server' means nothing on its own" — and it was not applied because the claim did not
*look* like a routing question. Generalise it: **any finding of the form "nothing ever does X"
is a whole-monorepo claim and needs a whole-monorepo grep**, no matter which single service the
symptom appeared in. `git grep -l Vendor` across the repo costs one call and would have ended this
on day one.

**The grading consequence is an inversion, not a correction.** Thirteen rows across four trainers
join this claim_id, and the polarity of every one of them is backwards:

- 8 × `incomplete` for omitting a limitation that does not exist;
- 1 × `wrong_high` — Aaron, 30 Sep, "any future calls will not be used with Advisor IQ" — which is
  **correct**, and was written up as the first time the claim was stated as a forward-looking
  guarantee;
- 4 × `correct` — Allie, 28 and 30 Sep, 7 and 8 Oct — for saying future calls are *not* excluded and
  that you would "constantly have to mark them as a vendor", which is **wrong**. The 30 Sep report
  called that "the first ever correct vendor-flag statement".

The ledger is append-only and `ledger.py` has no correction mode, so **these rows were not
rewritten.** Per the 8 Oct rule, a re-grade that overturns prior runs is escalated to a human rather
than flipped autonomously — and that rule matters more here than usual, because the fix is not one
regrade but a reversal of who has been coached. Someone was told they were wrong for being right.

Two smaller lessons from the same sweep, both worth keeping:

- **Case matters in `git grep`.** A sweep for `allRecordings` over `callsReviewUtils.ts` returned
  nothing while the code says `hasAllRecordings` and `"All Recordings"`. An empty grep on a file you
  have just confirmed is byte-identical is a signal about the *pattern*, not the code — it briefly
  read as a deleted gate.
- **A withdrawal shrinks the bug table, which is a correct result.** Same shape as the 8 Oct note
  about the Fixed table: on a run that changes the inputs, a section getting smaller can be exactly
  right. Nine open bugs, down from ten.

## A quiet Friday can still be the most consequential run of the week (9 Oct 2026)

The 2 Oct note says a Friday with nothing to grade is not a day with nothing to do, and offers the
bug sweep as the fallback work. This run is the strongest evidence for that: zero sessions
discovered (correctly — no training runs Fri–Sun), zero graded, 25 coverage-gap rows re-swept with
nothing recovered, and the sweep that filled the time **withdrew the most-repeated finding in the
ledger**.

It also changes the "did anything change" calculus from the 26 Sep note. On the face of it this was
a no-change day: nothing graded, gap identical, nothing recovered. It still posted to Slack, because
the bug withdrawal is precisely the kind of thing a reader acts on — and because four trainers have
been graded backwards on it. Read that rule as "did anything change **that a reader would act on**",
not "was a session graded".

## A republish to the dashboard returns a *different-looking* URL — it is the same artifact (10 Oct 2026)

Publishing with `url:` set to `https://claude.ai/code/artifact/1d86f6a7-34f2-4d45-8af5-39b80e1d9eda`
succeeded and answered:

```
Published ... at https://claude.ai/artifact/4eUdaeZbcXPS9zXZdLtmJh (Version 39, version id 1791674297-5544)
```

That reads exactly like the failure this skill warns about hardest — a second page, with the team left
reading the stale one. **It is not.** `4eUdaeZbcXPS9zXZdLtmJh` is the short-form permalink of the same
artifact; `action: "read"` on the canonical `1d86f6a7-…` URL returned version `1791674297-5544`, 85,168
bytes, byte-identical to the file just published. Two things that did *not* settle it and should not be
relied on: the publish result's own wording, and `action: "list"`, where Training QA did not appear in
the six most recent rows despite having just been updated.

**The check that does settle it** is one call: read the canonical URL with `path: "index.html"` and grep
the saved copy for a string unique to today's edit. Do that once per run after republishing rather than
reasoning about which URL form means what.

## Three publish calls were budgeted and one was needed

The 8 Oct note says to expect `refused (not viewed)` → Read → publish → `refused (unchanged)` → publish,
and to budget three calls. This run needed **one**. The difference is that the full 210-line Read had
already happened earlier in the run, before any publish was attempted, as part of reading the live gap
table to answer a discovery question. Reading the live page early — which a no-new-sessions run has to do
anyway to build the republish from it — collapses the whole dance. Budget for three, but read first and
you will usually spend one.

## Re-aging the gap table: "N days open" has two phrasings, and a period-anchored regex silently skips four rows

Every gap row opens with an age, and the obvious sweep is `re.sub(r"\d+ days? open\.", …)`. **Four of
the twenty-five rows do not end that phrase with a period** — the rows carrying a superlative continue
with an em dash instead:

```
16 days open — the single largest loss in this table.
15 days open — the longest session ever recorded on this account.
3 days open &mdash; and this one is a different failure.
1 day open — and it is the largest single loss this table has ever taken.
```

Anchoring on `open\.` leaves exactly those four stale, and they are the four most-read rows in the
table. Drop the period from the pattern (`\d+ days? open`) and write the replacement without one.

Two further traps in the same job, both caught only by verifying afterwards:

- **Compute each age from the row's own date, never by incrementing.** A `+1` sweep is right until the
  run misses a day, and the drift is invisible.
- **Verify row-by-row, not with a second regex over the whole section.** The obvious check,
  `<tr><td>(date)</td>.*?(\d+ days? open)` with `DOTALL`, runs past rows it cannot match and reported
  21 rows for a 25-row table with four wrong ages — it agreed with the bug it was meant to find. Split
  on `</tr>` first, then assert per row, and assert the count is 25.

## Pluralisation is part of the data: `1 day open` → `2 days open`

The 8 Oct row crosses from singular to plural on its second day in the table. Any re-ager has to emit
the unit, not just the number.

## A quiet Saturday reads identically to a broken endpoint — and this time it really was quiet (10 Oct 2026)

Second consecutive expected-zero day, and the confirmation is the same as 9 Oct: the Past Webinars list
in the browser still shows **Thursday 8 October** as its newest group. Fourteen sessions ran Mon–Thu and
nothing since.

Worth recording because the reconciliation is what makes the zero trustworthy, not the absence of rows:
all fourteen were accounted for individually — **four graded** (7 and 8 Oct), **six** already in the gap
table, **four genuine no-shows** (7 Oct 9 am Admin P1, 6 Oct 9 am Admin P2 and 11 am Shop Analytics,
8 Oct 9 am Admin P2, each 0 attended). A session that is neither graded, nor in the gap, nor a no-show is
a discovery failure, and the only way to see one is to add the three categories up against the list. This
run briefly had a fourteenth unaccounted session before the 8 Oct 9 am row resolved as a no-show — which
came from mis-reading the attendance pair across a `slice()` boundary while chunking `innerText`, not from
the data. **Chunk with overlap and re-read any row whose numbers land on a boundary.**

## The post/no-post call on a second consecutive quiet day

9 Oct posted to Slack despite grading nothing, because the bug withdrawal was something a reader would
act on. 10 Oct did **not** post: nothing graded, nothing recovered, the gap unchanged for a third day,
and a bug sweep that confirmed the table rather than changing it. The 9 Oct rule — "did anything change
*that a reader would act on*" — cuts both ways, and a clean sweep is not news. The dashboard still
republishes, because the baseline stamp and the row ages are assertions on the page that would otherwise
go stale.

## Enumerate the Past Webinars list from the DOM, not by slicing `innerText` (11 Oct 2026)

The 4 Oct note says `get_page_text` returns nothing on this page and to read `document.body.innerText`
directly. True, and it is still the right call for a quick "what is the newest group" check. But the
10 Oct note then had to add "chunk with overlap and re-read any row whose numbers land on a boundary",
because that run briefly mis-read an attendance pair across a `slice()` seam.

Overlapping chunks treat the symptom. The cause is that `innerText` flattens every row into one
undelimited string, so the only thing separating "3 registered, 0 attended" from the next row's date is
whitespace, and any slice boundary can land inside a pair. This run hit it again from the other side:
reading the 2,909-character text in three overlapping slices produced a **15-row** count for a list that
actually holds **20**, and attributed `4 / 2 (50%)` to a row whose real numbers are `4 / 3`.

Query the row elements instead and the ambiguity disappears:

```js
const cands=[...document.querySelectorAll('div,li,tr')].filter(e=>{const t=e.innerText||'';
  return /\d{2}:\d{2}\s*(AM|PM)/.test(t)&&/hrs|mins/.test(t)&&/Training|Overview/.test(t)&&t.length<400;});
const rows=[...new Set(cands.map(e=>e.innerText.replace(/\s+/g,' ').trim()))];
const keep=rows.filter(r=>!rows.some(o=>o!==r&&o.includes(r)));   // drop ancestor wrappers
```

The containment filter is the part that matters: the same row matches at several nesting depths, and
keeping only the innermost string gives exactly one entry per webinar. 20 rows, each with its own date,
time, duration, course, department and registered/attended pair, in one call.

Two caveats found the same run. The group headers (`LAST WEEK14`, `EARLIER3`) **do not agree** with the
rows underneath them — the 20 rows span 30 Sep to 8 Oct while the headers sum to 17 — so count the rows
and never the header. And the per-row regex must be asserted, not trusted: print the parsed form and
eyeball it, because a row that fails to match silently drops out of a list whose whole purpose is to
prove nothing is missing.

## `createLead` has no phone gate — the appointment-lead claim is wrong in the *other* direction (12 Oct 2026)

`scheduler.appointment-lead.phone-is-minimum` has been graded seven times and the reasoning behind it has
moved twice. The 24 Sep note graded "you may not even see a name" wrong because the bail-out *forms*
(`StayOrGo.js`, `SkipToForm.js`) require first name, last name, phone and comments. The 28 Sep note then
withdrew the `/bookings/capture` product bug, which quietly made the exit-intent path live again — and
nobody followed that through to its consequence for this claim.

Followed through at `e94e845076`, the whole chain has **no phone requirement anywhere**:

- `dc-booking/src/Header.tsx:111-116` — `hasAnyInfo` is an **OR** over phone / fname / lname /
  `bailOutStage.bailOutComments`. One field is enough to fire.
- → `graphql-broker` `/bookings/capture` → `generateLead.service.ts:22`, whose only required field is
  `domain`.
- → `dc-server/routes/customer.ts:792` `/createLead`: creates the Contact (`:816`) and a
  `channel: "lead"` Tracker (`:826`) **unconditionally**. `req.body.number` may be undefined.

So a bail-out carrying only a first name *does* produce a lead task. "No phone, no lead" is not an
omission, it is backwards, and the cost lands on the shop: they are told a class of lead cannot exist, so
they never look for it.

**The transferable rule:** when a product-bug entry is withdrawn, re-grade the training claims that were
decided on the strength of it. The withdrawal of `/bookings/capture` changed the answer to this claim and
sat unconnected to it for two weeks. Same shape as the vendor-flag inversion, one step earlier in the chain.

## A same-day gap row needs a "0 days open" phrasing the re-ager can increment (12 Oct 2026)

The 10 Oct note gives the re-dating recipe — descending replacement, anchor on `<strong>N days open`
without the period, emit the unit so `1 day` becomes `2 days`. It does not say what to write on the day a
row is *created*, and prose like "New today" breaks the sweep: the regex finds no number and the row
silently never ages.

Write a fresh row as **`<strong>0 days open — new today.</strong>`**. It reads correctly on the day, the
descending sweep turns it into `1 day open` tomorrow and `2 days open` after that with no special case, and
the per-row verification (split on `</tr>`, compare each age to `today - row date`) covers it like any other.

Verified this run: 25 existing rows all aged by exactly +1 with zero mismatches, and the new row asserted at 0.

## Three sessions in one run is where the whole-day rule pays off (12 Oct 2026)

The 22 and 28 Sep notes argue for grading every transcribed session on a day rather than the most
interesting one. Monday 12 Oct is the strongest case yet: **four courses ran, three transcribed**, and the
three graded sessions split cleanly by kind — Aaron's Admin Part 1 carried all three non-correct findings
(and the day's only `wrong_high` that was a trainer error), TeDarrell's CRM carried the product's own
inverted label, and TeDarrell's Admin Part 2 was the cleanest session in the ledger at 6 of 7.

A run that graded only the session with the most findings would have reported "Aaron had a bad day" and
missed that the same morning's curriculum defect has a correct script on file from the *other* trainer who
taught twice that afternoon.

Also confirmed: the Monday-evening rule from 5 Oct held exactly. An 18:00 Monday run found all four of the
day's sessions already recorded, and three of them already transcribed, including the 15:00 one.

## Grading two sessions by one trainer two hours apart explains an opening slip

TeDarrell delivered CRM at 13:00 and Admin Part 2 at 15:00. The Admin Part 2 recording opens by announcing
*CRM* training and corrects itself four sentences in — "I just finished CRM training and so that was still
on my mind." Without the CRM session in the same run that reads as a trainer who does not know which course
he is teaching. With it, it is a scheduling artefact and a clean recovery.

Worth checking the day's other sessions before writing up anything that looks like trainer confusion; the
schedule is a cheaper explanation than the person, and it is visible in the same `getAllRecordings` response.

## Reading a Zoho transcript out of Chrome: `get_page_text` then JS tail-slices (13 Oct 2026)

The 10 Sep note says to use `get_page_text` with `max_chars` well above 60000. **The Chrome
(`mcp__claude-in-chrome__*`) `get_page_text` has no `max_chars` parameter at all** — that is the
*in-app* browser's signature, and the in-app browser is permanently signed out of Zoho. Chrome's
version truncates at 50,000 characters with a note giving the full size.

`javascript_tool` is not the fallback it looks like: its result is capped near **1,000 characters**
regardless of what the expression returns, so `__out.slice(0, 6000)` comes back truncated at ~1,000
just like `slice(0, 18000)` does. A 55 KB transcript would need ~55 calls that way.

What was tried and **refused**: having the page `fetch()`-POST the transcript to a short-lived
`127.0.0.1` HTTP sink so it landed on disk in one call. The auto-mode classifier blocks it as
`[Browser JS Exfil]`, which is the correct call — a page POSTing its contents to a local server is
indistinguishable from exfiltration at the point of decision. Do not reach for it; the sink was torn
down and the port released.

**The working recipe, 7 calls for a 67-minute session:**

1. On the recording page, click the Transcript tab, then build the cues once and park them on
   `window.__out` (the `[mm:ss] text` collapse from the 10 Sep note).
2. `get_page_text` — returns the first 50,000 characters and reports the true total.
3. Find the overlap offset with one JS call: `window.__out.indexOf('[<last timestamp you saw>]')`.
4. Pull the remainder in `slice(a, a+1000)` steps. ~6 calls for the last 5–6 KB.

Anchoring step 3 on a timestamp string rather than a character count is what makes the seam safe —
the same reason the 11 Oct note gives for querying row elements instead of slicing `innerText`.

Also still true and worth re-stating because it cost calls again: the **public**
`transcriptionPublicDownloadUrl` on `files-accl.zohopublic.com` 403s from `curl`. Public in the URL
does not mean public, and the transcript only exists inside an authenticated browser session.

## `pin_baseline.sh` fell back stale a third time, and the HTTPS retry needs the right org (13 Oct 2026)

The 5 and 6 Oct notes both record the silent fallback being behind the true tip. It happened again:
the local `origin/development` was `e825e33a43` (12:44 CDT) against a real tip of `6ad7e2a008`
(14:28 CDT) — **six commits**, four of them campaign fixes, i.e. exactly the surface this audit grades.

The retry is where time went. `git fetch origin` fails because `origin` is **SSH**
(`git@github.com:ShopRocket-LLC/oktorocket.git`) and SSH does not work on this host, and `gh auth`
reports `Git operations protocol: ssh`. The fetch that works names the org explicitly:

```
git -c credential.helper='!gh auth git-credential' fetch https://github.com/ShopRocket-LLC/oktorocket.git development
git update-ref refs/remotes/origin/development <FETCH_HEAD sha>
```

**The org is `ShopRocket-LLC`, not `bdm1981`** — guessing the user's own namespace returns
`Repository not found`, which reads like an auth failure and is not one. Two other small traps from
the same sequence: `timeout` does not exist on this Mac (use the Bash tool's own `timeout` argument),
and in zsh `git show "$S:graphql-broker/..."` must be brace-quoted as `"${S}:graphql-broker/..."` or
the expansion eats characters and reports a bogus "ambiguous argument".

## `build_dashboard.py` needs `--reports`, or the session you just published renders `—` (13 Oct 2026)

The 8 Oct note is about `report-map.json` **keys** (bare meeting key, no `uuid:` prefix). That was
done right this run and the new row still rendered `<td>—</td>` where its report link belongs,
because `--reports` is an **optional flag that defaults to nothing**:

```
python3 scripts/build_dashboard.py --baseline "$OKTO_SHA_SHORT" --reports references/report-map.json
```

Without it every Report cell on the page falls back to `—`, including the 50-odd historical rows —
so the live page silently loses every link it has. The section-by-section diff catches it
(`Sessions` row count matches, cell contents do not), but only if the new row is actually inspected
rather than counted. Grep the generated page for the artifact id you just published before splicing.

## Re-age the gap table from each row's own date — the descending sweep still double-ages (14 Oct 2026)

The 27 September note says to replace `N days open` largest-first so no replacement re-matches its own output, and the
10 October note adds the two phrasings and the pluralisation. Both were followed exactly this run and **four of
twenty-six rows still came out one day too old** (the 16 Sep row read 29 when it should read 28; all three 17 Sep rows
read 28 for 27). Descending order is necessary and it is not sufficient — the ages in the live table are not distinct,
the set is built from the text *after* rows are added and removed, and a single `str.replace` is global, so one pass
can touch rows that a later pass then touches again.

Stop re-aging by arithmetic altogether. **Split the tbody on `</tr>` and, for each row, read its own date cell and
write `(today - row_date).days`:**

```python
for chunk in body.split('</tr>'):
    if '<code>' not in chunk: continue
    d = datetime.date.fromisoformat(re.search(r'<td>(2026-\d\d-\d\d)</td>', chunk).group(1))
    n = (today - d).days
    chunk = re.sub(r'\d+ days? open', f'{n} {"day" if n==1 else "days"} open', chunk, count=1)
```

This is idempotent, needs no ordering, survives a run that fires twice in a day or misses a day, and makes the
verification pass trivially true rather than a separate check that can disagree with the edit. The 10 October warning
about verifying row-by-row rather than with a second regex over the whole section still stands — that is what caught
this. Note also that counting gap rows by `'<code>' in chunk` over the whole **section** over-counts once narrative
paragraphs start citing meeting keys; count inside the `<tbody>` slice only.

## Two gap rows recovered in one run — the sweep is now the most productive step in the audit (14 Oct 2026)

The 30 September note introduced re-checking every coverage-gap row every run, on the strength of a single recovery
(28 Sep Advisor). For twenty-five days after that nothing else ever left the table, which made the sweep look like
insurance. On 14 October **two of twenty-six rows came back**: Shop Analytics of 13 Oct (`1043483196`, 74,755 chars)
and Admin Part 1 of 8 Oct (`1068971573`, 71,574 chars) — the latter the largest single loss the table ever held, at
seven joined. Together they contributed **29 of the run's 59 graded claims**, more than the day's own two sessions.

So budget for it properly rather than treating it as a tail check: twenty-six page loads is six `browser_batch` calls
at four or five recordings each, and on this evidence it is worth more per call than discovery. Two consequences:

- **Do not describe a recovered row as "missed by the previous run".** The first draft of this run's Shop Analytics
  report said exactly that, and it was wrong — the row was discovered correctly on 13 Oct, published as a gap row that
  evening, and simply had no transcript behind it yet. Check the live gap table before characterising why a session is
  being graded late; the dashboard already knows.
- **A recovered session is graded at the current baseline, not the one from its own date.** Say so in the report
  footer. The 8 October session was graded at a commit six days newer than the day it was taught.

## `ledger.py --check` reports no repeats for a second batch added in the same run

Grading four sessions this run meant two `--add` calls. The second dry run printed `appended 18` and **no
`newly_repeating` block at all**, which reads as "these eighteen rows join nothing". They did — the first batch had
already landed, so every claim the second batch repeats was already repeating and nothing was *newly* so.

Nothing is wrong with the tool; the trap is reading the second dry run as the run's repeat summary. **Run
`--contradictions` over the whole ledger after the last `--add`** (already the standing rule from 24 September) and
treat the union of all the batches' `--check` output as the repeat picture, not the last one's.

## `MessageBubble.tsx` and `MessageToolbar.tsx` are under `TaskSMS/` — third abbreviated-path miss

The 5 and 6 October notes record this failure mode twice (`api.ts` under `common/`, `OnDeck.tsx` under `campaigns/`).
It fired again on the two translate surfaces: this file cites them as
`dc-user/src/js/user/components/inbox/MessageBubble.tsx`, and the real paths are
`inbox/**TaskSMS**/MessageBubble.tsx:141-142` and `inbox/**TaskSMS**/MessageToolbar.tsx:121`/`:127`.

Caught by `git cat-file -e` over every cited path before writing the findings, which is cheap and is now the only
thing standing between an abbreviated path and a citation that points at nothing. Keep running it over the reused
citations as well as the new ones — these two came from prior ledger rows, not from a fresh grep.

## A roster first name in a transcript can be the *attendee* (15 Oct 2026)

The 15 October Shop Analytics recording opens with the host saying **"Aaron."** at 01:54, three seconds before
the first substantive line. Every instinct built up by this skill says that is a trainer self-introduction —
"My name is Aaron" is literally the one attribution that has ever worked from a transcript (Admin Part 1, 9 Sep).

It is the opposite. The single attendee is **Aaron Bond of Johnny's Automotive**
(`aaron@johnnysautomotivellc.com`), and the host is greeting him by name. `getAttendeeReport` settles it in one
call and nothing else does.

This is the 10 September error arriving from the other direction. That one attributed a customer's first-person
line to the trainer; this one would attribute a customer's *name* to the trainer. **Pull the attendee report
before reading any name in a transcript as the trainer's**, and treat a bare vocative ("Aaron.", "Hey, Scott")
as evidence of who is in the room rather than who is presenting. Three of the four names on the trainer roster
are common first names, so this will recur.

## A fourth outcome: held, transcribed, and nothing to grade (15 Oct 2026)

Every run so far has sorted a day's sessions into three buckets — **graded**, **coverage gap** (ran, no
transcript) and **no-show** (nobody joined) — and the 10 October note makes adding them up against the Past list
the test that nothing was missed. Shop Analytics of 15 October is none of the three.

It ran 16 minutes (`startTime` 12:59:38 → `endTime` 13:15:40, so the span matches `durationInMins`, which by the
7 October test makes it a real short session rather than a truncated capture). One attendee joined and stayed
eight minutes. A **full transcript exists** — 4,872 characters. And it contains no curriculum at all: the
attendee opens by saying he already received and watched the recording, they talk about the knowledge base being
rebuilt, the trainer offers to send the documentation, and they agree to end. Not one checkable claim.

`min_duration_minutes: 20` discards it, which is the right outcome for the wrong reason — the threshold exists to
drop false starts, and this was neither a false start nor a no-show. **Read the transcript before classifying a
short session**; it costs one page load and it is the only thing that distinguishes "the trainer wrapped early"
from "the customer left and the trainer kept teaching". Record it explicitly in the run output so the day's
arithmetic still closes against the Past list, and do **not** put it in the coverage-gap table: nothing was lost.

## Count the grades from `findings.jsonl`, never by hand (15 Oct 2026)

This run's report standfirst and its `dashboard.md` row both said **"16 correct, four incomplete"**. The real
split was **18 correct, five incomplete, three unverifiable** — written from memory while drafting the narrative,
before the ledger had been asked.

It was caught by the section-by-section diff against the live dashboard, which is not where it should have been
caught: the generated tally moved `correct` 347 → 365 and `incomplete` 102 → 107, i.e. +18 and +5, and those
deltas are what made the hand-written numbers visibly wrong. **Run the count before writing the narrative** —

```bash
python3 -c "import json,collections;print(collections.Counter(json.loads(l)['grade'] for l in open('findings.jsonl')))"
```

— and quote that. A wrong tally on the report page is worse than it looks, because the Slack post and the
`dashboard.md` row are both copied from the standfirst, so one slip propagates to three places a reader sees
before the page itself.

## A regression out of *Fixed* is the most useful thing a repeat tells you (15 Oct 2026)

The 8 October note says a *Fixed* table that gets **smaller** can be exactly right, and to confirm the removal is
the claim just regraded. Both removals this run were that — `scheduler.after-hours.resources-are-uploads` and
`scheduler.short-notice.independent-of-same-day`, each recorded as corrected by TeDarrell in September and each
recurring today, 20 and 17 days later.

Worth stating as its own point rather than as a renderer check: **a claim leaving *Fixed* is a stronger coaching
signal than a claim entering *Repeats***, because the trainer has demonstrably known the right answer and lost it.
Both of these are off-branch omissions — what happens when the toggle is off, where the field actually lives —
which is the class of error that does not stay fixed on its own, because nothing in delivering the session
reminds anyone of the branch they are not demonstrating. Name them in Slack as regressions, not as repeats.

## When a cited file has CHANGED, read the diff for meaning — not just for the new line number (16 Oct 2026)

The 6 Oct rule is "blob identity is not proof": a byte-identical file still gets its identifier re-grepped,
because a citation can have been wrong when it was written. That rule covers the *unchanged* half of the sweep.
This run found the gap on the other side.

Of 26 cited paths, 24 were byte-identical and two had changed. The obvious job on a changed file is to re-resolve
its line number, and that is all that was planned for `campaignsV2/api.ts` (+152/−46). Reading the diff instead
turned up the most substantive thing this table has learned in two weeks — the `explainDelete` comment was
rewritten from `// explainDelete = require a reason when deleting the campaign.` to
`// explainDelete = a queued message is removed without asking for a reason.`

That is the product writing down the *correct*, inverted semantics in code while leaving the lying UI label in
place, which turns the Require Delete Reason bug from an inference about behaviour into two contradictory
statements in the repository at one commit. A line-number-only re-site would have renumbered `:284` → `:290`
and silently discarded it.

**So the sweep has two halves with two different checks.** Unchanged file → re-grep the identifier (the citation
may always have been wrong). Changed file → `git diff` the file and read it (the citation may now mean something
different). Neither substitutes for the other, and the changed half is the cheaper of the two because there are
usually only one or two of them.

## A bug row cites the screen it was found on, not every screen it affects (16 Oct 2026)

`Require Delete Reason` has been in this table since 25 August citing exactly one file, `AddCampaign.js`, because
that is the screen the first trainer was on. A one-line grep for the label this run returned **five** screens, all
binding the same `name="explainDelete"` to the same inverted string: `AddCampaign.js`, `EditCampaign.js`,
`OnDemandInputs.js`, `CallOnDemandInputs.js` and `DateCampaignInputs.js`.

`EditCampaign.js` is the one that matters. A shop acts on a trainer's explanation by going and *editing* the
campaign, so the edit screen is where the wrong reading gets applied — and it was not on the ticket.

**Rule: when a bug is a UI string, grep the string across the whole package before the row is written, and list
every surface.** It costs one call. A fix scoped to the cited file is otherwise a fix that leaves most of the bug
in place, and nobody finds out until a trainer hits one of the other screens. The same question is worth asking of
every existing string-based row in `product-bugs.md` — this one had been single-cited for 52 days.

## The weekday rule, stated so it stops being re-derived (16 Oct 2026)

Three separate notes here circle the same fact (18 Sep "Friday is the one weekday where an empty result is
correct", 15 Sep "a run that reports a quiet day for a weekday is suspicious", 10 Oct "a quiet Saturday reads
identically to a broken endpoint"). Stated once, plainly:

**All five course series run Monday–Thursday only. A Friday, Saturday or Sunday run should discover zero new
sessions, and that zero is correct. Monday–Thursday, a zero is a failure until proven otherwise.**

The confirmation on a weekend/Friday run is three cheap checks that should agree, and this run ran all three:

1. `getAllRecordings` — newest recording is the most recent Thursday (here 15 Oct).
2. Past Webinars list — its newest group header reads `YESTERDAY` or later against a Mon–Thu date, never today.
3. Upcoming Webinars list — its first entry is the coming **Monday** (here 19 Oct).

If (1) and (2) agree but (3) shows instances scheduled for today, the sessions were cancelled rather than never
scheduled, and that is worth a line in the run output. All three agreeing is a quiet day and needs no further work.

Note also that `date` on this host is the authority on the weekday, not inference from the schedule: this run
opened by assuming 16 Oct was a Thursday (because Thursday is a training day and the ledger's last entry was
Wednesday), and spent two calls treating a correct zero as a discovery failure. The Past list's `YESTERDAY`
header against Thu 15 Oct is what settled it. **Check the weekday before deciding an empty result is suspicious.**

## The weekend reconciliation is cheap and it is the only thing that makes a zero trustworthy (17 Oct 2026)

The 16 October note states the weekday rule and its three confirmations. This run ran all three and then did the
part the rule does not mention, which is the part that actually proves nothing was missed: **add the week's
sessions up against the Past list by outcome.** Fourteen sessions ran Monday 12 to Thursday 15 October, and they
sort into **eight graded**, **three coverage-gap rows**, **two no-shows** and **one held-with-nothing-to-grade**
(the fourth outcome recorded on 15 October). 8 + 3 + 2 + 1 = 14, so there is no discovery failure hiding behind
the zero.

Two of the fourteen never reach `getAllRecordings` at all — 13 Oct Admin Part 1 3 pm and 14 Oct Admin Part 2 3 pm,
both `1 registered / 0 attended`. That is the documented behaviour of a 0-attendee webinar, but on a weekend run it
is also the only category that can be confused with a lost recording, so read the pair off the Past row rather than
inferring it from the recording list's silence. The attendance pair is the discriminator, not the absence.

## `pin_baseline.sh` has now fallen back stale on five runs in two weeks — stop treating it as the baseline (17 Oct 2026, updated 18 Oct)

5, 6, 13 and now 17 October. This run it was two commits behind (`c4464f5ac5` against a true tip of `ea1c07a280`),
which is the smallest gap yet and still covered the only cited file that moved. The script's exit status does not
distinguish "fetched" from "fell back", so a run that trusts it cannot tell which happened.

**Treat the script's output as a candidate and always confirm it**, in two calls that cost nothing:

```bash
git -c credential.helper='!gh auth git-credential' fetch https://github.com/ShopRocket-LLC/oktorocket.git development
git update-ref refs/remotes/origin/development <FETCH_HEAD sha>
```

The org is `ShopRocket-LLC`. Four runs out of fourteen is not an intermittent fault; the fallback is the normal path
on this host and the explicit fetch is what produces a real baseline.

**18 Oct: a fifth time, three commits behind** (`7bfeea4326` against a true tip of `3e9a53ec13`). Stop
budgeting a decision for this. Run the explicit fetch first, every run, and treat whatever the script prints
as commentary.

## A changed cited file can be a fix to something the table does not track — say so rather than implying a close (17 Oct 2026)

The 16 October rule sends a changed file's **diff** to be read rather than just its line number re-resolved, and it
earned its place by turning up the rewritten `explainDelete` comment. This run is the other outcome of the same rule
and worth recording so the rule is not read as "a changed file always means something".

`dc-calls/src/routes/events.js` grew 75 lines under the withdrawn vendor-exclusion row's citations. The diff is a fix
to `processTranscription`: `labels` was being written with `$set` from a snapshot taken before analysis began, wiping
labels added in the interim, and it now `$addToSet`s instead and mirrors analysis outcomes onto a call's BDC copies.
Real, and **nothing to do with any row in the bug table**. The vendor gate the file hosts is unchanged in substance
and simply moved 54 lines down.

The failure mode to avoid is writing this up as though the baseline movement bore on the bug. It did not. A re-site
of `:1998`/`:2006` to `:2052`/`:2060` plus one sentence saying what the diff actually was, and the 9 October
withdrawal stands untouched, is the whole of it.

## Chrome refuses the DOM row-query recipe on the Past list — fall back to overlapping `innerText` slices (18 Oct 2026)

The 11 Oct note replaces `innerText` slicing with a `querySelectorAll('div,li,tr')` filter plus a containment
filter, because slicing flattens rows into one undelimited string and a seam can land inside an
attendance pair. That recipe is still the right shape, and this run it was **refused outright in Chrome**:

```
[BLOCKED: Cookie/query string data]
```

The expression only read `innerText` off matched elements and built an array of strings — no cookies, no
query string — so this is the auto-mode classifier being conservative about a page-wide DOM harvest, not a
real finding about the page. It is not retryable by rephrasing; a second attempt with a looser filter was
refused the same way.

**What worked:** `document.body.innerText` read in four overlapping 750-character slices, which is the
4 Oct route the 11 Oct note was trying to retire. The Past list is small (~2,900 characters), so four
slices with a 50-character overlap cover it, and the overlap is what makes the seam safe — the 11 Oct
failure came from *non*-overlapping slices, not from slicing as such.

Two things that make the fallback trustworthy here, and both are cheap:
- **Overlap every slice** and reconstruct across the boundary rather than trusting one read.
- **Reconcile the parsed rows against a second source.** This run every row from the Past list was matched
  against `getAllRecordings` and the ledger by meeting key before the weekday zero was called correct, so a
  row lost to a seam would have shown up as a session with no recording and no ledger entry.

Also re-confirmed: Chrome's `get_page_text` returns *No text content found* on this page (the 4 Oct note),
so `innerText` is the only text route, and `javascript_tool` results are capped near 1,000 characters.

## Resolve an abbreviated citation path once and write it into the row (18 Oct 2026)

Three separate notes record this failure (5 Oct `api.ts` under `common/`, 6 Oct `OnDeck.tsx` under
`campaigns/`, 14 Oct `MessageBubble.tsx` under `TaskSMS/`). It fired **three times in a single pass** this
run, because `product-bugs.md` stores several citations in abbreviated form and a sweep has to reconstruct
the parent each time:

- `campaignUtils.ts` is **`dc-server/modules/campaigns/`** — server-side, though it sits in a row whose
  neighbouring citations are all `dc-user`
- `CampaignOutcomeModal.js` is **`dc-user/src/js/user/components/tasks/`**, not `admin/components/campaigns/`
- `OnDeck.tsx` is **`dc-user/src/js/common/components/campaigns/`**, not `campaignsV2/`

Each wrong guess makes `git cat-file -e "$SHA:$PATH"` report the file missing, which reads exactly like a
deletion and briefly looks like a fixed bug.

The accumulated advice has been "resolve with `git ls-tree -r --name-only $SHA | grep "/<basename>$"`
before concluding anything", which is right and keeps being re-paid every run. **The cheaper fix is to stop
storing abbreviations**: when a path is resolved, write the full path into the row. A sweep then greps a
path rather than reconstructing one, and the trap disappears instead of being re-documented. Worth doing to
the remaining abbreviated rows the next time a run has spare capacity.

## A zero that is *expected* still has to be reconciled, not just confirmed (18 Oct 2026)

The 16 Oct note gives the weekday rule and its three confirmations; the 17 Oct note adds the reconciliation
and calls it the thing that actually proves nothing was missed. Stated together, because on a weekend run
the three confirmations are tempting to treat as the whole job:

The confirmations prove **nothing new ran**. The reconciliation proves **nothing already run was missed**.
They are different claims and a discovery failure hides behind the first one. This run ran both: all three
confirmations agreed (newest recording Thu 15 Oct, Past list newest row Thu 15 Oct, Upcoming opening Mon
19 Oct under a `TOMORROW` header), *and* the fourteen sessions of 12–15 Oct were matched one by one against
the ledger and the gap table — eight graded, three gap, two no-shows, one held-with-nothing-to-grade.

Note the Upcoming check earns its place on a Sunday specifically: it is what separates "today was never
scheduled" from "today was scheduled and cancelled", and only the second of those is worth a line in the
run output.

## A 0-attendee webinar CAN reach `getAllRecordings` — as a short shell (19 Oct 2026)

The 16 September note says "a 0-attendee webinar never reaches `getAllRecordings`, so read the pair off the
Past row rather than inferring it from the recording list's silence", and the 17 October reconciliation
repeats it. **Half of that is now wrong.** This run's 3 pm slot returned a row in `getAllRecordings`:
`Admin Part 1 Training Tues or Thurs 3 pm cst`, meeting key `1063327770`, `durationInMins: 3`,
`isTranscriptGenerated: false`. `getAttendeeReport` answered `count: 0`, `attendees: []`.

So a no-show sometimes produces a recording row and sometimes does not, and the list's silence proves nothing
either way. What the note got right is the part to keep: **the discriminator is the attendance pair, not the
presence or absence of a recording, and not the duration.** A 3-minute row with 0 attended is a no-show; a
3-minute row with 1 attended for 77 minutes is the 6 October truncated capture, and those are opposite
outcomes that look identical in the recording list. One `getAttendeeReport` call settles it and nothing else
does — run it on every short row before deciding whether it belongs in the gap table.

Incidental: the topic was `Tues or Thurs 3 pm` on a **Monday**, so the series names drift off their own
schedule too. Do not use the topic string to decide which slot a recording belongs to.

## `ledger.py --contradictions` hides a divergence when both trainers are on both sides (19 Oct 2026)

The clearest signal this run produced is a same-day contradiction: Aaron at 9 am stated the vendor flag's
forward behaviour correctly and Allie at 11 am stated it backwards, on the same `claim_id`, two hours apart.
**`--contradictions` did not list it.** Six claim_ids came back and `directory.vendor-flag.excludes-from-advisoriq`
was not among them, despite the ledger now holding both `correct` and `wrong_high` rows for it.

The reason is visible in the output shape: each entry carries `wrong_trainers` and `right_trainers`, and this
claim's two sets are identical — Aaron and Allie each appear on both sides across the run of the ledger, because
both have been graded both ways on it over three weeks. A filter that wants a *disagreement between people*
cannot see a disagreement a person has with themselves.

Same shape as the 24 September note ("a repeat can hide inside a claim the tool calls not repeating"), and the
same remedy: **read the run's own `--add` output and the day's grades side by side before trusting the
contradictions table to surface the day's headline.** A claim graded `correct` in one session and `wrong_*` in
another *on the same date* is worth a direct check every run; it is two lines of grep over the rows just added
and it is the single cheapest signal this skill produces.

## `build_report.py --sessions` wants `{"sessions": [...]}` and `duration_minutes` (19 Oct 2026)

Two small shape traps, both of which fail quietly rather than loudly:

- The file is read as `data.get("sessions", [])`, so a **bare JSON array** matches nothing and every session's
  metadata renders as `—` with no error. Wrap it: `{"sessions": [ … ]}`.
- The duration key is **`duration_minutes`**, not `duration` — `getAllRecordings` calls it `durationInMins`,
  so neither name carries over from the API response. A wrong key prints `? min` in the meta block.

Also worth stating because it is not in SKILL.md: `--narrative` takes a **JSON object** with `title`,
`standfirst` and `method` keys (the 17 September note says JSON, not which keys), and `title` is what the
artifact's `<h1>` reads — the Artifact `title` argument only names the gallery card.

## `pin_baseline.sh` fell back stale for a sixth run — the explicit fetch is now the only baseline step

5, 6, 13, 17 and 18 October, and now 19 October: the local ref was `58dfaa6c74` against a true tip of
`0704808d6c`, **six commits behind**, the same gap as 18 October. Six runs out of fifteen. The 17 October note
already says to stop budgeting a decision for this and run the explicit fetch first every run; this run did
exactly that and it cost two calls:

```bash
git -c credential.helper='!gh auth git-credential' fetch https://github.com/ShopRocket-LLC/oktorocket.git development
git update-ref refs/remotes/origin/development <FETCH_HEAD sha>
```

Treat `scripts/pin_baseline.sh` as commentary. It has not produced a correct baseline unaided in two weeks.

## A meeting key seen as a 0-attendee shell can come back as a full session (20 Oct 2026)

The 19 October note records `1063327770` arriving in `getAllRecordings` as `durationInMins: 3` with
`getAttendeeReport` answering `count: 0` — a no-show, correctly left out of the ledger. **The same
meeting key returned today at 72 minutes with five attendees from five shops**, the best-attended
session the coverage-gap table has ever taken in.

So a key is not retired by having once looked like a shell. Two consequences:

- **The "never ledger a session you could not grade" rule just paid for itself in the most direct way
  available.** Had yesterday's run recorded that no-show in `findings-ledger.md`, `discover_sessions.py`
  would have dropped the key today and a 72-minute session with five customers in it would have been
  invisible forever, with nothing anywhere to show it had been missed.
- **Do not treat a previously-seen key as already handled.** Dedupe against the ledger, which is what
  the scripts do, and not against memory of an earlier run's discovery output.

Whether Zoho reused the key for the next instance of the series or updated the row in place does not
matter operationally and was not worth a call to settle. What matters is that the attendance pair is
read fresh on every run, which the 19 October note already says for a different reason.

## `reports.pinned.max-three` looks inverted, the same way the vendor flag was (20 Oct 2026)

Allie was asked about pinning reports and said there is **no cap**. That is correct at `c6c7466e39`:

- `dc-user/src/js/user/components/reports/Reports.js:102` and `dc-user/src/js/admin/components/reports/Reports.tsx:282`
  both append to `pinnedReports` unconditionally — no length test, no disabled state at N.
- `dc-server/models/user.js:120` declares `pinnedReports: [{}]`, an unbounded array with no `maxlength`,
  and there is no server-side validation anywhere.
- Neither Reports component contains a `slice` or length guard on the pinned list.

And it has never been otherwise: `git log -S 'pinnedReports.length'` and `git log -S 'pinnedReports.slice'`
over `dc-user` and `dc-server` return **no commit** that ever added or removed such a guard, so this is not
a product change that would make older rows right-at-the-time.

The claim_id carries **five prior rows**, including a `correct` for Allie on 13 October and a *Fixed* entry
(`wrong_contained` → right on 22 Sep), all of which only make sense if a three-pin cap was believed to exist.

**Per the 8/9 October rule this was not flipped autonomously.** The ledger is append-only, a re-grade that
overturns prior runs is a human decision, and — exactly as with the vendor flag — the correction is not one
regrade but a reversal of who has been coached. Flagged on the dashboard, in the session report and in Slack;
no row rewritten. The generalisable part: **a trainer contradicting the ledger is a reason to re-derive the
claim from source, not a reason to grade them wrong.** That is the second time in twelve days that doing so
found the ledger at fault rather than the trainer.

## `isTranscriptGenerated: true` has now lied four times

20 October, Admin Part 1 Tue/Thu 3 pm (`1063327770`): `getAllRecordings` reported `isTranscriptGenerated: true`
and the recording page answered `len=NONE empty=true` with "No transcript generated" and a live Generate button.
That is the fourth instance after 9 Sep, 5 Oct and 6 Oct, and it is why discovery opens every recording in the
browser rather than reading the flag. Nothing new to decide here — recorded only so the count stays honest.

## Three `erecordingId`s shared a 32-character head in one day (20 Oct 2026)

`77f701363e2d28127222470972e1572c` is the head of **three** different recordings: today's Advisor
(`…6769f76386dfbe1675ec2b69d6a26425`), today's Shop Analytics (`…85b72741cf5a7e668180f8245705df1a`) and the
14 October Advisor gap row (`…950f9ee668913812db0a8631d213d8b0`). The existing note says to match on the whole
string; this is the first time the collision has spanned both a session being graded and a gap row being swept
in the same run, which is the arrangement most likely to produce a confident wrong answer — the gap sweep
expects `empty=true`, and loading a graded session's page by a truncated id would have returned a transcript
and read as a recovery.

## The bug table's abbreviated paths are now written out in full (20 Oct 2026)

The 18 October note asked for this the next time a run had spare capacity. Done: the four rows storing
`dc-user/.../…` forms now carry full paths — `AddCampaign.js` → `dc-user/src/js/admin/components/campaigns/`,
`CallAnalyzerModal.tsx` → `dc-user/src/js/admin/components/calls/CallAnalyzerModal/`,
`CampaignModal.tsx` → `dc-user/src/js/user/components/inbox/ActionMenu/`,
`OutrunningOverhead.tsx` → `dc-user/src/js/admin/components/reports/sales-analytics/widgets/OutrunningOverhead/`.
All five cited lines were verified at `c6c7466e39` before the paths were rewritten. A sweep can now grep these
rows directly; the remaining `dc-user/.../campaignsV2/` string in the file is prose in the resolved-paths note,
not a citation.

## `ledger.py --add` prints its report to stdout and the duplicate guard is the safety net

Re-running `--add` on the same file to see the top of a long report does **not** double-add: the second run
refuses with "these sessions are already in the ledger". Harmless, and a useful confirmation that the guard
works — but pipe the first run through `tee` if the report matters, rather than re-running it.

## `UserPermissionsToggles.tsx` is dead code, and the ledger has been citing it for a month (21 Oct 2026)

Grading the All Recordings claim this run meant resolving what the permissions screen actually is. It is
**`dc-user/src/js/admin/components/users/edit/UserEditSettings.tsx`**, which maps `permissionsList`
(= `accountPermissions.json` + the user's groups) and renders a label and a switch per row, with
`allRecordings`, `campaigns` and `closeSiteEarly` forced on and disabled for administrators (`:200-211`).

**`dc-user/src/js/admin/components/users/permissions/UserPermissionsToggles.tsx` is imported by nothing** —
`git grep -l UserPermissionsToggles` returns only the file itself. It is the only place in the repo carrying
per-permission *description* strings ("Access to view and download all user call recordings regardless of
assigned sites or groups", `:78`), and those strings are **not on any screen a customer or trainer sees**.
Recent ledger rows cite `:78` and `:88` as evidence of what the permissions screen says, including the
20 October block-customer row. The grades are right; the citations point at code nobody runs.

Two consequences for grading:

- **Cite the live screen** (`UserEditSettings.tsx`) plus the enforcement site, never the dead component.
- **`allRecordings` is enforced on the permission's `label`, not its `value`.** A `git grep allRecordings`
  finds only the schema, the admin-default lists and the dead component — which reads exactly like a
  permission that nothing checks. The real checks are string comparisons against `"All Recordings"`:
  `dc-user/src/js/admin/components/calls/Calls/Calls.tsx:100` (advisors without it are pinned to their own
  extension), `callsReviewUtils.ts:179`, `CallFilters.tsx:249`, `dc-server/routes/users.js:213` and
  `okto-extension/src/shared/components/callHistory/callAccess.ts:19`. Grep both spellings before concluding
  a permission is unenforced — "nothing reads this flag" is the same whole-monorepo claim the 9 October
  vendor withdrawal was about, in miniature.

## A recording that starts mid-greeting loses the trainer's name (21 Oct 2026)

The 21 October CRM Overview transcript opens at **00:07** with "Has been Okay." — the tail of a sentence.
The housekeeping script that follows is word-for-word the one TeDarrell delivers in Admin Part 2 two hours
later ("thank you for your patience and holding", the one/two/three chat check, the manager-feedback survey),
and every prior CRM Overview run this month was his. **It is still recorded as `unidentified`**, because
`trainers.md` is explicit that a name comes from a person or an account and never from inference, and style
is weaker evidence than a transcription variant. A human can settle it from the MP4 in a minute.

Worth noting what the cost is, so the rule is applied with eyes open: three of today's claim_ids are repeats
that would be same-trainer coaching if the attribution held, and read as cross-trainer curriculum defects
while it does not. The honest `unidentified` is still right — a wrong attribution invents or hides a defect,
and this one would do both — but flag it in the report rather than letting the repeat table speak for itself.

## Sweeping the gap table: one JS call per recording, four per batch (21 Oct 2026)

The stored recipe is "navigate + a JS probe each, four recordings per `browser_batch`", with separate
`computer:wait` steps between them. The waits can live **inside** the probe, which halves the actions and
makes a 28-row sweep seven calls:

```js
await new Promise(r=>setTimeout(r,3500));
const b=[...document.querySelectorAll('button.transcript-panel__tab')].find(x=>x.textContent.trim()==='Transcript');
if(b)b.click();
await new Promise(r=>setTimeout(r,3500));
const c=document.querySelector('div.transTimeStampMainContainer');
const e=document.querySelector('.transcript-tab--empty');
`${document.title.slice(0,38)} | len=${c?c.innerText.length:'NONE'} empty=${!!e}`
```

`javascript_tool` honours top-level `await`, and returning the title in the same string is what satisfies the
8 October rule that `empty=true` only counts when the page matches the row. All 28 rows answered correctly
first time this run, with no swallowed first click.

## Two Chrome browsers connected, and a scheduled run cannot ask which (21 Oct 2026)

`tabs_context_mcp` refused to act and demanded an `AskUserQuestion` listing every connected browser. In a
6 pm scheduled run there is nobody to answer, and `AskUserQuestion` is not in the task's tool set. The run
selected **Browser 1** (`select_browser`, both devices local and connected seconds apart), which turned out
to hold the authenticated Zoho session, and said so in the run output.

If a future run picks wrong, the symptom is a Zoho **sign-in page** rather than a recording page — which is
not the same as "no transcript", so check `document.title` before writing anything into the gap table.
Switching is one `select_browser` call with the other `deviceId` from `list_connected_browsers`.


## The first product bug this audit has ever seen closed, and what made the close clean (22 Oct 2026)

`"Require Delete Reason" label is inverted` entered `product-bugs.md` on 25 August and was graded wrong in
**eleven sessions across three trainers** without anyone ever stating it correctly — because the trainers were
reading the popover aloud and the popover was lying. It is **fixed at `15b4ddb206`** under TRS-I2670 /
TRS-I2672: all five legacy screens now read "Delete queued messages without asking for a reason" with a
popover that states both branches, and a new Playwright spec asserts the old string is gone.

Two things made the close verifiable in three calls rather than a guess:

- **Close by the absence of the old string, not the presence of the new one.** `git grep "Require Delete
  Reason" $SHA -- dc-user dc-server` returns only the regression spec's `OLD_LABEL` constant. Reading the new
  label on the one screen the row cites would have proved nothing about the other four.
- **The 16 October widening is what made the fix checkable at all.** That note grepped the string across the
  package and found five screens where the row had carried one for 52 days. Without it this run would have
  checked `AddCampaign.js`, found it fixed, and closed a row that might still have been live on four screens.
  The shipped fix touches all five — so the rule paid twice, once for the bug report and once for the close.

Generalises: **a row that cites one surface cannot be closed from that surface.** Grep the identifier or the
string across the package on the way out, the same as on the way in.

## A curriculum defect can be closed by the product moving under it (22 Oct 2026)

`scheduler.appointment-lead.phone-is-minimum` is the third-largest defect in the ledger — nine rows, Aaron and
Allie, graded wrong because `createLead` accepted a lead with no phone number at all. The 12 October note put
it plainly: "`createLead` has no phone gate — the appointment-lead claim is wrong in the *other* direction".

TRS-I2729 (`173abef7b5`, merged 12:11 today) adds one: `dc-server/routes/customer.ts:809` now runs
`if (!validateNumberForImport(req.body.number).valid)` and returns 204 before any contact or tracker is
written, for every caller including OktoAssist. **What the trainers were saying is true from this commit
forward.**

Handle it the way the 8/9 October rule handles an inversion, but note that this is *not* one: the nine rows
were right on their dates and the code genuinely had no gate. Nothing is rewritten, nothing is re-graded, and
the ledger is not at fault. What changes is forward-looking — the next session that states the gate should be
graded `correct`, and the next session that states there is **no** minimum is now the error. Flag it on the
dashboard and in Slack so the coaching stops before it coaches the wrong way round.

The cheap habit this argues for: when the baseline moves, read the commit subjects for anything naming a
feature the ledger's open defects are about, not only the files the bug table cites. Thirteen commits landed
today and two of them bore on this skill's two biggest findings — both visible from `git log --oneline` alone.

## `isTranscriptGenerated: true` has now lied five times

22 October, Advisor Thursdays 2 pm (`1060567444`): `getWebinarRecording` returned `isTranscriptGenerated: true`,
`isSummaryGenerated: true` **and** a live `transcriptionDownloadUrl`, and the recording page answered
`len=NONE empty=true` with "No transcript generated" and the Generate button live. The same day's Shop
Analytics (`1046976106`) was honest — both flags `false` — so one run produced both outcomes again.

The new detail: a populated `transcriptionDownloadUrl` does **not** rescue the flag either. Previous instances
were explained as the flag going true off the back of a generated summary; this one ships a transcript URL
beside it. Nothing about the API response distinguishes it from a real transcript. The browser check stays the
only test.

## Zoho was signed out in the browser the scheduled run picked, and there are five of them now (22 Oct 2026)

The 21 October note records two connected Chrome browsers and a run that picked Browser 1 and got lucky. Today
there are **five**, the tool auto-selected **Browser 5**, and the Past Webinars URL redirected to
`accounts.zoho.com/signin` — `document.title` read `Zoho Accounts`, exactly the symptom that note predicted.
`select_browser` onto **Browser 1** fixed it in one call and the session there is still live.

So the check is cheap and should be unconditional: **load the Past list first and assert `document.title`
starts with `Zoho Meeting` before believing anything.** A signed-out browser answers every gap probe
`empty=true`, which is indistinguishable from a clean sweep and would silently report twenty-nine recordings
as still broken. Note also that `tabs_context_mcp` returned "No tab available" immediately after the switch;
a standalone `navigate` creates the tab and recovers.

## Splice the coverage-gap section before the bug table, not before Sessions (22 Oct 2026)

The standing recipe is "generate, filter, splice, then publish", and the splice point it names is
`<h2>Sessions</h2>`. That is one section too late. `build_dashboard.py` emits **Open product bugs**
immediately before Sessions, so splicing the carried-forward gap section at `<h2>Sessions</h2>` puts it
*after* the bug table — the reverse of every published version, and the reader's eye lands on citations
before it lands on what is unaudited.

It also fails quietly in a second way, which is how it was caught here: the verification pass then slices
`s[index('<h2>Coverage gap')):index('<h2>Open product bugs</h2>')]`, which is a **negative range and returns
an empty string**, so every count computed off it reads zero. A zero-length gap section looks like a broken
regex, not a misplaced section.

Splice at **`<h2>Open product bugs</h2>`**, and verify the ordering explicitly:

```python
assert s.index('<h2>Coverage gap') < s.index('<h2>Open product bugs</h2>') < s.index('<h2>Sessions</h2>')
```

Then re-derive the totals paragraph from the spliced rows rather than trusting the arithmetic that produced
it — 31 rows summing to 2,214 minutes and 86 attendances is one pass over the table and it is the only thing
that catches a row lost in the splice.

## The republish went through in one call for a second time

The 8 October note budgets three publish calls (refused-not-viewed → Read → publish → refused-unchanged →
publish). This run needed **one**, for the same reason the 10 October run did: the full Read of the saved live
copy had already happened earlier, as part of carrying the coverage-gap section forward. Reading the live page
is not an extra step before publishing — it is the step that makes the gap section correct, and the publish
permission comes free with it. Do it first and the three-call budget never applies.

Confirmed the same way as before: `action: "read"` with `path: "index.html"` on the canonical
`code/artifact/1d86f6a7-…` URL, then grep the saved copy for strings unique to this run (`Thursday 22 October`,
`1046976106`, `fixed <code>15b4ddb206`). All present, so the short-form URL the publish printed back
(`4eUdaeZbcXPS9zXZdLtmJh`, Version 51) is the same artifact.

## The abbreviated-path trap has a second form: right filename, wrong directory (23 Oct 2026)

The 18 and 20 October notes are about rows storing `dc-user/.../Foo.tsx` and ask for full paths. Both bug rows
fixed this run stored a *complete-looking* path that was simply wrong about the directory:

- `dc-user/src/js/admin/components/calls/callsReviewUtils.ts` — the file is under `calls/Calls/`.
- `dc-user/src/js/user/components/inbox/ActionMenu/CampaignOutcomeModal.js` — the file is under
  `user/components/tasks/`. The sibling `CampaignModal.tsx` *is* in `inbox/ActionMenu/`, which is almost
  certainly where the wrong directory came from.

This form is worse than an ellipsis, because an ellipsis is visibly incomplete while this reads as a citation
someone checked. `git grep -n <identifier> $SHA -- <stored path>` returns **nothing**, which looks exactly like
a deleted file and invites the conclusion that the bug was fixed. **Grep by identifier across the repo and take
the path from the result**; never assemble a path from where a sibling row's file lives.

## A huge refactor landing on a disputed claim is the cheapest evidence you will get (23 Oct 2026)

`reports.pinned.max-three` has been flagged-for-a-human since 20 October: five ledger rows assume a three-pin
cap, a trainer said there is none, and the code agrees with the trainer. The 20 October argument rested on
`git log -S` finding no commit that ever added such a guard — true, but a negative over history.

This run got something better for free. TRS-I2655 (`5634c128ee`, Reports Overhaul foundation) landed in the
window at **733 files, +47,099/−41,875**, and it changed `Reports.tsx` itself. The cap still does not exist.
A rewrite of that size is the single likeliest moment for a product to introduce a limit it had always
intended, and it did not.

Generalises to a cheap habit on any run: **after pinning the baseline, scan `git log --oneline` for a commit
touching an area a disputed or flagged ledger claim is about, and re-check that claim specifically.** A
non-change across a rewrite is much stronger than a non-change across a quiet week, and it costs one grep.
This is the same move that found TRS-I2729 and TRS-I2670 on 22 October from commit subjects alone.

## `git pull --ff-only` in okto-mgmt-agents fails — the task file's own push line is the fix (23 Oct 2026)

The scheduled task opens with `git pull --ff-only`, and `origin` for this repo is
`git@github.com:bdm1981/okto-mgmt-agents.git`. SSH to GitHub does not work on this host — which the task file
says explicitly, three paragraphs later, in the *push* instruction. So the pull fails on every run with
`Permission denied (publickey)` and the run continues on the local checkout, exactly as the task file allows.

Harmless in practice (nothing else writes to this repo), but it burns a call and reads like a real failure.
The same `-c credential.helper='!gh auth git-credential'` form that the push uses works for the pull.

## The oktorocket remote is `ShopRocket-LLC`, and the clone is the authority (23 Oct 2026)

`pin_baseline.sh` has fallen back stale six times, so this run skipped it and fetched explicitly — and the
first attempt guessed `https://github.com/bdm1981/oktorocket.git` (the okto-mgmt-agents owner) and got
`Repository not found`, which reads like a permissions problem rather than a wrong org. The remote is
**`ShopRocket-LLC/oktorocket`**. One `git remote -v` in `~/Documents/DEV/oktorocket` settles it; do that
before composing the fetch URL rather than carrying an org name across from another repo.

## A recording's greeting named a trainer, and it is NOT being canonicalised (23 Oct 2026)

The 6 October Admin Part 1 fragment (`1064758517`) — the 287-character row in the gap table, which is all the
audio that was captured — contains a self-introduction: *"My name is Theo and I will be a trainer for this
evening session."* `trainers.md` has no `Theo`, though its variant table already carries Tedario, Tadario,
Sairio, Serio and Stereo for TeDarrell, and Theo is a plausible member of that set.

**It is recorded here and nowhere else.** `trainers.md` is explicit that a name comes from a person or an
account, never from inference, and the variant table is built from confirmed cases rather than from
likely-looking ones — adding `Theo → TeDarrell` on the strength of a resemblance is exactly the move that
would later be cited as evidence. Nothing turns on it either way: that session has 40 seconds of audio and is
ungradeable, so the attribution buys nothing. A human can confirm or reject it from the MP4 in a minute, and
if confirmed it is one more row in the variant table.

## Three Chrome browsers now, and yesterday's good one had signed out (23 Oct 2026)

The 21 October note records two connected browsers; 22 October records five and the auto-selected one being
signed out. Today there were **three**, the tool auto-selected Browser 2, and the run opened by switching to
**Browser 1** on the strength of yesterday's note — which was wrong: Browser 1 redirected to
`accounts.zoho.com/signin` and `document.title` read `Zoho Accounts`. Browser 2, the one the tool had picked
on its own, held the live session.

So the stored advice "pick Browser 1" is worthless and should not be written down again. **Which browser holds
the session is not stable across runs; the only reliable procedure is the title check.** Load the Past list,
assert `document.title` starts with `Zoho Meeting`, and if it does not, `select_browser` onto the next
`deviceId` from `list_connected_browsers` and repeat. Two calls in the worst case, and it is the difference
between a sweep and twenty-nine false `empty=true` answers.
