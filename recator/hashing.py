"""
Stable hashing utilities that do not rely on hashlib/OpenSSL.
We implement FNV-1a 64-bit in pure Python for portability across environments
(e.g., Python builds without OpenSSL or with restricted algorithms).
"""
from typing import Iterable

FNV_64_OFFSET = 14695981039346656037
FNV_64_PRIME = 1099511628211


def fnv1a_64(data: bytes) -> int:
    """Compute 64-bit FNV-1a hash of the given bytes."""
    h = FNV_64_OFFSET
    for b in data:
        h ^= b
        h = (h * FNV_64_PRIME) & 0xFFFFFFFFFFFFFFFF
    return h


def stable_hash_bytes(data: bytes) -> str:
    """Return a stable 64-bit hex digest for bytes."""
    return f"{fnv1a_64(data):016x}"


def stable_hash_text(text: str) -> str:
    """Return a stable 64-bit hex digest for text (UTF-8)."""
    return stable_hash_bytes(text.encode("utf-8", errors="ignore"))


def stable_hash_tokens(tokens: Iterable[str]) -> str:
    """Return a stable 64-bit hex digest for a token sequence.

    We join tokens with an ASCII unit separator to avoid accidental collisions
    from simple concatenation (e.g., ["ab","c"] vs ["a","bc"]).
    """
    sep = "\x1f"  # Unit Separator
    return stable_hash_text(sep.join(tokens))
