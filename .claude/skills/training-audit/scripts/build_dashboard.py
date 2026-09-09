#!/usr/bin/env python3
"""Render the rolling Training QA dashboard from the findings ledger.

The dashboard answers three questions the per-session reports cannot:
  1. Which misconceptions recur across sessions or trainers (curriculum defects)?
  2. What product bugs are still open, and how many sessions have hit them?
  3. Is accuracy trending anywhere?

    ./build_dashboard.py --baseline fb8220cd6 --reports reports.json > dashboard.html
"""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import ledger as L
import render as R

REF = Path(__file__).resolve().parent.parent / "references"

BAD = ("wrong_high", "wrong_contained", "incomplete")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default="")
    ap.add_argument("--reports", help='JSON map {"uuid": "https://…report url"}')
    ap.add_argument("--fragment", action="store_true")
    args = ap.parse_args()

    rows = L.load()
    if not rows:
        raise SystemExit("ledger is empty — run an audit first")
    reports = json.loads(Path(args.reports).read_text(encoding="utf-8")) if args.reports else {}
    reps = L.repeats(rows)

    sessions = {}
    for r in rows:
        sessions.setdefault(r["uuid"], {"date": r["date"], "trainer": r["trainer"], "n": 0, "bad": 0})
        sessions[r["uuid"]]["n"] += 1
        if r["grade"] in BAD:
            sessions[r["uuid"]]["bad"] += 1

    grades = Counter(r["grade"] for r in rows)
    trainers = defaultdict(lambda: Counter())
    for r in rows:
        trainers[r["trainer"]][r["grade"]] += 1

    standalone = not args.fragment
    out = [R.head("Training QA", standalone), '<div class="wrap">']
    out.append('<p class="eyebrow">Training QA · Rolling</p>')
    out.append("<h1>Training QA</h1>")
    out.append(
        '<p class="standfirst">Every audited customer training session, graded against product '
        "source. Repeats across sessions are curriculum defects, not coaching notes — they lead.</p>"
    )
    out.append(
        R.meta(
            [
                ("Sessions audited", len(sessions)),
                ("Claims graded", len(rows)),
                (
                    "Curriculum defects",
                    sum(1 for v in reps.values() if v["curriculum_defect"])
                    + len(L.contradictions(rows)),
                ),
                ("Verified against", f"`origin/development` @ {args.baseline or '—'}"),
            ]
        )
    )
    out.append(
        R.tally(
            [
                (grades.get("wrong_high", 0), "Wrong · high impact", "crit"),
                (grades.get("wrong_contained", 0), "Wrong · contained", "crit"),
                (grades.get("incomplete", 0), "Incomplete", "warn"),
                (grades.get("correct", 0), "Verified correct", "ok"),
                (len(reps), "Repeating", "warn"),
                (len(L.contradictions(rows)), "Contradictions", "warn"),
            ]
        )
    )

    out.append("<h2>Repeats and curriculum defects</h2>")
    if reps:
        out.append(
            '<p class="sec-note">A claim graded wrong in more than one session. Where more than one '
            "trainer made it, the curriculum is at fault and coaching one person will not fix it.</p>"
        )
        ordered = sorted(reps.items(), key=lambda kv: (not kv[1]["curriculum_defect"], -kv[1]["count"]))
        out.append(
            R.table(
                ["Claim", "Times", "Sessions", "Trainers", "Verdict"],
                [
                    [
                        f"`{cid}`",
                        v["count"],
                        len(v["sessions"]),
                        ", ".join(v["trainers"]),
                        "**Curriculum defect**" if v["curriculum_defect"] else "Same trainer — coaching",
                    ]
                    for cid, v in ordered
                ],
            )
        )
    else:
        out.append('<p class="sec-note">No claim has yet been graded wrong in more than one session.</p>')

    cons = L.contradictions(rows)
    if cons:
        out.append("<h2>Contradictions</h2>")
        out.append(
            '<p class="sec-note">The same thing taught <strong>wrong in one session and correctly '
            "in another</strong>. Nobody is consistently wrong, so this never shows up as a repeat — "
            "but the curriculum is inconsistent, and the fix is free because a correct script "
            "already exists in a recording.</p>"
        )
        out.append(
            R.table(
                ["Claim", "Taught wrong by", "Taught right by", "Fix"],
                [
                    [
                        f"`{cid}`",
                        ", ".join(v["wrong_trainers"]),
                        ", ".join(v["right_trainers"]),
                        "Lift the correct wording into the other curriculum",
                    ]
                    for cid, v in sorted(cons.items())
                ],
            )
        )

    bugs = REF / "product-bugs.md"
    if bugs.exists():
        out.append("<h2>Open product bugs</h2>")
        out.append(
            '<p class="sec-note">Found while auditing, independent of any trainer. These keep '
            "producing wrong answers until fixed — several are the product contradicting itself.</p>"
        )
        body = bugs.read_text(encoding="utf-8")
        rows_md = [
            [c.strip() for c in l.strip().strip("|").split("|")]
            for l in body.splitlines()
            if l.strip().startswith("|") and not set(l.replace("|", "").strip()) <= set("-: ")
        ]
        rows_md = [r for r in rows_md if r and r[0].lower() not in ("what", "id")]
        if rows_md:
            out.append(R.table(["What", "Where", "Effect", "Status"], [r[:4] for r in rows_md]))

    out.append("<h2>Sessions</h2>")
    out.append(
        R.table(
            ["Date", "Trainer", "Claims", "Not correct", "Report"],
            [
                [
                    v["date"],
                    v["trainer"],
                    v["n"],
                    v["bad"],
                    f'[open]({reports[u]})' if reports.get(u) else "—",
                ]
                for u, v in sorted(sessions.items(), key=lambda kv: kv[1]["date"], reverse=True)
            ],
        )
    )

    out.append("<h2>By trainer</h2>")
    out.append(
        '<p class="sec-note">Counts, not a ranking. A trainer who covers more checkable ground '
        "accumulates more of everything, including errors.</p>"
    )
    out.append(
        R.table(
            ["Trainer", "Graded", "Wrong", "Incomplete", "Correct"],
            [
                [
                    t,
                    sum(c.values()),
                    c["wrong_high"] + c["wrong_contained"],
                    c["incomplete"],
                    c["correct"],
                ]
                for t, c in sorted(trainers.items(), key=lambda kv: -sum(kv[1].values()))
            ],
        )
    )

    out.append(
        "<footer>Rendered from <span class=\"mono\">references/findings-ledger.md</span>. "
        f"Code baseline {R.e(args.baseline or '—')}. Republish to the fixed URL in "
        "<span class=\"mono\">references/dashboard.md</span> — publishing without it creates a second page."
        "</footer>"
    )
    out.append("</div>")
    out.append(R.tail(standalone))
    print("\n".join(out))


if __name__ == "__main__":
    main()
