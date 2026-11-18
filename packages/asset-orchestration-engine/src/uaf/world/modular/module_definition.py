"""
ModuleDefinition models discrete modular building blocks (walls, floors, doors, stairs).
UAF-81.6 Sections 8, 9.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .connector import ConnectorDefinition, ConnectorType
from ...geometry.models.mesh_data import MeshData
from ...core.hashing.canonical_hasher import CanonicalHasher


class ModuleCategory(str, Enum):
    WALL = "WALL"
    FLOOR = "FLOOR"
    CEILING = "CEILING"
    ROOF = "ROOF"
    DOOR = "DOOR"
    WINDOW = "WINDOW"
    STAIR = "STAIR"
    RAMP = "RAMP"
    COLUMN = "COLUMN"
    BEAM = "BEAM"
    CORRIDOR = "CORRIDOR"
    ROOM = "ROOM"
    PLATFORM = "PLATFORM"


@dataclass
class ModuleDefinition:
    module_id: str
    category: ModuleCategory
    dimensions: List[float] = field(default_factory=lambda: [2.0, 0.2, 3.0])  # Width, Depth, Height
    connectors: List[ConnectorDefinition] = field(default_factory=list)
    mesh_data: Optional[MeshData] = None
    semantic_tags: List[str] = field(default_factory=list)
    gameplay_tags: List[str] = field(default_factory=list)
    materials: List[str] = field(default_factory=list)

    def get_connector(self, connector_id: str) -> Optional[ConnectorDefinition]:
        for c in self.connectors:
            if c.connector_id == connector_id:
                return c
        return None

    @property
    def module_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "module_id": self.module_id,
            "category": self.category.value,
            "dimensions": self.dimensions,
            "connectors": [c.to_dict() for c in self.connectors],
            "mesh_data": self.mesh_data.to_dict() if self.mesh_data else None,
            "semantic_tags": self.semantic_tags,
            "gameplay_tags": self.gameplay_tags,
            "materials": self.materials,
        }
