"""
Universal Asset Factory (UAF) - Procedural Modular Asset, Blockout, Kitbash, Architecture & Building System (UAF-81.39)
"""

from .models import (
    ModuleType39,
    PivotType39,
    SnapMode39,
    KitStyle39,
    ModuleDimensions39,
    ModularKitbashSpecification,
)

from .engine import (
    ModularKitbashFabricationPlatform,
)

from .validation import (
    ModularKitbashQualityScore,
    ModularKitbashValidationReport,
    ModularKitbashValidator,
)

from .package import (
    ModularKitbashPackage,
)

__all__ = [
    "ModuleType39",
    "PivotType39",
    "SnapMode39",
    "KitStyle39",
    "ModuleDimensions39",
    "ModularKitbashSpecification",
    "ModularKitbashFabricationPlatform",
    "ModularKitbashQualityScore",
    "ModularKitbashValidationReport",
    "ModularKitbashValidator",
    "ModularKitbashPackage",
]
