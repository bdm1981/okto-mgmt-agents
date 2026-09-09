#!/usr/bin/env python3
"""Which recordings in a window are training sessions we have not audited yet.

Selection is deliberately conservative: a recording must come from an allowlisted
host AND match a topic pattern AND be long enough to be a real session. Guessing
wider means auditing standups and 1:1s, which is both wasteful and a privacy
problem.

    ./discover_sessions.py --from 2026-09-01 --to 2026-09-08 > sessions.json
"""

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

import zoom_client as zc

REF = Path(__file__).resolve().parent.parent / "references"


def _table_rows(md: str, heading: str) -> list[list[str]]:
    """Pull the first markdown table under a heading. Keeps config human-editable."""
    lines = md.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip().lower().startswith(heading.lower()))
    except StopIteration:
        return []
    rows = []
    for l in lines[start + 1 :]:
        s = l.strip()
        if s.startswith("#") and rows:
            break
        if not s.startswith("|"):
            if rows:
                break
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells or set("".join(cells)) <= set("-: "):
            continue
        if cells[0].lower() in ("host", "pattern", "email"):
            continue
        rows.append(cells)
    return rows


def load_sources() -> dict:
    md = (REF / "sources.md").read_text(encoding="utf-8")
    hosts = [r[0] for r in _table_rows(md, "## Hosts") if r and r[0]]
    patterns = [r[0] for r in _table_rows(md, "## Topic patterns") if r and r[0]]
    m = re.search(r"min_duration_minutes:\s*(\d+)", md)
    min_dur = int(m.group(1)) if m else 20
    m = re.search(r"slack_channel:\s*(\S+)", md)
    channel = m.group(1) if m else None
    if not hosts:
        sys.exit("sources.md lists no hosts under '## Hosts' — nothing can be discovered.")
    return {
        "hosts": hosts,
        "patterns": [re.compile(p, re.I) for p in patterns] or [re.compile(r".")],
        "min_duration": min_dur,
        "slack_channel": channel,
    }


def audited_uuids() -> set[str]:
    """UUIDs already in the ledger. Re-auditing corrupts repeat detection."""
    p = REF / "findings-ledger.md"
    if not p.exists():
        return set()
    return set(re.findall(r"`uuid:([^`]+)`", p.read_text(encoding="utf-8")))


def month_chunks(frm: str, to: str):
    """Zoom caps one recordings query at a month."""
    a = dt.date.fromisoformat(frm)
    b = dt.date.fromisoformat(to)
    while a <= b:
        end = min(a + dt.timedelta(days=29), b)
        yield a.isoformat(), end.isoformat()
        a = end + dt.timedelta(days=1)


def main():
    ap = argparse.ArgumentParser()
    default_to = dt.date.today()
    ap.add_argument("--from", dest="frm", default=(default_to - dt.timedelta(days=7)).isoformat())
    ap.add_argument("--to", dest="to", default=default_to.isoformat())
    ap.add_argument("--all", action="store_true", help="include already-audited sessions")
    args = ap.parse_args()

    src = load_sources()
    seen = set() if args.all else audited_uuids()

    # host_id -> name, so reports say "Aaron" not "-CuLbEopTeOm5ntQ0uX_YA"
    try:
        names = {
            u["id"]: (f"{u.get('first_name','')} {u.get('last_name','')}".strip() or u.get("email", ""))
            for u in zc.list_users()
        }
        emails = {u["id"]: u.get("email", "") for u in zc.list_users()}
    except zc.ZoomError as e:
        sys.exit(f"Zoom auth/scope problem: {e}")

    out, skipped = [], {"already_audited": 0, "no_transcript": 0, "too_short": 0, "topic": 0}
    for host in src["hosts"]:
        for a, b in month_chunks(args.frm, args.to):
            try:
                meetings = zc.list_recordings(host, a, b)
            except zc.ZoomError as e:
                print(f"warn: host {host} {a}..{b}: {e}", file=sys.stderr)
                continue

            for m in meetings:
                uuid = m.get("uuid", "")
                topic = m.get("topic", "") or ""
                if uuid in seen:
                    skipped["already_audited"] += 1
                    continue
                if not any(p.search(topic) for p in src["patterns"]):
                    skipped["topic"] += 1
                    continue
                if int(m.get("duration") or 0) < src["min_duration"]:
                    skipped["too_short"] += 1
                    continue
                vtt = zc.transcript_url(m)
                if not vtt:
                    skipped["no_transcript"] += 1
                    print(f"warn: no transcript for {topic!r} {m.get('start_time')}", file=sys.stderr)
                    continue
                hid = m.get("host_id", "")
                out.append(
                    {
                        "uuid": uuid,
                        "meeting_id": m.get("id"),
                        "topic": topic,
                        "start_time": m.get("start_time"),
                        "duration_minutes": m.get("duration"),
                        "timezone": m.get("timezone"),
                        "host_id": hid,
                        "trainer": names.get(hid) or emails.get(hid) or host,
                        "transcript_url": vtt,
                        "share_url": m.get("share_url"),
                    }
                )

    out.sort(key=lambda s: s.get("start_time") or "")
    json.dump({"sessions": out, "skipped": skipped, "window": [args.frm, args.to]}, sys.stdout, indent=2)
    print("", file=sys.stdout)
    print(
        f"discovered {len(out)} session(s); skipped {skipped}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
