#!/usr/bin/env bash
# Fetch and pin the code baseline for a run. Every grep in the audit must run
# against this ref, not the working tree — a dirty checkout or a feature branch
# would silently grade the trainer against code that never shipped.
#
#   eval "$(scripts/pin_baseline.sh)"      # exports OKTO_REPO / OKTO_REF / OKTO_SHA
set -euo pipefail

REPO="${OKTO_REPO:-$HOME/Documents/DEV/oktorocket}"
REF="${OKTO_REF:-origin/development}"

if [ ! -d "$REPO/.git" ]; then
  echo "pin_baseline: no git repo at $REPO (set OKTO_REPO)" >&2
  exit 1
fi

# SSH to github is dead on this host; the gh credential helper over HTTPS works.
if ! git -C "$REPO" -c credential.helper='!gh auth git-credential' \
        fetch --quiet origin "${REF#origin/}" 2>/dev/null; then
  echo "pin_baseline: fetch failed — grading against the local $REF" >&2
fi

SHA="$(git -C "$REPO" rev-parse "$REF")"
SHORT="$(git -C "$REPO" rev-parse --short "$REF")"
WHEN="$(git -C "$REPO" log -1 --format=%ci "$REF")"

echo "export OKTO_REPO=$(printf %q "$REPO")"
echo "export OKTO_REF=$(printf %q "$REF")"
echo "export OKTO_SHA=$(printf %q "$SHA")"
echo "export OKTO_SHA_SHORT=$(printf %q "$SHORT")"
echo "# baseline: $SHORT ($WHEN)" >&2
