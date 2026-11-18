"""
SurfaceDetailFabricationPlatform manufactures all 15 required surface types from Section 157.
UAF-81.22 Sections 157, 168, 169.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import SurfaceDetailDefinition, PhysicalMaterialClass, SurfaceLayerType
from ..models.textures import SurfaceDetailChannel


class SurfaceDetailFabricationPlatform:
    """
    Fabricates complete production surfaces, master materials, and texture channel sets (Section 157).
    """

    @classmethod
    def _create_standard_textures(cls, prefix: str, res: int, has_emissive: bool = False) -> List[SurfaceDetailChannel]:
        textures = [
            SurfaceDetailChannel(f"T_{prefix}_Albedo", "ALBEDO", "sRGB", res),
            SurfaceDetailChannel(f"T_{prefix}_Normal", "NORMAL", "LINEAR", res),
            SurfaceDetailChannel(f"T_{prefix}_ORM", "ORM", "LINEAR", res),
        ]
        if has_emissive:
            textures.append(SurfaceDetailChannel(f"T_{prefix}_Emissive", "EMISSIVE", "sRGB", res))
        return textures

    @classmethod
    def build_painted_metal_with_wear(cls, s_id: str = "Surf_PaintedMetal_Wear") -> Tuple[SurfaceDetailDefinition, List[SurfaceDetailChannel], str, str]:
        """1. Metal pintado con desgaste."""
        s_def = SurfaceDetailDefinition(s_id, PhysicalMaterialClass.METAL, "DEFAULT_LIT", "#305070", 0.35, 0.9, 1.2, [
            SurfaceLayerType.BASE, SurfaceLayerType.PAINT, SurfaceLayerType.SCRATCH, SurfaceLayerType.DIRT
        ])
        textures = cls._create_standard_textures(s_id, 2048)
        return s_def, textures, "M_Master_Metal_Layered", f"MI_{s_id}"

    @classmethod
    def build_corroded_metal(cls, s_id: str = "Surf_Corroded_Steel") -> Tuple[SurfaceDetailDefinition, List[SurfaceDetailChannel], str, str]:
        """2. Metal corroído."""
        s_def = SurfaceDetailDefinition(s_id, PhysicalMaterialClass.METAL, "DEFAULT_LIT", "#4A3525", 0.85, 0.4, 1.5, [
            SurfaceLayerType.BASE, SurfaceLayerType.RUST, SurfaceLayerType.CORROSION
        ])
        textures = cls._create_standard_textures(s_id, 2048)
        return s_def, textures, "M_Master_Metal_Corroded", f"MI_{s_id}"

    @classmethod
    def build_fabric_material(cls, s_id: str = "Surf_Fabric_Denim") -> Tuple[SurfaceDetailDefinition, List[SurfaceDetailChannel], str, str]:
        """3. Material de tela."""
        s_def = SurfaceDetailDefinition(s_id, PhysicalMaterialClass.FABRIC, "DEFAULT_LIT", "#2B3A4A", 0.75, 0.0, 1.0, [
            SurfaceLayerType.BASE, SurfaceLayerType.COATING
        ])
        textures = cls._create_standard_textures(s_id, 2048)
        return s_def, textures, "M_Master_Fabric", f"MI_{s_id}"

    @classmethod
    def build_leather_material(cls, s_id: str = "Surf_Leather_Worn") -> Tuple[SurfaceDetailDefinition, List[SurfaceDetailChannel], str, str]:
        """4. Material de cuero."""
        s_def = SurfaceDetailDefinition(s_id, PhysicalMaterialClass.LEATHER, "DEFAULT_LIT", "#3D2614", 0.55, 0.0, 1.1, [
            SurfaceLayerType.BASE, SurfaceLayerType.SCRATCH
        ])
        textures = cls._create_standard_textures(s_id, 2048)
        return s_def, textures, "M_Master_Leather", f"MI_{s_id}"

    @classmethod
    def build_skin_material(cls, s_id: str = "Surf_Skin_Human") -> Tuple[SurfaceDetailDefinition, List[SurfaceDetailChannel], str, str]:
        """5. Material de piel."""
        s_def = SurfaceDetailDefinition(s_id, PhysicalMaterialClass.SKIN, "SUBSURFACE", "#D8A080", 0.45, 0.0, 0.9, [
            SurfaceLayerType.BASE
        ])
        textures = cls._create_standard_textures(s_id, 4096)
        return s_def, textures, "M_Master_SubsurfaceSkin", f"MI_{s_id}"

    @classmethod
    def build_concrete_material(cls, s_id: str = "Surf_Concrete_Rough") -> Tuple[SurfaceDetailDefinition, List[SurfaceDetailChannel], str, str]:
        """6. Material de hormigón."""
        s_def = SurfaceDetailDefinition(s_id, PhysicalMaterialClass.CONCRETE, "DEFAULT_LIT", "#7A7A7A", 0.9, 0.0, 1.4, [
            SurfaceLayerType.BASE, SurfaceLayerType.DIRT
        ])
        textures = cls._create_standard_textures(s_id, 2048)
        return s_def, textures, "M_Master_Concrete", f"MI_{s_id}"

    @classmethod
    def build_wood_material(cls, s_id: str = "Surf_Wood_Plank") -> Tuple[SurfaceDetailDefinition, List[SurfaceDetailChannel], str, str]:
        """7. Material de madera."""
        s_def = SurfaceDetailDefinition(s_id, PhysicalMaterialClass.WOOD, "DEFAULT_LIT", "#5C3A21", 0.6, 0.0, 1.0, [
            SurfaceLayerType.BASE, SurfaceLayerType.COATING
        ])
        textures = cls._create_standard_textures(s_id, 2048)
        return s_def, textures, "M_Master_Wood", f"MI_{s_id}"

    @classmethod
    def build_glass_material(cls, s_id: str = "Surf_Glass_Window") -> Tuple[SurfaceDetailDefinition, List[SurfaceDetailChannel], str, str]:
        """8. Material de cristal."""
        s_def = SurfaceDetailDefinition(s_id, PhysicalMaterialClass.GLASS, "CLEAR_COAT", "#E0F0FF", 0.05, 0.1, 0.5, [
            SurfaceLayerType.BASE, SurfaceLayerType.COATING
        ])
        textures = cls._create_standard_textures(s_id, 2048)
        return s_def, textures, "M_Master_Glass_ClearCoat", f"MI_{s_id}"

    @classmethod
    def build_emissive_material(cls, s_id: str = "Surf_Energy_Core") -> Tuple[SurfaceDetailDefinition, List[SurfaceDetailChannel], str, str]:
        """9. Material emissive."""
        s_def = SurfaceDetailDefinition(s_id, PhysicalMaterialClass.ENERGY, "UNLIT", "#00FFFF", 0.2, 0.0, 0.0, [
            SurfaceLayerType.BASE, SurfaceLayerType.EMISSIVE
        ])
        textures = cls._create_standard_textures(s_id, 2048, has_emissive=True)
        return s_def, textures, "M_Master_EmissiveEnergy", f"MI_{s_id}"

    @classmethod
    def build_procedural_tileable_material(cls, s_id: str = "Surf_Tileable_HexPattern") -> Tuple[SurfaceDetailDefinition, List[SurfaceDetailChannel], str, str]:
        """10. Material procedural tileable."""
        s_def = SurfaceDetailDefinition(s_id, PhysicalMaterialClass.PLASTIC, "DEFAULT_LIT", "#1A1A1A", 0.4, 0.0, 1.0, [
            SurfaceLayerType.BASE
        ])
        textures = cls._create_standard_textures(s_id, 1024)
        return s_def, textures, "M_Master_Tileable_Pattern", f"MI_{s_id}"

    @classmethod
    def build_trim_sheet_material(cls, s_id: str = "Surf_Trim_SciFiPanel") -> Tuple[SurfaceDetailDefinition, List[SurfaceDetailChannel], str, str]:
        """11. Trim sheet."""
        s_def = SurfaceDetailDefinition(s_id, PhysicalMaterialClass.METAL, "DEFAULT_LIT", "#3C3C3C", 0.3, 0.8, 1.2, [
            SurfaceLayerType.BASE, SurfaceLayerType.DECAL
        ])
        textures = cls._create_standard_textures(s_id, 4096)
        return s_def, textures, "M_Master_TrimSheet", f"MI_{s_id}"

    @classmethod
    def build_texture_atlas_material(cls, s_id: str = "Surf_Atlas_Props") -> Tuple[SurfaceDetailDefinition, List[SurfaceDetailChannel], str, str]:
        """12. Texture Atlas."""
        s_def = SurfaceDetailDefinition(s_id, PhysicalMaterialClass.CUSTOM, "DEFAULT_LIT", "#555555", 0.5, 0.2, 1.0, [
            SurfaceLayerType.BASE
        ])
        textures = cls._create_standard_textures(s_id, 4096)
        return s_def, textures, "M_Master_TextureAtlas", f"MI_{s_id}"

    @classmethod
    def build_decal_set_material(cls, s_id: str = "Surf_Decal_BloodSplatter") -> Tuple[SurfaceDetailDefinition, List[SurfaceDetailChannel], str, str]:
        """13. Decal set."""
        s_def = SurfaceDetailDefinition(s_id, PhysicalMaterialClass.LIQUID, "DEFAULT_LIT", "#660000", 0.2, 0.0, 0.8, [
            SurfaceLayerType.BASE, SurfaceLayerType.BLOOD, SurfaceLayerType.DECAL
        ])
        textures = cls._create_standard_textures(s_id, 1024)
        return s_def, textures, "M_Master_DeferredDecal", f"MI_{s_id}"

    @classmethod
    def build_multilayer_composite_material(cls, s_id: str = "Surf_Multilayer_Chassis") -> Tuple[SurfaceDetailDefinition, List[SurfaceDetailChannel], str, str]:
        """14. Material multicapa."""
        s_def = SurfaceDetailDefinition(s_id, PhysicalMaterialClass.CERAMIC, "DEFAULT_LIT", "#AAAAAA", 0.25, 0.1, 1.0, [
            SurfaceLayerType.BASE, SurfaceLayerType.COATING, SurfaceLayerType.DIRT, SurfaceLayerType.SCRATCH
        ])
        textures = cls._create_standard_textures(s_id, 2048)
        return s_def, textures, "M_Master_Multilayer_Composite", f"MI_{s_id}"

    @classmethod
    def build_highpoly_baked_material(cls, s_id: str = "Surf_HighPoly_BakedBake") -> Tuple[SurfaceDetailDefinition, List[SurfaceDetailChannel], str, str]:
        """15. Material horneado desde high-poly."""
        s_def = SurfaceDetailDefinition(s_id, PhysicalMaterialClass.METAL, "DEFAULT_LIT", "#888888", 0.3, 0.7, 1.5, [
            SurfaceLayerType.BASE
        ])
        textures = cls._create_standard_textures(s_id, 4096)
        return s_def, textures, "M_Master_HighPolyBake", f"MI_{s_id}"
