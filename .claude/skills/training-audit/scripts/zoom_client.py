#!/usr/bin/env python3
"""Zoom Server-to-Server OAuth client — cloud recordings + transcripts.

Why this exists rather than the Zoom MCP connector: the connector is per-user
OAuth and only ever returns the *authenticated user's* own recordings. Training
sessions are hosted by the training account, so an audit run driven by anyone
else's identity sees nothing. An account-level admin recording scope is the only
path that can enumerate another host's recordings unattended.

Credentials — from the process environment, or from a credentials file
(`$OKTO_ZOOM_ENV`, default `~/.config/okto/zoom.env`, mode 600):
    ZOOM_ACCOUNT_ID
    ZOOM_CLIENT_ID
    ZOOM_CLIENT_SECRET

Do NOT put these in `~/.zshrc`: that file is sourced only by interactive zsh, so
a scheduled (non-interactive) run would not see them and would fail silently
every week.

Required app scopes (granular — Zoom retired the coarse `recording:read:admin`):
    cloud_recording:read:list_user_recordings:admin   list a host's recordings + download the VTT
    user:read:list_users:admin                        resolve host_id -> name/email

Standard library only.
"""

import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.zoom.us/v2"
OAUTH = "https://zoom.us/oauth/token"

_token_cache = {"token": None, "expires_at": 0.0}


class ZoomError(RuntimeError):
    pass


KEYS = ("ZOOM_ACCOUNT_ID", "ZOOM_CLIENT_ID", "ZOOM_CLIENT_SECRET")

# Default location for the credentials file. Deliberately NOT the shell profile:
# `~/.zshrc` is sourced only by INTERACTIVE zsh, so credentials exported there are
# invisible to every non-interactive shell — which is what a scheduled run uses.
# That failure mode is silent and weekly, so the job loads its own file instead.
CRED_FILE = os.environ.get("OKTO_ZOOM_ENV") or os.path.expanduser(
    "~/.config/okto/zoom.env"
)


def _load_cred_file(path: str = "") -> int:
    """Read KEY=value lines from the credentials file into os.environ.

    Process env always wins, so an explicit export still overrides the file.
    Missing file is not an error — env alone is a valid setup.
    """
    path = path or CRED_FILE
    if not os.path.isfile(path):
        return 0
    loaded = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export ") :]
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k in KEYS and not os.environ.get(k):
                os.environ[k] = v
                loaded += 1
    return loaded


def _require_env():
    _load_cred_file()
    missing = [k for k in KEYS if not os.environ.get(k)]
    if missing:
        raise ZoomError(
            "missing credentials: "
            + ", ".join(missing)
            + f"\nLooked in the process environment and {CRED_FILE}."
            + "\nNote: exports in ~/.zshrc are invisible to non-interactive shells"
            + " (scheduled runs included) — use the credentials file."
            + "\nSee references/sources.md."
        )


def token() -> str:
    """Account-credentials grant. Cached until 60s before expiry."""
    if _token_cache["token"] and time.time() < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    _require_env()
    basic = base64.b64encode(
        f"{os.environ['ZOOM_CLIENT_ID']}:{os.environ['ZOOM_CLIENT_SECRET']}".encode()
    ).decode()
    body = urllib.parse.urlencode(
        {"grant_type": "account_credentials", "account_id": os.environ["ZOOM_ACCOUNT_ID"]}
    ).encode()
    req = urllib.request.Request(
        OAUTH,
        data=body,
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            payload = json.load(r)
    except urllib.error.HTTPError as e:
        raise ZoomError(
            f"OAuth failed ({e.code}). Check the three ZOOM_* vars and that the "
            f"app is activated: {e.read().decode('utf-8', 'replace')[:300]}"
        ) from e

    _token_cache["token"] = payload["access_token"]
    _token_cache["expires_at"] = time.time() + float(payload.get("expires_in", 3600))
    return _token_cache["token"]


def _get(path: str, params: dict | None = None, retries: int = 4):
    url = f"{API}{path}"
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})

    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token()}"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            # 429 carries Retry-After; Zoom's per-second limits are easy to trip
            # when a week has many sessions.
            if e.code == 429 and attempt < retries - 1:
                time.sleep(float(e.headers.get("Retry-After", 2 ** attempt)))
                continue
            if e.code in (502, 503, 504) and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            detail = e.read().decode("utf-8", "replace")[:300]
            raise ZoomError(f"GET {path} -> {e.code}: {detail}") from e
    raise ZoomError(f"GET {path} exhausted retries")


