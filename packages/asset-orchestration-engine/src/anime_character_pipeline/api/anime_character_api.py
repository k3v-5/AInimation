"""
Anime Character Pipeline API Facade
===================================
Unified interface for creating, configuring, and exporting production-ready
anime 3D characters within the Asset Orchestration Engine (AOE).
"""

from typing import Dict, Any, List, Optional
from ..core.anime_types import (
    AnimeProportionsPreset,
    AnimeEyeStyle,
    AnimeHairStyle,
    NPROutlineMode,
    AnimeShadingModel
)
from ..core.anime_schema import (
    AnimeCharacterSpec,
    AnimeHeadTopologySpec,
    AnimeBodyTopologySpec,
    NPROutlineSpec,
    AnimeCharacterBuildResult
)
from ..generators.organic_body_generator import OrganicBodyGenerator
from ..generators.bezier_hair_generator import BezierHairGenerator
from ..generators.npr_shading_generator import NPRShadingGenerator
from ..generators.inverted_hull_outlines import InvertedHullOutlines
from ..generators.tactical_props_generator import TacticalPropsGenerator


class AnimeCharacterAPI:
    """Public facade for generating authentic anime characters."""

    def __init__(self):
        pass

    def validate_spec(self, spec: AnimeCharacterSpec) -> List[str]:
        """Validates character specifications against physical and visual invariants."""
        issues = []
        if not spec.character_id:
            issues.append("Character ID cannot be empty.")
        if spec.body_spec.total_height <= 0.5 or spec.body_spec.total_height > 2.5:
            issues.append(f"Invalid height {spec.body_spec.total_height}m (must be between 0.5m and 2.5m).")
        if spec.head_spec.chin_sharpness < 0.0 or spec.head_spec.chin_sharpness > 1.0:
            issues.append("Chin sharpness must be normalized between 0.0 and 1.0.")
        if spec.outline_spec.thickness < 0.0005 or spec.outline_spec.thickness > 0.02:
            issues.append(f"Outline thickness {spec.outline_spec.thickness}m out of reasonable range (0.5mm to 20mm).")
        return issues

    def build_character_plan(self, spec: AnimeCharacterSpec) -> Dict[str, Any]:
        """Plans the execution pipeline for character construction."""
        validation_issues = self.validate_spec(spec)
        if validation_issues:
            raise ValueError(f"Specification validation failed: {validation_issues}")

        body_gen = OrganicBodyGenerator(spec.head_spec, spec.body_spec)
        hair_gen = BezierHairGenerator(spec.hair_style.value)
        shading_gen = NPRShadingGenerator(spec.shading_model)
        outline_gen = InvertedHullOutlines(spec.outline_spec)

        head_rings = body_gen.compute_head_profile_rings()
        torso_rings = body_gen.compute_torso_profile_rings()
        hair_strands = hair_gen.generate_hair_strands()
        outline_params = outline_gen.compute_modifier_parameters()

        return {
            "character_id": spec.character_id,
            "character_name": spec.character_name,
            "proportions_preset": spec.proportions_preset.value,
            "head_rings_count": len(head_rings),
            "torso_rings_count": len(torso_rings),
            "hair_strands_count": len(hair_strands),
            "outline_enabled": spec.outline_spec.mode == NPROutlineMode.INVERTED_HULL_SOLIDIFY,
            "outline_thickness": spec.outline_spec.thickness,
            "shading_model": spec.shading_model.value,
            "tactical_props_enabled": spec.include_tactical_katana,
            "status": "READY_FOR_BLENDER_ORCHESTRATION"
        }
