"""
Universal Asset Factory (UAF) - Character & Creature Production System (UAF-81.49)
"""

from .models import (
    CharacterType49,
    SpeciesType49,
    BodyRepresentation49,
    BodyDimensions49,
    CharacterCreatureSpecification,
)

from .engine import (
    CharacterCreatureFabricationPlatform,
)

from .validation import (
    CharacterCreatureQualityScore,
    CharacterCreatureValidationReport,
    CharacterCreatureValidator,
)

from .package import (
    CharacterCreaturePackage,
)

__all__ = [
    "CharacterType49",
    "SpeciesType49",
    "BodyRepresentation49",
    "BodyDimensions49",
    "CharacterCreatureSpecification",
    "CharacterCreatureFabricationPlatform",
    "CharacterCreatureQualityScore",
    "CharacterCreatureValidationReport",
    "CharacterCreatureValidator",
    "CharacterCreaturePackage",
]
