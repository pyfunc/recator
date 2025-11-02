import os
from pathlib import Path
import shutil
import tempfile

from recator import Recator


def create_test_project() -> str:
    """Create a temporary project directory with deliberate duplicates."""
    test_dir = tempfile.mkdtemp(prefix="recator_pytest_")

    p1 = Path(test_dir) / "a.py"
    p2 = Path(test_dir) / "b.py"

    duplicate_block = (
        "    if not email:\n"
        "        raise ValueError('Email is required')\n"
        "    if '@' not in email:\n"
        "        raise ValueError('Invalid email format')\n"
        "    if not email.endswith('.com') and not email.endswith('.org'):\n"
        "        raise ValueError('Invalid email domain')\n"
    )

    p1.write_text(
        """
def validate_email(email):
    """Validate email address"""
{}    return True

def process_user(username, email):
{}    return {{"username": username, "email": email}}
""".format(duplicate_block, duplicate_block)
    )

    p2.write_text(
        """
def update_user_email(user_id, email):
{}    return True
""".format(duplicate_block)
    )

    return test_dir


def test_api_analyze_finds_duplicates():
    project = create_test_project()
    try:
        config = {
            "languages": ["python"],
            "min_lines": 3,
            "min_tokens": 10,
            "similarity_threshold": 0.75,
            "exclude_patterns": [],
            "safe_mode": True,
        }

        rec = Recator(project, config)
        results = rec.analyze()

        assert results["total_files"] >= 2
        assert results["parsed_files"] >= 2
        assert results["duplicates_found"] >= 1
        assert isinstance(results["duplicates"], list)
        assert any(d.get("type") in {"exact", "exact_block", "token_sequence", "similar_block", "structural"} for d in results["duplicates"])

        # Preview refactor plan
        preview = rec.refactor_duplicates(dry_run=True)
        assert isinstance(preview, dict)
        assert "total_actions" in preview
        assert "affected_files" in preview
    finally:
        shutil.rmtree(project)
