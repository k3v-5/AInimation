"""
AssetAssemblyGraph and AssetLifecycleState models.
UAF-81.8 Sections 4, 14, 123, 124.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class AssetLifecycleState(str, Enum):
    DRAFT = "DRAFT"
    GENERATED = "GENERATED"
    VALIDATED = "VALIDATED"
    OPTIMIZED = "OPTIMIZED"
    PACKAGED = "PACKAGED"
    PUBLISHED = "PUBLISHED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


@dataclass
class AssetAssemblyGraph:
    asset_id: str
    render_components: List[str] = field(default_factory=list)
    material_slots: Dict[int, str] = field(default_factory=dict)  # slot_index -> material_id
    collision_shapes: List[str] = field(default_factory=list)
    physics_bodies: List[str] = field(default_factory=list)
    socket_ids: List[str] = field(default_factory=list)
    lifecycle_state: AssetLifecycleState = AssetLifecycleState.GENERATED
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def graph_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "render_components": self.render_components,
            "material_slots": {str(k): v for k, v in self.material_slots.items()},
            "collision_shapes": self.collision_shapes,
            "physics_bodies": self.physics_bodies,
            "socket_ids": self.socket_ids,
            "lifecycle_state": self.lifecycle_state.value,
            "metadata": self.metadata,
        }
