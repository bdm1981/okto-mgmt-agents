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
| `meeting:read:list_past_participants:admin` | **exact attendee counts** — see below | ✅ |

### Attendee counts

`GET /past_meetings/{uuid}/participants`, via `zoom_client.attendees()`. All August training
recordings are `type: 8` (recurring meeting) — **zero webinars** — so the webinar variant of this
scope is deliberately not granted.

Three traps, all found in live data:

1. **One record per JOIN, not per person.** A participant who drops and rejoins appears twice, so
   `total_records` overcounts — 5 records for 3 people in the session this was built against.
2. **`user_id` is per-join, not per-person.** The same guest returned as `16793600` and
   `16794624`. `id` and `user_email` are both empty for external guests, so the only stable key is
   the display name lowercased and trimmed — which also collapses "Scott"/"scott".
3. **Waiting-room entries look like attendance.** `status == "in_waiting_room"` records carry a
   duration (24 s in one case) but the person never got in.

**A meeting UUID containing `/` or `==` must be double URL-encoded.** Single-encoded, Zoom answers
400 and it reads like a malformed request. Before the scope was granted the same call returned
`400 code 4711 — does not contain scopes`, which also reads like a bad request; if this endpoint
starts failing, check the scope before the encoding.

The dashboard keeps a second `spoke` column (distinct non-trainer transcript speakers) because the
*gap* is informative: 3 attended / 0 spoke is a passive session. `spoke` alone is not a usable
proxy — 05 Aug 18:00 read 0 speakers and had 3 people present for the full 67 minutes.
