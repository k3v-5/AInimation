"""
ModularKitDefinition groups interoperable modular building blocks.
UAF-81.6 Section 7.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .module_definition import ModuleDefinition, ModuleCategory
from .connector import ConnectorDefinition, ConnectorType
from ...geometry.models.mesh_data import MeshData
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class ModularKitDefinition:
    kit_id: str
    theme: str
    modules: Dict[str, ModuleDefinition] = field(default_factory=dict)
    grid_unit_meters: float = 2.0
    wall_height_meters: float = 3.0
    version: str = "1.0.0"

    def get_module(self, module_id: str) -> Optional[ModuleDefinition]:
        return self.modules.get(module_id)

    def find_by_category(self, category: ModuleCategory) -> List[ModuleDefinition]:
        return [m for m in self.modules.values() if m.category == category]

    @property
    def kit_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kit_id": self.kit_id,
            "theme": self.theme,
            "modules": {k: v.to_dict() for k, v in sorted(self.modules.items())},
            "grid_unit_meters": self.grid_unit_meters,
            "wall_height_meters": self.wall_height_meters,
            "version": self.version,
        }

    @classmethod
    def create_standard_scifi_kit(cls, kit_id: str = "Kit_SciFi_Facility") -> "ModularKitDefinition":
        """Preloads standard architectural modules (Walls, Floors, Doors, Stairs, Columns)."""
        modules: Dict[str, ModuleDefinition] = {}

        # 1. Floor 2x2m
        floor_connectors = [
            ConnectorDefinition("conn_north", ConnectorType.FLOOR, [0.0, 1.0, 0.0], [0.0, 0.0, 0.0], [2.0, 0.2]),
            ConnectorDefinition("conn_south", ConnectorType.FLOOR, [0.0, -1.0, 0.0], [0.0, 0.0, 180.0], [2.0, 0.2]),
            ConnectorDefinition("conn_east", ConnectorType.FLOOR, [1.0, 0.0, 0.0], [0.0, 0.0, 90.0], [2.0, 0.2]),
            ConnectorDefinition("conn_west", ConnectorType.FLOOR, [-1.0, 0.0, 0.0], [0.0, 0.0, -90.0], [2.0, 0.2]),
        ]
        modules["Mod_Floor_2x2"] = ModuleDefinition(
            module_id="Mod_Floor_2x2",
            category=ModuleCategory.FLOOR,
            dimensions=[2.0, 2.0, 0.2],
            connectors=floor_connectors,
            mesh_data=MeshData.create_cube(size=2.0),
            semantic_tags=["structural", "walkable"],
        )

        # 2. Wall 2x3m
        wall_connectors = [
            ConnectorDefinition("conn_left", ConnectorType.WALL, [-1.0, 0.0, 1.5], [0.0, 0.0, -90.0], [0.2, 3.0]),
            ConnectorDefinition("conn_right", ConnectorType.WALL, [1.0, 0.0, 1.5], [0.0, 0.0, 90.0], [0.2, 3.0]),
            ConnectorDefinition("conn_bottom", ConnectorType.FLOOR, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [2.0, 0.2]),
            ConnectorDefinition("conn_top", ConnectorType.CEILING, [0.0, 0.0, 3.0], [0.0, 0.0, 0.0], [2.0, 0.2]),
        ]
        modules["Mod_Wall_2x3"] = ModuleDefinition(
            module_id="Mod_Wall_2x3",
            category=ModuleCategory.WALL,
            dimensions=[2.0, 0.2, 3.0],
            connectors=wall_connectors,
            mesh_data=MeshData.create_cube(size=2.0),
            semantic_tags=["structural", "blocking"],
        )

        # 3. Doorway 2x3m
        door_connectors = list(wall_connectors) + [
            ConnectorDefinition("conn_door_portal", ConnectorType.DOOR, [0.0, 0.0, 1.2], [0.0, 0.0, 0.0], [1.2, 2.4]),
        ]
        modules["Mod_Door_2x3"] = ModuleDefinition(
            module_id="Mod_Door_2x3",
            category=ModuleCategory.DOOR,
            dimensions=[2.0, 0.2, 3.0],
            connectors=door_connectors,
            mesh_data=MeshData.create_cube(size=2.0),
            semantic_tags=["structural", "portal", "navigable"],
        )

        # 4. Stair 2x3m (Connecting z=0 to z=3m)
        stair_connectors = [
            ConnectorDefinition("conn_stair_bottom", ConnectorType.FLOOR, [0.0, -1.0, 0.0], [0.0, 0.0, 0.0], [2.0, 0.2]),
            ConnectorDefinition("conn_stair_top", ConnectorType.FLOOR, [0.0, 1.0, 3.0], [0.0, 0.0, 0.0], [2.0, 0.2]),
        ]
        modules["Mod_Stair_2x3"] = ModuleDefinition(
            module_id="Mod_Stair_2x3",
            category=ModuleCategory.STAIR,
            dimensions=[2.0, 2.0, 3.0],
            connectors=stair_connectors,
            mesh_data=MeshData.create_cube(size=2.0),
            semantic_tags=["structural", "vertical_transition", "navigable"],
        )

        return cls(kit_id=kit_id, theme="SCI_FI_FACILITY", modules=modules)
