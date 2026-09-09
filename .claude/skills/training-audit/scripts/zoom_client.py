#!/usr/bin/env python3
"""Zoom Server-to-Server OAuth client — cloud recordings + transcripts.

Why this exists rather than the Zoom MCP connector: the connector is per-user
OAuth and only ever returns the *authenticated user's* own recordings. Training
sessions are hosted by the training account, so an audit run driven by anyone
else's identity sees nothing. Account-level `recording:read:admin` is the only
path that can enumerate another host's recordings unattended.

Credentials (env, never committed):
    ZOOM_ACCOUNT_ID
    ZOOM_CLIENT_ID
    ZOOM_CLIENT_SECRET

Required app scopes:
    recording:read:admin        list + download recordings for any host
    user:read:admin             resolve host_id -> name/email

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


def _require_env():
    missing = [
        k
        for k in ("ZOOM_ACCOUNT_ID", "ZOOM_CLIENT_ID", "ZOOM_CLIENT_SECRET")
        if not os.environ.get(k)
    ]
    if missing:
        raise ZoomError(
            "missing env: "
            + ", ".join(missing)
            + "\nSee references/sources.md for how to create the S2S app."
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
