"""
Universal Asset Factory (UAF) - Procedural Modular Environment & World Fabrication (UAF-81.12)
"""

from .spatial import (
    SnapCategory,
    SnapPoint,
    GridProfile,
    ModularPiece,
)

from .grammar import (
    ModularGrammarRule,
    ModularGrammar,
)

from .topology import (
    RoomType,
    RoomNode,
    BuildingFacilityGraph,
)

from .generator import (
    ProceduralEnvironmentFabricator,
)

from .validation import (
    EnvironmentQualityScore,
    EnvironmentValidationReport,
    EnvironmentValidator,
)

from .package import (
    EnvironmentPackage,
)

__all__ = [
    "SnapCategory",
    "SnapPoint",
    "GridProfile",
    "ModularPiece",
    "ModularGrammarRule",
    "ModularGrammar",
    "RoomType",
    "RoomNode",
    "BuildingFacilityGraph",
    "ProceduralEnvironmentFabricator",
    "EnvironmentQualityScore",
    "EnvironmentValidationReport",
    "EnvironmentValidator",
    "EnvironmentPackage",
]
