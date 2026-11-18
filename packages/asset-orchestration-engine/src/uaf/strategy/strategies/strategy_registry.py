"""
StrategyRegistry catalogs and queries generation strategies.
UAF-81.2 Section 64.
"""

from typing import List, Optional
from ...contracts.registry import BaseRegistry
from ...core.identity.asset_types import AssetType
from .generation_strategy import GenerationStrategy
from .strategy_category import StrategyCategory, DeterminismMode


class StrategyRegistry(BaseRegistry[GenerationStrategy]):
    """
    Registry indexing all available production strategies across asset categories.
    """
    def __init__(self):
        super().__init__(name="StrategyRegistry")
        self._init_standard_strategies()

    def _init_standard_strategies(self) -> None:
        standards = [
            GenerationStrategy(
                strategy_id="PrimitiveProceduralStrategy",
                name="Primitive Procedural Strategy",
                category=StrategyCategory.PROCEDURAL,
                description="Fast CSG/primitive procedural synthesis for low complexity props or primitive avatars.",
                supported_assets=[AssetType.PROP, AssetType.CHARACTER, AssetType.WEAPON],
                required_capabilities=["primitive_procedural_geometry"],
                optional_capabilities=["basic_material"],
                quality_rating=0.3,
                cost_rating=0.1,
                risk_rating=0.05,
                determinism=DeterminismMode.SEEDED_DETERMINISTIC,
                supported_complexities=["C0"],
                pipeline_node_templates=[
                    {"node_id": "primitive_mesh", "capability": "primitive_procedural_geometry", "dependencies": []},
                    {"node_id": "basic_mat", "capability": "basic_material", "dependencies": ["primitive_mesh"]},
                ],
            ),
            GenerationStrategy(
                strategy_id="ParametricHumanoidStrategy",
                name="Parametric Humanoid Strategy",
                category=StrategyCategory.PARAMETRIC,
                description="Parametric bipedal geometry generation for game characters (C1-C2).",
                supported_assets=[AssetType.CHARACTER],
                required_capabilities=["parametric_anatomy", "basic_rigging"],
                optional_capabilities=["basic_facial_mesh"],
                quality_rating=0.6,
                cost_rating=0.3,
                risk_rating=0.15,
                determinism=DeterminismMode.SEEDED_DETERMINISTIC,
                supported_complexities=["C1", "C2"],
                pipeline_node_templates=[
                    {"node_id": "anatomy_mesh", "capability": "parametric_anatomy", "dependencies": []},
                    {"node_id": "skeleton_rig", "capability": "basic_rigging", "dependencies": ["anatomy_mesh"]},
                ],
            ),
            GenerationStrategy(
                strategy_id="HybridCharacterStrategy",
                name="Hybrid Character Strategy",
                category=StrategyCategory.HYBRID,
                description="Production hybrid pipeline combining anatomical forms, modular armor, and procedural texturing (C3).",
                supported_assets=[AssetType.CHARACTER],
                required_capabilities=["organic_surface_generation", "skeletal_rigging", "cloth_geometry"],
                optional_capabilities=["advanced_facial_generation"],
                quality_rating=0.8,
                cost_rating=0.6,
                risk_rating=0.25,
                determinism=DeterminismMode.SEEDED_DETERMINISTIC,
                supported_complexities=["C3"],
                pipeline_node_templates=[
                    {"node_id": "anatomy", "capability": "organic_surface_generation", "dependencies": []},
                    {"node_id": "cloth", "capability": "cloth_geometry", "dependencies": ["anatomy"]},
                    {"node_id": "rig", "capability": "skeletal_rigging", "dependencies": ["anatomy", "cloth"]},
                ],
            ),
            GenerationStrategy(
                strategy_id="AdvancedHeroCharacterStrategy",
                name="Advanced Hero Character Strategy",
                category=StrategyCategory.HYBRID,
                description="Highest fidelity character synthesis: facial microdetail, high-frequency anatomy, clothing, and production skinning (C4-C5).",
                supported_assets=[AssetType.CHARACTER],
                required_capabilities=[
                    "organic_surface_generation",
                    "skeletal_rigging",
                    "advanced_facial_generation",
                    "cloth_geometry",
                    "high_detail_surface",
                ],
                optional_capabilities=["skin_weight_generation", "advanced_topology"],
                quality_rating=0.95,
                cost_rating=0.85,
                risk_rating=0.3,
                determinism=DeterminismMode.SEEDED_DETERMINISTIC,
                supported_complexities=["C4", "C5"],
                pipeline_node_templates=[
                    {"node_id": "anatomy", "capability": "organic_surface_generation", "dependencies": []},
                    {"node_id": "face", "capability": "advanced_facial_generation", "dependencies": ["anatomy"]},
                    {"node_id": "cloth", "capability": "cloth_geometry", "dependencies": ["anatomy"]},
                    {"node_id": "surface_detail", "capability": "high_detail_surface", "dependencies": ["anatomy", "face", "cloth"]},
                    {"node_id": "rig", "capability": "skeletal_rigging", "dependencies": ["surface_detail"]},
                ],
            ),
            GenerationStrategy(
                strategy_id="ModularAssemblyStrategy",
                name="Modular Assembly Strategy",
                category=StrategyCategory.MODULAR,
                description="Socket-matching and grid-aligned assembly for architecture, kits, and levels.",
                supported_assets=[AssetType.MODULAR_KIT, AssetType.ARCHITECTURE, AssetType.PROP],
                required_capabilities=["modular_assembly", "socket_alignment"],
                optional_capabilities=["lod_generation"],
                quality_rating=0.75,
                cost_rating=0.4,
                risk_rating=0.1,
                determinism=DeterminismMode.DETERMINISTIC,
                pipeline_node_templates=[
                    {"node_id": "module_layout", "capability": "modular_assembly", "dependencies": []},
                    {"node_id": "sockets", "capability": "socket_alignment", "dependencies": ["module_layout"]},
                ],
            ),
        ]
        for s in standards:
            self.register(s.strategy_id, s, overwrite=True)

    def find_for_asset(self, asset_type: AssetType) -> List[GenerationStrategy]:
        return self.find(lambda s: asset_type in s.supported_assets)
