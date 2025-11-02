#!/usr/bin/env bash
set -euo pipefail

# Build, install from local dist, and smoke test the CLI
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

# Ensure we're in a virtual environment for build
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  echo "This script should be run inside a virtual environment."
  echo "Run:  python3 -m venv .venv && . .venv/bin/activate"
  exit 1
fi

python -m pip install -U pip
python -m pip install build
rm -rf dist/ build/ *.egg-info || true
python -m build

# create temp venv to validate isolated install
TMPDIR="$(mktemp -d)"
python3 -m venv "$TMPDIR/venv"
source "$TMPDIR/venv/bin/activate"
python -m pip install -U pip
# Prefer local artifacts
python -m pip install dist/*.whl || python -m pip install dist/*.tar.gz

# Smoke test CLI against itself (limit scope to avoid venv)
python -m recator.cli recator --analyze -v
python -m recator.cli recator --refactor --dry-run

echo "Package smoke test completed."
