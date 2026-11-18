"""
PBRSurfaceFabricationPlatform manufactures canonical Golden Materials matching Section 149.
UAF-81.43 Sections 149, 166, 178.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import (
    PBRSurfaceSpecification,
    MaterialCategory43,
    UVStrategy43,
    TexelDensityProfile43,
    PBRProperties43,
)


class PBRSurfaceFabricationPlatform:
    """
    Synthesizes complete, production-grade PBR materials, textures, and instances for Unreal Engine.
    """

    @classmethod
    def build_golden_skin(cls, mat_id: str = "Mat_Gold_Skin") -> Tuple[PBRSurfaceSpecification, str, str, str]:
        """1. GOLDEN_SKIN (Section 149: subsurface skin PBR, rough=0.45, met=0.0)."""
        pbr = PBRProperties43(base_color_rgb=(0.85, 0.65, 0.55), metallic=0.0, roughness=0.45, emissive_intensity=0.0, resolution=2048)
        spec = PBRSurfaceSpecification(mat_id, MaterialCategory43.SKIN, UVStrategy43.CONFORMAL, TexelDensityProfile43.HERO, pbr)
        return (
            spec,
            f"/Game/Materials/Masters/M_{mat_id}",
            f"/Game/Materials/Instances/MI_{mat_id}",
            f"/Game/Textures/Sets/T_{mat_id}",
        )

    @classmethod
    def build_golden_metal(cls, mat_id: str = "Mat_Gold_Metal") -> Tuple[PBRSurfaceSpecification, str, str, str]:
        """2. GOLDEN_METAL (Section 149: raw conductive metal, rough=0.20, met=1.0)."""
        pbr = PBRProperties43(base_color_rgb=(0.95, 0.95, 0.95), metallic=1.0, roughness=0.20, emissive_intensity=0.0, resolution=2048)
        spec = PBRSurfaceSpecification(mat_id, MaterialCategory43.METAL, UVStrategy43.SMART_PROJECT, TexelDensityProfile43.HIGH, pbr)
        return (
            spec,
            f"/Game/Materials/Masters/M_{mat_id}",
            f"/Game/Materials/Instances/MI_{mat_id}",
            f"/Game/Textures/Sets/T_{mat_id}",
        )

    @classmethod
    def build_golden_painted_metal(cls, mat_id: str = "Mat_Gold_PaintedMetal") -> Tuple[PBRSurfaceSpecification, str, str, str]:
        """3. GOLDEN_PAINTED_METAL (Section 149: coated metal, wear masks, rough=0.35, met=0.1)."""
        pbr = PBRProperties43(base_color_rgb=(0.2, 0.4, 0.8), metallic=0.1, roughness=0.35, emissive_intensity=0.0, resolution=2048)
        spec = PBRSurfaceSpecification(mat_id, MaterialCategory43.PAINTED_METAL, UVStrategy43.SMART_PROJECT, TexelDensityProfile43.HIGH, pbr)
        return (
            spec,
            f"/Game/Materials/Masters/M_{mat_id}",
            f"/Game/Materials/Instances/MI_{mat_id}",
            f"/Game/Textures/Sets/T_{mat_id}",
        )

    @classmethod
    def build_golden_fabric(cls, mat_id: str = "Mat_Gold_Fabric") -> Tuple[PBRSurfaceSpecification, str, str, str]:
        """4. GOLDEN_FABRIC (Section 149: woven cloth weave, rough=0.85, met=0.0)."""
        pbr = PBRProperties43(base_color_rgb=(0.3, 0.35, 0.4), metallic=0.0, roughness=0.85, emissive_intensity=0.0, resolution=2048)
        spec = PBRSurfaceSpecification(mat_id, MaterialCategory43.FABRIC, UVStrategy43.TRIM_SHEET, TexelDensityProfile43.HIGH, pbr)
        return (
            spec,
            f"/Game/Materials/Masters/M_{mat_id}",
            f"/Game/Materials/Instances/MI_{mat_id}",
            f"/Game/Textures/Sets/T_{mat_id}",
        )

    @classmethod
    def build_golden_leather(cls, mat_id: str = "Mat_Gold_Leather") -> Tuple[PBRSurfaceSpecification, str, str, str]:
        """5. GOLDEN_LEATHER (Section 149: organic grain leather, rough=0.55, met=0.0)."""
        pbr = PBRProperties43(base_color_rgb=(0.4, 0.25, 0.15), metallic=0.0, roughness=0.55, emissive_intensity=0.0, resolution=2048)
        spec = PBRSurfaceSpecification(mat_id, MaterialCategory43.LEATHER, UVStrategy43.CONFORMAL, TexelDensityProfile43.HIGH, pbr)
        return (
            spec,
            f"/Game/Materials/Masters/M_{mat_id}",
            f"/Game/Materials/Instances/MI_{mat_id}",
            f"/Game/Textures/Sets/T_{mat_id}",
        )

    @classmethod
    def build_golden_concrete(cls, mat_id: str = "Mat_Gold_Concrete") -> Tuple[PBRSurfaceSpecification, str, str, str]:
        """6. GOLDEN_CONCRETE (Section 149: rough mineral stone/aggregate, rough=0.80, met=0.0)."""
        pbr = PBRProperties43(base_color_rgb=(0.6, 0.6, 0.6), metallic=0.0, roughness=0.80, emissive_intensity=0.0, resolution=2048)
        spec = PBRSurfaceSpecification(mat_id, MaterialCategory43.CONCRETE, UVStrategy43.CUBIC, TexelDensityProfile43.MEDIUM, pbr)
        return (
            spec,
            f"/Game/Materials/Masters/M_{mat_id}",
            f"/Game/Materials/Instances/MI_{mat_id}",
            f"/Game/Textures/Sets/T_{mat_id}",
        )

    @classmethod
    def build_golden_glass(cls, mat_id: str = "Mat_Gold_Glass") -> Tuple[PBRSurfaceSpecification, str, str, str]:
        """7. GOLDEN_GLASS (Section 149: transmissive refractive surface, rough=0.05, met=0.0)."""
        pbr = PBRProperties43(base_color_rgb=(0.95, 0.98, 1.0), metallic=0.0, roughness=0.05, emissive_intensity=0.0, resolution=1024)
        spec = PBRSurfaceSpecification(mat_id, MaterialCategory43.GLASS, UVStrategy43.PLANAR, TexelDensityProfile43.HIGH, pbr)
        return (
            spec,
            f"/Game/Materials/Masters/M_{mat_id}",
            f"/Game/Materials/Instances/MI_{mat_id}",
            f"/Game/Textures/Sets/T_{mat_id}",
        )

    @classmethod
    def build_golden_organic(cls, mat_id: str = "Mat_Gold_Organic") -> Tuple[PBRSurfaceSpecification, str, str, str]:
        """8. GOLDEN_ORGANIC (Section 149: chitin/carapace/vegetation, rough=0.50, met=0.0)."""
        pbr = PBRProperties43(base_color_rgb=(0.2, 0.5, 0.2), metallic=0.0, roughness=0.50, emissive_intensity=0.0, resolution=2048)
        spec = PBRSurfaceSpecification(mat_id, MaterialCategory43.ORGANIC, UVStrategy43.CONFORMAL, TexelDensityProfile43.HIGH, pbr)
        return (
            spec,
            f"/Game/Materials/Masters/M_{mat_id}",
            f"/Game/Materials/Instances/MI_{mat_id}",
            f"/Game/Textures/Sets/T_{mat_id}",
        )

    @classmethod
    def build_golden_emissive(cls, mat_id: str = "Mat_Gold_Emissive") -> Tuple[PBRSurfaceSpecification, str, str, str]:
        """9. GOLDEN_EMISSIVE (Section 149: glowing neon/plasma display, emissive=5.0)."""
        pbr = PBRProperties43(base_color_rgb=(0.1, 0.8, 1.0), metallic=0.0, roughness=0.15, emissive_intensity=5.0, resolution=1024)
        spec = PBRSurfaceSpecification(mat_id, MaterialCategory43.EMISSIVE, UVStrategy43.PLANAR, TexelDensityProfile43.HIGH, pbr)
        return (
            spec,
            f"/Game/Materials/Masters/M_{mat_id}",
            f"/Game/Materials/Instances/MI_{mat_id}",
            f"/Game/Textures/Sets/T_{mat_id}",
        )

    @classmethod
    def build_golden_technical(cls, mat_id: str = "Mat_Gold_Technical") -> Tuple[PBRSurfaceSpecification, str, str, str]:
        """10. GOLDEN_TECHNICAL (Section 149: composite carbon fiber/silicon, rough=0.30, met=0.4)."""
        pbr = PBRProperties43(base_color_rgb=(0.15, 0.15, 0.18), metallic=0.4, roughness=0.30, emissive_intensity=0.0, resolution=2048)
        spec = PBRSurfaceSpecification(mat_id, MaterialCategory43.TECHNICAL, UVStrategy43.SMART_PROJECT, TexelDensityProfile43.HIGH, pbr)
        return (
            spec,
            f"/Game/Materials/Masters/M_{mat_id}",
            f"/Game/Materials/Instances/MI_{mat_id}",
            f"/Game/Textures/Sets/T_{mat_id}",
        )
