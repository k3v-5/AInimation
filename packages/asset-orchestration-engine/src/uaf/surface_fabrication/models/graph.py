"""
MaterialParameterType and MaterialGraphContract models.
UAF-81.15 Sections 9, 10, 11, 24, 25.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ...core.hashing.canonical_hasher import CanonicalHasher


class MaterialParameterType(str, Enum):
    STATIC = "STATIC"
    DYNAMIC = "DYNAMIC"
    INSTANCE = "INSTANCE"
    GLOBAL = "GLOBAL"


@dataclass
class MaterialGraphContract:
    graph_id: str
    master_material_id: str = "M_Master_Surface"
    parameters: Dict[str, Any] = field(default_factory=dict)
    material_functions: List[str] = field(default_factory=lambda: ["DetailBlend", "NormalBlend"])
    has_triplanar: bool = False

    @property
    def contract_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "master_material_id": self.master_material_id,
            "parameters": self.parameters,
            "material_functions": self.material_functions,
            "has_triplanar": self.has_triplanar,
        }
