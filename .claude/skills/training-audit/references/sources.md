# Sources & configuration

Everything the discovery step needs. Edit the tables; `discover_sessions.py` parses them.

## Hosts

Zoom user id **or email** of every account that hosts customer training. A recording
from anyone not listed here is ignored — that is deliberate: widening this to the whole
account would pull in standups and 1:1s, which is both wasteful and a privacy problem.

| host | who | notes |
|---|---|---|
| training@oktorocket.com | OktoRocket Training | the shared training account. Verified: 18 recordings 20–31 Aug 2026, all of them trainings |

Verified that `aaron@oktorocket.com` hosts **zero** recordings of his own — every session runs
through the shared account, so this one host is sufficient. `scripts/zoom_client.py` run directly
prints every active user with id and email, which is how to add another.

## Topic excludes

Regexes matched against the meeting topic. A recording from an allowlisted host is audited
**unless** it matches one of these.

| pattern | why excluded |
|---|---|
| `standup` | internal, not a customer training |
| `retro` | internal |
| `interview` | hiring |
| `internal` | anything explicitly marked internal |

Patterns must not contain a `|` — the table parser splits on it, and an escaped `\|` leaves a
trailing backslash that fails to compile. Use one row per alternative. An unparseable pattern is
warned about and ignored rather than aborting the run.

This started life as an *include* list — a required topic match — and that was wrong. Two of the
four seed sessions ("OktoRocket CRM - Campaigns & Schedules 4:30 pm cst" and "Mastering Sales
Analytics") matched none of the obvious patterns and would have been silently dropped, including
the session with the most severe findings. Topics are hand-typed and drift: the same window
contains "Founations" twice.

On a dedicated training account an include list can only ever *lose* sessions, and it fails
silently. Excluding is the safer default for an audit tool — err toward auditing something
irrelevant over missing something real. `discover_sessions.py` prints every exclusion by topic so
a bad rule is visible rather than quiet.

## Thresholds

```
min_duration_minutes: 20
slack_channel: #team-training-audits
slack_channel_id: C0C1HH5P0RW
```

- **min_duration_minutes** — anything shorter is a false start or a no-show, not a session.
  Verified against 20–31 Aug 2026: 7 of 18 recordings on the training account were Zoom's
  0-minute shells for false starts, plus 7- and 11-minute fragments. All correctly dropped.
- **slack_channel** — where the run posts its summary. `#team-training-audits` is **private**
  (created 2026-09-09), which is the right shape: these reports assess named employees and must
  not reach a customer-facing or all-hands channel. Prefer the **ID** over the name when posting —
  a rename silently breaks name-based posting, and the failure comes at the very end of a run
  after all the work is done.

## Zoom access — Server-to-Server OAuth

The Zoom *connector* (per-user OAuth) is **not** usable for this job. It only ever returns
the authenticated user's own cloud recordings, so a run driven by anyone but the training
account sees nothing. Verified: listing 20–31 Aug 2026 as `bdm@oktorocket.com` returned 10
recordings, all hosted by that same account, and none of the four training sessions.

Create one Server-to-Server OAuth app (Zoom Marketplace → Develop → Build App → S2S OAuth):

| scope | why | held? |
|---|---|---|
| `cloud_recording:read:list_user_recordings:admin` | list a host's cloud recordings, and download the VTT via the `download_url` it returns | ✅ |
| `user:read:list_users:admin` | resolve `host_id` to a name, so reports say "Aaron" not an opaque id | ✅ |
| a meeting-participants scope | **exact attendee counts** — see below | ❌ |

### Attendee counts need one more scope

The dashboard's Sessions table has a `spoke` column: distinct non-trainer speakers in the
transcript. It is a **floor**, not attendance — anyone who never unmutes is invisible. For the
August Foundations runs it reads 0–2, and two full-length sessions show 0 speakers, so for
one-to-one training it is close to useless as a proxy.

Exact counts come from a Zoom participants endpoint. All three are currently refused with
`code 4711 — Invalid access token, does not contain scopes`, which confirms the endpoints and the
UUID encoding are fine and only the grant is missing:

```
GET /past_meetings/{doubly-encoded-uuid}/participants
GET /report/meetings/{doubly-encoded-uuid}/participants
GET /metrics/meetings/{doubly-encoded-uuid}/participants
```

Add whichever the scope picker offers under **Meeting** or **Report** — search for
`participants`. Prefer the narrowest that returns a list of past-meeting participants. UUIDs
containing `/` or `==` must be **double URL-encoded**; `zoom_client` does not do this for you on
these paths.

Until then the column stays labelled `spoke` and the dashboard says why. Do not relabel it
"attendees" — the number would be wrong and the error is invisible to a reader.

Zoom has replaced the old coarse scopes (`recording:read:admin`, `user:read:admin`) with granular
ones; searching the picker for the old names returns unrelated results. Search for
`list_user_recordings` and `list_users` instead.

Deliberately **not** granted: `cloud_recording:read:list_account_recordings:admin`, which would
list every recording on the account. Per-host enumeration against the allowlist above means the
job can only ever read the training accounts' recordings, not anyone's 1:1s. Keep it that way.

There is no separate download scope — the recording read scope authorises fetching the file at
the `download_url` with the bearer token.

Then export three values in the runner's environment — never commit them:

```bash
export ZOOM_ACCOUNT_ID=…
export ZOOM_CLIENT_ID=…
export ZOOM_CLIENT_SECRET=…
```

Verify before scheduling anything:

```bash
scripts/zoom_client.py          # prints "OK — authenticated, N active users visible"
```

Notes that will save an hour:

- Cloud recording **and** audio transcription must be on for the host, and transcription
  must have been on *at the time of the meeting*. Retro-enabling does not generate a VTT
  for past recordings — those sessions are permanently unauditable and get skipped.
- Recordings age out of the cloud on the account's retention setting. Run at least weekly,
  or the window closes on sessions you never audited.
- Zoom caps one recordings query at a month; `discover_sessions.py` chunks wider windows.
