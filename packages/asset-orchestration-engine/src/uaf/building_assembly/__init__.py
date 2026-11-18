"""
Universal Asset Factory (UAF) - Procedural Environment, Modular Building, Blockout & World Assembly System (UAF-81.35)
"""

from .models import (
    WorldType35,
    GridMode35,
    ModularKitComponent35,
    RoomType35,
    RoomDefinition35,
    BuildingAssemblySpecification,
)

from .engine import (
    BuildingAssemblyFabricationPlatform,
)

from .validation import (
    BuildingAssemblyQualityScore,
    BuildingAssemblyValidationReport,
    BuildingAssemblyValidator,
)

from .package import (
    BuildingAssemblyPackage,
)

__all__ = [
    "WorldType35",
    "GridMode35",
    "ModularKitComponent35",
    "RoomType35",
    "RoomDefinition35",
    "BuildingAssemblySpecification",
    "BuildingAssemblyFabricationPlatform",
    "BuildingAssemblyQualityScore",
    "BuildingAssemblyValidationReport",
    "BuildingAssemblyValidator",
    "BuildingAssemblyPackage",
]
