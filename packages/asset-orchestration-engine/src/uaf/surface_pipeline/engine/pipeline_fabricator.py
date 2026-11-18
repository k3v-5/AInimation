"""
SurfacePipelineFabricationPlatform manufactures production-ready surface sets for Section 130-133 canonical scenarios.
UAF-81.27 Sections 130, 131, 132, 133.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import (
    SurfaceDefinition27,
    SurfaceClass27,
    UVStrategyType,
    TextureMapDefinition,
    ColorSpace27,
)


class SurfacePipelineFabricationPlatform:
    """
    Synthesizes complete UV sets, PBR textures, procedural masks, and material instances.
    """

    @classmethod
    def build_character_surface(cls, asset_id: str = "Char_Hero_Surface") -> Tuple[SurfaceDefinition27, str, str]:
        """1. CHARACTER SURFACE (Section 130: UDIM / seam-based UVs, skin subsurface, multi-layer clothing)."""
        textures = [
            TextureMapDefinition(f"T_{asset_id}_BC", "BASE_COLOR", 2048, ColorSpace27.SRGB),
            TextureMapDefinition(f"T_{asset_id}_N", "NORMAL", 2048, ColorSpace27.NORMAL_MAP),
            TextureMapDefinition(f"T_{asset_id}_ORM", "ORM", 2048, ColorSpace27.LINEAR),
            TextureMapDefinition(f"T_{asset_id}_SSSMask", "MASK", 2048, ColorSpace27.MASK),
        ]
        s_def = SurfaceDefinition27(
            surface_id=f"Surf_{asset_id}",
            asset_id=asset_id,
            surface_class=SurfaceClass27.SKIN,
            uv_strategy=UVStrategyType.UDIM,
            texel_density=20.48,
            textures=textures,
        )
        return s_def, "M_Master_SubsurfaceHero", f"MI_{asset_id}"

    @classmethod
    def build_weapon_surface(cls, asset_id: str = "Wpn_Rifle_Surface") -> Tuple[SurfaceDefinition27, str, str]:
        """2. WEAPON SURFACE (Section 131: metal body, paint wear, rubber grip, glass optics, decals)."""
        textures = [
            TextureMapDefinition(f"T_{asset_id}_BC", "BASE_COLOR", 2048, ColorSpace27.SRGB),
            TextureMapDefinition(f"T_{asset_id}_N", "NORMAL", 2048, ColorSpace27.NORMAL_MAP),
            TextureMapDefinition(f"T_{asset_id}_ORM", "ORM", 2048, ColorSpace27.LINEAR),
            TextureMapDefinition(f"T_{asset_id}_Emissive", "EMISSIVE", 1024, ColorSpace27.SRGB),
        ]
        s_def = SurfaceDefinition27(
            surface_id=f"Surf_{asset_id}",
            asset_id=asset_id,
            surface_class=SurfaceClass27.PAINTED_METAL,
            uv_strategy=UVStrategyType.SEAM_BASED,
            texel_density=20.48,
            textures=textures,
        )
        return s_def, "M_Master_HardSurfaceWeapon", f"MI_{asset_id}"

    @classmethod
    def build_environment_surface(cls, asset_id: str = "Env_Facility_Surface") -> Tuple[SurfaceDefinition27, str, str]:
        """3. ENVIRONMENT SURFACE (Section 132: concrete, metal trim, dirt procedural masks, tileables)."""
        textures = [
            TextureMapDefinition(f"T_{asset_id}_BC", "BASE_COLOR", 2048, ColorSpace27.SRGB),
            TextureMapDefinition(f"T_{asset_id}_N", "NORMAL", 2048, ColorSpace27.NORMAL_MAP),
            TextureMapDefinition(f"T_{asset_id}_ORM", "ORM", 2048, ColorSpace27.LINEAR),
            TextureMapDefinition(f"T_{asset_id}_DirtMask", "MASK", 1024, ColorSpace27.MASK),
        ]
        s_def = SurfaceDefinition27(
            surface_id=f"Surf_{asset_id}",
            asset_id=asset_id,
            surface_class=SurfaceClass27.CONCRETE,
            uv_strategy=UVStrategyType.BOX,
            texel_density=10.24,
            textures=textures,
        )
        return s_def, "M_Master_WorldSurfaceBlend", f"MI_{asset_id}"

    @classmethod
    def build_modular_kit_surface(cls, asset_id: str = "Kit_SciFiCorridor_Surface") -> Tuple[SurfaceDefinition27, str, str]:
        """4. MODULAR KIT SURFACE (Section 133: shared trim sheets, atlases, zero duplication)."""
        textures = [
            TextureMapDefinition(f"TRIM_{asset_id}_BC", "BASE_COLOR", 4096, ColorSpace27.SRGB),
            TextureMapDefinition(f"TRIM_{asset_id}_N", "NORMAL", 4096, ColorSpace27.NORMAL_MAP),
            TextureMapDefinition(f"TRIM_{asset_id}_ORM", "ORM", 4096, ColorSpace27.LINEAR),
        ]
        s_def = SurfaceDefinition27(
            surface_id=f"Surf_{asset_id}",
            asset_id=asset_id,
            surface_class=SurfaceClass27.METAL,
            uv_strategy=UVStrategyType.TRIM,
            texel_density=10.24,
            textures=textures,
        )
        return s_def, "M_Master_TrimSheet", f"MI_{asset_id}"
