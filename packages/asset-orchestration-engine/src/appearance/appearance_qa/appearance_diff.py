from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class AppearanceDiff:
    material_changes: List[Dict[str, Any]] = field(default_factory=list)
    texture_changes: List[Dict[str, Any]] = field(default_factory=list)
    uv_changes: List[Dict[str, Any]] = field(default_factory=list)
    geometry_changes: List[Dict[str, Any]] = field(default_factory=list) # Strictly empty by default

    def to_dict(self) -> Dict[str, Any]:
        return {
            "material_changes": self.material_changes,
            "texture_changes": self.texture_changes,
            "uv_changes": self.uv_changes,
            "geometry_changes": self.geometry_changes
        }
