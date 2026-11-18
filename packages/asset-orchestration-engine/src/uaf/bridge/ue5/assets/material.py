"""Material and Material Instance bridge for parameter synchronization."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MaterialBridgePayload:
    asset_id: str
    semantic_name: str
    is_instance: bool = True
    parent_material_path: Optional[str] = "/Game/UAF/Materials/M_MasterDefault"
    scalar_parameters: Dict[str, float] = field(default_factory=dict)
    vector_parameters: Dict[str, List[float]] = field(default_factory=dict)
    texture_parameters: Dict[str, str] = field(default_factory=dict)
    blend_mode: str = "BLEND_Opaque"
    shading_model: str = "MSM_DefaultLit"
    two_sided: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "semantic_name": self.semantic_name,
            "is_instance": self.is_instance,
            "parent_material_path": self.parent_material_path,
            "scalar_parameters": self.scalar_parameters,
            "vector_parameters": self.vector_parameters,
            "texture_parameters": self.texture_parameters,
            "blend_mode": self.blend_mode,
            "shading_model": self.shading_model,
            "two_sided": self.two_sided,
        }
