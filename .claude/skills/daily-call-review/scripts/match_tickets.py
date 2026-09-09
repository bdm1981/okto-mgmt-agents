#!/usr/bin/env python3
"""Join Zoho Desk tickets to support calls: per-rep ticketing discipline + unticketed calls.

Usage:
  match_tickets.py --tickets FILE [FILE ...] --calls FILE [FILE ...] --map map.json
                   [--teams Support] [--min-talk 180] [--window-min 120]

--tickets  one or more spilled searchTickets tool-result files (pages of the same query are fine;
           tickets are de-duplicated by id)
--calls    spilled list_calls tool-result files
--map      the extension -> {name, team} JSON used by triage_calls.py
--teams    comma-separated team names to report on (default: Support)

For each rep: substantive calls, phone-channel tickets they created, and how many inbound calls
have ANY phone ticket by that rep created within --window-min after the call started. Then lists
the inbound calls with no ticket by anyone within the window -- the "did this get written down"
list a manager actually wants.
"""
import argparse, json, collections
from datetime import datetime, timedelta


def load_json_pages(paths, key):
    out = {}
    for p in paths:
        doc = json.load(open(p))
        rows = doc["data"]["data"] if key == "tickets" else doc["data"]
        for r in rows:
            out[r["id"] if key == "tickets" else r["callId"]] = r
    return list(out.values())


def dt(s):
    return datetime.fromisoformat(s.replace("Z", "").split(".")[0])


def agent(t):
    a = t.get("assignee") or {}
    return f"{a.get('firstName', '')} {a.get('lastName', '')}".strip() or "Unassigned"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickets", nargs="+", required=True)
    ap.add_argument("--calls", nargs="+", required=True)
    ap.add_argument("--map", required=True)
    ap.add_argument("--teams", default="Support")
    ap.add_argument("--min-talk", type=int, default=180)
    ap.add_argument("--window-min", type=int, default=120)
    a = ap.parse_args()

    tickets = load_json_pages(a.tickets, "tickets")
    calls = load_json_pages(a.calls, "calls")
    roster = json.load(open(a.map))
    teams = {t.strip() for t in a.teams.split(",")}
    reps = {ext: v["name"] for ext, v in roster.items() if v.get("team") in teams}
    win = timedelta(minutes=a.window_min)

    phone_t = [t for t in tickets if t.get("channel") == "Phone"]
    by_agent = collections.defaultdict(list)
    for t in phone_t:
        by_agent[agent(t)].append(dt(t["createdTime"]))
    all_times = sorted(dt(t["createdTime"]) for t in phone_t)

    print(f"## Ticketing discipline ({', '.join(sorted(teams))})\n")
    print(f"_{len(tickets)} tickets in window, {len(phone_t)} phone-channel. "
          f"Substantive = talk >= {a.min_talk}s. Match = a phone ticket by the same rep "
          f"created within {a.window_min} min of call start._\n")
    print("| Rep | Calls >=3m | Inbound | Phone tickets | Tickets/call | Inbound w/ own ticket |")
    print("|---|---|---|---|---|---|")
    unticketed = []
    for ext, name in sorted(reps.items(), key=lambda kv: kv[1]):
        cs = [c for c in calls if c.get("answeringExtension") == ext
              and (c.get("talkTimeSeconds") or 0) >= a.min_talk]
        inb = [c for c in cs if c.get("direction") == "inbound"]
        n_t = len(by_agent.get(name, []))
        own = 0
        for c in inb:
            t0 = dt(c["date"])
            if any(timedelta(0) <= tt - t0 <= win for tt in by_agent.get(name, [])):
                own += 1
            elif not any(timedelta(0) <= tt - t0 <= win for tt in all_times):
                unticketed.append((name, c))
        ratio = f"{n_t / len(cs):.2f}" if cs else "-"
        pct = f"{100 * own / len(inb):.0f}%" if inb else "-"
        print(f"| {name} | {len(cs)} | {len(inb)} | {n_t} | {ratio} | {own}/{len(inb)} ({pct}) |")

    print(f"\n## Inbound calls >=3m with NO phone ticket by anyone within {a.window_min} min "
          f"({len(unticketed)})\n")
    print("| Rep | When (UTC) | Caller | Talk | IQ | Call ID |")
    print("|---|---|---|---|---|---|")
    for name, c in sorted(unticketed, key=lambda x: -(x[1].get("talkTimeSeconds") or 0))[:40]:
        print(f"| {name} | {c['date'][:16]} | {(c.get('name') or c.get('from') or '')[:26]} "
              f"| {(c.get('talkTimeSeconds') or 0) // 60}m | "
              f"{c.get('advisorIqScore') if c.get('advisorIqScore') is not None else '-'} "
              f"| `{c['callId']}` |")
    print("\n_A same-window ticket by anyone is treated as captured; time-matching is approximate "
          "-- confirm against the account before naming it in a review._")


if __name__ == "__main__":
    main()
