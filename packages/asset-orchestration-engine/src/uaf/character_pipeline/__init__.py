"""
Universal Asset Factory (UAF) - Professional Character Rigging, Skinning, Clothing, Hair, Facial & Animation-Ready Character System (UAF-81.37)
"""

from .models import (
    CharacterArchetype37,
    RigType37,
    ControlType37,
    CharacterProportions37,
    CharacterProductionSpecification,
)

from .engine import (
    CharacterPipelineFabricationPlatform,
)

from .validation import (
    CharacterPipelineQualityScore,
    CharacterPipelineValidationReport,
    CharacterPipelineValidator,
)

from .package import (
    CharacterPipelinePackage,
)

__all__ = [
    "CharacterArchetype37",
    "RigType37",
    "ControlType37",
    "CharacterProportions37",
    "CharacterProductionSpecification",
    "CharacterPipelineFabricationPlatform",
    "CharacterPipelineQualityScore",
    "CharacterPipelineValidationReport",
    "CharacterPipelineValidator",
    "CharacterPipelinePackage",
]
