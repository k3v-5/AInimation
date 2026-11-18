"""
UAF-81.90: Universal Procedural Level Design, Modular Assembly (WFC) & Dynamic Mission Director.
Decoupled, deterministic procedural generation and mission orchestration for Unreal Engine 5.
"""

from uaf.level_design.core.contracts import (
    Direction2D,
    Direction3D,
    OPPOSITE_DIR_2D,
    OPPOSITE_DIR_3D,
    DIR_OFFSETS_2D,
    DIR_OFFSETS_3D,
    SocketType,
    are_sockets_compatible,
    RoomType,
    ObjectiveType,
    ObjectiveState,
    DependencyType,
    PacingPhase,
    ModularTileDefinition,
    PlacedTile,
    PlayerStressMetric,
    PacingDecision,
)
from uaf.level_design.wfc import (
    WaveFunctionCollapse2D,
    WaveFunctionCollapse3D,
    WFCContradictionError,
    create_scifi_interior_catalog_2d,
    create_scifi_multilevel_catalog_3d,
)
from uaf.level_design.topology import (
    TopologyNode,
    LevelTopologyGraph,
    KeyItem,
    LockedDoor,
    LockKeyProgressionResult,
    LockAndKeyGenerator,
)
from uaf.level_design.mission import (
    VolumeTrigger,
    MissionNode,
    MissionGraph,
    MissionCycleError,
)
from uaf.level_design.pacing import (
    SpatialSpawnPoint,
    DynamicPacingDirector,
)
from uaf.level_design.export import (
    UE5ActorInstance,
    UE5LevelManifest,
    UE5LevelExporter,
)

__all__ = [
    # Core
    "Direction2D",
    "Direction3D",
    "OPPOSITE_DIR_2D",
    "OPPOSITE_DIR_3D",
    "DIR_OFFSETS_2D",
    "DIR_OFFSETS_3D",
    "SocketType",
    "are_sockets_compatible",
    "RoomType",
    "ObjectiveType",
    "ObjectiveState",
    "DependencyType",
    "PacingPhase",
    "ModularTileDefinition",
    "PlacedTile",
    "PlayerStressMetric",
    "PacingDecision",
    # WFC
    "WaveFunctionCollapse2D",
    "WaveFunctionCollapse3D",
    "WFCContradictionError",
    "create_scifi_interior_catalog_2d",
    "create_scifi_multilevel_catalog_3d",
    # Topology
    "TopologyNode",
    "LevelTopologyGraph",
    "KeyItem",
    "LockedDoor",
    "LockKeyProgressionResult",
    "LockAndKeyGenerator",
    # Mission
    "VolumeTrigger",
    "MissionNode",
    "MissionGraph",
    "MissionCycleError",
    # Pacing
    "SpatialSpawnPoint",
    "DynamicPacingDirector",
    # Export
    "UE5ActorInstance",
    "UE5LevelManifest",
    "UE5LevelExporter",
]
