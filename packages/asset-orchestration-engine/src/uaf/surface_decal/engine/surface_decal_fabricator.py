"""
SurfaceDecalFabricationPlatform manufactures canonical Material Presets matching Section 7.
UAF-81.34 Sections 7, 127.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import (
    SurfaceAuthoringSpecification,
    MaterialFamily34,
    WearType34,
    DamageType34,
    SurfaceDecalItem,
)


class SurfaceDecalFabricationPlatform:
    """
    Synthesizes complete, production-grade procedural materials, wear, decals, and surface details.
    """

    @classmethod
    def build_golden_brushed_steel(cls, surf_id: str = "Mat_Gold_BrushedSteel") -> Tuple[SurfaceAuthoringSpecification, str, str]:
        """1. MAT_BRUSHED_STEEL (Section 7: metallic 1.0, low roughness, edge wear)."""
        wear = [WearType34.EDGE_WEAR, WearType34.MECHANICAL_WEAR]
        spec = SurfaceAuthoringSpecification(surf_id, MaterialFamily34.METAL, roughness_base=0.25, metallic_base=1.0, wear_types=wear)
        return spec, "M_Master_HardSurfacePBR", f"MI_{surf_id}"

    @classmethod
    def build_golden_damaged_steel(cls, surf_id: str = "Mat_Gold_DamagedSteel") -> Tuple[SurfaceAuthoringSpecification, str, str]:
        """2. MAT_DAMAGED_STEEL (Section 7: metallic 1.0, bullet dents, scratches, rust)."""
        damage = [DamageType34.BULLET_IMPACT, DamageType34.SCRATCH, DamageType34.DENT]
        decals = [SurfaceDecalItem("Decal_BulletHit", "IMPACT", [15.0, 15.0], 1.0)]
        spec = SurfaceAuthoringSpecification(surf_id, MaterialFamily34.METAL, roughness_base=0.45, metallic_base=1.0, damage_types=damage, decals=decals)
        return spec, "M_Master_HardSurfacePBR", f"MI_{surf_id}"

    @classmethod
    def build_golden_black_rubber(cls, surf_id: str = "Mat_Gold_BlackRubber") -> Tuple[SurfaceAuthoringSpecification, str, str]:
        """3. MAT_BLACK_RUBBER (Section 7: non-metallic 0.0, high roughness, contact wear)."""
        wear = [WearType34.CONTACT_WEAR, WearType34.SURFACE_WEAR]
        spec = SurfaceAuthoringSpecification(surf_id, MaterialFamily34.RUBBER, roughness_base=0.85, metallic_base=0.0, wear_types=wear)
        return spec, "M_Master_PolymerPBR", f"MI_{surf_id}"

    @classmethod
    def build_golden_tactical_fabric(cls, surf_id: str = "Mat_Gold_TacticalFabric") -> Tuple[SurfaceAuthoringSpecification, str, str]:
        """4. MAT_TACTICAL_FABRIC (Section 7: cloth micro-normal, zero metallic, fabric weave)."""
        wear = [WearType34.FREQUENCY_WEAR]
        spec = SurfaceAuthoringSpecification(surf_id, MaterialFamily34.FABRIC, roughness_base=0.75, metallic_base=0.0, wear_types=wear)
        return spec, "M_Master_ClothPBR", f"MI_{surf_id}"

    @classmethod
    def build_golden_human_skin(cls, surf_id: str = "Mat_Gold_HumanSkin") -> Tuple[SurfaceAuthoringSpecification, str, str]:
        """5. MAT_HUMAN_SKIN (Section 7: subsurface scattering profile, micro-pore roughness)."""
        spec = SurfaceAuthoringSpecification(surf_id, MaterialFamily34.SKIN, roughness_base=0.42, metallic_base=0.0)
        return spec, "M_Master_SubsurfaceProfile", f"MI_{surf_id}"

    @classmethod
    def build_golden_alien_skin(cls, surf_id: str = "Mat_Gold_AlienSkin") -> Tuple[SurfaceAuthoringSpecification, str, str]:
        """6. MAT_ALIEN_SKIN (Section 7: organic iridescent subsurface, mottled mask)."""
        spec = SurfaceAuthoringSpecification(surf_id, MaterialFamily34.ORGANIC, roughness_base=0.30, metallic_base=0.0)
        return spec, "M_Master_SubsurfaceProfile", f"MI_{surf_id}"

    @classmethod
    def build_golden_concrete(cls, surf_id: str = "Mat_Gold_Concrete") -> Tuple[SurfaceAuthoringSpecification, str, str]:
        """7. MAT_CONCRETE (Section 7: architectural roughness, chip damage, dirt accumulation)."""
        damage = [DamageType34.CHIP, DamageType34.CRACK]
        wear = [WearType34.ENVIRONMENTAL_WEAR]
        spec = SurfaceAuthoringSpecification(surf_id, MaterialFamily34.CONCRETE, roughness_base=0.90, metallic_base=0.0, wear_types=wear, damage_types=damage)
        return spec, "M_Master_ArchitecturalPBR", f"MI_{surf_id}"

    @classmethod
    def build_golden_rusted_metal(cls, surf_id: str = "Mat_Gold_RustedMetal") -> Tuple[SurfaceAuthoringSpecification, str, str]:
        """8. MAT_RUSTED_METAL (Section 7: painted metal with peeling mask, corrosion)."""
        wear = [WearType34.ENVIRONMENTAL_WEAR, WearType34.SURFACE_WEAR]
        spec = SurfaceAuthoringSpecification(surf_id, MaterialFamily34.PAINTED_METAL, roughness_base=0.65, metallic_base=0.7, wear_types=wear)
        return spec, "M_Master_CorrosionPBR", f"MI_{surf_id}"

    @classmethod
    def build_golden_polished_chrome(cls, surf_id: str = "Mat_Gold_PolishedChrome") -> Tuple[SurfaceAuthoringSpecification, str, str]:
        """9. MAT_POLISHED_CHROME (Section 7: metallic 1.0, ultra low roughness 0.05)."""
        spec = SurfaceAuthoringSpecification(surf_id, MaterialFamily34.METAL, roughness_base=0.05, metallic_base=1.0)
        return spec, "M_Master_MirrorChromePBR", f"MI_{surf_id}"

    @classmethod
    def build_golden_obsidian(cls, surf_id: str = "Mat_Gold_Obsidian") -> Tuple[SurfaceAuthoringSpecification, str, str]:
        """10. MAT_OBSIDIAN (Section 7: deep gloss stone, high specularity, glass-like fracture)."""
        damage = [DamageType34.CHIP]
        spec = SurfaceAuthoringSpecification(surf_id, MaterialFamily34.STONE, roughness_base=0.08, metallic_base=0.0, damage_types=damage)
        return spec, "M_Master_GlassyMineralPBR", f"MI_{surf_id}"
