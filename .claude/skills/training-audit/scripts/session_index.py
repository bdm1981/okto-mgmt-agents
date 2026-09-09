#!/usr/bin/env python3
"""Per-session metadata index: duration, speakers, course, trainer.

Kept separate from the findings ledger on purpose. The ledger is append-only and
claim-shaped — one row per graded claim — so session facts would either duplicate
across every row or force a schema change on 80+ existing rows. This is a small
join table the dashboard reads instead.

    ./session_index.py --sessions sessions.json --transcripts /tmp/fnd --add

Attendee counting: `speakers` is the number of DISTINCT non-trainer speakers in
the transcript, which is a FLOOR on attendance, not attendance. Anyone who never
unmutes is invisible to it. Exact counts need a Zoom participants endpoint and
the scope for it (see references/sources.md); until then the dashboard labels
this column "spoke", never "attended".
"""

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ledger import canonical_trainer  # noqa: E402  (shared alias map)

REF = Path(__file__).resolve().parent.parent / "references"
INDEX = REF / "sessions-index.md"

HEADER = """# Session index

Per-session facts the dashboard joins onto the findings ledger. Written by
`scripts/session_index.py`.

`spoke` is the count of distinct non-trainer speakers in the transcript — a **floor**
on attendance, not attendance. Someone who never unmutes does not appear. Exact
counts require a Zoom participants scope the audit app does not yet hold.

| date | uuid | course | minutes | spoke | trainer |
|---|---|---|---|---|---|
"""

HOST_LABELS = re.compile(r"^(oktorocket training|audio shared by|recording|zoom)", re.I)


def course_of(topic: str) -> str:
    t = (topic or "").lower()
    for key, label in (
        ("deep", "Deep Dive"), ("founation", "Foundations"), ("foundation", "Foundations"),
        ("crm", "CRM"), ("analytic", "Sales Analytics"), ("one on one", "1:1 Client"),
    ):
        if key in t:
            return label
    return "Other"


def speakers(path: str) -> tuple[int, list[str]]:
    """Distinct non-host speaker labels in a compacted transcript."""
    names = {}
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\[[\d:]+\]\s+([^:]{1,60}?):\s", line)
        if not m:
            continue
        who = m.group(1).strip()
        if HOST_LABELS.match(who):
            continue
        names[who] = names.get(who, 0) + 1
    return len(names), sorted(names)


def trainer_of(path: str) -> str:
    """Trainer name from the transcript's own introduction, canonicalised.

    Zoom mis-transcribes spoken names (one trainer came back four ways), so the
    raw capture goes through the ledger's alias map rather than into a row as-is
    — otherwise the index and the ledger disagree about who ran a session and
    the dashboard shows both spellings.
    """
    txt = Path(path).read_text(encoding="utf-8", errors="replace")[:9000]
    m = re.search(r"my name is ([A-Z][A-Za-z]+)", txt, re.I)
    if not m:
        return "unidentified"
    return canonical_trainer(m.group(1))


def existing() -> set:
    if not INDEX.exists():
        return set()
    return set(re.findall(r"`uuid:([^`]+)`", INDEX.read_text(encoding="utf-8")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sessions", required=True)
    ap.add_argument("--transcripts", required=True, help="dir of compacted .txt files")
    ap.add_argument("--add", action="store_true", help="write; otherwise dry run")
    args = ap.parse_args()

    sess = json.load(open(args.sessions))["sessions"]
    have = existing()
    rows, skipped = [], 0

    for s in sess:
        if s["uuid"] in have:
            skipped += 1
            continue
        tag = s["start_time"][:10] + "-" + s["start_time"][11:16].replace(":", "")
        cand = os.path.join(args.transcripts, f"{tag}.txt")
        if not os.path.isfile(cand):
            hits = glob.glob(os.path.join(args.transcripts, "*.txt"))
            cand = next((h for h in hits if tag in h), "")
        if not cand or not os.path.isfile(cand):
            print(f"warn: no transcript for {tag}, skipping", file=sys.stderr)
            continue
        n, who = speakers(cand)
        rows.append(
            "| {d} | `uuid:{u}` | {c} | {m} | {n} | {t} |".format(
                d=s["start_time"][:10], u=s["uuid"], c=course_of(s.get("topic", "")),
                m=s.get("duration_minutes", "?"), n=n, t=trainer_of(cand))
        )
        print(f"  {tag}  {course_of(s.get('topic','')):16s} {s.get('duration_minutes'):>3}m  "
              f"spoke={n} {who if n else ''}")

    if args.add and rows:
        if not INDEX.exists():
            INDEX.write_text(HEADER, encoding="utf-8")
        with INDEX.open("a", encoding="utf-8") as fh:
            fh.write("\n".join(rows) + "\n")
    print(f"\n{len(rows)} indexed, {skipped} already present"
          f"{'' if args.add else ' (dry run — pass --add to write)'}", file=sys.stderr)


if __name__ == "__main__":
    main()