def list_users() -> list[dict]:
    """Every user in the account, so a host_id can be named."""
    out, token_pg = [], None
    while True:
        page = _get("/users", {"page_size": 300, "next_page_token": token_pg, "status": "active"})
        out.extend(page.get("users", []))
        token_pg = page.get("next_page_token") or None
        if not token_pg:
            return out


def list_recordings(user_id: str, frm: str, to: str) -> list[dict]:
    """Cloud recordings for one host.

    Zoom caps a single query at one month, so callers passing a wider window
    must chunk it. `user_id` may be a Zoom user id or an email address; "me"
    resolves to the app's own user and is almost never what you want here.
    """
    out, token_pg = [], None
    while True:
        page = _get(
            f"/users/{urllib.parse.quote(user_id)}/recordings",
            {"from": frm, "to": to, "page_size": 300, "next_page_token": token_pg},
        )
        out.extend(page.get("meetings", []))
        token_pg = page.get("next_page_token") or None
        if not token_pg:
            return out


def transcript_url(meeting: dict) -> str | None:
    """The VTT download URL from a recordings-list meeting object.

    Zoom labels it file_type TRANSCRIPT / recording_type audio_transcript. A
    meeting recorded before the account enabled audio transcription simply has
    no such file — that is a skip, not an error.
    """
    for f in meeting.get("recording_files", []):
        if f.get("file_type") == "TRANSCRIPT" and f.get("status") == "completed":
            return f.get("download_url")
    return None


def download(url: str, dest: str) -> int:
    """Download a recording file. S2S download URLs need the bearer token."""
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token()}"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        raise ZoomError(f"download failed ({e.code}) for {url[:80]}…") from e
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    with open(dest, "wb") as fh:
        fh.write(data)
    return len(data)


def past_participants(meeting_uuid: str) -> list[dict]:
    """Raw participant records for one past meeting.

    NOTE the double URL-encoding. A meeting UUID containing "/" or "==" must be
    encoded TWICE or Zoom rejects the path — this is the single most common way
    this endpoint appears broken.

    Needs `meeting:read:list_past_participants:admin`. Without it Zoom answers
    400 code 4711 ("does not contain scopes"), which reads like a bad request.
    """
    enc = urllib.parse.quote(urllib.parse.quote(meeting_uuid, safe=""), safe="")
    out, tok = [], None
    while True:
        page = _get(
            f"/past_meetings/{enc}/participants",
            {"page_size": 300, "next_page_token": tok},
        )
        out.extend(page.get("participants", []))
        tok = page.get("next_page_token") or None
        if not tok:
            return out


def attendees(meeting_uuid: str, host_name: str = "OktoRocket Training") -> dict:
    """Distinct real attendees, excluding the host and waiting-room-only joins.

    Three traps, all found in live data rather than reasoned about:

    1. **One record per JOIN, not per person.** A participant who drops and
       rejoins appears twice. `total_records` is therefore an overcount — 5
       records for 3 people in the session this was built against.
    2. **`user_id` is per-join, not per-person.** The same "seades" came back
       as 16793600 and 16794624, so it cannot dedupe. `id` and `user_email` are
       both empty for external guests. The only stable key is the display
       name, lowercased and trimmed — which also collapses "Scott"/"scott".
    3. **Waiting-room entries look like attendance.** `status ==
       "in_waiting_room"` records carry a duration (24s in one case) but the
       person never got in.

    Returns counts plus per-attendee seconds, so a drive-by join (8 minutes of
    a 70-minute session) is distinguishable from someone who sat the whole thing.
    """
    recs = past_participants(meeting_uuid)
    guests = [
        p for p in recs
        if (p.get("name") or "").strip().lower() != host_name.strip().lower()
        and p.get("status") != "in_waiting_room"
    ]
    seconds: dict[str, int] = {}
    display: dict[str, str] = {}
    for p in guests:
        key = (p.get("name") or "?").strip().lower()
        seconds[key] = seconds.get(key, 0) + int(p.get("duration") or 0)
        display.setdefault(key, (p.get("name") or "?").strip())
    return {
        "count": len(seconds),
        "raw_records": len(recs),
        "waiting_room_only": sum(1 for p in recs if p.get("status") == "in_waiting_room"),
        "attendees": [
            {"name": display[k], "seconds": v}
            for k, v in sorted(seconds.items(), key=lambda kv: -kv[1])
        ],
    }


if __name__ == "__main__":
    # Smoke test: prove the credentials work and the scopes are right.
    try:
        token()
        users = list_users()
    except ZoomError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"OK — authenticated, {len(users)} active users visible")
    for u in users[:20]:
        print(f"  {u.get('id','?'):24s} {u.get('email','?'):34s} {u.get('first_name','')} {u.get('last_name','')}")
