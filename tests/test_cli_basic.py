import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def create_test_project() -> str:
    d = tempfile.mkdtemp(prefix="recator_cli_")
    p1 = Path(d) / "x.py"
    p2 = Path(d) / "y.py"
    block = (
        "if not email:\n"
        "    raise ValueError('Email is required')\n"
        "if '@' not in email:\n"
        "    raise ValueError('Invalid email format')\n"
    )
    p1.write_text(
        f"""

def a(email):
    {block}
    return True
"""
    )
    p2.write_text(
        f"""

def b(email):
    {block}
    return True
"""
    )
    return d


def test_cli_analyze_and_refactor_preview():
    proj = create_test_project()
    try:
        # Analyze
        cmd_analyze = [sys.executable, "-m", "recator.cli", proj, "--analyze", "-v"]
        r1 = subprocess.run(cmd_analyze, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert r1.returncode == 0, f"Analyze failed: {r1.stderr}"
        assert "Analysis Results" in r1.stdout

        # Refactor preview (dry run)
        cmd_refactor = [sys.executable, "-m", "recator.cli", proj, "--refactor", "--dry-run"]
        r2 = subprocess.run(cmd_refactor, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert r2.returncode == 0, f"Refactor preview failed: {r2.stderr}"
        assert "Refactoring" in r2.stdout
    finally:
        # Cleanup temp project directory
        import shutil
        shutil.rmtree(proj)
