#!/usr/bin/env bash
# Verifies local development prerequisites are available.
# Phase 1 scope only — a small utility script (TRD v1.0 Section 24: "scripts/
# kept minimal"). Does not install anything or touch business logic.

set -euo pipefail

check() {
  local name="$1"
  local cmd="$2"
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "[ok]   $name found: $("$cmd" --version 2>&1 | head -n1)"
  else
    echo "[MISSING] $name ('$cmd') not found on PATH"
  fi
}

echo "FoodFlow — local prerequisite check (Phase 1)"
echo "----------------------------------------------"
check "Python 3" python3
check "Node.js" node
check "npm" npm
check "Docker" docker 2>/dev/null || echo "[MISSING] Docker not found on PATH (optional — only needed for docker-compose.yml)"
echo "----------------------------------------------"
echo "Next steps: see backend/README.md and frontend/README.md."
