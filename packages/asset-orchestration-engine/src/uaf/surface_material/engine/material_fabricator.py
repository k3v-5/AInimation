"""
SurfaceMaterialProductionPlatform manufactures all 8 canonical Golden Surfaces from Section 149.
UAF-81.30 Section 149.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import (
    ProductionSurfaceDefinition,
    SurfaceType30,
    MaterialModel30,
    SurfaceMapItem,
    ColorSpace30,
)


class SurfaceMaterialProductionPlatform:
    """
    Synthesizes complete, production-grade procedural materials, texture sets, and PBR surfaces.
    """

    @classmethod
    def _create_pbr_maps(cls, prefix: str, is_emissive: bool = False, is_sss: bool = False) -> List[SurfaceMapItem]:
        maps = [
            SurfaceMapItem(f"T_{prefix}_BC", "BASE_COLOR", 2048, ColorSpace30.SRGB),
            SurfaceMapItem(f"T_{prefix}_N", "NORMAL", 2048, ColorSpace30.NORMAL_MAP),
            SurfaceMapItem(f"T_{prefix}_ORM", "ORM", 2048, ColorSpace30.LINEAR),
        ]
        if is_emissive:
            maps.append(SurfaceMapItem(f"T_{prefix}_E", "EMISSIVE", 1024, ColorSpace30.SRGB))
        if is_sss:
            maps.append(SurfaceMapItem(f"T_{prefix}_SSSMask", "MASK", 2048, ColorSpace30.LINEAR))
        return maps

    @classmethod
    def build_golden_skin(cls, surface_id: str = "Surf_Golden_Skin") -> Tuple[ProductionSurfaceDefinition, str, str]:
        """1. GOLDEN_SKIN (Section 149: Subsurface scattering, micro-pore normal, low metallic)."""
        maps = cls._create_pbr_maps("Skin", is_sss=True)
        s_def = ProductionSurfaceDefinition(surface_id, SurfaceType30.SKIN, MaterialModel30.SUBSURFACE, maps, roughness_base=0.45, metallic_base=0.0)
        return s_def, "M_Master_SubsurfaceProfile", f"MI_{surface_id}"

    @classmethod
    def build_golden_metal(cls, surface_id: str = "Surf_Golden_Metal") -> Tuple[ProductionSurfaceDefinition, str, str]:
        """2. GOLDEN_METAL (Section 149: Full metallic 1.0, brushed normal, low roughness)."""
        maps = cls._create_pbr_maps("Metal")
        s_def = ProductionSurfaceDefinition(surface_id, SurfaceType30.METAL, MaterialModel30.PBR_METALLIC_ROUGHNESS, maps, roughness_base=0.25, metallic_base=1.0)
        return s_def, "M_Master_HardSurfacePBR", f"MI_{surface_id}"

    @classmethod
    def build_golden_fabric(cls, surface_id: str = "Surf_Golden_Fabric") -> Tuple[ProductionSurfaceDefinition, str, str]:
        """3. GOLDEN_FABRIC (Section 149: Cloth model, weave micro-normal, zero metallic)."""
        maps = cls._create_pbr_maps("Fabric")
        s_def = ProductionSurfaceDefinition(surface_id, SurfaceType30.FABRIC, MaterialModel30.CLOTH, maps, roughness_base=0.80, metallic_base=0.0)
        return s_def, "M_Master_ClothShading", f"MI_{surface_id}"

    @classmethod
    def build_golden_concrete(cls, surface_id: str = "Surf_Golden_Concrete") -> Tuple[ProductionSurfaceDefinition, str, str]:
        """4. GOLDEN_CONCRETE (Section 149: Rough architectural surface, cavity mask)."""
        maps = cls._create_pbr_maps("Concrete")
        s_def = ProductionSurfaceDefinition(surface_id, SurfaceType30.CONCRETE, MaterialModel30.PBR_METALLIC_ROUGHNESS, maps, roughness_base=0.85, metallic_base=0.0)
        return s_def, "M_Master_ArchitecturalPBR", f"MI_{surface_id}"

    @classmethod
    def build_golden_wood(cls, surface_id: str = "Surf_Golden_Wood") -> Tuple[ProductionSurfaceDefinition, str, str]:
        """5. GOLDEN_WOOD (Section 149: Fiber grain normal, organic varnish clearcoat)."""
        maps = cls._create_pbr_maps("Wood")
        s_def = ProductionSurfaceDefinition(surface_id, SurfaceType30.WOOD, MaterialModel30.CLEAR_COAT, maps, roughness_base=0.40, metallic_base=0.0)
        return s_def, "M_Master_ClearCoatWood", f"MI_{surface_id}"

    @classmethod
    def build_golden_glass(cls, surface_id: str = "Surf_Golden_Glass") -> Tuple[ProductionSurfaceDefinition, str, str]:
        """6. GOLDEN_GLASS (Section 149: Translucent surface, high specular, ultra smooth)."""
        maps = cls._create_pbr_maps("Glass")
        s_def = ProductionSurfaceDefinition(surface_id, SurfaceType30.GLASS, MaterialModel30.TRANSLUCENT, maps, roughness_base=0.05, metallic_base=0.0)
        return s_def, "M_Master_ThinTranslucentGlass", f"MI_{surface_id}"

    @classmethod
    def build_golden_energy(cls, surface_id: str = "Surf_Golden_Energy") -> Tuple[ProductionSurfaceDefinition, str, str]:
        """7. GOLDEN_ENERGY (Section 149: High bloom emissive, pulse glow modulation)."""
        maps = cls._create_pbr_maps("Energy", is_emissive=True)
        s_def = ProductionSurfaceDefinition(surface_id, SurfaceType30.ENERGY, MaterialModel30.EMISSIVE, maps, roughness_base=0.10, metallic_base=0.0)
        return s_def, "M_Master_EmissiveEnergyPulse", f"MI_{surface_id}"

    @classmethod
    def build_golden_terrain(cls, surface_id: str = "Surf_Golden_Terrain") -> Tuple[ProductionSurfaceDefinition, str, str]:
        """8. GOLDEN_TERRAIN (Section 149: Multi-layer blend, rock/soil/sand macro variation)."""
        maps = cls._create_pbr_maps("Terrain")
        s_def = ProductionSurfaceDefinition(surface_id, SurfaceType30.SOIL, MaterialModel30.PBR_METALLIC_ROUGHNESS, maps, roughness_base=0.90, metallic_base=0.0)
        return s_def, "M_Master_LandscapeLayerBlend", f"MI_{surface_id}"
