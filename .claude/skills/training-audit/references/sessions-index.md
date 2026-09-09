# Session index

Per-session facts the dashboard joins onto the findings ledger. Written by
`scripts/session_index.py`.

`spoke` is the count of distinct non-trainer speakers in the transcript — a **floor**
on attendance, not attendance. Someone who never unmutes does not appear. Exact
counts require a Zoom participants scope the audit app does not yet hold.

| date | uuid | course | minutes | spoke | trainer |
|---|---|---|---|---|---|
| 2026-08-03 | `uuid:22K0raRETFGplf4gsZyXbw==` | Foundations | 74 | 1 | Aaron |
| 2026-08-03 | `uuid:cMDGQ0NTTm2+mGRx8G8VgA==` | Foundations | 77 | 1 | Aaron |
| 2026-08-05 | `uuid:wzTsah3sTtqgZx1P1RTasg==` | Foundations | 64 | 1 | unidentified |
| 2026-08-05 | `uuid:8gmGDmavT+2DklYCFHgFDg==` | Foundations | 67 | 0 | Aaron |
| 2026-08-12 | `uuid:Ly5O48RHRwam9j/t2X4vHQ==` | Foundations | 53 | 1 | Tadario |
| 2026-08-12 | `uuid:58/yY1W5TOyPmR2ARL2HDQ==` | Foundations | 64 | 1 | unidentified |
| 2026-08-12 | `uuid:c5APhu/PShGxXRHqPQQfUg==` | Foundations | 80 | 1 | unidentified |
| 2026-08-17 | `uuid:tWqNJWzNTGmBvvQepUo3gA==` | Foundations | 74 | 1 | Tedario |
| 2026-08-19 | `uuid:8cFDlYxaQleDwFSHE4f5bQ==` | Foundations | 66 | 1 | unidentified |
| 2026-08-19 | `uuid:Xchd7/5+SOGaGqttysM1sg==` | Foundations | 65 | 1 | Tedario |
| 2026-08-19 | `uuid:AqXc21WgRqqpPCinTZZ63g==` | Foundations | 70 | 0 | unidentified |
| 2026-08-24 | `uuid:cLKwX8jvQQiPFgYxjRhUFA==` | Foundations | 64 | 2 | Aaron |
| 2026-08-24 | `uuid:ELZkz9AsSPCVLs8bSynDhQ==` | Foundations | 67 | 2 | Tedarios |
| 2026-08-26 | `uuid:99svzltpQ8iJpEsJ1pmATg==` | Foundations | 48 | 1 | Tadirio |
| 2026-08-26 | `uuid:KhqtymUkTieJKHLqJ2pmYA==` | Foundations | 68 | 2 | unidentified |
| 2026-09-03 | `uuid:yLMACd4kQIiCsc4B4HbohA==` | Deep Dive | 103 | 2 | unidentified |
| 2026-08-27 | `uuid:wj2mARB6RtWx2Ij1/K/xIw==` | Deep Dive | 81 | 2 | Aaron |
