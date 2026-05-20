#!/usr/bin/env bash
# Serve the MetaMask deploy UI (must be http://, not file://).
set -euo pipefail
cd "$(dirname "$0")"
PORT="${1:-8787}"
echo "Open http://127.0.0.1:${PORT} in your browser (MetaMask required)."
exec python3 -m http.server "$PORT" --bind 127.0.0.1
