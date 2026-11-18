"""
Universal Asset Factory (UAF) - Character & Creature Production 2.0: High-Fidelity Anatomy, Clothing, Hair, Rigging, Skinning, Facial System & Animation-Ready Asset Generation (UAF-81.45)
"""

from .models import (
    CharacterArchetype45,
    ProportionProfile45,
    SymmetryMode45,
    PlatformProfile45,
    AnatomicalDimensions45,
    CharacterProdV2Specification,
)

from .engine import (
    CharacterProdV2FabricationPlatform,
)

from .validation import (
    CharacterProdV2QualityScore,
    CharacterProdV2ValidationReport,
    CharacterProdV2Validator,
)

from .package import (
    CharacterProdV2Package,
)

__all__ = [
    "CharacterArchetype45",
    "ProportionProfile45",
    "SymmetryMode45",
    "PlatformProfile45",
    "AnatomicalDimensions45",
    "CharacterProdV2Specification",
    "CharacterProdV2FabricationPlatform",
    "CharacterProdV2QualityScore",
    "CharacterProdV2ValidationReport",
    "CharacterProdV2Validator",
    "CharacterProdV2Package",
]
