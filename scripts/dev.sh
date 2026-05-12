#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_PID=""
WEB_PID=""

cleanup() {
  if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
  if [[ -n "$WEB_PID" ]] && kill -0 "$WEB_PID" 2>/dev/null; then
    kill "$WEB_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

(
  cd "$ROOT_DIR/apps/backend"
  python main.py
) &
BACKEND_PID=$!

(
  cd "$ROOT_DIR/apps/web"
  npm run dev
) &
WEB_PID=$!

wait -n "$BACKEND_PID" "$WEB_PID"
