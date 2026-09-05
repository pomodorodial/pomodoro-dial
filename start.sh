#!/usr/bin/env bash
# Serves the Pomodoro Dial on http://localhost:8080 (127.0.0.1 only, not reachable from other devices).
cd "$(dirname "$0")"
PORT="${1:-8080}"
echo "Pomodoro Dial running at http://localhost:$PORT  (Ctrl+C to stop)"
exec python3 -m http.server "$PORT" --bind 127.0.0.1 --directory .
