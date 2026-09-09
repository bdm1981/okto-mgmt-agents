#!/usr/bin/env python3
"""Render the support-manager daily dashboard from computed stats + authored narrative.

Usage:
  build_dashboard.py --date 2026-09-04 --calls FILES --tickets FILES --map map.json
                     --notes notes.jsonl --narrative narrative.json --out daily.html
                     [--tz America/Chicago] [--teams Support]

notes.jsonl  -- one JSON object per transcript READ, written by the reviewer as they go:
  {"callId":..,"ext":"8039","customer":"..","issue":"..","outcome":"..",
   "remote":"none|needed|partial|not_needed","ticket":"#21882|none|unknown",
   "flags":["dial-loop","no-history","dropped-request","rushing","dominating","misidentified"],
   "quote":".."}
narrative.json -- authored by the reviewer after reading everything:
  {"headline": "one sentence", "owners":[{"name","severity":"crit|warn|good","text","tag"}],
   "techs":{"8039":{"well":{"text","quote","ref"},"fix":{"text","quote","ref"}}, ...},
   "patterns":[{"title","text"}], "caveats":["..."]}
Numbers are computed here so the reviewer only writes words.
"""
import argparse, json, collections, html, os, re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ap = argparse.ArgumentParser()
for k in ("--date", "--map", "--notes", "--narrative", "--out"): ap.add_argument(k, required=True)
ap.add_argument("--calls", nargs="+", required=True); ap.add_argument("--tickets", nargs="+", required=True)
ap.add_argument("--tz", default="America/Chicago"); ap.add_argument("--teams", default="Support")
a = ap.parse_args()
tz = ZoneInfo(a.tz); teams = {t.strip() for t in a.teams.split(",")}
roster = json.load(open(a.map)); reps = {e: v["name"] for e, v in roster.items() if v.get("team") in teams}
nar = json.load(open(a.narrative))
notes = [json.loads(l) for l in open(a.notes) if l.strip()]
E = html.escape
CALL_URL = "https://app.digitalconcierge.io/userPortal/admin/calls?callId="
TICKET_URL = {}   # ticketNumber -> agent web URL, filled once tickets are loaded

def L(text):
    """Escape, then turn 24-hex call ids and #NNNNN ticket numbers into links."""
    t = E(text or "")
    t = re.sub(r"\b([0-9a-f]{24})\b", lambda m: f'<a class="id" href="{CALL_URL}{m.group(1)}" target="_blank" rel="noopener">{m.group(1)}</a>', t)
    t = re.sub(r"\b([0-9a-f]{8})…", lambda m: m.group(0), t)
    def tk(m):
        n = m.group(1); u = TICKET_URL.get(n)
        return f'<a class="id" href="{u}" target="_blank" rel="noopener">#{n}</a>' if u else f"#{n}"
    t = re.sub(r"#(\d{5})\b", tk, t)
    t = re.sub(r"#(\d{5})-(\d{2})\b", lambda m: tk(m) if False else m.group(0), t)
    return t

def load(paths, key):
    out = {}
    for p in paths:
        d = json.load(open(p)); rows = d["data"]["data"] if key == "t" else d["data"]
        for r in rows: out[r["id"] if key == "t" else r["callId"]] = r
    return list(out.values())
calls, tickets = load(a.calls, "c"), load(a.tickets, "t")
for _t in tickets:
    if _t.get("ticketNumber") and _t.get("webUrl"): TICKET_URL[str(_t["ticketNumber"])] = _t["webUrl"]
D = lambda s: datetime.fromisoformat(s.replace("Z", "").split(".")[0]).replace(tzinfo=timezone.utc)
day = datetime.strptime(a.date, "%Y-%m-%d").date()
def local(r): return D(r["date"]).astimezone(tz)
def internal(r):
    f, t = r.get("from") or "", r.get("to") or ""
    return f.isdigit() and t.isdigit() and len(f) <= 5 and len(t) <= 5
