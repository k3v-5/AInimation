"""
MaterialInstance represents parameter-specialized lightweight instances of a master material.
UAF-81.4 Sections 40, 41, 42, 43.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class MaterialInstance:
    instance_id: str
    parent_material_id: str
    scalar_parameters: Dict[str, float] = field(default_factory=dict)
    vector_parameters: Dict[str, List[float]] = field(default_factory=dict)
    texture_parameters: Dict[str, str] = field(default_factory=dict)
    static_switch_parameters: Dict[str, bool] = field(default_factory=dict)

    @property
    def instance_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "parent_material_id": self.parent_material_id,
            "scalar_parameters": self.scalar_parameters,
            "vector_parameters": self.vector_parameters,
            "texture_parameters": self.texture_parameters,
            "static_switch_parameters": self.static_switch_parameters,
        }
