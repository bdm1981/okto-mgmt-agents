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
