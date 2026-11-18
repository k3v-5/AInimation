"""
UAF-81.83: Modular Sequence Number Arithmetic and Wrapping Utilities.
"""

from __future__ import annotations


def sequence_greater_than(s1: int, s2: int, max_sequence: int = 65536) -> bool:
    """
    Evaluate if sequence s1 is strictly newer than s2 under modular integer wrapping.
    Default modulus is 16-bit (65536) with half-range threshold (32768).
    """
    half = max_sequence // 2
    return ((s1 > s2 and (s1 - s2) <= half) or
            (s1 < s2 and (s2 - s1) > half))


def sequence_diff(s1: int, s2: int, max_sequence: int = 65536) -> int:
    """
    Calculate the modular signed distance from s2 to s1: (s1 - s2).
    Positive indicates s1 is newer than s2; negative indicates s1 is older.
    """
    diff = (s1 - s2) % max_sequence
    half = max_sequence // 2
    if diff > half:
        diff -= max_sequence
    return diff


def sequence_less_than(s1: int, s2: int, max_sequence: int = 65536) -> bool:
    """Evaluate if sequence s1 is strictly older than s2 under modular integer wrapping."""
    return sequence_greater_than(s2, s1, max_sequence)

