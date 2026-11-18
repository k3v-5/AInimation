"""
UniversalSurfaceFabricationPlatform manufactures canonical Golden Materials matching Section 143.
UAF-81.52 Sections 143, 147, 150.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import (
    UniversalSurfaceSpecification,
    SurfaceType52,
    PBRSurfaceProperties52,
    TextureResolution52,
)


class UniversalSurfaceFabricationPlatform:
    """
    Synthesizes complete, production-grade universal PBR materials, textures, and material instances for Unreal Engine.
    """

    @classmethod
    def build_golden_metal(cls, surf_id: str = "Surf_Gold_Metal52") -> Tuple[UniversalSurfaceSpecification, str, str, str]:
        """1. GOLDEN_METAL (Section 143: metallic=1.0, roughness=0.25, industrial steel/aluminum)."""
        props = PBRSurfaceProperties52(base_color_rgb=(0.8, 0.8, 0.85), metallic=1.0, roughness=0.25, specular=0.5, opacity=1.0)
        spec = UniversalSurfaceSpecification(surf_id, SurfaceType52.METAL, props)
        return (
            spec,
            f"/Game/Materials/Universal/Master/M_{surf_id}",
            f"/Game/Materials/Universal/Instances/MI_{surf_id}",
            f"/Game/Materials/Universal/Textures/T_{surf_id}",
        )

    @classmethod
    def build_golden_wood(cls, surf_id: str = "Surf_Gold_Wood52") -> Tuple[UniversalSurfaceSpecification, str, str, str]:
        """2. GOLDEN_WOOD (Section 143: metallic=0.0, roughness=0.65, varnished oak/grain)."""
        props = PBRSurfaceProperties52(base_color_rgb=(0.55, 0.35, 0.2), metallic=0.0, roughness=0.65, specular=0.4, opacity=1.0)
        spec = UniversalSurfaceSpecification(surf_id, SurfaceType52.WOOD, props)
        return (
            spec,
            f"/Game/Materials/Universal/Master/M_{surf_id}",
            f"/Game/Materials/Universal/Instances/MI_{surf_id}",
            f"/Game/Materials/Universal/Textures/T_{surf_id}",
        )

    @classmethod
    def build_golden_stone(cls, surf_id: str = "Surf_Gold_Stone52") -> Tuple[UniversalSurfaceSpecification, str, str, str]:
        """3. GOLDEN_STONE (Section 143: metallic=0.0, roughness=0.85, carved granite/slate)."""
        props = PBRSurfaceProperties52(base_color_rgb=(0.45, 0.45, 0.45), metallic=0.0, roughness=0.85, specular=0.3, opacity=1.0)
        spec = UniversalSurfaceSpecification(surf_id, SurfaceType52.STONE, props)
        return (
            spec,
            f"/Game/Materials/Universal/Master/M_{surf_id}",
            f"/Game/Materials/Universal/Instances/MI_{surf_id}",
            f"/Game/Materials/Universal/Textures/T_{surf_id}",
        )

    @classmethod
    def build_golden_concrete(cls, surf_id: str = "Surf_Gold_Concrete52") -> Tuple[UniversalSurfaceSpecification, str, str, str]:
        """4. GOLDEN_CONCRETE (Section 143: metallic=0.0, roughness=0.90, porous architectural concrete)."""
        props = PBRSurfaceProperties52(base_color_rgb=(0.6, 0.6, 0.58), metallic=0.0, roughness=0.90, specular=0.25, opacity=1.0)
        spec = UniversalSurfaceSpecification(surf_id, SurfaceType52.CONCRETE, props)
        return (
            spec,
            f"/Game/Materials/Universal/Master/M_{surf_id}",
            f"/Game/Materials/Universal/Instances/MI_{surf_id}",
            f"/Game/Materials/Universal/Textures/T_{surf_id}",
        )

    @classmethod
    def build_golden_fabric(cls, surf_id: str = "Surf_Gold_Fabric52") -> Tuple[UniversalSurfaceSpecification, str, str, str]:
        """5. GOLDEN_FABRIC (Section 143: metallic=0.0, roughness=0.80, woven cloth/canvas)."""
        props = PBRSurfaceProperties52(base_color_rgb=(0.25, 0.35, 0.5), metallic=0.0, roughness=0.80, specular=0.2, opacity=1.0)
        spec = UniversalSurfaceSpecification(surf_id, SurfaceType52.FABRIC, props)
        return (
            spec,
            f"/Game/Materials/Universal/Master/M_{surf_id}",
            f"/Game/Materials/Universal/Instances/MI_{surf_id}",
            f"/Game/Materials/Universal/Textures/T_{surf_id}",
        )

    @classmethod
    def build_golden_glass(cls, surf_id: str = "Surf_Gold_Glass52") -> Tuple[UniversalSurfaceSpecification, str, str, str]:
        """6. GOLDEN_GLASS (Section 143: metallic=0.0, roughness=0.05, opacity=0.15, refractive glass)."""
        props = PBRSurfaceProperties52(base_color_rgb=(0.95, 0.98, 1.0), metallic=0.0, roughness=0.05, specular=0.95, opacity=0.15)
        spec = UniversalSurfaceSpecification(surf_id, SurfaceType52.GLASS, props)
        return (
            spec,
            f"/Game/Materials/Universal/Master/M_{surf_id}",
            f"/Game/Materials/Universal/Instances/MI_{surf_id}",
            f"/Game/Materials/Universal/Textures/T_{surf_id}",
        )

    @classmethod
    def build_golden_leather(cls, surf_id: str = "Surf_Gold_Leather52") -> Tuple[UniversalSurfaceSpecification, str, str, str]:
        """7. GOLDEN_LEATHER (Section 143: metallic=0.0, roughness=0.45, treated cowhide/seams)."""
        props = PBRSurfaceProperties52(base_color_rgb=(0.35, 0.22, 0.12), metallic=0.0, roughness=0.45, specular=0.4, opacity=1.0)
        spec = UniversalSurfaceSpecification(surf_id, SurfaceType52.LEATHER, props)
        return (
            spec,
            f"/Game/Materials/Universal/Master/M_{surf_id}",
            f"/Game/Materials/Universal/Instances/MI_{surf_id}",
            f"/Game/Materials/Universal/Textures/T_{surf_id}",
        )

    @classmethod
    def build_golden_terrain(cls, surf_id: str = "Surf_Gold_Terrain52") -> Tuple[UniversalSurfaceSpecification, str, str, str]:
        """8. GOLDEN_TERRAIN (Section 143: metallic=0.0, roughness=0.95, dirt/rock landscape blend)."""
        props = PBRSurfaceProperties52(base_color_rgb=(0.4, 0.32, 0.22), metallic=0.0, roughness=0.95, specular=0.2, opacity=1.0)
        spec = UniversalSurfaceSpecification(surf_id, SurfaceType52.TERRAIN if hasattr(SurfaceType52, "TERRAIN") else SurfaceType52.SOIL, props)
        return (
            spec,
            f"/Game/Materials/Universal/Master/M_{surf_id}",
            f"/Game/Materials/Universal/Instances/MI_{surf_id}",
            f"/Game/Materials/Universal/Textures/T_{surf_id}",
        )

    @classmethod
    def build_golden_vegetation(cls, surf_id: str = "Surf_Gold_Vegetation52") -> Tuple[UniversalSurfaceSpecification, str, str, str]:
        """9. GOLDEN_VEGETATION (Section 143: metallic=0.0, roughness=0.50, subsurface leafy foliage)."""
        props = PBRSurfaceProperties52(base_color_rgb=(0.15, 0.5, 0.1), metallic=0.0, roughness=0.50, specular=0.3, opacity=1.0)
        spec = UniversalSurfaceSpecification(surf_id, SurfaceType52.FOLIAGE, props)
        return (
            spec,
            f"/Game/Materials/Universal/Master/M_{surf_id}",
            f"/Game/Materials/Universal/Instances/MI_{surf_id}",
            f"/Game/Materials/Universal/Textures/T_{surf_id}",
        )

    @classmethod
    def build_golden_water(cls, surf_id: str = "Surf_Gold_Water52") -> Tuple[UniversalSurfaceSpecification, str, str, str]:
        """10. GOLDEN_WATER (Section 143: metallic=0.0, roughness=0.02, opacity=0.30, aquatic refraction)."""
        props = PBRSurfaceProperties52(base_color_rgb=(0.1, 0.3, 0.45), metallic=0.0, roughness=0.02, specular=0.8, opacity=0.30)
        spec = UniversalSurfaceSpecification(surf_id, SurfaceType52.WATER, props)
        return (
            spec,
            f"/Game/Materials/Universal/Master/M_{surf_id}",
            f"/Game/Materials/Universal/Instances/MI_{surf_id}",
            f"/Game/Materials/Universal/Textures/T_{surf_id}",
        )
