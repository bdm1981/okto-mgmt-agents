#!/usr/bin/env python3
"""Parse spilled list_calls output, join a roster map, rank calls for transcript review.

Usage:
  triage_calls.py --calls FILE [FILE ...] --map map.json [--tz America/Chicago]
                  [--budget 30] [--exclude-ext 8097,8098]

--calls  one or more tool-result files from list_calls (raw JSON, possibly several pages)
--map    JSON: {"8039": {"name": "Tucker Hensley", "team": "support-tech"}, ...}

Prints: coverage stats, per-extension table, at-risk contacts, and a ranked read queue.
Everything is derived from list_calls rows alone -- no per-call fetches -- so the caller
can decide what is worth spending get_call/get_transcript on.
"""
import argparse, json, sys, collections
from datetime import datetime, timezone
try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

AT_RISK_LABELS = {"lost", "cancel", "cancelled", "canceled", "escalation", "escalated",
                  "complaint", "churn", "refund", "billing_issue"}
MISS_LABELS = {"missed", "voicemail", "abandoned"}


def load_rows(paths):
    rows, seen = [], set()
    for p in paths:
        raw = open(p).read().strip()
        try:
            doc = json.loads(raw)
        except json.JSONDecodeError as e:
            sys.exit(f"{p}: not JSON ({e}). Pass the raw tool-result file.")
        page = doc.get("data", doc if isinstance(doc, list) else [])
        for r in page:
            cid = r.get("callId")
            if cid and cid in seen:
                continue          # pages can overlap on a cursor retry
            seen.add(cid)
            rows.append(r)
    return rows


def parse_dt(s):
    if not s:
        return None
    s = s.rstrip("Z")
    try:
        return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def is_internal(r):
    """Extension-to-extension calls: both legs are short numeric, no +country code."""
    f, t = (r.get("from") or ""), (r.get("to") or "")
    return f.isdigit() and t.isdigit() and len(f) <= 5 and len(t) <= 5


