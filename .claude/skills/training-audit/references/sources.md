# Sources & configuration

Everything the discovery step needs. Edit the tables; `discover_sessions.py` parses them.

## Hosts

Zoom user id **or email** of every account that hosts customer training. A recording
from anyone not listed here is ignored — that is deliberate: widening this to the whole
account would pull in standups and 1:1s, which is both wasteful and a privacy problem.

| host | who | notes |
|---|---|---|
| training@oktorocket.com | OktoRocket Training | the shared training account — CRM, Foundations, Deep Dive, Shop Analytics |

> Replace with the real address(es). `scripts/zoom_client.py` run directly prints every
> active user with their id and email, which is the easy way to fill this in.

## Topic patterns

Case-insensitive regexes matched against the meeting topic. A recording must match
at least one.

| pattern | matches |
|---|---|
| `training` | "CRM Training", "Foundations Training" |
| `foundations` | Foundations sessions with a bare topic |
| `deep ?dive` | admin Deep Dive |
| `shop analytics` | Shop Analytics webinars |
| `onboarding` | onboarding walkthroughs |

## Thresholds

```
min_duration_minutes: 20
slack_channel: #training-qa
```

- **min_duration_minutes** — anything shorter is a false start or a no-show, not a session.
- **slack_channel** — where the run posts its summary. Keep this a **limited channel**:
  these reports assess named employees. It must not be a customer-facing or all-hands channel.

## Zoom access — Server-to-Server OAuth

The Zoom *connector* (per-user OAuth) is **not** usable for this job. It only ever returns
the authenticated user's own cloud recordings, so a run driven by anyone but the training
account sees nothing. Verified: listing 20–31 Aug 2026 as `bdm@oktorocket.com` returned 10
recordings, all hosted by that same account, and none of the four training sessions.

Create one Server-to-Server OAuth app (Zoom Marketplace → Develop → Build App → S2S OAuth):

| scope | why |
|---|---|
| `recording:read:admin` | list + download recordings for **any** host in the account |
| `user:read:admin` | resolve `host_id` to a name, so reports say "Aaron" not an opaque id |

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
