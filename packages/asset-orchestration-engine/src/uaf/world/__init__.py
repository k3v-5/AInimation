"""
Universal Asset Factory (UAF) - World Geometry, Modular Blockout & Procedural Level Fabric (UAF-81.6)
"""

from .spatial import (
    WorldGrid,
    WorldSpecification,
)

from .modular import (
    ConnectorType,
    ConnectorDefinition,
    ModuleCategory,
    ModuleDefinition,
    ModularKitDefinition,
)

from .assembly import (
    AssemblyNode,
    AssemblyGraph,
    RoomType,
    RoomDefinition,
    BuildingDefinition,
)

from .gameplay import (
    CoverType,
    CoverDefinition,
    SpawnPoint,
    ObjectiveDefinition,
    NavigationMeshMetadata,
)

from .partition import (
    DataLayer,
    WorldPartitionCell,
    HLODMetadata,
)

from .validation import (
    WorldQualityScore,
    WorldValidationReport,
    WorldValidator,
)

from .package import (
    WorldPackage,
)

__all__ = [
    "WorldGrid",
    "WorldSpecification",
    "ConnectorType",
    "ConnectorDefinition",
    "ModuleCategory",
    "ModuleDefinition",
    "ModularKitDefinition",
    "AssemblyNode",
    "AssemblyGraph",
    "RoomType",
    "RoomDefinition",
    "BuildingDefinition",
    "CoverType",
    "CoverDefinition",
    "SpawnPoint",
    "ObjectiveDefinition",
    "NavigationMeshMetadata",
    "DataLayer",
    "WorldPartitionCell",
    "HLODMetadata",
    "WorldQualityScore",
    "WorldValidationReport",
    "WorldValidator",
    "WorldPackage",
]