def secs(r, key):
    v = r.get(key)
    return v if isinstance(v, (int, float)) else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calls", nargs="+", required=True)
    ap.add_argument("--map", default=None)
    ap.add_argument("--tz", default="America/Chicago")
    ap.add_argument("--budget", type=int, default=30)
    ap.add_argument("--exclude-ext", default="")
    a = ap.parse_args()

    rows = load_rows(a.calls)
    if not rows:
        sys.exit("no call rows found")

    roster = json.load(open(a.map)) if a.map else {}
    drop = {e.strip() for e in a.exclude_ext.split(",") if e.strip()}
    tz = ZoneInfo(a.tz) if ZoneInfo else timezone.utc

    roster_names = {v.get("name", "") for v in roster.values()}

    def who(ext):
        m = roster.get(ext or "")
        if not m:
            return (f"ext {ext}" if ext else "(unattributed)"), "unknown"
        return m.get("name", f"ext {ext}"), m.get("team", "unknown")

    internal = [r for r in rows if is_internal(r)]
    vendor = [r for r in rows if r.get("vendor") and not is_internal(r)]
    excluded = [r for r in rows if (r.get("answeringExtension") in drop) and not is_internal(r)]
    ext_drop = {r["callId"] for r in excluded}
    cust = [r for r in rows
            if not is_internal(r) and not r.get("vendor") and r["callId"] not in ext_drop]

    print(f"## Coverage\n")
    print(f"- rows parsed: **{len(rows)}**")
    print(f"- customer calls analysed: **{len(cust)}**")
    print(f"- excluded: {len(internal)} internal ext-to-ext, {len(vendor)} vendor, "
          f"{len(excluded)} test/system extension")
    have_ext = sum(1 for r in cust if r.get("answeringExtension"))
    have_iq = sum(1 for r in cust if r.get("advisorIqScore") is not None)
    print(f"- attributed to an extension: {have_ext}/{len(cust)}")
    print(f"- carry an AdvisorIQ score: {have_iq}/{len(cust)}")
    ts = [parse_dt(r.get("date")) for r in cust]
    ts = [t for t in ts if t]
    if ts:
        lo, hi = min(ts).astimezone(tz), max(ts).astimezone(tz)
        print(f"- window (local {a.tz}): {lo:%Y-%m-%d %H:%M} to {hi:%H:%M}")

    # ---- per-day shape (only worth printing for a multi-day window) ----
    by_day = collections.defaultdict(list)
    for r in cust:
        t = parse_dt(r.get("date"))
        if t:
            by_day[t.astimezone(tz).date()].append(r)
    if len(by_day) > 1:
        print("\n## Per-day\n")
        print("| Day | Calls | In/Out | Missed | Neg IQ | Talk hours |")
        print("|---|---|---|---|---|---|")
        for d in sorted(by_day):
            rs = by_day[d]
            inb = sum(1 for r in rs if r.get("direction") == "inbound")
            missed = sum(1 for r in rs if MISS_LABELS & set(r.get("labels") or []))
            neg = sum(1 for r in rs if r.get("advisorIqScore") == -1)
            hrs = sum(secs(r, "talkTimeSeconds") for r in rs) / 3600.0
            print(f"| {d:%a %Y-%m-%d} | {len(rs)} | {inb}/{len(rs)-inb} | {missed} "
                  f"| {neg} | {hrs:.1f} |")

    # ---- per-extension performance, grouped by team ----
    by_ext = collections.defaultdict(list)
    for r in cust:
        by_ext[r.get("answeringExtension") or ""].append(r)

    def row(ext, rs):
        name, team = who(ext)
        inb = sum(1 for r in rs if r.get("direction") == "inbound")
        talk = [secs(r, "talkTimeSeconds") for r in rs if secs(r, "talkTimeSeconds") > 0]
        avg = f"{sum(talk)/len(talk)/60:.1f}m" if talk else "-"
        tot = f"{sum(talk)/3600:.1f}h" if talk else "-"
        missed = sum(1 for r in rs if MISS_LABELS & set(r.get("labels") or []))
        iq = collections.Counter(r.get("advisorIqScore") for r in rs)
        return (f"| {ext or '(none)'} | {name} | {len(rs)} | {inb}/{len(rs)-inb} | {avg} "
                f"| {tot} | {missed} | {iq.get(1,0)}/{iq.get(0,0)}/{iq.get(-1,0)} |")

    teams = collections.defaultdict(list)
    for ext, rs in by_ext.items():
        teams[who(ext)[1]].append((ext, rs))

    print("\n## Activity by team\n")
    order = sorted(teams, key=lambda t: -sum(len(rs) for _, rs in teams[t]))
    for team in order:
        members = sorted(teams[team], key=lambda kv: -len(kv[1]))
        total = sum(len(rs) for _, rs in members)
        print(f"\n### {team} — {total} calls\n")
        print("| Ext | Name | Calls | In/Out | Avg talk | Total talk | Missed | IQ +/0/- |")
        print("|---|---|---|---|---|---|---|---|")
        for ext, rs in members:
            print(row(ext, rs))

    # ---- at-risk contacts ----
    by_contact = collections.defaultdict(list)
    for r in cust:
        if r.get("contactId"):
            by_contact[r["contactId"]].append(r)

    at_risk = []
    for cid, rs in by_contact.items():
        rs.sort(key=lambda r: parse_dt(r.get("date")) or datetime.min.replace(tzinfo=timezone.utc))
        labels = {l for r in rs for l in (r.get("labels") or [])}
        # Strong signals stand on their own. A same-day callback is ordinary traffic --
        # it only counts as risk when something else is already wrong, otherwise every
        # shop that phones twice lands on the manager's desk.
        strong, weak = [], []
        # Frequency has to be measured per local day, not across the whole window --
        # 18 calls over a week is a busy account, 18 calls in one day is a fire.
        per_day = collections.Counter()
        for r in rs:
            t = parse_dt(r.get("date"))
            if t:
                per_day[t.astimezone(tz).date()] += 1
        peak_day, peak = (per_day.most_common(1) or [(None, 0)])[0]
        if peak >= 3:
            strong.append(f"{peak} calls on {peak_day:%a %m-%d}")
            if len(rs) > peak:
                weak.append(f"{len(rs)} across the window")
        elif len(rs) >= 6:
            strong.append(f"{len(rs)} calls across the window")
        elif peak == 2:
            weak.append("called back same day")
        if labels & AT_RISK_LABELS:
            strong.append("label: " + ", ".join(sorted(labels & AT_RISK_LABELS)))
        if any(r.get("advisorIqScore") == -1 for r in rs):
            strong.append("negative AdvisorIQ")
        last = rs[-1]
        if MISS_LABELS & set(last.get("labels") or []):
            strong.append("day ended on a missed call/voicemail")
        if peak == 2 and MISS_LABELS & set(rs[0].get("labels") or []):
            strong.append("called back after a missed call")
            weak = [w for w in weak if "called back" not in w]
        reasons = strong + weak if strong else []
        inb = sum(1 for r in rs if r.get("direction") == "inbound")
        outb = len(rs) - inb
        answered = sum(1 for r in rs if secs(r, "talkTimeSeconds") > 0)
        # Two things masquerade as a distressed customer:
        #  - a dial storm: we called them repeatedly and they never called us
        #  - internal staff whose own number is a contact record
        kind = "customer"
        if inb == 0 and outb >= 3:
            kind = "outreach"
        if (rs[0].get("name") or "") in roster_names:
            kind = "internal"
        # The `vendor` boolean is always false in practice; the signal is the `vendor`
        # LABEL, which marks inbound sales pitches. A refused cold-call gets tagged
        # `lost` and would otherwise read as a churning customer.
        if "vendor" in labels:
            kind = "vendor"
        if reasons:
            at_risk.append({
                "kind": kind, "inb": inb, "outb": outb, "answered": answered,
                "contactId": cid, "name": rs[0].get("name") or rs[0].get("from"),
                "calls": len(rs), "reasons": reasons,
                "callIds": [r["callId"] for r in rs],
                "exts": [r.get("answeringExtension") or "-" for r in rs],
                "worst": min((r.get("advisorIqScore") if r.get("advisorIqScore") is not None
                              else 9) for r in rs),
                "talk": sum(secs(r, "talkTimeSeconds") for r in rs),
            })
    at_risk.sort(key=lambda c: (c["worst"], -c["calls"], -c["talk"]))

    real = [c for c in at_risk if c["kind"] == "customer"]
    outreach = [c for c in at_risk if c["kind"] == "outreach"]
    internal = [c for c in at_risk if c["kind"] == "internal"]
    vendors = [c for c in at_risk if c["kind"] == "vendor"]

    print(f"\n## At-risk contacts ({len(real)})\n")
    if not real:
        print("_none flagged_")
    else:
        print("| Contact | Calls | In/Out | Answered | Why | Call IDs |")
        print("|---|---|---|---|---|---|")
        for c in real[:30]:
            ids = ", ".join(f"`{i}`" for i in c["callIds"][:4])
            print(f"| {c['name']} | {c['calls']} | {c['inb']}/{c['outb']} | {c['answered']} "
                  f"| {'; '.join(c['reasons'])} | {ids} |")

    if outreach:
        print(f"\n## Outbound dial storms ({len(outreach)}) — we called them, they never called us\n")
        print("| Number | Attempts | Answered | Extensions |")
        print("|---|---|---|---|")
        for c in sorted(outreach, key=lambda c: -c["calls"])[:15]:
            exts = collections.Counter(r for r in c["exts"])
            print(f"| {c['name']} | {c['outb']} | {c['answered']} "
                  f"| {', '.join(f'{e} x{n}' for e, n in exts.most_common(3))} |")

    if vendors:
        print(f"\n## Vendor cold-calls filtered out of at-risk ({len(vendors)})\n")
        print(", ".join(f"{c['name']}" for c in vendors))

    if internal:
        print(f"\n## Internal numbers filtered out of at-risk ({len(internal)})\n")
        print(", ".join(f"{c['name']} ({c['calls']})" for c in internal))

    # ---- ranked transcript read queue ----
    risk_ids = {i for c in real for i in c["callIds"]}

    def score(r):
        s = 0.0
        if r.get("advisorIqScore") == -1:
            s += 100
        if r["callId"] in risk_ids:
            s += 40
        if AT_RISK_LABELS & set(r.get("labels") or []):
            s += 35
        s += min(secs(r, "talkTimeSeconds") / 60.0, 30)      # long calls, capped
        if secs(r, "talkTimeSeconds") < 45:
            s -= 50                                          # too short to coach
        return s

    queue = sorted((r for r in cust if secs(r, "talkTimeSeconds") >= 45),
                   key=score, reverse=True)[:a.budget]
    print(f"\n## Transcript read queue (top {len(queue)})\n")
    print("| # | Call ID | Ext | Name | Contact | Talk | IQ | Why |")
    print("|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(queue, 1):
        name, _ = who(r.get("answeringExtension"))
        why = []
        if r.get("advisorIqScore") == -1:
            why.append("neg IQ")
        if r["callId"] in risk_ids:
            why.append("at-risk contact")
        if AT_RISK_LABELS & set(r.get("labels") or []):
            why.append("risk label")
        if not why:
            why.append("long call")
        print(f"| {i} | `{r['callId']}` | {r.get('answeringExtension') or '-'} | {name} "
              f"| {r.get('name') or r.get('from')} | {secs(r,'talkTimeSeconds')//60}m "
              f"| {r.get('advisorIqScore') if r.get('advisorIqScore') is not None else '-'} "
              f"| {', '.join(why)} |")

    print(f"\n_Fetch transcripts for the queue above with get_transcript; "
          f"{len(cust)-len(queue)} remaining calls stay summary-only._")


if __name__ == "__main__":
    main()
