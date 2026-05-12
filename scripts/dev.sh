#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/apps/backend"
BACKEND_VENV="$BACKEND_DIR/.venv"
BACKEND_PYTHON="$BACKEND_VENV/bin/python"
BACKEND_URL="http://localhost:8000"
WEB_URL="http://localhost:9002"
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

wait_for_url() {
  local url="$1"
  local label="$2"

  for _ in {1..60}; do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.5
  done

  echo "Timed out waiting for $label at $url" >&2
  return 1
}

warm_next_routes() {
  local routes=(
    "/"
    "/flashcards"
    "/search"
    "/reader"
    "/notebook"
    "/games"
    "/games/gender"
    "/games/maze"
  )

  echo "Warming Next.js routes..."
  for route in "${routes[@]}"; do
    curl -fsS "$WEB_URL$route" >/dev/null 2>&1 || true
  done
  echo "App is ready: $WEB_URL"
}

ensure_backend_venv() {
  if [[ ! -x "$BACKEND_PYTHON" ]]; then
    python -m venv "$BACKEND_VENV"
  fi

  "$BACKEND_PYTHON" -m pip install -q -r "$BACKEND_DIR/requirements.txt"
}

trap cleanup EXIT INT TERM

ensure_backend_venv

(
  cd "$BACKEND_DIR"
  "$BACKEND_PYTHON" main.py
) &
BACKEND_PID=$!

(
  cd "$ROOT_DIR/apps/web"
  npm run dev
) &
WEB_PID=$!

wait_for_url "$BACKEND_URL/" "backend"
wait_for_url "$WEB_URL/" "web"
warm_next_routes &

wait -n "$BACKEND_PID" "$WEB_PID"
