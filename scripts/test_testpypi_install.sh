#!/usr/bin/env bash
set -euo pipefail

# Install from TestPyPI into a fresh venv and smoke test
PACKAGE_NAME="recator"
TMPDIR="$(mktemp -d)"
python3 -m venv "$TMPDIR/venv"
source "$TMPDIR/venv/bin/activate"
python -m pip install -U pip
python -m pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple "$PACKAGE_NAME"

python -m recator.cli . --analyze -v
python -m recator.cli . --refactor --dry-run

echo "Remote TestPyPI install smoke test completed."
