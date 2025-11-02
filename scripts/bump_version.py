#!/usr/bin/env python3
"""
Bump the version in recator/__init__.py.
Usage:
  python scripts/bump_version.py [patch|minor|major]
Defaults to 'patch'. Prints the new version to stdout.
"""
from pathlib import Path
import re
import sys

PARTS = {"major", "minor", "patch"}

def bump(version: str, part: str) -> str:
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:[.-].*)?$", version)
    if not m:
        raise ValueError(f"Unsupported version format: {version}")
    major, minor, patch = map(int, m.groups())
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"

def main():
    repo_root = Path(__file__).resolve().parents[1]
    init_py = repo_root / "recator" / "__init__.py"
    text = init_py.read_text(encoding="utf-8")
    m = re.search(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", text, re.M)
    if not m:
        raise SystemExit("Could not find __version__ in recator/__init__.py")
    current = m.group(1)
    part = (sys.argv[1] if len(sys.argv) > 1 else "patch").lower()
    if part not in PARTS:
        raise SystemExit(f"Unknown bump part '{part}'. Use one of: {', '.join(sorted(PARTS))}")
    new_version = bump(current, part)
    new_text = re.sub(
        r"^__version__\s*=\s*['\"]([^'\"]+)['\"]",
        f"__version__ = \"{new_version}\"",
        text,
        count=1,
        flags=re.M,
    )
    init_py.write_text(new_text, encoding="utf-8")
    print(new_version)

if __name__ == "__main__":
    main()
