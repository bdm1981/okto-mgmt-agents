# Published pages

## Rolling dashboard — Training QA

```
url: https://claude.ai/code/artifact/1d86f6a7-34f2-4d45-8af5-39b80e1d9eda
```

The first run publishes `dashboard.html` and records the URL here. **Every later run must
republish to that URL** (pass it as `url:` to the Artifact tool). Publishing without it
creates a second page, and the team ends up reading a stale one — this is the single most
common way this kind of skill breaks.

Only the artifact's owner can republish. One identity should run the audit; everyone else
consumes the link.

## Per-session reports

New artifact per session, recorded in the ledger row and linked from the dashboard's
Sessions table. These are not republished — a session's report is a fixed record of what
was said and what the code did on that day's commit.

**Course-level reports.** Where a course has many runs (Foundations ran 15 times in August),
one report grades the *script* and states how many runs carried each claim, and every run's
ledger rows point at it. Fifteen near-identical reports would bury the finding that matters —
that the same feature is described three incompatible ways across runs.

| date | session | url |
|---|---|---|
| 2026-08-25 | CRM & scheduler | https://claude.ai/code/artifact/1c83803b-606c-4f7a-b413-f89ec077f9c2 |
| 2026-08-24…25 | Analytics · Deep Dive · Foundations | https://claude.ai/code/artifact/253dda9e-77ef-4e75-acfc-3fb12e49a195 |
| 2026-08-27 | Deep Dive | https://claude.ai/code/artifact/dd17ce3f-ccf4-4d50-8346-928aa5c41744 |
| 2026-09-03 | Deep Dive (both 27 Aug errors fixed; first Okto Assist audit) | https://claude.ai/code/artifact/8b4e9948-a765-4a68-9058-786be1e73928 |
| 2026-08 (15 runs) | **Foundations, August** — course-level | https://claude.ai/code/artifact/78db82b4-5edc-46e4-a8d4-9215c7998b61 |
| 2026-09-02 | Foundations (On Deck fixed; last-login hedge) | https://claude.ai/code/artifact/e1d1b737-88c8-4490-ad49-7c2abe84566e |
| 2026-09-03 | Deep Dive (disable-user private-task gap) | https://claude.ai/code/artifact/c0f57918-6b71-4d38-b833-84173f7ce919 |
| 2026-09-08 | Shop Analytics (goal formula; Rocket Gauge gap) | https://claude.ai/code/artifact/3eb616fa-5637-4e7c-934a-d69cec0a11f3 |
| 2026-09-08 | Admin Part 1 (inverted Require Delete Reason) | https://claude.ai/code/artifact/5e30a542-2607-4c09-b981-b32450b24142 |
| 2026-09-09 | Admin Part 1 — Aaron (**translate defect closed**) | https://claude.ai/code/artifact/da58725d-412e-458c-aa56-3f25730f33af |
| 2026-09-09 | CRM Overview (two Aug errors taught right) | https://claude.ai/code/artifact/8fa59e6a-574a-4109-82fa-759d14c04508 |
| 2026-09-09 | Admin Part 2 (live tenant change flagged) | https://claude.ai/code/artifact/85d76d26-0f6e-4072-afba-543cc1075474 |
| 2026-09-14 | Admin Part 1 — Aaron (8 attendees; all checkable claims correct) | https://claude.ai/artifact/MXM5PWMeEbhpmGi8DMZWZh |
| 2026-09-14 | Admin Part 2 — TeDarrell (**block-customer permission inverted**) | https://claude.ai/artifact/7jsXWm3vnTT5ZCwjvJw9CN |
| 2026-09-15 | Admin Part 1 — TeDarrell? (**block-customer inverted again**; Require Delete Reason) | https://claude.ai/artifact/TDUauToxAN91qyM9Vy1yuk |
| 2026-09-15 | Shop Analytics (trainer caught Outrunning Overhead colour bug live) | https://claude.ai/artifact/J7Ttwhd6bLFLskNDb7kRq5 |
| 2026-09-16 | Admin Part 1 — Aaron (role-vs-permission theme; 10 of 13 correct) | https://claude.ai/artifact/XDsbHzEGuCYaAL8iwtu4Vu |
| 2026-09-17 | **Advisor Training — Allie** (first Advisor audit; block-customer taught right) | https://claude.ai/artifact/D7xW1RbY5LJcjXdGbRMvwx |
| 2026-09-21 | Admin Part 1 — unidentified (role-vs-permission again; demo lost admin scope) | https://claude.ai/artifact/XXkFEtoaVcY2kQekmtNTaD |
| 2026-09-21 | **Advisor Training — Allie** (closes the `calls.role-access` gap; new SMS-label product bug) | https://claude.ai/artifact/Cg88XUMmSpFnWsMjNWjr7w |
| 2026-09-21 | Admin Part 2 — TeDarrell (**All Recordings taught as a recording switch**; block-customer corrected) | https://claude.ai/artifact/4hefXCQjiyjRhYHR9EALdD |
| 2026-09-22 | Admin Part 2 — unidentified (**auto-reply gate**; directly-assigned campaign tasks widen to admins) | https://claude.ai/artifact/CoG64ixqBeuyUZzt5cQmcY |
| 2026-09-22 | **Advisor Training — Allie** (pinned-reports + SMS-label findings closed; **block-customer regressed**) | https://claude.ai/artifact/PfjhzMnwgLWPRaX3DCcGcw |
| 2026-09-22 | Admin Part 1 — TeDarrell? (11 of 14 correct; **Require Delete Reason label hits a 4th run**) | https://claude.ai/artifact/EFid33mck3htFEn9mNtK15 |
| 2026-09-23 | Advisor Training — unidentified (substitute trainer; service-description targeting) | https://claude.ai/artifact/LoPDr6QJNLa1AM4iC4Rt47 |
| 2026-09-23 | CRM Overview — unidentified (outcome-prompt repeat; third write path for the campaigns flag) | https://claude.ai/artifact/BzWCER7vmkRgVSGtmovS5W |
| 2026-09-24 | **Admin Part 1 — Aaron** (**Manage Campaigns contradiction**; new dead `/bookings/capture` bug) | https://claude.ai/artifact/BdVb8mLw4Cnq2mthsEKyzm |
| 2026-09-28 | **Admin Part 1 — Aaron** (appointment-lead minimum wrong a 3rd time, all Aaron; campaign-schedule contradiction) | https://claude.ai/artifact/AqrybKe9fsk3cD8HuA34Nx |
| 2026-09-28 | CRM Overview — TeDarrell? (8 of 9 correct; **Require Delete Reason label hits a 5th run**) | https://claude.ai/artifact/7mUaXa2gutXULBfedea6pm |
| 2026-09-29 | **Admin Part 1 — TeDarrell** (12 of 15 correct; **appointment-lead claim taught right for the first time**; Require Delete Reason hits a 6th run) | https://claude.ai/artifact/UwkHBjF9mzj4qyEVN7BvFM |
| 2026-09-29 | **Admin Part 2 — Aaron** (11 of 14 correct; three omissions, each missing the inverting branch) | https://claude.ai/artifact/1eEyjUvqmadzG3W174QXk3 |
| 2026-09-30 | **Admin Part 1 — Aaron** (5 of 10 correct; **vendor exclusion taught as forward-looking**, appointment-lead minimum wrong a 4th time) | https://claude.ai/artifact/REM99yMZEoDR9tRXQc9mZY |
| 2026-09-30 | **Advisor Training — Allie** (11 of 14 correct; **first ever correct vendor-flag statement**; block-customer regressed from 28 Sep) | https://claude.ai/artifact/FqSSwF9pjRjmDp4Xm2KXQ5 |
| 2026-09-28 | **Advisor Training — Allie** (recovered from the coverage gap; holds the correct script for vendor flag **and** block-customer) | https://claude.ai/artifact/6LUnRYzhpZ1ZzHxiFEsxe3 |
| 2026-10-07 | **CRM Overview — TeDarrell** (9 of 10 correct; **Require Delete Reason hits a 7th run**; campaign-schedule claim closed after six weeks) | https://claude.ai/artifact/9Rg1WcN9QdVvvRr8hq9K1o |
| 2026-10-07 | **Advisor Training — Allie** (14 of 16 correct, best Advisor session on record; **message-search and sentiment-timeline both closed**, block-customer correct again) | https://claude.ai/artifact/3TaTKy4vqmh12A2gbD6H23 |
| 2026-10-08 | **Shop Analytics — Aaron** (4 of 8 checkable correct; **"Tekmetric is the only system with authorized" is wrong — CE shops have job data too**; advisor autofill is a median with no 5% uplift) | https://claude.ai/artifact/Vgde3T9qGuCwi9NMtgo5vU |
| 2026-10-08 | **Advisor Training — Allie** (**12 of 13 checkable correct — best session on record**; sentiment timeline regressed from 7 Oct and the two runs disagree on identical code) | https://claude.ai/artifact/KYUspwes8ettnLX95rMtCE |
| 2026-10-12 | **Admin Part 1 — Aaron** (9 of 12 correct, 5 shops, mics open and three live questions; **appointment-lead minimum wrong a 5th time** — now a cross-trainer curriculum defect) | https://claude.ai/artifact/YL4ybkDz6TYoBss55Azty1 |
| 2026-10-12 | **CRM Overview — TeDarrell** (9 of 11 correct; **Require Delete Reason label hits an 8th run**; new keyword once-per-conversation omission) | https://claude.ai/artifact/PX74fJfs5A3yqFakaX6cdi |
| 2026-10-12 | **Admin Part 2 — TeDarrell** (6 of 7 correct — cleanest session on record; block-customer permission taught the right way round) | https://claude.ai/artifact/7Y96EpqqXFRb49NTxrjhbA |
| 2026-10-13 | **Advisor Training — Allie** (19 of 25 correct; **appointment-lead minimum wrong a 6th time**, now with the phone gate shown not to exist anywhere in the chain; missed-call definition taught via voicemail rather than talk time) | https://claude.ai/artifact/DKybJV8ugDdBwmUgKdb3rS |
| 2026-10-13 | Shop Analytics | https://claude.ai/artifact/Nt5XtBdrWu4L96Vx8TusiT |
| 2026-10-14 | Admin Part 1 | https://claude.ai/artifact/6fHnmPQoYWJGhVgqjH9m3h |
| 2026-10-14 | CRM Overview | https://claude.ai/artifact/Toxtc7sGymSaKHHPcEBdDM |
| 2026-10-08 | Admin Part 1 (recovered from the coverage gap on 14 Oct) | https://claude.ai/artifact/9pn6gFpvCpYUkMeu5NUKFS |
| 2026-10-15 | **Admin Part 2 — TeDarrell?** (18 of 26 correct, none wrong; **block-customer taught right a 4th time**; five off-branch omissions, two of them regressions out of Fixed) | https://claude.ai/artifact/MGRz9q3FULuFGAJhVruXoA |
| 2026-10-19 | **Admin Part 1 — Aaron** (5 of 8 correct; **vendor flag taught right**, and contradicted by Advisor two hours later; transcript-download role line drawn one rung too high) | https://claude.ai/artifact/HcjKjQwiuWNvhDP82zrFUk |
| 2026-10-19 | **Advisor Training — Allie** (11 of 12 correct; **advisor report default of 14 verified exactly**; vendor flag **regressed to wrong_high** on the same day Aaron taught it right) | https://claude.ai/artifact/DRTUCrHL28uwQPLd6qtSrZ |
| 2026-10-19 | **CRM Overview — TeDarrell** (6 of 8 correct, 1 attendee, fully consultative; **Require Delete Reason label hits a 10th run**) | https://claude.ai/artifact/Ppi3pNSNYiXSs4fmjwm1iF |
| 2026-10-20 | **Admin Part 2 — Aaron** (9 of 12 correct, none wrong; **block-customer and the group/individual report lock both read off the screen correctly**; stale-task window omitted a 6th time) | https://claude.ai/artifact/EYdgcXa3ydgSDoLUSVMCgd |
| 2026-10-20 | **Shop Analytics — Aaron** (4 of 12 checkable correct; **advisor autofill is a 3-month median with no 5% uplift — Aaron's 2nd time**; Rocket Gauge "every metric" hits a 5th run; Outrunning Overhead corrected out of wrong) | https://claude.ai/artifact/Cm5MGQVJDtNLwhtaw6WUZt |
| 2026-10-20 | **Advisor Training — Allie** (**13 of 13 correct — first clean session on record**; vendor flag taught right, reversing yesterday; **pinned-reports answer contradicts 5 ledger rows and the ledger looks wrong**) | https://claude.ai/artifact/LFJ7zJPwm4nmKWSS8CeaUS |
| 2026-10-21 | **CRM Overview — unidentified** (13 of 20 correct; **Require Delete Reason label hits an 11th run**; the Do Not Track Outcomes toggle read backwards) | https://claude.ai/artifact/X3dN2b1LPkDuJ25AC4rAFV |
| 2026-10-21 | **Admin Part 2 — TeDarrell** (16 of 24 correct; **All Recordings taught as a recording switch again**, a month after the same trainer made the same error; block-customer right a 5th time) | https://claude.ai/artifact/DL3jvUFEW3hRQbJpi3vjCq |
| 2026-10-27 | **Advisor Training — Allie** (8 of 13 checkable correct; **appointment-lead minimum wrong a 7th time**, now 10 wrong rows across two named trainers; sentiment timeline and pinned-reports both settled in her favour) | https://claude.ai/artifact/JWe3PDvNgrtLGnKx3NDdFJ |
| 2026-10-27 | **Admin Part 1 — TeDarrell** (7 of 9 checkable correct; all seven report categories and the four dashboard gauges named exactly; **unconfirmed-appointment direction inverted** and the Marketing Disabled filter read backwards) | https://claude.ai/artifact/McR6rGLAdKjwvGQzCkzFLr |
| 2026-10-29 | **Advisor Training — Allie** (18 of 23 checkable correct, best Advisor session since 20 Oct; **appointment-lead minimum wrong an 8th time** — 11 wrong rows across two trainers; **unconfirmed-appointment direction taught right, contradicting Admin Part 1 two days ago**; blockers and canned-response visibility both closed) | https://claude.ai/artifact/DchFaRDabdQf1gKFj8DMsq |
| 2026-11-02 | **Admin Part 1 — Aaron** (6 of 9 checkable correct, 4 of 4 present with mics open; **appointment-lead minimum taught right for the first time** after TRS-I2729 moved the product under it; transcript-download role line one rung too high a 3rd time; **reviews taught as Google-only — Carfax has been a second source since TRS-I332**) | https://claude.ai/artifact/Tuex6gHoti4WDqiEyVc9cu |
| 2026-11-02 | **Advisor Training — Allie** (13 of 16 checkable correct, best Advisor session since 20 Oct; block-customer right a 6th time, All Recordings override stated where Admin Part 1 omitted it; **call share-link visibility contradicts Admin Part 1 two hours earlier**; sentiment-timeline answer disagrees with the ledger and the ledger looks wrong) | https://claude.ai/artifact/1CFz9saSVmD4Lk1z5Wroe6 |
| 2026-11-02 | **CRM Overview — TeDarrell** (12 of 13 checkable correct — cleanest CRM session on record; **Require Delete Reason taught correctly for the first time in ledger history** now the label is fixed; Do Not Track Outcomes read the right way round, reversing 21 Oct; keyword once-per-conversation omitted a 4th time) | https://claude.ai/artifact/TPWtAxrCHiZHk5y4EdAHQm |
| 2026-11-03 | **Admin Part 2 — Aaron** (15 of 18 checkable correct; **unread stale tasks taught correctly for the first time by a named trainer**; recording retention stated as a one-year floor when 365 is only the default; disable-user private-task trap omitted a 4th time, in the very session that taught user voicemails as private) | https://claude.ai/artifact/DiZm5naiyKn5fHAfnd5B4z |
| 2026-11-03 | **Shop Analytics — Aaron** (6 of 10 checkable correct; **trainer said on air he would file a bug against Out-running Overhead — the widget works as designed and the colour clash he spotted is already an open row, so the ticket would duplicate a known issue**; job data taught as Tekmetric-only twice in one session, 5th row; recommend-from-history formula stated in full for the first time) | https://claude.ai/artifact/U8gw9KvhHqByaz1L8GAAN4 |
| 2026-11-03 | **Advisor Training — Allie** (16 of 17 checkable correct, cleanest session of the run; **Disable Campaigns taught as all-channel against the modal's own SMS wording — she is right and the copy is wrong**; Carfax named as a second review source, reversing Admin Part 1 on 2 Nov; Shop-Ware gate on unconfirmed appointments omitted) | https://claude.ai/artifact/74yEdm7A4dwUi82pwM2gjn |
| 2026-11-03 | **Admin Part 1 — TeDarrell** (7 of 8 checkable correct; **unconfirmed-appointment direction taught right, reversing his own 27 Oct session**; Shop-Ware gate omitted here too, making it a two-trainer curriculum defect on one day) | https://claude.ai/artifact/3ZDGwGwPQYRAeMUopb4mdH |
| 2026-11-04 | **Admin Part 1 — unidentified** (3 of 6 checkable correct; **site managers taught as unable to download call recordings and transcripts when the gate includes them**; appointment-lead minimum given as phone-only when email alone also raises a lead; whole reviews segment taught as Google-only, omitting Carfax) | https://claude.ai/artifact/Fe8YEGZShhwZmz3DWXQFp2 |
| 2026-11-04 | **CRM Overview — unidentified** (4 of 7 checkable correct, graded on the last 37 min of a 59-min recording; **short-notice booking described backwards as a cap on how far ahead customers may book**; Campaigns V2 presented as unreleased when it ships behind a per-tenant flag; keyword once-per-conversation omitted a 5th time) | https://claude.ai/artifact/LsffvFteq77bpvkeBCFJBB |
| 2026-11-04 | **Advisor Training — Allie** (11 of 12 checkable correct, cleanest Advisor session on record; **three separate claims where she contradicts the ledger and the ledger is at fault** — Disable Campaigns all-channel, no pinned-report cap, vendor calls excluded from Advisor IQ; appointment-lead phone-vs-email omitted) | https://claude.ai/artifact/EcUiZspRT2cDsn8LfozGZ3 |
| 2026-11-04 | **Admin Part 2 — TeDarrell** (7 of 7 checkable correct, no errors found; **clearest delivery of Restrict Advisor Block Customer on record — he names the inversion out loud and proves it by impersonation**; per-user call recording given with its off branch unprompted) | https://claude.ai/artifact/GUdBn2QWwzyWoLae6x2XJU |
| 2026-11-05 | **Shop Analytics — unidentified** (new product bug: **goal-wizard working days ignore the site's configured holiday schedule**, found live when the customer's Thanksgiving was not subtracted; trainer verified it on air and said he would file it; job data taught as Tekmetric-only a 6th time when CE shops get it too; no name stated anywhere in the recording) | https://claude.ai/artifact/SGvkvk7n4vGa4ajHfmysK3 |
| 2026-11-05 | **Advisor Training — Allie** (20 of 22 correct; **named the All Recordings override and the Carfax review source that Admin Part 1 missed the same afternoon**, and stated Disable Campaigns all-channel against the modal's own SMS copy for a third consecutive session; On Deck taught as having no bulk approve when a multi-select toggle exists) | https://claude.ai/artifact/5xZLNTtJL22pjzRBcjzrfu |
| 2026-11-05 | **Admin Part 1 — Aaron** (14 of 20 correct; **a Mitchell 1 shop told to expect unconfirmed appointments, which are ShopWare-gated** — Allie named the gate correctly two hours earlier; site managers again taught as unable to download recordings or transcripts; reviews taught as Google-only, omitting Carfax) | https://claude.ai/artifact/PNGXYPXmT2Cc7dGX6LsUcB |
| 2026-10-20 | **Admin Part 1 — TeDarrell** (recovered from the coverage gap after 15 days; 10 of 14 checkable correct, 5 shops in the room; **Require Delete Reason read off the inverted label two days before the label was fixed**; On Deck, message rotation and the Google rating floor all stated exactly) | https://claude.ai/artifact/DMZYmPzj31iLK1WTRmhXbF |
| 2026-10-22 | **Advisor Training — Allie** (recovered from the coverage gap after 13 days; **15 of 16 checkable correct and nothing wrong — the cleanest session in the ledger**; first trainer ever to state the Disable-Campaigns-free message-search split correctly, and block-customer named as a restriction rather than a grant) | https://claude.ai/artifact/Fi5DTMD2MTaZ6FwrKPRzgX |
| 2026-10-28 | **Admin Part 1 — Aaron** (recovered from the coverage gap after 7 days; 11 of 15 checkable correct; **site managers told they cannot download recordings or transcripts, then told three minutes later they can adjust AI scores — both sit behind the same role check**; appointment lead given as phone-only when email alone also raises one; **first correct two-way statement of the translate feature in ledger history**) | https://claude.ai/artifact/XzQ5QcXymTpvBQrAWbjERp |
| 2026-11-09 | **Admin Part 2 — unidentified** (20 of 30 correct and **nothing graded wrong** — the cleanest Admin Part 2 in the ledger; **the OktoAssist 250-call allowance and $0.75 overage moved into code, so a claim filed unverifiable five times since September is now verified correct**; Rocket Shield taught as challenging every unrecognised caller when only weak-attestation calls are screened; name dropped by the transcriber at 00:18) | https://claude.ai/artifact/GdjFdR3kqTiSepe92fg36h |
| 2026-11-10 | **Admin Part 1 — TeDarrell** (7 of 9 checkable correct, nothing wrong; **the Google rating floor stated exactly, default of 4 and the private-feedback route included**; block-customer named as the default it is; the inbox translator taught as English/Spanish the day after French shipped) | https://claude.ai/artifact/UcDYptbN153fKiPnfeowao |
| 2026-11-10 | **Shop Analytics — Aaron** (4 of 7 checkable correct, nothing wrong, 3 genuinely unverifiable; **the recommended-goals formula stated correctly for a third consecutive run — growth of 5% with a seasonal factor, the claim that was wrong_high in August**; threshold presets right on values; ~10 min lost to one attendee's login, closing third compressed) | https://claude.ai/artifact/HUciEWdBgE2TonYmA4VqCc |
| 2026-11-10 | **Advisor Training — Allie** (**10 of 11 checkable correct and nothing wrong — cleanest session of the run**; contradicted the modal's own SMS-only copy on Disable Campaigns again, named the ShopWare gate on unconfirmed appointments precisely, demonstrated the appointment lead live; the translator's new French support is the one gap) | https://claude.ai/artifact/PG4YTP5WaKQ2yD81KQdpfN |
| 2026-11-11 | **CRM Overview — TeDarrell** (9 of 12 checkable correct; **the delete-reason polarity taught correctly for a second consecutive run, closing out the ledger's most-repeated misconception**; but **Skip to Form taught as a faster route onto the calendar when it creates no appointment at all — it is a lead-capture bailout form**; after-hours resources described as hosted items rather than links) | https://claude.ai/artifact/CDkqZiAkWPxnGmo5he7SdT |
| 2026-11-11 | **Admin Part 2 — TeDarrell** (9 of 16 correct, 2 unverifiable; **All Recordings taught as a recording switch for the third time — it is a visibility grant, so following it over-grants an advisor every colleague's calls**; the inverted block-customer permission and both directions of call-recording precedence handled correctly; OktoAssist allowance verified against the billing contract) | https://claude.ai/artifact/Jv5pVCykyKUfRyyuvd8jjh |
| 2026-11-12 | **Shop Analytics — Aaron** (re-rendered 13 Nov with the customer health check; **the account rates at_risk — goals never configured and employees never synced three months after install, and the owner asked who he could hire to implement it**; 7 of 8 checkable correct, **nothing wrong**; **the recommended-goals formula right for a fourth consecutive run, seasonal factor and all**; two open product bugs reported accurately and unprompted — the goal-wizard holiday gap and the Outrunning Overhead colour; ~12 min lost to a demo that would not load, taught on the customer's own data with consent) | https://claude.ai/artifact/UqmQnaaDF7DzcyQ7x5jw3h |
| 2026-11-12 | **Admin Part 1 — Aaron** (re-rendered 13 Nov with model-delivery examples and the customer health check; 5 of 8 checkable correct; **the inbox Callback badge taught as unreleased when it shipped 27 days earlier — and it was the direct answer to the customer's own question about advisors closing tasks without calling back**; reviews taught as Google-only two weeks after CARFAX shipped; the bailout-lead phone rule stated exactly) | https://claude.ai/artifact/U91nN2Z2FCDFhm8i1a1X5n |
