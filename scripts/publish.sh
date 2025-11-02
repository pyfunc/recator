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
  echo "\nWarning: The active Python interpreter (${PYBIN}) lacks the standard module '_posixsubprocess'." >&2
  echo "Some tooling may misbehave. Consider recreating venv with a full Python (e.g., python3.11) or installing system packages:" >&2
  echo "  Debian/Ubuntu:  sudo apt-get update && sudo apt-get install -y python3-venv python3-full" >&2
  echo "  Then: rm -rf venv && make PY=python3.11 venv && make install-dev" >&2
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
TWINE_ENV=("TWINE_NON_INTERACTIVE=1")

load_token() {
  local which_repo="$1"
  local token=""
  if [[ "$which_repo" == "pypi" ]]; then
    # Priority: env var value, env file, home file, repo file
    if [[ -n "${PYPI_TOKEN:-}" ]]; then token="$PYPI_TOKEN"; fi
    if [[ -z "$token" && -n "${PYPI_TOKEN_FILE:-}" && -f "$PYPI_TOKEN_FILE" ]]; then token="$(<"$PYPI_TOKEN_FILE")"; fi
    if [[ -z "$token" && -f "$HOME/.pypi_token" ]]; then token="$(<"$HOME/.pypi_token")"; fi
    if [[ -z "$token" && -f "$HOME/.pypi-token" ]]; then token="$(<"$HOME/.pypi-token")"; fi
    if [[ -z "$token" && -f ".pypi_token" ]]; then token="$(<".pypi_token")"; fi
    if [[ -z "$token" && -f ".pypi-token" ]]; then token="$(<".pypi-token")"; fi
    # generic fallbacks
    if [[ -z "$token" && -f ".token" ]]; then token="$(<".token")"; fi
    if [[ -z "$token" && -f "$HOME/.token" ]]; then token="$(<"$HOME/.token")"; fi
  else
    if [[ -n "${TESTPYPI_TOKEN:-}" ]]; then token="$TESTPYPI_TOKEN"; fi
    if [[ -z "$token" && -n "${TESTPYPI_TOKEN_FILE:-}" && -f "$TESTPYPI_TOKEN_FILE" ]]; then token="$(<"$TESTPYPI_TOKEN_FILE")"; fi
    if [[ -z "$token" && -f "$HOME/.testpypi_token" ]]; then token="$(<"$HOME/.testpypi_token")"; fi
    if [[ -z "$token" && -f "$HOME/.testpypi-token" ]]; then token="$(<"$HOME/.testpypi-token")"; fi
    if [[ -z "$token" && -f ".testpypi_token" ]]; then token="$(<".testpypi_token")"; fi
    if [[ -z "$token" && -f ".testpypi-token" ]]; then token="$(<".testpypi-token")"; fi
    # generic fallbacks
    if [[ -z "$token" && -f ".token" ]]; then token="$(<".token")"; fi
    if [[ -z "$token" && -f "$HOME/.token" ]]; then token="$(<"$HOME/.token")"; fi
  fi
  if [[ -n "$token" ]]; then
    # Trim and export for twine
    token="${token%%[[:space:]]*}"
    TWINE_ENV+=("TWINE_USERNAME=__token__" "TWINE_PASSWORD=$token")
    return 0
  fi
  return 1
}

if [[ "$repo" == "pypi" ]]; then
  echo "Uploading to PyPI..."
  if load_token pypi; then
    env "${TWINE_ENV[@]}" "$PYBIN" -m twine upload --non-interactive dist/*
  else
    echo "No PyPI token found. Set one of: PYPI_TOKEN, PYPI_TOKEN_FILE, ~/.pypi_token, ./.pypi_token or configure ~/.pypirc." >&2
    echo "Falling back to ~/.pypirc if present; otherwise this will fail non-interactively." >&2
    env "${TWINE_ENV[@]}" "$PYBIN" -m twine upload --non-interactive dist/*
  fi
else
  echo "Uploading to TestPyPI..."
  if load_token testpypi; then
    env "${TWINE_ENV[@]}" "$PYBIN" -m twine upload --non-interactive --repository testpypi dist/*
  else
    echo "No TestPyPI token found. Set one of: TESTPYPI_TOKEN, TESTPYPI_TOKEN_FILE, ~/.testpypi_token, ./.testpypi_token or configure ~/.pypirc." >&2
    echo "Falling back to ~/.pypirc if present; otherwise this will fail non-interactively." >&2
    env "${TWINE_ENV[@]}" "$PYBIN" -m twine upload --non-interactive --repository testpypi dist/*
  fi
fi

echo "Done."
