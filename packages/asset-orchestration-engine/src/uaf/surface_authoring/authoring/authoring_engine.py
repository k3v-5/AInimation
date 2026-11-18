"""
SurfaceAuthoringEngine produces calibrated PBR surfaces across all 9 canonical asset archetypes.
UAF-81.11 Sections 195, 196.
"""

from typing import Dict, Any, Tuple, List
from ..models.regions import (
    MaterialFamilyType,
    SurfaceRegion,
    MaterialCompositionLayer,
    MaterialRegionGraph,
    MaterialLayerBlendMode,
)
from ...surface.models.texture_set import TextureSet
from ...surface.synthesis.procedural_synthesizer import ProceduralTextureSynthesizer


class SurfaceAuthoringEngine:
    """
    Synthesizes complete PBR textures and surface region graphs for all 9 canonical asset classes.
    """

    @classmethod
    def author_organic_humanoid_surface(cls, asset_id: str, seed: int = 42) -> Tuple[MaterialRegionGraph, TextureSet]:
        """1. Organic Humanoid (Human Skin)."""
        graph = MaterialRegionGraph(asset_id=asset_id)
        graph.add_region(SurfaceRegion("reg_face", MaterialFamilyType.SKIN, roughness_range=[0.3, 0.6]))
        graph.add_region(SurfaceRegion("reg_body", MaterialFamilyType.SKIN, roughness_range=[0.4, 0.7]))

        tex_set = ProceduralTextureSynthesizer.synthesize_pbr_set(
            set_id=f"{asset_id}_Skin",
            material_family="SKIN",
            resolution=2048,
            seed=seed,
        )
        return graph, tex_set

    @classmethod
    def author_robot_surface(cls, asset_id: str, seed: int = 42) -> Tuple[MaterialRegionGraph, TextureSet]:
        """2. Robot (Hard Surface Metallic + Emissive tech)."""
        graph = MaterialRegionGraph(asset_id=asset_id)
        graph.add_region(SurfaceRegion("reg_chassis", MaterialFamilyType.METAL, metallic=1.0, roughness_range=[0.15, 0.4]))
        graph.add_region(SurfaceRegion("reg_sensors", MaterialFamilyType.ENERGY, metallic=0.0, roughness_range=[0.1, 0.2]))

        tex_set = ProceduralTextureSynthesizer.synthesize_pbr_set(
            set_id=f"{asset_id}_Robot",
            material_family="EMISSIVE_METAL",
            resolution=2048,
            seed=seed,
        )
        return graph, tex_set

    @classmethod
    def author_creature_surface(cls, asset_id: str, seed: int = 42) -> Tuple[MaterialRegionGraph, TextureSet]:
        """3. Creature (Organic Leather / Scales / Horns)."""
        graph = MaterialRegionGraph(asset_id=asset_id)
        graph.add_region(SurfaceRegion("reg_hide", MaterialFamilyType.ORGANIC, roughness_range=[0.5, 0.85]))
        graph.add_region(SurfaceRegion("reg_claws", MaterialFamilyType.CERAMIC, roughness_range=[0.2, 0.4]))

        tex_set = ProceduralTextureSynthesizer.synthesize_pbr_set(
            set_id=f"{asset_id}_Hide",
            material_family="ORGANIC",
            resolution=2048,
            seed=seed,
        )
        return graph, tex_set

    @classmethod
    def author_weapon_surface(cls, asset_id: str, seed: int = 42) -> Tuple[MaterialRegionGraph, TextureSet]:
        """4. Weapon (Anodized Gunmetal + Polymer Grip)."""
        graph = MaterialRegionGraph(asset_id=asset_id)
        graph.add_region(SurfaceRegion("reg_receiver", MaterialFamilyType.METAL, metallic=0.95, roughness_range=[0.2, 0.45]))
        graph.add_region(SurfaceRegion("reg_grip", MaterialFamilyType.PLASTIC, metallic=0.0, roughness_range=[0.6, 0.9]))

        tex_set = ProceduralTextureSynthesizer.synthesize_pbr_set(
            set_id=f"{asset_id}_Gunmetal",
            material_family="METAL",
            resolution=2048,
            seed=seed,
        )
        return graph, tex_set

    @classmethod
    def author_armor_surface(cls, asset_id: str, seed: int = 42) -> Tuple[MaterialRegionGraph, TextureSet]:
        """5. Armor Piece (Ceramic Composite + Ballistic Weave)."""
        graph = MaterialRegionGraph(asset_id=asset_id)
        graph.add_region(SurfaceRegion("reg_plates", MaterialFamilyType.CERAMIC, metallic=0.1, roughness_range=[0.25, 0.5]))
        graph.add_region(SurfaceRegion("reg_straps", MaterialFamilyType.FABRIC, metallic=0.0, roughness_range=[0.7, 0.95]))

        tex_set = ProceduralTextureSynthesizer.synthesize_pbr_set(
            set_id=f"{asset_id}_Armor",
            material_family="CERAMIC",
            resolution=2048,
            seed=seed,
        )
        return graph, tex_set

    @classmethod
    def author_clothing_surface(cls, asset_id: str, seed: int = 42) -> Tuple[MaterialRegionGraph, TextureSet]:
        """6. Clothing Piece (Woven Tactical Fabric + Leather)."""
        graph = MaterialRegionGraph(asset_id=asset_id)
        graph.add_region(SurfaceRegion("reg_fabric", MaterialFamilyType.FABRIC, roughness_range=[0.75, 0.95]))
        graph.add_region(SurfaceRegion("reg_trim", MaterialFamilyType.LEATHER, roughness_range=[0.4, 0.65]))

        tex_set = ProceduralTextureSynthesizer.synthesize_pbr_set(
            set_id=f"{asset_id}_Fabric",
            material_family="FABRIC",
            resolution=2048,
            seed=seed,
        )
        return graph, tex_set

    @classmethod
    def author_industrial_prop_surface(cls, asset_id: str, seed: int = 42) -> Tuple[MaterialRegionGraph, TextureSet]:
        """7. Industrial Prop (Painted Steel with Grime and Edge Wear)."""
        graph = MaterialRegionGraph(asset_id=asset_id)
        graph.add_region(SurfaceRegion("reg_main", MaterialFamilyType.PAINTED_METAL, metallic=0.8, roughness_range=[0.3, 0.7]))
        # Composite rust layer
        graph.add_composition_layer(
            "reg_main",
            MaterialCompositionLayer("comp_rust", MaterialFamilyType.METAL, "mask_edge_wear", MaterialLayerBlendMode.MASK_BLEND),
        )

        tex_set = ProceduralTextureSynthesizer.synthesize_pbr_set(
            set_id=f"{asset_id}_Prop",
            material_family="PAINTED_METAL",
            resolution=2048,
            seed=seed,
        )
        return graph, tex_set

    @classmethod
    def author_architectural_block_surface(cls, asset_id: str, seed: int = 42) -> Tuple[MaterialRegionGraph, TextureSet]:
        """8. Architectural Block (Reinforced Concrete / Stone)."""
        graph = MaterialRegionGraph(asset_id=asset_id)
        graph.add_region(SurfaceRegion("reg_wall", MaterialFamilyType.CONCRETE, roughness_range=[0.7, 0.95]))
        graph.add_region(SurfaceRegion("reg_rebar", MaterialFamilyType.METAL, metallic=1.0, roughness_range=[0.4, 0.6]))

        tex_set = ProceduralTextureSynthesizer.synthesize_pbr_set(
            set_id=f"{asset_id}_Concrete",
            material_family="CONCRETE",
            resolution=2048,
            seed=seed,
        )
        return graph, tex_set

    @classmethod
    def author_natural_surface(cls, asset_id: str, seed: int = 42) -> Tuple[MaterialRegionGraph, TextureSet]:
        """9. Natural Surface (Weathered Stone / Soil)."""
        graph = MaterialRegionGraph(asset_id=asset_id)
        graph.add_region(SurfaceRegion("reg_rock", MaterialFamilyType.STONE, roughness_range=[0.65, 0.9]))

        tex_set = ProceduralTextureSynthesizer.synthesize_pbr_set(
            set_id=f"{asset_id}_Stone",
            material_family="STONE",
            resolution=2048,
            seed=seed,
        )
        return graph, tex_set
