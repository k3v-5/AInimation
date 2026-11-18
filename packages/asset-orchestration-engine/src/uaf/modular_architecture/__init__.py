"""
Universal Asset Factory (UAF) - Procedural Modular Asset & Architecture Production System (UAF-81.31)
"""

from .models import (
    ModuleType31,
    ArchitecturalKitType31,
    SocketType31,
    ArchitecturalModulePiece,
    ModularArchitectureKitDefinition,
)

from .engine import (
    ModularArchitectureFabricationPlatform,
)

from .validation import (
    ModularArchitectureQualityScore,
    ModularArchitectureValidationReport,
    ModularArchitectureValidator,
)

from .package import (
    ModularArchitecturePackage,
)

__all__ = [
    "ModuleType31",
    "ArchitecturalKitType31",
    "SocketType31",
    "ArchitecturalModulePiece",
    "ModularArchitectureKitDefinition",
    "ModularArchitectureFabricationPlatform",
    "ModularArchitectureQualityScore",
    "ModularArchitectureValidationReport",
    "ModularArchitectureValidator",
    "ModularArchitecturePackage",
]
