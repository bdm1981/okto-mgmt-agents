#!/usr/bin/env bash
# Render a built dashboard HTML to a Letter-size PDF with headless Chrome.
# Usage: export_pdf.sh daily.html out.pdf
set -euo pipefail
IN="$1"; OUT="$2"; HERE="$(cd "$(dirname "$0")" && pwd)"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[ -x "$CHROME" ] || { echo "Chrome not found at $CHROME (set CHROME=...)"; exit 1; }
TMP="$(mktemp -t dash).html"
python3 - "$IN" "$HERE/../assets/print.css" "$TMP" <<'PY'
import sys
h=open(sys.argv[1],encoding="utf-8").read(); css=open(sys.argv[2]).read()
h=h.replace("</style>", "</style><style media=\"print\">"+css+"</style>",1)
open(sys.argv[3],"w",encoding="utf-8").write("<!doctype html><html><head><meta charset='utf-8'>"+h+"</html>")
PY
"$CHROME" --headless=new --disable-gpu --no-first-run --no-default-browser-check \
  --run-all-compositor-stages-before-draw --virtual-time-budget=8000 --no-pdf-header-footer \
  --print-to-pdf="$OUT" "file://$TMP" 2>/dev/null
rm -f "$TMP"; echo "wrote $OUT ($(stat -f%z "$OUT") bytes)"
