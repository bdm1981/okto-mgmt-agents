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
import re
from collections import Counter, defaultdict
from pathlib import Path

import ledger as L
import render as R

REF = Path(__file__).resolve().parent.parent / "references"


def session_index() -> dict:
    """uuid -> {course, minutes, spoke, trainer} from references/sessions-index.md.

    Missing entries are normal (a session audited before the index existed), so
    the Sessions table renders an em dash rather than dropping the row.
    """
    p = REF / "sessions-index.md"
    if not p.exists():
        return {}
    out = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        t = line.strip()
        if not t.startswith("| 2026"):
            continue
        c = [x.strip() for x in t.strip("|").split("|")]
        if len(c) < 7:
            continue
        out[re.sub(r"^`uuid:|`$", "", c[1])] = {
            "course": c[2], "minutes": c[3], "att": c[4], "spoke": c[5], "trainer": c[6],
        }
    return out

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
                (len(L.resolutions(rows)), "Fixed", "ok"),
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

    res = L.resolutions(rows)
    if res:
        out.append("<h2>Fixed</h2>")
        out.append(
            '<p class="sec-note">A claim the same trainer got wrong earlier and right later. Worth '
            "showing as prominently as the failures: it is the evidence that flagging things works, "
            "and leaving a corrected error standing as an open repeat would be unfair.</p>"
        )
        out.append(
            R.table(
                ["Claim", "Trainer", "Was", "Wrong through", "Right from"],
                [
                    [f"`{cid}`", e["trainer"], e["was"], e["last_wrong"], e["first_right"]]
                    for cid, entries in sorted(res.items())
                    for e in entries
                ],
            )
        )

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

    idx = session_index()
    out.append("<h2>Sessions</h2>")
    out.append(
        '<p class="sec-note"><strong>Att</strong> is real attendance from Zoom — distinct '
        "non-host names, waiting-room-only joins excluded, per-join duplicates collapsed. "
        "<strong>Spoke</strong> is distinct non-trainer speakers in the transcript. The gap "
        "between them is the point: 3 attended / 0 spoke is a passive session, and the "
        "transcript alone would have reported that as nobody there.</p>"
    )
    out.append(
        R.table(
            ["Date", "Course", "Min", "Att", "Spoke", "Trainer", "Claims", "Not correct", "Report"],
            [
                [
                    v["date"],
                    idx.get(u, {}).get("course", "—"),
                    idx.get(u, {}).get("minutes", "—"),
                    idx.get(u, {}).get("att", "—"),
                    idx.get(u, {}).get("spoke", "—"),
                    v["trainer"],
                    v["n"],
                    v["bad"],
                    f'[open]({reports[u]})' if reports.get(u) else "—",
                ]
                for u, v in sorted(sessions.items(), key=lambda kv: kv[1]["date"], reverse=True)
            ],
        )
    )
    total_min = sum(int(m) for m in (idx.get(u, {}).get("minutes") for u in sessions)
                    if str(m).isdigit())
    total_att = sum(int(a) for a in (idx.get(u, {}).get("att") for u in sessions)
                    if str(a).isdigit())
    if total_min:
        out.append(
            f'<p class="sec-note">{len(sessions)} sessions · '
            f"{total_min:,} minutes of training audited ({total_min/60:.1f} hours) · "
            f"{total_att} customer attendances.</p>"
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
