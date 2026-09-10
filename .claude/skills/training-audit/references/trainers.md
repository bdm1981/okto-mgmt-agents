# Trainers

The ledger's repeat and contradiction detection keys on **trainer**, so a name that varies
between rows splits one person into several and manufactures curriculum defects that do not
exist. This file is the canonical spelling.

## Roster

| canonical | Zoom account | notes |
|---|---|---|
| Aaron | aaron@oktorocket.com | Aaron Viratos. Runs Foundations, Deep Dive, Shop Analytics |
| TeDarrell | tedarrell@oktorocket.com | TeDarrell Cantrell. Runs Foundations and CRM. No individual *Zoom* account; hosts Zoom sessions via the shared training account. Confirmed 9 Sep 2026 from his Zoho Meeting user record — the first non-human-memory source for this spelling |
| Allie | aldith@oktorocket.com | Allie Gratton — note the account's `firstName` is **Aldith**, so a name pulled from Zoho may read "Aldith Gratton". Added to the roster 10 Sep 2026 on Brad's confirmation that the trainer bench is Aaron, Allie and TeDarrell; she had been missing entirely. Member of the OktoRocket Training department; "Mock Advisor Training - Allie Gratton" (31 Aug) suggests Advisor is hers |

## Aliases

Zoom's transcription mangles spoken names. Every variant seen so far, all one person:

| variant | canonical |
|---|---|
| TeDarrell | TeDarrell |
| Tedario | TeDarrell |
| Tadario | TeDarrell |
| Tedarios | TeDarrell |
| Tadirio | TeDarrell |
| CRM trainer | TeDarrell |
| Ali | Allie |
| Aldith | Allie |

Four spellings appeared across four August Foundations runs, and **none of them was correct** —
the real name is TeDarrell, confirmed by a human. The audit originally canonicalised on
"Tedario" simply because it was the most frequent transcription, which was wrong.

**The canonical spelling must come from a person or a Zoom account, never from a transcript.**
Zoom's speech-to-text is the source of the variants; it cannot also be the arbiter of which one
is right. When a new name appears, add the variant and ask someone rather than picking the
plurality spelling.

## Identifying the trainer

1. **Not from the Zoom host.** Every session runs through the shared `training@oktorocket.com`
   account, so the host is always "OktoRocket Training".
2. **From the transcript's own introduction** — "my name is …", usually in the first two minutes.
3. **When the name is never stated** (5 of 15 August Foundations runs, and 4 of the 5 Zoho
   sessions on 8-9 Sep), do not guess from writing style. Record `unidentified` and say so in the
   report's caveats. A wrong attribution is worse than a missing one: it invents a cross-trainer
   defect or hides a real one.

## Attributed via the AI summary — Advisor Training, 9 Sep 2026 = Allie

The one Zoho session with a name attached, and it came from an unexpected place. The recording's
**AI summary** opens: *"Webinar host introduced self as new trainer Ali and confirmed the session
comprises two attendees despite scheduling three."* `Ali` → **Allie** (Allie Gratton), consistent
with her being newly added to the bench and with "Mock Advisor Training - Allie Gratton" (31 Aug).

**Caveat that must travel with this attribution:** it is Zoho's *generated summary*, not verbatim
transcript — the transcript for that session still does not exist. Treat it as strong but
derived, and confirm with a human before it hardens into ledger history. It also does not license
using summaries for grading: a summary is a paraphrase and cannot support a `path:line` finding.

**The inference built on that line was wrong twice over.** "This is the third one, the one I did
earlier today for the CRM" (Admin Part 2, 01:49) was read as the trainer and used to link CRM and
Admin Part 2 to one person. It was **the customer** — Jason Simms, who attended both. Confirmed
10 Sep: CRM was **Aaron**, Admin Part 2 was **TeDarrell**, Advisor was **Allie**. See gotchas.md,
"Without speaker labels, do not attribute a first-person line to the trainer".

## Confirmed attributions, 8-9 Sep 2026 (from Brad, 10 Sep)

| session | trainer | how |
|---|---|---|
| 8 Sep Shop Analytics | Aaron | Brad |
| 8 Sep Admin Part 1 | *still unidentified* | — |
| 9 Sep Admin Part 1 | Aaron | stated in transcript |
| 9 Sep CRM Overview | Aaron | Brad |
| 9 Sep Advisor | Allie | AI summary, confirmed by Brad |
| 9 Sep Admin Part 2 | TeDarrell | Brad |

Re-attribution changed the analysis, which is the whole reason it matters: the two Shop Analytics
repeats became **Aaron twice** (coaching) rather than cross-trainer (curriculum), and two claims
became genuine **TeDarrell-wrong / Aaron-right** contradictions where the correct script already
exists on a recording.

## Zoho attribution: every metadata route is a dead end

Checked 10 Sep 2026 against the five 8-9 Sep sessions. None of these identifies the deliverer:

- **Webinar `presenter` / `presenterEmail` / `displayName`** — **Jada Baker on every session**, because
  she schedules them all. Same shared-host problem as Zoom's `training@oktorocket.com`, new name.
  `getWebinarDetails` returns no co-organizer or speaker field.
- **Recording `creatorName`** — also Jada, for every recording.
- **`getSpecificUserDetails`** — returns no timezone, so a transcript line like "the Eastern Time
  zone like me" (CRM, 9 Sep) cannot be matched to a person.
- **Transcript sweep** — searched all five for Aaron / Allie / TeDarrell plus every known
  mis-transcription (Erin, Aron, Ally, Ali, Aldith, Tedario, Tadario, Tadirio, Tedarios, Darrell)
  and Jada. Exactly one hit: "My name is Aaron", Admin Part 1, 9 Sep.

**Do NOT infer the trainer from the mock-training titles.** They are named per person — "Admin 1
Mock Training - TeDarrell Cantrell", "Admin 2 Mock Training - Aaron Viratos", "Mock Advisor
Training - Allie Gratton" — which looks like a course-to-trainer map and is not one: Aaron
demonstrably delivered **Admin Part 1** on 9 Sep, the course the mock assigns to TeDarrell.

**What does work.** The recordings are MP4s with the trainer on camera — a human can name all four
in about a minute, and that is the fastest route for a backlog. Permanently, either ask trainers to
state their name in the opening (the Zoom-era Foundations script did this and attribution worked),
or add the actual trainer as a Zoho **co-organizer / speaker** so the API can read it.

**One free pairing:** the transcripts establish that CRM (11am) and Admin Part 2 (3pm) on 9 Sep were
the same person — "the one I did earlier today for the CRM". Identify one and the other follows.
