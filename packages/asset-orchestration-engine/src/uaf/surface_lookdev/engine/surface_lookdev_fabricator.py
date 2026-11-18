"""
SurfaceLookdevFabricationPlatform manufactures canonical Golden Surfaces matching Section 147.
UAF-81.38 Sections 147, 149.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import (
    SurfaceLookdevSpecification,
    MaterialType38,
    ColorSpace38,
    NormalProfile38,
    PBRSurfaceProperties38,
)


class SurfaceLookdevFabricationPlatform:
    """
    Synthesizes complete, production-grade procedural surfaces, materials, instances, and PBR textures for Unreal Engine.
    """

    @classmethod
    def build_golden_skin(cls, surf_id: str = "Lookdev_Gold_Skin") -> Tuple[SurfaceLookdevSpecification, str, str]:
        """1. skin (Section 147: subsurface scattering, micro-pore roughness, linear normal)."""
        prop = PBRSurfaceProperties38(roughness=0.42, metallic=0.0, specular=0.5, emissive_intensity=0.0)
        spec = SurfaceLookdevSpecification(surf_id, MaterialType38.SKIN, prop, NormalProfile38.DIRECTX, ColorSpace38.SRGB, 2048, 2048)
        return spec, "/Game/Materials/Masters/M_Master_SkinPBR", f"/Game/Materials/Instances/MI_{surf_id}"

    @classmethod
    def build_golden_metal(cls, surf_id: str = "Lookdev_Gold_Metal") -> Tuple[SurfaceLookdevSpecification, str, str]:
        """2. metal (Section 147: metallic 1.0, low roughness, DirectX normal)."""
        prop = PBRSurfaceProperties38(roughness=0.25, metallic=1.0, specular=0.5, emissive_intensity=0.0)
        spec = SurfaceLookdevSpecification(surf_id, MaterialType38.METAL, prop, NormalProfile38.DIRECTX, ColorSpace38.SRGB, 2048, 2048)
        return spec, "/Game/Materials/Masters/M_Master_HardSurfacePBR", f"/Game/Materials/Instances/MI_{surf_id}"

    @classmethod
    def build_golden_fabric(cls, surf_id: str = "Lookdev_Gold_Fabric") -> Tuple[SurfaceLookdevSpecification, str, str]:
        """3. fabric (Section 147: cloth sheen, zero metallic, high roughness 0.8)."""
        prop = PBRSurfaceProperties38(roughness=0.80, metallic=0.0, specular=0.3, emissive_intensity=0.0)
        spec = SurfaceLookdevSpecification(surf_id, MaterialType38.FABRIC, prop, NormalProfile38.DIRECTX, ColorSpace38.SRGB, 2048, 2048)
        return spec, "/Game/Materials/Masters/M_Master_ClothPBR", f"/Game/Materials/Instances/MI_{surf_id}"

    @classmethod
    def build_golden_leather(cls, surf_id: str = "Lookdev_Gold_Leather") -> Tuple[SurfaceLookdevSpecification, str, str]:
        """4. leather (Section 147: organic roughness 0.5, subtle specularity)."""
        prop = PBRSurfaceProperties38(roughness=0.50, metallic=0.0, specular=0.4, emissive_intensity=0.0)
        spec = SurfaceLookdevSpecification(surf_id, MaterialType38.LEATHER, prop, NormalProfile38.DIRECTX, ColorSpace38.SRGB, 2048, 2048)
        return spec, "/Game/Materials/Masters/M_Master_LeatherPBR", f"/Game/Materials/Instances/MI_{surf_id}"

    @classmethod
    def build_golden_concrete(cls, surf_id: str = "Lookdev_Gold_Concrete") -> Tuple[SurfaceLookdevSpecification, str, str]:
        """5. concrete (Section 147: high roughness 0.9, micro-cavity normal, zero metallic)."""
        prop = PBRSurfaceProperties38(roughness=0.90, metallic=0.0, specular=0.2, emissive_intensity=0.0)
        spec = SurfaceLookdevSpecification(surf_id, MaterialType38.CONCRETE, prop, NormalProfile38.DIRECTX, ColorSpace38.SRGB, 2048, 2048)
        return spec, "/Game/Materials/Masters/M_Master_ArchitecturalPBR", f"/Game/Materials/Instances/MI_{surf_id}"

    @classmethod
    def build_golden_rock(cls, surf_id: str = "Lookdev_Gold_Rock") -> Tuple[SurfaceLookdevSpecification, str, str]:
        """6. rock (Section 147: macro variation, rocky roughness 0.85, height displacement)."""
        prop = PBRSurfaceProperties38(roughness=0.85, metallic=0.0, specular=0.3, emissive_intensity=0.0)
        spec = SurfaceLookdevSpecification(surf_id, MaterialType38.STONE, prop, NormalProfile38.DIRECTX, ColorSpace38.SRGB, 2048, 2048)
        return spec, "/Game/Materials/Masters/M_Master_TerrainPBR", f"/Game/Materials/Instances/MI_{surf_id}"

    @classmethod
    def build_golden_wood(cls, surf_id: str = "Lookdev_Gold_Wood") -> Tuple[SurfaceLookdevSpecification, str, str]:
        """7. wood (Section 147: anisotropic grain, roughness 0.45, zero metallic)."""
        prop = PBRSurfaceProperties38(roughness=0.45, metallic=0.0, specular=0.35, emissive_intensity=0.0)
        spec = SurfaceLookdevSpecification(surf_id, MaterialType38.WOOD, prop, NormalProfile38.DIRECTX, ColorSpace38.SRGB, 2048, 2048)
        return spec, "/Game/Materials/Masters/M_Master_OrganicPBR", f"/Game/Materials/Instances/MI_{surf_id}"

    @classmethod
    def build_golden_glass(cls, surf_id: str = "Lookdev_Gold_Glass") -> Tuple[SurfaceLookdevSpecification, str, str]:
        """8. glass (Section 147: translucent PBR, ultra low roughness 0.05, zero metallic)."""
        prop = PBRSurfaceProperties38(roughness=0.05, metallic=0.0, specular=0.9, emissive_intensity=0.0)
        spec = SurfaceLookdevSpecification(surf_id, MaterialType38.GLASS, prop, NormalProfile38.DIRECTX, ColorSpace38.SRGB, 2048, 2048)
        return spec, "/Game/Materials/Masters/M_Master_GlassPBR", f"/Game/Materials/Instances/MI_{surf_id}"

    @classmethod
    def build_golden_plastic(cls, surf_id: str = "Lookdev_Gold_Plastic") -> Tuple[SurfaceLookdevSpecification, str, str]:
        """9. plastic (Section 147: smooth dielectric, roughness 0.25, zero metallic)."""
        prop = PBRSurfaceProperties38(roughness=0.25, metallic=0.0, specular=0.5, emissive_intensity=0.0)
        spec = SurfaceLookdevSpecification(surf_id, MaterialType38.PLASTIC, prop, NormalProfile38.DIRECTX, ColorSpace38.SRGB, 2048, 2048)
        return spec, "/Game/Materials/Masters/M_Master_PolymerPBR", f"/Game/Materials/Instances/MI_{surf_id}"

    @classmethod
    def build_golden_energy(cls, surf_id: str = "Lookdev_Gold_Energy") -> Tuple[SurfaceLookdevSpecification, str, str]:
        """10. energy (Section 147: emissive intensity 5.0, additive/translucent profile)."""
        prop = PBRSurfaceProperties38(roughness=0.10, metallic=0.0, specular=0.0, emissive_intensity=5.0)
        spec = SurfaceLookdevSpecification(surf_id, MaterialType38.ENERGY, prop, NormalProfile38.DIRECTX, ColorSpace38.SRGB, 1024, 1024)
        return spec, "/Game/Materials/Masters/M_Master_EmissiveVFX", f"/Game/Materials/Instances/MI_{surf_id}"

    @classmethod
    def build_golden_robot_surface(cls, surf_id: str = "Lookdev_Gold_RobotSurface") -> Tuple[SurfaceLookdevSpecification, str, str]:
        """11. robot_surface (Section 147: painted metal, edge wear mask, scratch damage)."""
        prop = PBRSurfaceProperties38(roughness=0.35, metallic=0.85, specular=0.5, emissive_intensity=0.5)
        spec = SurfaceLookdevSpecification(surf_id, MaterialType38.METAL, prop, NormalProfile38.DIRECTX, ColorSpace38.SRGB, 2048, 2048)
        return spec, "/Game/Materials/Masters/M_Master_HardSurfacePBR", f"/Game/Materials/Instances/MI_{surf_id}"

    @classmethod
    def build_golden_armor_surface(cls, surf_id: str = "Lookdev_Gold_ArmorSurface") -> Tuple[SurfaceLookdevSpecification, str, str]:
        """12. armor_surface (Section 147: heavy composite, high hardness, metallic 0.9)."""
        prop = PBRSurfaceProperties38(roughness=0.40, metallic=0.90, specular=0.6, emissive_intensity=0.0)
        spec = SurfaceLookdevSpecification(surf_id, MaterialType38.METAL, prop, NormalProfile38.DIRECTX, ColorSpace38.SRGB, 2048, 2048)
        return spec, "/Game/Materials/Masters/M_Master_HardSurfacePBR", f"/Game/Materials/Instances/MI_{surf_id}"

    @classmethod
    def build_golden_weapon_surface(cls, surf_id: str = "Lookdev_Gold_WeaponSurface") -> Tuple[SurfaceLookdevSpecification, str, str]:
        """13. weapon_surface (Section 147: gunmetal steel, anodized finish, micro-wear)."""
        prop = PBRSurfaceProperties38(roughness=0.28, metallic=0.95, specular=0.55, emissive_intensity=0.0)
        spec = SurfaceLookdevSpecification(surf_id, MaterialType38.METAL, prop, NormalProfile38.DIRECTX, ColorSpace38.SRGB, 2048, 2048)
        return spec, "/Game/Materials/Masters/M_Master_HardSurfacePBR", f"/Game/Materials/Instances/MI_{surf_id}"

    @classmethod
    def build_golden_environment_surface(cls, surf_id: str = "Lookdev_Gold_EnvSurface") -> Tuple[SurfaceLookdevSpecification, str, str]:
        """14. environment_surface (Section 147: architectural trim, tileable PBR)."""
        prop = PBRSurfaceProperties38(roughness=0.65, metallic=0.10, specular=0.4, emissive_intensity=0.0)
        spec = SurfaceLookdevSpecification(surf_id, MaterialType38.CERAMIC, prop, NormalProfile38.DIRECTX, ColorSpace38.SRGB, 2048, 2048)
        return spec, "/Game/Materials/Masters/M_Master_ArchitecturalPBR", f"/Game/Materials/Instances/MI_{surf_id}"
