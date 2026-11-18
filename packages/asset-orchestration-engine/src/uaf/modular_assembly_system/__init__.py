"""
Universal Asset Factory (UAF) - Environment, Architecture & Modular World Assembly System (UAF-81.50)
"""

from .models import (
    EnvironmentType50,
    ModularPieceType50,
    AssemblyDimensions50,
    ModularAssemblySpecification,
)

from .engine import (
    ModularAssemblyFabricationPlatform,
)

from .validation import (
    ModularAssemblyQualityScore,
    ModularAssemblyValidationReport,
    ModularAssemblyValidator,
)

from .package import (
    ModularAssemblyPackage,
)

__all__ = [
    "EnvironmentType50",
    "ModularPieceType50",
    "AssemblyDimensions50",
    "ModularAssemblySpecification",
    "ModularAssemblyFabricationPlatform",
    "ModularAssemblyQualityScore",
    "ModularAssemblyValidationReport",
    "ModularAssemblyValidator",
    "ModularAssemblyPackage",
]
