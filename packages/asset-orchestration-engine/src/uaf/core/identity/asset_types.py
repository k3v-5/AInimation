"""
AssetType enumerates domain-recognized asset categories.
UAF-81.0 Section 12.
"""

from enum import Enum


class AssetType(str, Enum):
    CHARACTER = "CHARACTER"
    CREATURE = "CREATURE"
    WEAPON = "WEAPON"
    PROP = "PROP"
    MODULAR_KIT = "MODULAR_KIT"
    ARCHITECTURE = "ARCHITECTURE"
    ENVIRONMENT = "ENVIRONMENT"
    MATERIAL = "MATERIAL"
    TEXTURE = "TEXTURE"
    VFX = "VFX"
    AUDIO = "AUDIO"
    ANIMATION = "ANIMATION"
    RIG = "RIG"
    LEVEL = "LEVEL"
    WORLD = "WORLD"
    BLUEPRINT = "BLUEPRINT"
    OTHER = "OTHER"

    @classmethod
    def from_str(cls, value: str) -> "AssetType":
        normalized = value.strip().upper()
        try:
            return cls(normalized)
        except ValueError:
            return cls.OTHER
