"""
SurfaceProductionFabricator manufactures UV layouts, calibrated PBR textures, master materials, instances, and variants.
UAF-81.18 Sections 220, 221, 222.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import SurfaceDefinition, MaterialPBRProfile, SurfaceWeatheringState
from ..models.textures import TextureChannelDefinition, TexturePackingType


class SurfaceProductionFabricator:
    """
    Synthesizes complete production-ready surfaces satisfying Section 220 final acceptance criteria.
    """

    @classmethod
    def fabricate_surface(
        cls,
        mesh_id: str,
        surface_def: SurfaceDefinition,
        material_profile: MaterialPBRProfile,
    ) -> Tuple[
        str,                           # uv_set_name
        List[TextureChannelDefinition],# textures
        str,                           # master_material_id
        str,                           # material_instance_id
        Dict[str, Dict[str, Any]],     # variants
    ]:
        """
        Synthesizes UV channel, complete PBR texture set (ALBEDO, NORMAL, ORM), master material, instance, and variants.
        """
        uv_set_name = f"{mesh_id}_UVChannel_0"
        prefix = f"T_{surface_def.surface_id}"
        res = surface_def.resolution

        # Complete PBR Texture Set with strict color space enforcement (Section 26, 27)
        textures = [
            TextureChannelDefinition(f"{prefix}_BC", "ALBEDO", "sRGB", res),
            TextureChannelDefinition(f"{prefix}_N", "NORMAL", "LINEAR", res),
            TextureChannelDefinition(f"{prefix}_ORM", "ORM", "LINEAR", res),
        ]

        if material_profile.emissive_hex:
            textures.append(TextureChannelDefinition(f"{prefix}_E", "EMISSIVE", "sRGB", res))

        master_material_id = f"M_Master_{surface_def.surface_type.capitalize()}PBR"
        material_instance_id = f"MI_{surface_def.surface_id}"

        # Weathering Variants (Section 201, 220)
        variants = {
            "CLEAN": {
                "roughness_multiplier": 1.0,
                "wear_intensity": 0.0,
                "tint": material_profile.base_color_hex,
            },
            "WORN": {
                "roughness_multiplier": 1.15,
                "wear_intensity": 0.45,
                "tint": material_profile.base_color_hex,
            },
            "DAMAGED": {
                "roughness_multiplier": 1.35,
                "wear_intensity": 0.85,
                "tint": "#706860",
            },
        }

        return uv_set_name, textures, master_material_id, material_instance_id, variants
