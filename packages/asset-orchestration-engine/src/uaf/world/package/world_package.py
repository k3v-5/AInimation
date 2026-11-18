"""
WorldPackage encapsulates complete levels ready for Unreal Engine 5 World Partition import.
UAF-81.6 Sections 2, 3, 99, 100.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..spatial.world_specification import WorldSpecification
from ..modular.modular_kit import ModularKitDefinition
from ..assembly.assembly_graph import AssemblyGraph
from ..assembly.room import RoomDefinition
from ..assembly.building import BuildingDefinition
from ..gameplay.spatial_gameplay import SpawnPoint, CoverDefinition, ObjectiveDefinition
from ..gameplay.navigation import NavigationMeshMetadata
from ..partition.world_partition import WorldPartitionCell, HLODMetadata
from ..validation.world_validator import WorldValidationReport
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class WorldPackage:
    world_id: str
    specification: WorldSpecification
    kit: ModularKitDefinition
    assembly: AssemblyGraph
    rooms: List[RoomDefinition] = field(default_factory=list)
    buildings: List[BuildingDefinition] = field(default_factory=list)
    spawns: List[SpawnPoint] = field(default_factory=list)
    covers: List[CoverDefinition] = field(default_factory=list)
    objectives: List[ObjectiveDefinition] = field(default_factory=list)
    navigation: Optional[NavigationMeshMetadata] = None
    partition_cells: List[WorldPartitionCell] = field(default_factory=list)
    hlod: Optional[HLODMetadata] = None
    validation_report: Optional[WorldValidationReport] = None
    version: str = "1.0.0"

    @property
    def build_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "specification": self.specification.to_dict(),
            "kit": self.kit.to_dict(),
            "assembly": self.assembly.to_dict(),
            "rooms": [r.to_dict() for r in self.rooms],
            "buildings": [b.to_dict() for b in self.buildings],
            "spawns": [s.to_dict() for s in self.spawns],
            "covers": [c.to_dict() for c in self.covers],
            "objectives": [o.to_dict() for o in self.objectives],
            "navigation": self.navigation.to_dict() if self.navigation else None,
            "partition_cells": [p.to_dict() for p in self.partition_cells],
            "hlod": self.hlod.to_dict() if self.hlod else None,
            "validation_report": self.validation_report.to_dict() if self.validation_report else None,
            "version": self.version,
        }
