#!/bin/sh
# Render print-media PDF and 2x PNG(s), checking every page before writing.
set -eu
exec python3 "$(dirname "$0")/render.py" "$@"
