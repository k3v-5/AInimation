"""
ModularSemanticModel defines kits, grid snaps, modules, and connection compatibility.
UAF-81.1 Sections 40, 41.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class ConnectionSocket:
    socket_id: str
    socket_type: str  # e.g., "wall_edge", "floor_edge", "roof_mount"
    position: List[float]
    direction: List[float]
    compatible_types: List[str] = field(default_factory=list)

    def is_compatible_with(self, other: "ConnectionSocket") -> bool:
        return other.socket_type in self.compatible_types or self.socket_type in other.compatible_types


@dataclass
class ModularModule:
    module_id: str
    module_type: str  # wall, corner, door, window, floor, roof
    dimensions_meters: List[float]
    sockets: List[ConnectionSocket] = field(default_factory=list)
    variants: List[str] = field(default_factory=list)
    material_slots: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "module_id": self.module_id,
            "module_type": self.module_type,
            "dimensions_meters": self.dimensions_meters,
            "sockets": [s.__dict__ for s in self.sockets],
            "variants": self.variants,
            "material_slots": self.material_slots,
        }


@dataclass
class ModularKitSemanticModel:
    kit_name: str
    grid_size_meters: float = 1.0
    modules: Dict[str, ModularModule] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kit_name": self.kit_name,
            "grid_size_meters": self.grid_size_meters,
            "modules": {k: v.to_dict() for k, v in self.modules.items()},
        }
