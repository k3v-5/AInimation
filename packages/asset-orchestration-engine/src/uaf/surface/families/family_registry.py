"""
MaterialFamilyRegistry maintains production master material families.
UAF-81.4 Sections 45, 46, 47, 48.
"""

from typing import List, Optional
from ...contracts.registry import BaseRegistry
from ..models.channels import ShaderModel
from .material_family import MaterialFamily


class MaterialFamilyRegistry(BaseRegistry[MaterialFamily]):
    def __init__(self):
        super().__init__(name="MaterialFamilyRegistry")
        self._init_standard_families()

    def _init_standard_families(self) -> None:
        standards = [
            MaterialFamily(
                family_id="PAINTED_METAL",
                name="Painted Metal Master",
                base_shader_model=ShaderModel.DEFAULT_LIT,
                master_material_id="M_Master_PaintedMetal",
                supported_layers=["base_metal", "primer", "paint", "wear", "dirt", "scratches"],
                default_parameters={
                    "paint_color": [0.2, 0.25, 0.3, 1.0],
                    "metallic": 0.0,  # Paint covers metal initially
                    "roughness": 0.35,
                    "wear_amount": 0.0,
                    "dirt_amount": 0.0,
                    "metal_roughness": 0.25,
                },
                description="Production layered painted metal with edge-wear and grime.",
            ),
            MaterialFamily(
                family_id="HUMAN_SKIN",
                name="Human Skin Master",
                base_shader_model=ShaderModel.SUBSURFACE,
                master_material_id="M_Master_HumanSkin",
                supported_layers=["subsurface_profile", "epidermis", "pores", "micro_wrinkles", "flush"],
                default_parameters={
                    "skin_tone": [0.85, 0.65, 0.55, 1.0],
                    "subsurface_color": [0.95, 0.35, 0.25, 1.0],
                    "subsurface_radius": 1.2,
                    "roughness": 0.45,
                    "pore_depth": 0.6,
                },
                description="Physically-based subsurface scattering skin material for hero avatars.",
            ),
            MaterialFamily(
                family_id="TACTICAL_CLOTH",
                name="Tactical Cloth Master",
                base_shader_model=ShaderModel.DEFAULT_LIT,
                master_material_id="M_Master_TacticalCloth",
                supported_layers=["weave_pattern", "fabric_base", "camo_overlay", "dirt", "thread_fray"],
                default_parameters={
                    "fabric_color": [0.15, 0.18, 0.14, 1.0],
                    "roughness": 0.75,
                    "weave_tiling": 16.0,
                    "sheen_intensity": 0.2,
                },
                description="Weaved tactical fabrics and ballistic nylon.",
            ),
            MaterialFamily(
                family_id="WEAPON_STEEL",
                name="Weapon Steel Master",
                base_shader_model=ShaderModel.DEFAULT_LIT,
                master_material_id="M_Master_WeaponSteel",
                supported_layers=["milled_steel", "bluing", "gun_oil", "burnish", "powder_burn"],
                default_parameters={
                    "base_color": [0.12, 0.12, 0.12, 1.0],
                    "metallic": 1.0,
                    "roughness": 0.28,
                    "oil_sheen": 0.15,
                },
                description="Machined and blued firearm steel.",
            ),
            MaterialFamily(
                family_id="EMISSIVE_GLASS",
                name="Emissive Glass Master",
                base_shader_model=ShaderModel.CLEAR_COAT,
                master_material_id="M_Master_EmissiveGlass",
                supported_layers=["glass_substrate", "emissive_core", "surface_condensation", "dust"],
                default_parameters={
                    "tint_color": [0.1, 0.8, 1.0, 0.8],
                    "emissive_color": [0.0, 0.9, 1.0, 1.0],
                    "emissive_intensity": 5.0,
                    "clear_coat": 1.0,
                    "roughness": 0.05,
                },
                description="Visors, plasma conduits, weapon lenses, and sci-fi glowing indicators.",
            ),
        ]
        for f in standards:
            self.register(f.family_id, f)
