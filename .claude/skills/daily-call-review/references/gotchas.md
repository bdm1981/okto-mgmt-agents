# Data gotchas — read before trusting a number

Everything here was learned the hard way in the first two weeks of running the review.

## Partner MCP (`mcp__oktorocket__*`)
- `list_calls` rows carry `answeringExtension` but **not** `summary` or `hasTranscript`; those need `get_call`. `get_transcript` returns transcript + summary + `talkMetrics` in one call — prefer it.
- `date` on list rows has no `Z` but **is UTC**. Day boundary for America/Chicago is 05:00Z in CDT (Mar–Nov), 06:00Z in CST.
- `advisorIqScore` is −1 / 0 / +1 and absent on ~25 % of calls. It tracks customer frustration, not rep quality — every −1 call read so far was competent work. Use it to pick what to read, never as the finding.
- `scorecardScore` / `scorecardMaxScore` / `scorecardTemplate` appear on `get_call` when a scorecard ran. That is the only objective quality number.
- The `vendor` **boolean is always false**; the signal is the `vendor` **label**. A refused cold-call gets tagged `lost` and will look like churn unless you filter on the label.
- **A missed call is a row carrying the `missed` label. Count that, nothing else.** Do not infer misses from ring time, 0-second legs or "nobody connected within 3 minutes" — those heuristics undercounted 21 labelled misses as 1 on 2026-09-08. Most missed legs land on the routing-target extensions 8765 and 8000, so never drop labelled misses when excluding those extensions. `voicemail` is a separate label; report it alongside, not inside, the missed count. 0-second legs *without* the label are ring-group artefacts and are not misses.
- Extensions `8765` and `8000` take inbound calls, never answer, and are in no roster — routing targets, not people.
- The key sees exactly one site (`634c8538a3be38fc4c8ed28c`, OktoRocket's own tenant). `get_ro_summary` / `get_advisor_attribution` are empty for it.

## Roster (`list_users`)
- **`status` is inverted: `"0"` = active, `"1"` = disabled.**
- Extensions are not unique — 8013, 8021, 8025, 8031, 8036, 8043 each map to two accounts. Pick active + most recent `lastLogin`; the roster file records the resolution.
- `roleId` does **not** describe internal teams; nearly everyone is `Advisor`. The team split lives in `team-roles.md`.
- **Extension ≠ person when phones are shared.** On 2026-09-04 every call on 8021 (Manuel's) opened "Shawn speaking" while 8035 sat idle — Manuel was away. Check the greeting on the first transcript of the day for each extension.

## Zoho Desk (`mcp__3a249e78-…__searchTickets`)
- `limit` caps at **100**; `count` reports the true total. Page with `from: 100, 200, …`. A day is ~30–80 tickets, a week ~290.
- Account names rarely match caller IDs: Arch Automotive → "Cataca LLC (Org)", TransMedics contact has **no account**, "Home Town" ≠ "Hometown". Match on time + assignee first; confirm a specific case with `accountName` wildcards (`*Medics*`). `_all` with a multi-word wildcard returns noise.
- Ticket text almost never records that a remote session happened (3 of 289). Remote-session rate can only come from transcripts.
- "Own ticket" in the dashboard = a phone-channel ticket by the same rep within 2 h of the inbound call. On a busy day "any ticket by anyone within 2 h" matches everything and means nothing.

## Transcripts
- Two summaries per day have been observed containing the summariser's own prompt instead of a summary. Never review from summaries alone.
- The PII redactor replaces phone numbers and RO numbers with `[CREDIT_CARD_n]` and has missed a spoken password. Treat redacted tokens as unreliable and never quote a credential.
