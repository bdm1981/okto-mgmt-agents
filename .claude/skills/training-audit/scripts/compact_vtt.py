#!/usr/bin/env python3
"""VTT -> one '[mm:ss] Speaker: text' line per cue, plus a speaker tally.

A 70-minute session is ~2,000 VTT cues across ~2,200 lines of timing scaffolding.
Compacted it is ~500 readable lines, which is what you actually want in context.

Consecutive cues from the same speaker are NOT merged: in a single-speaker
webinar that collapses the whole session into one unreadable blob.

    ./compact_vtt.py raw/x.vtt > compact/x.txt
"""

import re
import sys
from pathlib import Path


def compact(text: str):
    lines = text.splitlines()
    out, speakers, i = [], {}, 0
    while i < len(lines):
        if "-->" in lines[i]:
            start = lines[i].split("-->")[0].strip()
            try:
                hh, mm, rest = start.split(":")
                ss = rest.split(".")[0]
                stamp = f"{int(hh) * 60 + int(mm):02d}:{ss}"
            except ValueError:
                stamp = "??:??"
            i += 1
            buf = []
            while i < len(lines) and lines[i].strip():
                buf.append(lines[i].strip())
                i += 1
            if buf:
                txt = " ".join(buf)
                m = re.match(r"^([^:]{1,60}?):\s(.*)$", txt)
                if m:
                    speakers[m.group(1)] = speakers.get(m.group(1), 0) + 1
                out.append(f"[{stamp}] {txt}")
        i += 1
    return out, speakers


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: compact_vtt.py <file.vtt>")
    raw = Path(sys.argv[1]).read_text(encoding="utf-8-sig", errors="replace")
    rows, speakers = compact(raw)
    print("\n".join(rows))
    print(f"\n# {len(rows)} cues", file=sys.stderr)
    for s, c in sorted(speakers.items(), key=lambda x: -x[1]):
        print(f"#   {c:5d}  {s}", file=sys.stderr)
    if len(speakers) <= 1:
        print(
            "# WARNING: one speaker only — the attendee was not transcribed.\n"
            "#          Do not infer customer questions; note it in the caveats.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
