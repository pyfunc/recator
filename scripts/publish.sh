#!/usr/bin/env bash
set -euo pipefail

# Publish script for Recator
# Usage:
#  ./scripts/publish.sh test [patch|minor|major]   # upload to TestPyPI
#  ./scripts/publish.sh pypi [patch|minor|major]   # upload to PyPI
# Requires: build, twine, and a configured ~/.pypirc or TWINE_* env vars

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

# Ensure we're in a virtual environment (avoid system package manager issues)
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  echo "This script should be run inside a virtual environment."
  echo "Run:  python3 -m venv venv && . venv/bin/activate"
  exit 1
fi

PYBIN="${VIRTUAL_ENV}/bin/python"

# Preflight: detect broken Python builds (missing _posixsubprocess)
if ! "$PYBIN" - <<'PY'
import sys
try:
    import _posixsubprocess  # noqa: F401
except Exception as e:
    print(f"MISSING:_posixsubprocess:{e}")
    sys.exit(2)
PY
then
  echo "\nError: The active Python interpreter (${PYBIN}) lacks the standard module '_posixsubprocess'." >&2
  echo "This is a known issue with incomplete Python installations." >&2
  echo "Fix by recreating venv with a full Python (e.g., python3.11) or installing system packages:" >&2
  echo "  Debian/Ubuntu:  sudo apt-get update && sudo apt-get install -y python3-venv python3-full" >&2
  echo "  Then: rm -rf venv && make PY=python3.11 venv && make install-dev" >&2
  exit 2
fi

# Ensure pip is available and up to date
"$PYBIN" -m ensurepip --upgrade || true
"$PYBIN" -m pip install -U pip
"$PYBIN" -m pip install build twine

# Clean previous artifacts
rm -rf dist/ build/ *.egg-info || true

# Bump version (default: patch)
part="${2:-patch}"
"$PYBIN" scripts/bump_version.py "$part"

# Build sdist and wheel
"$PYBIN" -m build

repo="${1:-test}"
if [[ "$repo" == "pypi" ]]; then
  echo "Uploading to PyPI..."
  "$PYBIN" -m twine upload dist/*
else
  echo "Uploading to TestPyPI..."
  "$PYBIN" -m twine upload --repository testpypi dist/*
fi

echo "Done."
