#!/usr/bin/env python3
"""Download one session's VTT.

    ./fetch_transcript.py --sessions sessions.json --uuid <uuid> --out raw/x.vtt
    ./fetch_transcript.py --url <download_url> --out raw/x.vtt
"""

import argparse
import json
import sys

import zoom_client as zc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sessions", help="sessions.json from discover_sessions.py")
    ap.add_argument("--uuid")
    ap.add_argument("--url")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    url = args.url
    if not url:
        if not (args.sessions and args.uuid):
            sys.exit("give --url, or --sessions with --uuid")
        data = json.load(open(args.sessions))
        match = next((s for s in data["sessions"] if s["uuid"] == args.uuid), None)
        if not match:
            sys.exit(f"uuid {args.uuid} not in {args.sessions}")
        url = match["transcript_url"]

    try:
        n = zc.download(url, args.out)
    except zc.ZoomError as e:
        sys.exit(str(e))
    print(f"{args.out}  {n:,} bytes")


if __name__ == "__main__":
    main()
