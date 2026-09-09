#!/usr/bin/env python3
"""The findings ledger: append a run, detect repeats, report product-bug deltas.

This is the piece that makes a scheduled audit worth more than four ad-hoc ones.
A `claim_id` seen in more than one session — especially from more than one
trainer — is a curriculum defect rather than a coaching note, and that is the
finding management should act on first.

    ./ledger.py --add findings.jsonl                 # append + print deltas
    ./ledger.py --repeats                            # current repeat table
    ./ledger.py --check findings.jsonl               # dry run, changes nothing
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "references"
LEDGER = REF / "findings-ledger.md"

GRADES = ("wrong_high", "wrong_contained", "incomplete", "correct", "unverifiable")

HEADER = """# Findings ledger

Append-only. One row per graded claim, oldest first. `claim_id` is the join key:
reuse an existing id when the same misconception recurs, so repeats are
detectable. Written by `scripts/ledger.py`; do not hand-edit rows.

| date | uuid | trainer | claim_id | grade | stamp | evidence |
|---|---|---|---|---|---|---|
"""


def load() -> list[dict]:
    if not LEDGER.exists():
        return []
    rows = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s.startswith("|") or s.startswith("|---") or "| date |" in s:
            continue
        c = [x.strip() for x in s.strip("|").split("|")]
        if len(c) < 7:
            continue
        rows.append(
            {
                "date": c[0],
                "uuid": re.sub(r"^`uuid:|`$", "", c[1]),
                "trainer": c[2],
                "claim_id": re.sub(r"^`|`$", "", c[3]),
                "grade": c[4],
                "stamp": c[5],
                "evidence": c[6],
            }
        )
    return rows


def repeats(rows: list[dict]) -> dict:
    by_claim = defaultdict(list)
    for r in rows:
        if r["grade"] in ("wrong_high", "wrong_contained", "incomplete"):
            by_claim[r["claim_id"]].append(r)
    out = {}
    for cid, rs in by_claim.items():
        sessions = {r["uuid"] for r in rs}
        trainers = {r["trainer"] for r in rs}
        if len(sessions) > 1:
            out[cid] = {
                "count": len(rs),
                "sessions": sorted(sessions),
                "trainers": sorted(trainers),
                "curriculum_defect": len(trainers) > 1,
                "worst": min(rs, key=lambda r: GRADES.index(r["grade"]) if r["grade"] in GRADES else 9)["grade"],
            }
    return out


def contradictions(rows: list[dict]) -> dict:
    """Same claim taught WRONG in one session and CORRECT in another.

    This is a distinct defect from a repeat and was the single most useful
    finding in the seed set: after-hours resource links were taught as file
    uploads in one session and correctly as links-only in another, five weeks
    apart. Nobody was consistently wrong, so repeat detection missed it — yet
    the curriculum is plainly inconsistent, and the fix is free because a
    correct script already exists in-house.
    """
    by_claim = defaultdict(list)
    for r in rows:
        by_claim[r["claim_id"]].append(r)

    out = {}
    for cid, rs in by_claim.items():
        wrong = [r for r in rs if r["grade"] in ("wrong_high", "wrong_contained", "incomplete")]
        right = [r for r in rs if r["grade"] == "correct"]
        if wrong and right and {r["uuid"] for r in wrong} != {r["uuid"] for r in right}:
            out[cid] = {
                "wrong_in": sorted({r["uuid"] for r in wrong}),
                "right_in": sorted({r["uuid"] for r in right}),
                "wrong_trainers": sorted({r["trainer"] for r in wrong}),
                "right_trainers": sorted({r["trainer"] for r in right}),
                # A correct version exists, so this is fixable by copying it.
                "fix_exists": True,
            }
    return out


def append(findings: list[dict], dry: bool) -> dict:
    before = load()
    known_claims = {r["claim_id"] for r in before}
    known_uuids = {r["uuid"] for r in before}

    dupes = sorted({f["session"] for f in findings} & known_uuids)
    if dupes:
        sys.exit(
            "refusing to append: these sessions are already in the ledger, and\n"
            "re-auditing corrupts repeat detection:\n  " + "\n  ".join(dupes)
        )

    new_rows = []
    for f in findings:
        ev = ", ".join(f.get("evidence") or []) or "—"
        new_rows.append(
            "| {date} | `uuid:{uuid}` | {trainer} | `{cid}` | {grade} | {stamp} | {ev} |".format(
                date=f.get("date", ""),
                uuid=f["session"],
                trainer=f.get("trainer", "?"),
                cid=f["claim_id"],
                grade=f["grade"],
                stamp=f.get("stamp", ""),
                ev=ev,
            )
        )

    if not dry:
        if not LEDGER.exists():
            LEDGER.write_text(HEADER, encoding="utf-8")
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write("\n".join(new_rows) + "\n")

    after = before + [
        {
            "date": f.get("date", ""),
            "uuid": f["session"],
            "trainer": f.get("trainer", "?"),
            "claim_id": f["claim_id"],
            "grade": f["grade"],
            "stamp": f.get("stamp", ""),
            "evidence": ", ".join(f.get("evidence") or []),
        }
        for f in findings
    ]

    rep_before, rep_after = repeats(before), repeats(after)
    newly_repeat = {k: v for k, v in rep_after.items() if k not in rep_before}
    con_before, con_after = contradictions(before), contradictions(after)
    newly_contra = {k: v for k, v in con_after.items() if k not in con_before}
    new_bugs = [f for f in findings if f.get("product_bug") and f["claim_id"] not in known_claims]

    return {
        "appended": len(new_rows),
        "dry_run": dry,
        "newly_repeating": newly_repeat,
        "all_repeating": rep_after,
        "newly_contradicting": newly_contra,
        "all_contradicting": con_after,
        "new_product_bugs": [
            {"claim_id": f["claim_id"], "reality": f.get("reality", ""), "evidence": f.get("evidence", [])}
            for f in new_bugs
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--add", metavar="findings.jsonl")
    ap.add_argument("--check", metavar="findings.jsonl")
    ap.add_argument("--repeats", action="store_true")
    ap.add_argument("--contradictions", action="store_true")
    args = ap.parse_args()

    if args.repeats:
        json.dump(repeats(load()), sys.stdout, indent=2)
        print()
        return

    if args.contradictions:
        json.dump(contradictions(load()), sys.stdout, indent=2)
        print()
        return

    path = args.add or args.check
    if not path:
        ap.error("give --add, --check, --repeats or --contradictions")

    findings = []
    for i, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            f = json.loads(line)
        except json.JSONDecodeError as e:
            sys.exit(f"{path}:{i}: bad JSON: {e}")
        for k in ("session", "claim_id", "grade"):
            if not f.get(k):
                sys.exit(f"{path}:{i}: missing required field {k!r}")
        if f["grade"] not in GRADES:
            sys.exit(f"{path}:{i}: grade {f['grade']!r} not one of {GRADES}")
        if f["grade"] in ("wrong_high", "wrong_contained", "incomplete") and not f.get("evidence"):
            sys.exit(
                f"{path}:{i}: {f['claim_id']} is graded {f['grade']} with no evidence.\n"
                "Every non-correct finding needs a path:line, or grade it 'unverifiable'."
            )
        findings.append(f)

    json.dump(append(findings, dry=bool(args.check)), sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
