#!/usr/bin/env python3
"""List every call whose transcript the daily review must read.

Usage: select_transcripts.py --calls FILE [FILE ...] --map map.json [--teams Support] [--min-talk 45]
Prints one line per call: callId ext name talk direction iq -- newest first. Excludes internal
ext-to-ext calls, unrecorded calls, vendor-labelled calls, and calls under --min-talk seconds
(too short to coach). Read ALL of these; the ranked triage queue is for prioritising order, not
for skipping.
"""
import argparse, json
ap = argparse.ArgumentParser()
ap.add_argument("--calls", nargs="+", required=True); ap.add_argument("--map", required=True)
ap.add_argument("--teams", default="Support"); ap.add_argument("--min-talk", type=int, default=45)
a = ap.parse_args()
roster = json.load(open(a.map)); teams = {t.strip() for t in a.teams.split(",")}
exts = {e for e, v in roster.items() if v.get("team") in teams}
seen, rows = set(), []
for p in a.calls:
    for r in json.load(open(p))["data"]:
        if r["callId"] in seen: continue
        seen.add(r["callId"]); rows.append(r)
def internal(r):
    f, t = r.get("from") or "", r.get("to") or ""
    return f.isdigit() and t.isdigit() and len(f) <= 5 and len(t) <= 5
sel = [r for r in rows if r.get("answeringExtension") in exts and r.get("recorded")
       and (r.get("talkTimeSeconds") or 0) >= a.min_talk and not internal(r)
       and "vendor" not in (r.get("labels") or [])]
sel.sort(key=lambda r: r["date"], reverse=True)
print(f"# {len(sel)} transcripts to read ({', '.join(sorted(teams))}, talk >= {a.min_talk}s)")
for r in sel:
    print(f"{r['callId']} {r.get('answeringExtension')} {(r.get('name') or r.get('from') or '')[:24]!r} "
          f"{(r.get('talkTimeSeconds') or 0)//60}m {r['direction'][:3]} iq={r.get('advisorIqScore')}")
