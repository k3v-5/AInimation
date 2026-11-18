"""
MaterialSemanticModel defines PBR channels and hierarchical semantic layers.
UAF-81.1 Sections 37, 38.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class MaterialLayer:
    name: str
    layer_type: str  # e.g., "base", "wear", "damage", "dirt", "emission"
    blend_mode: str = "mix"
    opacity: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "layer_type": self.layer_type,
            "blend_mode": self.blend_mode,
            "opacity": self.opacity,
            "properties": self.properties,
        }


@dataclass
class MaterialSemanticModel:
    material_name: str
    base_color: str = "#808080"
    metallic: float = 0.0
    roughness: float = 0.5
    specular: float = 0.5
    subsurface: float = 0.0
    clearcoat: float = 0.0
    anisotropy: float = 0.0
    layers: List[MaterialLayer] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "material_name": self.material_name,
            "base_color": self.base_color,
            "metallic": self.metallic,
            "roughness": self.roughness,
            "specular": self.specular,
            "subsurface": self.subsurface,
            "clearcoat": self.clearcoat,
            "anisotropy": self.anisotropy,
            "layers": [layer.to_dict() for layer in self.layers],
        }