excl = {e for e, v in roster.items() if v.get("team") == "exclude"}
cust = [r for r in calls if local(r).date() == day and not internal(r) and r.get("answeringExtension") not in excl]
T = lambda r: r.get("talkTimeSeconds") or 0
# ---- department numbers
inb = [r for r in cust if r["direction"] == "inbound"]
talk_h = sum(T(r) for r in cust) / 3600
# Missed = rows carrying the `missed` label, counted BEFORE the extension exclusion:
# most missed legs land on routing-target extensions (8765/8000) that `excl` removes.
dayrows = [r for r in calls if local(r).date() == day and not internal(r) and r["direction"] == "inbound"]
missed = [r for r in dayrows if "missed" in (r.get("labels") or [])]
voicemail = [r for r in dayrows if "voicemail" in (r.get("labels") or [])]
missed_callers = len({r.get("from") for r in missed})
tday = [t for t in tickets if D(t["createdTime"]).astimezone(tz).date() == day]
tclosed = [t for t in tickets if t.get("closedTime") and D(t["closedTime"]).astimezone(tz).date() == day]
topen = [t for t in tickets if t["statusType"] == "Open"]
overdue = [t for t in topen if t.get("isOverDue")]
call_issue = [t for t in tday if t.get("category") == "Call Issues"]
cats = collections.Counter(t.get("category") or "uncategorised" for t in tday).most_common(3)
sup = [r for r in cust if r.get("answeringExtension") in reps]

# ---- hourly chart (local hours 7..19)
hours = list(range(7, 20)); hc = collections.Counter(local(r).hour for r in cust); hn = collections.Counter(local(r).hour for r in cust if r.get("advisorIqScore") == -1)
peak = max([hc[h] for h in hours] + [1]); W, H0, BW = 560, 150, 30
bars = []
for i, h in enumerate(hours):
    x = 40 + i * 40; v = hc[h]; hh = v / peak * 110
    bars.append(f'<rect class="bar" x="{x}" y="{H0-hh:.1f}" width="{BW}" height="{hh:.1f}"/><text class="lbl" x="{x+BW/2}" y="{H0-hh-4:.1f}" text-anchor="middle">{v}</text>')
    if hn[h]:
        nh = hn[h] / peak * 110
        bars.append(f'<rect class="bar2" x="{x+BW-8}" y="{H0-nh:.1f}" width="8" height="{nh:.1f}"/>')
    bars.append(f'<text x="{x+BW/2}" y="{H0+18}" text-anchor="middle">{h%12 or 12}{"a" if h<12 else "p"}</text>')
chart = f'<svg viewBox="0 0 {W} 180" width="100%" role="img" aria-label="Calls by local hour"><line class="axis" x1="36" x2="{W-10}" y1="{H0}.5" y2="{H0}.5"/>{"".join(bars)}</svg>'

# ---- per-tech
by_agent = collections.defaultdict(list)
def agent(t): x = t.get("assignee") or {}; return f"{x.get('firstName','')} {x.get('lastName','')}".strip()
for t in tickets:
    if t.get("channel") == "Phone": by_agent[agent(t)].append(D(t["createdTime"]))
