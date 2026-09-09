#!/usr/bin/env python3
"""Render one session's report from findings.jsonl + a narrative file.

    ./build_report.py --session <uuid> --findings findings.jsonl \
        --narrative narrative.json --sessions sessions.json > report.html

narrative.json (authored by the reviewer, words only):
    {"title": "...", "standfirst": "...", "method": "...",
     "practice_notes": [{"heading": "...", "paras": ["..."]}],
     "footer": "..."}
"""

import argparse
import json
import sys
from pathlib import Path

import render as R


def load_jsonl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", required=True)
    ap.add_argument("--findings", required=True)
    ap.add_argument("--narrative")
    ap.add_argument("--sessions", help="sessions.json, for session metadata")
    ap.add_argument("--baseline", default="", help="short SHA of the pinned commit")
    ap.add_argument("--fragment", action="store_true", help="emit an artifact fragment, not a full doc")
    args = ap.parse_args()

    findings = [f for f in load_jsonl(args.findings) if f.get("session") == args.session]
    if not findings:
        sys.exit(f"no findings for session {args.session} in {args.findings}")

    nar = json.loads(Path(args.narrative).read_text(encoding="utf-8")) if args.narrative else {}
    sess = {}
    if args.sessions:
        data = json.load(open(args.sessions))
        sess = next((s for s in data.get("sessions", []) if s["uuid"] == args.session), {})

    counts = {g: sum(1 for f in findings if f.get("grade") == g) for g in R.GRADE_ORDER}
    bugs = sum(1 for f in findings if f.get("product_bug"))

    title = nar.get("title") or (sess.get("topic") or "Training audit")
    standalone = not args.fragment
    out = [R.head(title, standalone), '<div class="wrap">']
    out.append('<p class="eyebrow">Training QA · Verified against source</p>')
    out.append(f"<h1>{R.e(title)}</h1>")
    if nar.get("standfirst"):
        out.append(f'<p class="standfirst">{R.rich(nar["standfirst"])}</p>')

    start = (sess.get("start_time") or "")[:10]
    out.append(
        R.meta(
            [
                ("Session", sess.get("topic", "—")),
                ("Recorded", start or "—"),
                ("Trainer", sess.get("trainer", "—")),
                ("Duration", f"{sess.get('duration_minutes','?')} min"),
                ("Verified against", f"`origin/development` @ {args.baseline or '—'}"),
            ]
        )
    )
    out.append(
        R.tally(
            [
                (counts["wrong_high"], "Wrong · high impact", "crit"),
                (counts["wrong_contained"], "Wrong · contained", "crit"),
                (counts["incomplete"], "Incomplete", "warn"),
                (counts["correct"], "Verified correct", "ok"),
                (bugs, "Product bugs", "crit"),
            ]
        )
    )
    if nar.get("method"):
        out.append(f'<p class="method">{R.rich(nar["method"])}</p>')

    # One section per grade, worst first. Empty grades are skipped rather than
    # rendered as an empty heading.
    seq = 0
    for grade in R.GRADE_ORDER:
        group = [f for f in findings if f.get("grade") == grade]
        if not group:
            continue
        out.append(f"<h2>{R.e(R.GRADE_LABEL[grade])}</h2>")
        if grade == "unverifiable":
            out.append(
                '<p class="sec-note">Claims that depend on tenant configuration, '
                "infrastructure, billing terms or third-party behavior. Listed, not graded.</p>"
            )
        for f in group:
            seq += 1
            out.append(R.finding(f, f"{seq:02d}"))

    for note in nar.get("practice_notes", []):
        if note is nar.get("practice_notes", [])[0]:
            out.append("<h2>Practice notes</h2>")
        out.append('<div class="block">')
        out.append(f'<h3>{R.rich(note.get("heading",""))}</h3>')
        for p in note.get("paras", []):
            out.append(f"<p>{R.rich(p)}</p>")
        out.append("</div>")

    out.append(
        "<footer>"
        + R.rich(
            nar.get("footer")
            or f"Claims traced against `origin/development` at {args.baseline or 'the pinned commit'}. "
            "Timestamps refer to the Zoom transcript."
        )
        + "</footer>"
    )
    out.append("</div>")
    out.append(R.tail(standalone))
    print("\n".join(out))


if __name__ == "__main__":
    main()
