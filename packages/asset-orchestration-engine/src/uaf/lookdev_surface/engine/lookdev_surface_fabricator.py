"""
LookdevSurfaceFabricationPlatform manufactures canonical Golden Surfaces matching Section 114.
UAF-81.46 Sections 114, 124, 125.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import (
    LookdevSurfaceSpecification,
    MaterialFamily46,
    LookdevQualityTier46,
    SurfacePBRProperties46,
)


class LookdevSurfaceFabricationPlatform:
    """
    Synthesizes complete, production-grade look-development surfaces, master shaders, and instances for Unreal Engine.
    """

    @classmethod
    def build_golden_skin(cls, surf_id: str = "Surf_Gold_Skin") -> Tuple[LookdevSurfaceSpecification, str, str, str]:
        """1. GOLDEN_SKIN (Section 114: subsurface skin lookdev, rough=0.45, met=0.0)."""
        pbr = SurfacePBRProperties46(base_color_rgb=(0.86, 0.67, 0.58), metallic=0.0, roughness=0.45, ao=1.0, emission=0.0, resolution=2048)
        spec = LookdevSurfaceSpecification(surf_id, MaterialFamily46.SKIN, LookdevQualityTier46.HERO, pbr)
        return (
            spec,
            f"/Game/Lookdev/Materials/M_{surf_id}",
            f"/Game/Lookdev/Instances/MI_{surf_id}",
            f"/Game/Lookdev/Textures/T_{surf_id}",
        )

    @classmethod
    def build_golden_metal(cls, surf_id: str = "Surf_Gold_Metal") -> Tuple[LookdevSurfaceSpecification, str, str, str]:
        """2. GOLDEN_METAL (Section 114: polished conductive alloy, rough=0.18, met=1.0)."""
        pbr = SurfacePBRProperties46(base_color_rgb=(0.96, 0.96, 0.96), metallic=1.0, roughness=0.18, ao=1.0, emission=0.0, resolution=2048)
        spec = LookdevSurfaceSpecification(surf_id, MaterialFamily46.METAL, LookdevQualityTier46.HIGH, pbr)
        return (
            spec,
            f"/Game/Lookdev/Materials/M_{surf_id}",
            f"/Game/Lookdev/Instances/MI_{surf_id}",
            f"/Game/Lookdev/Textures/T_{surf_id}",
        )

    @classmethod
    def build_golden_fabric(cls, surf_id: str = "Surf_Gold_Fabric") -> Tuple[LookdevSurfaceSpecification, str, str, str]:
        """3. GOLDEN_FABRIC (Section 114: woven micro-fiber fabric, rough=0.88, met=0.0)."""
        pbr = SurfacePBRProperties46(base_color_rgb=(0.25, 0.30, 0.45), metallic=0.0, roughness=0.88, ao=1.0, emission=0.0, resolution=2048)
        spec = LookdevSurfaceSpecification(surf_id, MaterialFamily46.FABRIC, LookdevQualityTier46.HIGH, pbr)
        return (
            spec,
            f"/Game/Lookdev/Materials/M_{surf_id}",
            f"/Game/Lookdev/Instances/MI_{surf_id}",
            f"/Game/Lookdev/Textures/T_{surf_id}",
        )

    @classmethod
    def build_golden_wood(cls, surf_id: str = "Surf_Gold_Wood") -> Tuple[LookdevSurfaceSpecification, str, str, str]:
        """4. GOLDEN_WOOD (Section 114: organic grain varnished timber, rough=0.40, met=0.0)."""
        pbr = SurfacePBRProperties46(base_color_rgb=(0.45, 0.28, 0.16), metallic=0.0, roughness=0.40, ao=1.0, emission=0.0, resolution=2048)
        spec = LookdevSurfaceSpecification(surf_id, MaterialFamily46.WOOD, LookdevQualityTier46.HIGH, pbr)
        return (
            spec,
            f"/Game/Lookdev/Materials/M_{surf_id}",
            f"/Game/Lookdev/Instances/MI_{surf_id}",
            f"/Game/Lookdev/Textures/T_{surf_id}",
        )

    @classmethod
    def build_golden_concrete(cls, surf_id: str = "Surf_Gold_Concrete") -> Tuple[LookdevSurfaceSpecification, str, str, str]:
        """5. GOLDEN_CONCRETE (Section 114: aggregate architectural concrete, rough=0.82, met=0.0)."""
        pbr = SurfacePBRProperties46(base_color_rgb=(0.62, 0.62, 0.62), metallic=0.0, roughness=0.82, ao=1.0, emission=0.0, resolution=2048)
        spec = LookdevSurfaceSpecification(surf_id, MaterialFamily46.CONCRETE, LookdevQualityTier46.MEDIUM, pbr)
        return (
            spec,
            f"/Game/Lookdev/Materials/M_{surf_id}",
            f"/Game/Lookdev/Instances/MI_{surf_id}",
            f"/Game/Lookdev/Textures/T_{surf_id}",
        )

    @classmethod
    def build_golden_glass(cls, surf_id: str = "Surf_Gold_Glass") -> Tuple[LookdevSurfaceSpecification, str, str, str]:
        """6. GOLDEN_GLASS (Section 114: dielectric specular glass, rough=0.04, met=0.0)."""
        pbr = SurfacePBRProperties46(base_color_rgb=(0.95, 0.98, 1.0), metallic=0.0, roughness=0.04, ao=1.0, emission=0.0, resolution=1024)
        spec = LookdevSurfaceSpecification(surf_id, MaterialFamily46.GLASS, LookdevQualityTier46.HERO, pbr)
        return (
            spec,
            f"/Game/Lookdev/Materials/M_{surf_id}",
            f"/Game/Lookdev/Instances/MI_{surf_id}",
            f"/Game/Lookdev/Textures/T_{surf_id}",
        )

    @classmethod
    def build_golden_organic(cls, surf_id: str = "Surf_Gold_Organic") -> Tuple[LookdevSurfaceSpecification, str, str, str]:
        """7. GOLDEN_ORGANIC (Section 114: chitin carapace/exoskeleton, rough=0.35, met=0.05)."""
        pbr = SurfacePBRProperties46(base_color_rgb=(0.22, 0.38, 0.18), metallic=0.05, roughness=0.35, ao=1.0, emission=0.0, resolution=2048)
        spec = LookdevSurfaceSpecification(surf_id, MaterialFamily46.ORGANIC, LookdevQualityTier46.HIGH, pbr)
        return (
            spec,
            f"/Game/Lookdev/Materials/M_{surf_id}",
            f"/Game/Lookdev/Instances/MI_{surf_id}",
            f"/Game/Lookdev/Textures/T_{surf_id}",
        )
