"""
SurfaceFabricationEngine produces production-ready PBR surface configurations across all 10 canonical materials.
UAF-81.15 Sections 163, 164, 165, 200, 201.
"""

from typing import Tuple, List, Dict, Any
from ..models.profile import (
    MaterialClassification,
    MaterialDomain,
    SurfaceWearType,
    SurfaceProfile,
)
from ..models.graph import MaterialGraphContract


class SurfaceFabricationEngine:
    """
    Fabricates calibrated, target-ready materials, shader graph contracts, and texture channel sets.
    """

    @classmethod
    def build_skin_surface(cls, surf_id: str = "Surf_Human_Skin", seed: int = 101) -> Tuple[SurfaceProfile, MaterialGraphContract, List[str]]:
        """1. Skin Material (Subsurface scattering, micro pores)."""
        prof = SurfaceProfile(
            surface_id=surf_id,
            surface_type="SKIN",
            material_classification=MaterialClassification.SUBSURFACE,
            roughness_range=[0.35, 0.6],
            metallic_range=[0.0, 0.0],
            base_color_hex="#D2A084",
            seed=seed,
        )
        graph = MaterialGraphContract(
            graph_id=f"{surf_id}_Graph",
            master_material_id="M_Master_SubsurfaceSkin",
            parameters={"SubsurfaceColor": "#A02010", "PoreTiling": 24.0},
            material_functions=["DetailBlend", "NormalBlend"],
        )
        textures = [f"T_{surf_id}_BC", f"T_{surf_id}_N", f"T_{surf_id}_ORM", f"T_{surf_id}_SS"]
        return prof, graph, textures

    @classmethod
    def build_metal_surface(cls, surf_id: str = "Surf_Hardened_Steel", seed: int = 202) -> Tuple[SurfaceProfile, MaterialGraphContract, List[str]]:
        """2. Metal Material (High metallic, edge wear, micro scratches)."""
        prof = SurfaceProfile(
            surface_id=surf_id,
            surface_type="METAL",
            material_classification=MaterialClassification.OPAQUE,
            roughness_range=[0.15, 0.45],
            metallic_range=[0.95, 1.0],
            base_color_hex="#C0C4C8",
            wears=[SurfaceWearType.EDGE_WEAR, SurfaceWearType.SCRATCH],
            seed=seed,
        )
        graph = MaterialGraphContract(
            graph_id=f"{surf_id}_Graph",
            master_material_id="M_Master_MetalPBR",
            parameters={"EdgeWearIntensity": 0.7, "Anisotropy": 0.4},
            material_functions=["EdgeWear", "DetailBlend"],
        )
        textures = [f"T_{surf_id}_BC", f"T_{surf_id}_N", f"T_{surf_id}_ORM"]
        return prof, graph, textures

    @classmethod
    def build_fabric_surface(cls, surf_id: str = "Surf_Tactical_Nylon", seed: int = 303) -> Tuple[SurfaceProfile, MaterialGraphContract, List[str]]:
        """3. Fabric Material (Woven weave pattern, fuzz/sheen)."""
        prof = SurfaceProfile(
            surface_id=surf_id,
            surface_type="FABRIC",
            material_classification=MaterialClassification.OPAQUE,
            roughness_range=[0.7, 0.95],
            metallic_range=[0.0, 0.0],
            base_color_hex="#2B3A2C",
            seed=seed,
        )
        graph = MaterialGraphContract(
            graph_id=f"{surf_id}_Graph",
            master_material_id="M_Master_Fabric",
            parameters={"FuzzRoughness": 0.9, "WeaveTiling": 32.0},
            material_functions=["DetailBlend"],
        )
        textures = [f"T_{surf_id}_BC", f"T_{surf_id}_N", f"T_{surf_id}_ORM"]
        return prof, graph, textures

    @classmethod
    def build_concrete_surface(cls, surf_id: str = "Surf_Reinforced_Concrete", seed: int = 404) -> Tuple[SurfaceProfile, MaterialGraphContract, List[str]]:
        """4. Concrete Material (Rough porous surface, dirt stains)."""
        prof = SurfaceProfile(
            surface_id=surf_id,
            surface_type="CONCRETE",
            material_classification=MaterialClassification.OPAQUE,
            roughness_range=[0.75, 0.98],
            metallic_range=[0.0, 0.05],
            base_color_hex="#8A8A88",
            wears=[SurfaceWearType.DIRT, SurfaceWearType.ABRASION],
            seed=seed,
        )
        graph = MaterialGraphContract(
            graph_id=f"{surf_id}_Graph",
            master_material_id="M_Master_Architecture",
            parameters={"DirtAmount": 0.5, "MacroBreakup": 1.0},
            material_functions=["Dirt", "Triplanar"],
            has_triplanar=True,
        )
        textures = [f"T_{surf_id}_BC", f"T_{surf_id}_N", f"T_{surf_id}_ORM"]
        return prof, graph, textures

    @classmethod
    def build_wood_surface(cls, surf_id: str = "Surf_Varnished_Walnut", seed: int = 505) -> Tuple[SurfaceProfile, MaterialGraphContract, List[str]]:
        """5. Wood Material (Anisotropic grain, glossy varnish coats)."""
        prof = SurfaceProfile(
            surface_id=surf_id,
            surface_type="WOOD",
            material_classification=MaterialClassification.OPAQUE,
            roughness_range=[0.25, 0.65],
            metallic_range=[0.0, 0.0],
            base_color_hex="#5C3A21",
            seed=seed,
        )
        graph = MaterialGraphContract(
            graph_id=f"{surf_id}_Graph",
            master_material_id="M_Master_WoodPBR",
            parameters={"GrainDepth": 0.3, "ClearCoat": 0.8},
            material_functions=["DetailBlend"],
        )
        textures = [f"T_{surf_id}_BC", f"T_{surf_id}_N", f"T_{surf_id}_ORM"]
        return prof, graph, textures

    @classmethod
    def build_stone_surface(cls, surf_id: str = "Surf_Granite_Cliff", seed: int = 606) -> Tuple[SurfaceProfile, MaterialGraphContract, List[str]]:
        """6. Stone Material (Chiseled rock with triplanar mapping)."""
        prof = SurfaceProfile(
            surface_id=surf_id,
            surface_type="STONE",
            material_classification=MaterialClassification.OPAQUE,
            roughness_range=[0.6, 0.9],
            metallic_range=[0.0, 0.0],
            base_color_hex="#68625E",
            seed=seed,
        )
        graph = MaterialGraphContract(
            graph_id=f"{surf_id}_Graph",
            master_material_id="M_Master_NaturalStone",
            parameters={"TriplanarScale": 4.0},
            material_functions=["Triplanar", "NormalBlend"],
            has_triplanar=True,
        )
        textures = [f"T_{surf_id}_BC", f"T_{surf_id}_N", f"T_{surf_id}_ORM"]
        return prof, graph, textures

    @classmethod
    def build_glass_surface(cls, surf_id: str = "Surf_Architectural_Glass", seed: int = 707) -> Tuple[SurfaceProfile, MaterialGraphContract, List[str]]:
        """7. Glass Material (Refractive translucent with surface smudges)."""
        prof = SurfaceProfile(
            surface_id=surf_id,
            surface_type="GLASS",
            material_classification=MaterialClassification.TRANSLUCENT,
            roughness_range=[0.05, 0.2],
            metallic_range=[0.0, 0.0],
            base_color_hex="#EBF5FB",
            wears=[SurfaceWearType.DIRT],
            seed=seed,
        )
        graph = MaterialGraphContract(
            graph_id=f"{surf_id}_Graph",
            master_material_id="M_Master_TranslucentGlass",
            parameters={"IOR": 1.52, "Opacity": 0.15},
            material_functions=["DetailBlend"],
        )
        textures = [f"T_{surf_id}_BC", f"T_{surf_id}_N", f"T_{surf_id}_ORM"]
        return prof, graph, textures

    @classmethod
    def build_vegetation_surface(cls, surf_id: str = "Surf_Jungle_Leaves", seed: int = 808) -> Tuple[SurfaceProfile, MaterialGraphContract, List[str]]:
        """8. Vegetation Material (Two-sided foliage shading with transmission)."""
        prof = SurfaceProfile(
            surface_id=surf_id,
            surface_type="VEGETATION",
            material_classification=MaterialClassification.FOLIAGE,
            roughness_range=[0.3, 0.7],
            metallic_range=[0.0, 0.0],
            base_color_hex="#228B22",
            seed=seed,
        )
        graph = MaterialGraphContract(
            graph_id=f"{surf_id}_Graph",
            master_material_id="M_Master_TwoSidedFoliage",
            parameters={"SubsurfaceTransmission": 0.65},
            material_functions=["DetailBlend"],
        )
        textures = [f"T_{surf_id}_BC", f"T_{surf_id}_N", f"T_{surf_id}_ORM", f"T_{surf_id}_Opacity"]
        return prof, graph, textures

    @classmethod
    def build_terrain_surface(cls, surf_id: str = "Surf_Landscape_Terrain", seed: int = 909) -> Tuple[SurfaceProfile, MaterialGraphContract, List[str]]:
        """9. Terrain Material (World-aligned slope blend between rock and grass)."""
        prof = SurfaceProfile(
            surface_id=surf_id,
            surface_type="TERRAIN",
            material_classification=MaterialClassification.OPAQUE,
            roughness_range=[0.65, 0.95],
            metallic_range=[0.0, 0.0],
            base_color_hex="#4D5D38",
            seed=seed,
        )
        graph = MaterialGraphContract(
            graph_id=f"{surf_id}_Graph",
            master_material_id="M_Master_LandscapeTerrain",
            parameters={"SlopeThreshold": 0.45},
            material_functions=["WorldAligned", "Triplanar"],
            has_triplanar=True,
        )
        textures = [f"T_{surf_id}_Rock_BC", f"T_{surf_id}_Soil_BC", f"T_{surf_id}_N", f"T_{surf_id}_ORM"]
        return prof, graph, textures

    @classmethod
    def build_energy_surface(cls, surf_id: str = "Surf_Plasma_Shield", seed: int = 1010) -> Tuple[SurfaceProfile, MaterialGraphContract, List[str]]:
        """10. Energy Material (Additive pulsating emissive hologram)."""
        prof = SurfaceProfile(
            surface_id=surf_id,
            surface_type="ENERGY",
            material_classification=MaterialClassification.ADDITIVE,
            roughness_range=[0.0, 0.1],
            metallic_range=[0.0, 0.0],
            base_color_hex="#00FFFF",
            seed=seed,
        )
        graph = MaterialGraphContract(
            graph_id=f"{surf_id}_Graph",
            master_material_id="M_Master_AdditiveEnergy",
            parameters={"PulseSpeed": 2.5, "EmissiveStrength": 12.0},
            material_functions=["Noise"],
        )
        textures = [f"T_{surf_id}_Emissive", f"T_{surf_id}_Noise"]
        return prof, graph, textures
