"""
MuleTrace AI — UUID Helper Utilities.

Functions for UUID v4 generation, validation, and short reference formatting.
"""

from __future__ import annotations


import uuid


def generate_uuid() -> uuid.UUID:
    """Generate a new random UUID v4.

    Returns:
        uuid.UUID object.
    """
    return uuid.uuid4()


def is_valid_uuid(val: str) -> bool:
    """Validate whether a string is a valid UUID.

    Args:
        val: Input string to validate.

    Returns:
        True if valid UUID, False otherwise.
    """
    try:
        uuid.UUID(str(val))
        return True
    except (ValueError, TypeError, AttributeError):
        return False


def generate_short_id(prefix: str = "REF") -> str:
    """Generate a short human-readable reference identifier.

    Args:
        prefix: Prefix string (e.g., 'ALT', 'CAS', 'STR').

    Returns:
        Formatted reference string (e.g., 'ALT-7F2A9B').
    """
    short_hash = uuid.uuid4().hex[:6].upper()
    return f"{prefix}-{short_hash}"
