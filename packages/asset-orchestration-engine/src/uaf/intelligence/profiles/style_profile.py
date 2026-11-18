"""
StyleProfile decouples visual language and aesthetic principles from functional asset archetypes.
UAF-81.1 Sections 27, 28.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass(frozen=True)
class StyleProfile:
    """
    Aesthetic language configuration governing surface shapes, colors, and proportions.
    """
    style_id: str
    visual_language: str = "realistic_scifi"
    shape_language: str = "angular_hard_surface"
    color_language: str = "monochromatic_muted"
    material_language: str = "military_spec_metals"
    detail_language: str = "functional_greebles"
    proportion_language: str = "heroic_humanoid"
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "style_id": self.style_id,
            "visual_language": self.visual_language,
            "shape_language": self.shape_language,
            "color_language": self.color_language,
            "material_language": self.material_language,
            "detail_language": self.detail_language,
            "proportion_language": self.proportion_language,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StyleProfile":
        return cls(
            style_id=data["style_id"],
            visual_language=data.get("visual_language", "realistic_scifi"),
            shape_language=data.get("shape_language", "angular_hard_surface"),
            color_language=data.get("color_language", "monochromatic_muted"),
            material_language=data.get("material_language", "military_spec_metals"),
            detail_language=data.get("detail_language", "functional_greebles"),
            proportion_language=data.get("proportion_language", "heroic_humanoid"),
            tags=data.get("tags", []),
        )