all_pt = sorted(tt for v in by_agent.values() for tt in v)
notes_by_ext = collections.defaultdict(list)
for n in notes: notes_by_ext[str(n.get("ext"))].append(n)
tech_html, unticketed, remote_rows = [], [], []
for ext, name in sorted(reps.items(), key=lambda kv: -len([r for r in sup if r.get("answeringExtension") == kv[0]])):
    rs = [r for r in sup if r.get("answeringExtension") == ext]
    if not rs: continue
    subs = [r for r in rs if T(r) >= 180]; sin = [r for r in subs if r["direction"] == "inbound"]
    own = sum(1 for r in sin if any(timedelta(0) <= tt - D(r["date"]) <= timedelta(hours=2) for tt in by_agent.get(name, [])))
    for r in sin:
        # 'anyone within 2h' is meaningless on a busy day (~37 phone tickets/day); require the same rep
        if not any(timedelta(0) <= tt - D(r["date"]) <= timedelta(hours=2) for tt in by_agent.get(name, [])): unticketed.append((name, r))
    mine_t = [t for t in tday if agent(t) == name and t.get("channel") == "Phone"]
    allmine = [t for t in tickets if agent(t) == name]; myopen = [t for t in allmine if t["statusType"] == "Open"]
    talk = [T(r) for r in rs if T(r) > 0]; avg = f"{sum(talk)/len(talk)/60:.1f}m" if talk else "-"
    iq = collections.Counter(r.get("advisorIqScore") for r in rs)
    ns = notes_by_ext[ext]; used = [n for n in ns if n.get("remote") in ("needed", "partial", "not_needed")]
    bad = [n for n in used if n["remote"] == "not_needed"]; part = [n for n in used if n["remote"] == "partial"]
    cls = "no" if bad else ("mid" if part else "ok")
    rtxt = f"{len(used)} of {len(ns)} read" + (f" · {len(bad)} not needed" if bad else "") + (f" · {len(part)} partial" if part else "")
    for n in used: remote_rows.append((name, n))
    pct = f"{100*own/len(sin):.0f}%" if sin else "-"; ratio = f"{len(mine_t)/len(subs):.2f}" if subs else "-"
    trk = "" if not sin or own/len(sin) >= .6 else ("lo" if own/len(sin) >= .4 else "vlo")
    nn = nar.get("techs", {}).get(ext, {}); well, fix = nn.get("well", {}), nn.get("fix", {})
    def note(kind, d):
        if not d: return ""
        q = f'<blockquote>{E(d.get("quote",""))}</blockquote>' if d.get("quote") else ""
        return f'<div class="note {kind}"><div class="h">{"Doing great" if kind=="well" else "Address"}</div><p>{L(d.get("text",""))}</p>{q}<div class="ref">{L(d.get("ref",""))}</div></div>'
    tech_html.append(f'''<article class="tech"><header><h3>{E(name)}</h3><span class="ext">ext {ext} · {E(roster[ext]["team"])}</span></header>
<div class="stats num"><div>Calls<b>{len(rs)}</b></div><div>Avg talk<b>{avg}</b></div><div>Talk hours<b>{sum(talk)/3600:.1f}</b></div><div>IQ +/0/−<b>{iq.get(1,0)}/{iq.get(0,0)}/{iq.get(-1,0)}</b></div></div>
<div class="bars"><div class="bar-l"><span>Own ticket on inbound calls ≥3m</span><span class="num">{own} / {len(sin)} · {pct}</span></div><div class="track {trk}"><span style="width:{(100*own/len(sin)) if sin else 0:.0f}%"></span></div>
<div class="bar-l" style="margin-top:8px"><span>Phone tickets today / substantive call</span><span class="num">{len(mine_t)} / {len(subs)} · {ratio}</span></div><div class="track"><span style="width:{min(100,(100*len(mine_t)/len(subs)) if subs else 0):.0f}%"></span></div>
<div style="margin-top:8px;font-size:12.5px;color:var(--muted)">Desk: {len(allmine)} tickets in window · {len(myopen)} open · <span style="color:var(--crit)">{sum(1 for t in myopen if t.get("isOverDue"))} overdue</span> · transcripts read today: {len(ns)}</div></div>
<div class="remote"><b>Remote sessions</b> {E(rtxt)} <span class="pill {cls}">{ {"no":"check our side first","mid":"partly justified","ok":"fine"}[cls] }</span></div>
<div class="notes">{note("well", well)}{note("fix", fix)}</div></article>''')

# ---- owners, remote table, patterns, caveats
own_html = "".join(f'<div class="owner {E(o.get("severity","warn"))}"><div class="stripe"></div><div class="body"><b>{E(o["name"])}</b><p>{L(o["text"])}</p></div><div class="tag">{L(o.get("tag",""))}</div></div>' for o in nar.get("owners", []))
V = {"needed": ("ok", "needed"), "partial": ("mid", "partly"), "not_needed": ("no", "not needed")}
rem_html = "".join(f'<tr><td class="mono">{L(n["callId"])}</td><td>{E(name)}</td><td>{E(n.get("issue",""))}</td><td><span class="verdict {V[n["remote"]][0]}">{V[n["remote"]][1]}</span></td><td>{L(n.get("outcome",""))}</td></tr>' for name, n in remote_rows) or '<tr><td colspan="5" style="color:var(--muted)">No remote sessions in any transcript read today.</td></tr>'
unt_html = "".join(f'<tr><td>{E(name)}</td><td class="mono">{local(r):%H:%M}</td><td>{E((r.get("name") or r.get("from") or "")[:28])}</td><td class="num">{T(r)//60}m</td><td class="mono">{L(r["callId"])}</td></tr>' for name, r in sorted(unticketed, key=lambda x: -T(x[1]))) or '<tr><td colspan="5" style="color:var(--muted)">Every inbound call ≥3 min has a ticket by its rep within 2 h.</td></tr>'
pat_html = "".join(f'<div class="pattern"><div class="n">{"①②③④⑤⑥⑦"[i]}</div><div><h3>{E(p["title"])}</h3><p>{L(p["text"])}</p></div></div>' for i, p in enumerate(nar.get("patterns", [])[:7]))
cav_html = "".join(f"<li>{L(c)}</li>" for c in nar.get("caveats", []))
css = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "dashboard.css")).read()
nice = day.strftime("%a %b %-d, %Y")

