#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_root"
recator 1 --analyze --languages javascript --min-lines 7 --show-snippets --max-show 0 --max-blocks 0 -v
