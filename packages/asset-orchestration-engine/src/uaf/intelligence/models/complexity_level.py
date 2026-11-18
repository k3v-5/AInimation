"""
ComplexityLevel defines standardized complexity tiers for assets.
UAF-81.1 Section 34.
"""

from enum import Enum


class ComplexityLevel(str, Enum):
    C0_PRIMITIVE = "C0"
    C1_SIMPLE = "C1"
    C2_GAME_READY = "C2"
    C3_PRODUCTION = "C3"
    C4_HERO = "C4"
    C5_CINEMATIC = "C5"

    @classmethod
    def from_str(cls, value: str) -> "ComplexityLevel":
        v = value.strip().upper()
        for member in cls:
            if member.value == v or member.name.startswith(v):
                return member
        return cls.C2_GAME_READY