page = f'''<title>Support Desk Daily</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600;700&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{css}
a.id{{color:inherit;text-decoration:underline dotted;text-decoration-color:var(--accent);text-underline-offset:2px}}
a.id:hover{{color:var(--accent-ink);text-decoration-style:solid}}</style>
<div class="wrap">
<header class="masthead"><div><div class="eyebrow">OktoRocket · Support · site 634c8538</div><h1>Support Desk Daily</h1>
<p style="margin:8px 0 0;color:var(--ink-2)">{nice} · {E(a.tz)} · {len(reps)} technicians · every Support transcript read ({len(notes)})</p></div>
<div class="meta"><b>For the support manager</b>{E(nar.get("headline",""))}</div></header>
<section class="board">
<div class="tile"><div class="k">Customer calls</div><div class="v num">{len(cust)}</div><div class="s">{len(inb)} in · {len(cust)-len(inb)} out · {talk_h:.1f} talk-hours</div></div>
<div class="tile"><div class="k">Support team</div><div class="v num">{len(sup)}</div><div class="s">{100*len(sup)//max(1,len(cust))}% of calls · {sum(T(r) for r in sup)/3600:.1f} h talk</div></div>
<div class="tile {"crit" if missed else ""}"><div class="k">Missed calls</div><div class="v num">{len(missed)}</div><div class="s">`missed` label · {missed_callers} callers · {len(voicemail)} voicemails</div></div>
<div class="tile"><div class="k">Tickets opened</div><div class="v num">{len(tday)}</div><div class="s">{sum(1 for t in tday if t.get("channel")=="Phone")} by phone · {len(tclosed)} closed today</div></div>
<div class="tile warn"><div class="k">Open &amp; overdue</div><div class="v num">{len(overdue)}</div><div class="s">of {len(topen)} open in window</div></div>
<div class="tile"><div class="k">Call-issue tickets</div><div class="v num">{len(call_issue)}</div><div class="s">{" · ".join(f"{E(c)} {n}" for c,n in cats)}</div></div>
</section>
<div class="chartrow"><div class="panel"><h3>Calls by hour, with negative-AdvisorIQ calls</h3><div class="sub">Local time · thin red bars are calls scored −1</div>{chart}
<div class="legend"><span><i style="background:var(--accent)"></i>customer calls</span><span><i style="background:var(--crit)"></i>scored −1</span></div></div>
<div class="panel"><h3>Inbound calls ≥3 min without the rep’s own ticket</h3><div class="sub">No phone-channel ticket by the answering rep within 2 h · check the account before raising it</div><div class="scroll"><table><tr><th>Rep</th><th>Time</th><th>Caller</th><th>Talk</th><th>Call ID</th></tr>{unt_html}</table></div></div></div>
<h2>Needs an owner tomorrow</h2><div class="owners">{own_html}</div>
<h2>The technicians</h2><p style="color:var(--ink-2)">Calls ≥3 min count as substantive. “Own ticket” = a phone ticket this rep created within 2 h of an inbound call. Quotes are verbatim from transcripts; every claim carries a call ID or ticket number.</p>
<div class="techs">{"".join(tech_html)}</div>
<h2>Remote sessions today</h2><div class="scroll"><table><tr><th>Call</th><th>Rep</th><th>Issue</th><th>Verdict</th><th>Outcome</th></tr>{rem_html}</table></div>
<p style="margin-top:12px"><b>Norm:</b> check our side first — call logs, registration state, routing/porting config, sister-site status — and open a remote session only after those come back clean or for a guided install.</p>
<h2>Patterns for the department</h2>{pat_html}
<h2>Method &amp; caveats</h2><ul class="caveats">{cav_html}</ul>
<footer>Call ids open the call in the admin portal · ticket numbers open Zoho Desk · Generated by /daily-call-review · read-only</footer></div>'''
open(a.out, "w").write(page)
print(f"wrote {a.out} ({len(page)} bytes): {len(cust)} calls, {len(sup)} support, {len(notes)} transcripts noted, {len(unticketed)} unticketed")
