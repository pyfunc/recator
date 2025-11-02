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
  echo "Run:  python3 -m venv .venv && . .venv/bin/activate"
  exit 1
fi

python -m pip install -U pip
python -m pip install build twine

# Clean previous artifacts
rm -rf dist/ build/ *.egg-info || true

# Bump version (default: patch)
part="${2:-patch}"
python scripts/bump_version.py "$part"

# Build sdist and wheel
python -m build

repo="${1:-test}"
if [[ "$repo" == "pypi" ]]; then
  echo "Uploading to PyPI..."
  python -m twine upload dist/*
else
  echo "Uploading to TestPyPI..."
  python -m twine upload --repository testpypi dist/*
fi

echo "Done."
