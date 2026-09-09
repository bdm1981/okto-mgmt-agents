# Session index

Per-session facts the dashboard joins onto the findings ledger. Written by
`scripts/session_index.py`.

Two different questions, so two columns:

- **`att`** — real attendance, from Zoom's past-meeting participants endpoint. Distinct
  non-host names, waiting-room-only joins excluded, per-join duplicates collapsed. See
  `zoom_client.attendees()` for the three traps this avoids.
- **`spoke`** — distinct non-trainer speakers in the transcript. Kept because the *gap*
  between the two is informative: 3 attended / 0 spoke is a passive session.

`spoke` badly understated attendance and is not a usable proxy — 05 Aug 18:00 read 0
speakers and had 3 people present for the full 67 minutes.

| date | uuid | course | minutes | att | spoke | trainer |
|---|---|---|---|---|---|---|
| 2026-08-03 | `uuid:22K0raRETFGplf4gsZyXbw==` | Foundations | 74 | 3 | 1 | Aaron |
| 2026-08-03 | `uuid:cMDGQ0NTTm2+mGRx8G8VgA==` | Foundations | 77 | 1 | 1 | Aaron |
| 2026-08-05 | `uuid:wzTsah3sTtqgZx1P1RTasg==` | Foundations | 64 | 1 | 1 | unidentified |
| 2026-08-05 | `uuid:8gmGDmavT+2DklYCFHgFDg==` | Foundations | 67 | 3 | 0 | Aaron |
| 2026-08-12 | `uuid:Ly5O48RHRwam9j/t2X4vHQ==` | Foundations | 53 | 2 | 1 | TeDarrell |
| 2026-08-12 | `uuid:58/yY1W5TOyPmR2ARL2HDQ==` | Foundations | 64 | 3 | 1 | unidentified |
| 2026-08-12 | `uuid:c5APhu/PShGxXRHqPQQfUg==` | Foundations | 80 | 1 | 1 | unidentified |
| 2026-08-17 | `uuid:tWqNJWzNTGmBvvQepUo3gA==` | Foundations | 74 | 1 | 1 | TeDarrell |
| 2026-08-19 | `uuid:8cFDlYxaQleDwFSHE4f5bQ==` | Foundations | 66 | 2 | 1 | unidentified |
| 2026-08-19 | `uuid:Xchd7/5+SOGaGqttysM1sg==` | Foundations | 65 | 2 | 1 | TeDarrell |
| 2026-08-19 | `uuid:AqXc21WgRqqpPCinTZZ63g==` | Foundations | 70 | 3 | 0 | unidentified |
| 2026-08-24 | `uuid:cLKwX8jvQQiPFgYxjRhUFA==` | Foundations | 64 | 2 | 2 | Aaron |
| 2026-08-24 | `uuid:ELZkz9AsSPCVLs8bSynDhQ==` | Foundations | 67 | 2 | 2 | TeDarrell |
| 2026-08-26 | `uuid:99svzltpQ8iJpEsJ1pmATg==` | Foundations | 48 | 1 | 1 | TeDarrell |
| 2026-08-26 | `uuid:KhqtymUkTieJKHLqJ2pmYA==` | Foundations | 68 | 3 | 2 | unidentified |
| 2026-09-03 | `uuid:yLMACd4kQIiCsc4B4HbohA==` | Deep Dive | 103 | 2 | 2 | unidentified |
| 2026-08-27 | `uuid:wj2mARB6RtWx2Ij1/K/xIw==` | Deep Dive | 81 | 2 | 2 | Aaron |
