"""
World Partition, Streaming Cells, HLOD, and Data Layer models.
UAF-81.6 Sections 80, 81, 102.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class DataLayer(str, Enum):
    BASE = "BASE"
    GAMEPLAY = "GAMEPLAY"
    DECORATION = "DECORATION"
    DAMAGE = "DAMAGE"
    NIGHT = "NIGHT"
    MISSION = "MISSION"


@dataclass
class WorldPartitionCell:
    cell_id: str
    min_point: List[float]  # [x, y, z]
    max_point: List[float]  # [x, y, z]
    actor_instance_ids: List[str] = field(default_factory=list)
    hlod_level: int = 0
    is_spatially_loaded: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cell_id": self.cell_id,
            "min_point": self.min_point,
            "max_point": self.max_point,
            "actor_instance_ids": self.actor_instance_ids,
            "hlod_level": self.hlod_level,
            "is_spatially_loaded": self.is_spatially_loaded,
        }


@dataclass
class HLODMetadata:
    hlod_id: str
    cell_ids: List[str] = field(default_factory=list)
    draw_distance_meters: float = 150.0
    reduction_ratio: float = 0.25
    cluster_radius_meters: float = 32.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hlod_id": self.hlod_id,
            "cell_ids": self.cell_ids,
            "draw_distance_meters": self.draw_distance_meters,
            "reduction_ratio": self.reduction_ratio,
            "cluster_radius_meters": self.cluster_radius_meters,
        }
