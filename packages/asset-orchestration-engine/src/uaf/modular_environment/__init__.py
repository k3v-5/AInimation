"""
Universal Asset Factory (UAF) - Modular Geometry, Building Blocks & Procedural Environment Assembly System (UAF-81.47)
"""

from .models import (
    ModuleCategory47,
    SnapType47,
    EnvironmentStyle47,
    EnvironmentDimensions47,
    ModularEnvironmentSpecification,
)

from .engine import (
    ModularEnvironmentFabricationPlatform,
)

from .validation import (
    ModularEnvironmentQualityScore,
    ModularEnvironmentValidationReport,
    ModularEnvironmentValidator,
)

from .package import (
    ModularEnvironmentPackage,
)

__all__ = [
    "ModuleCategory47",
    "SnapType47",
    "EnvironmentStyle47",
    "EnvironmentDimensions47",
    "ModularEnvironmentSpecification",
    "ModularEnvironmentFabricationPlatform",
    "ModularEnvironmentQualityScore",
    "ModularEnvironmentValidationReport",
    "ModularEnvironmentValidator",
    "ModularEnvironmentPackage",
]
