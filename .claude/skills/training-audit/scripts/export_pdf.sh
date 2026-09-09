#!/usr/bin/env bash
# Letter-size PDF from a rendered report, links preserved, light palette forced.
#   scripts/export_pdf.sh report-<uuid>.html [out.pdf]
set -euo pipefail
SRC="${1:?usage: export_pdf.sh <html> [out.pdf]}"
OUT="${2:-${SRC%.html}.pdf}"
CHROME="${CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[ -x "$CHROME" ] || { echo "export_pdf: no Chrome at $CHROME (set CHROME_BIN)" >&2; exit 1; }
"$CHROME" --headless --disable-gpu --no-sandbox --no-pdf-header-footer \
  --run-all-compositor-stages-before-draw --virtual-time-budget=15000 \
  --print-to-pdf="$OUT" "file://$(cd "$(dirname "$SRC")" && pwd)/$(basename "$SRC")" 2>/dev/null
echo "$OUT"
