"""
ArchetypeRegistry manages cataloging and querying of asset archetypes.
UAF-81.1 Section 14.
"""

from typing import Dict, List, Optional
from ...contracts.registry import BaseRegistry
from ...core.identity.asset_types import AssetType
from .archetype import AssetArchetype


class ArchetypeRegistry(BaseRegistry[AssetArchetype]):
    """
    Registry for querying and validating archetypes.
    Pre-populates the normative archetypes defined in UAF-81.1 Section 14.
    """
    def __init__(self):
        super().__init__(name="ArchetypeRegistry")
        self._init_standard_archetypes()

    def _init_standard_archetypes(self) -> None:
        standard = [
            AssetArchetype(
                archetype_id="HumanoidCharacter",
                asset_type=AssetType.CHARACTER,
                description="Standard bipedal humanoid character with anatomical hierarchy.",
                required_parameters=["height", "build"],
                default_parameters={"height": 1.80, "build": "athletic", "species": "humanoid"},
                required_capabilities=["organic_surface_generation", "skeletal_rigging", "skin_weight_generation"],
                supported_targets=["generic", "unreal", "blender"],
            ),
            AssetArchetype(
                archetype_id="Creature",
                asset_type=AssetType.CREATURE,
                description="Non-humanoid quadrupedal or exotic organic creature.",
                required_parameters=["scale", "morphology"],
                default_parameters={"scale": 1.0, "morphology": "quadruped"},
                required_capabilities=["organic_surface_generation", "creature_rigging"],
                supported_targets=["generic", "unreal", "blender"],
            ),
            AssetArchetype(
                archetype_id="MilitaryWeapon",
                asset_type=AssetType.WEAPON,
                description="Firearm or tactical weapon with mechanical parts and attachments.",
                required_parameters=["weapon_type", "caliber"],
                default_parameters={"weapon_type": "rifle", "caliber": "standard"},
                required_capabilities=["hard_surface_modeling", "mechanical_assembly"],
                supported_targets=["generic", "unreal"],
            ),
            AssetArchetype(
                archetype_id="SciFiProp",
                asset_type=AssetType.PROP,
                description="Generic hard-surface or electronic scientific/tactical prop.",
                required_parameters=["dimensions"],
                default_parameters={"dimensions": [1.0, 1.0, 1.0]},
                required_capabilities=["hard_surface_modeling"],
                supported_targets=["generic", "unreal", "blender"],
            ),
            AssetArchetype(
                archetype_id="ModularWall",
                asset_type=AssetType.MODULAR_KIT,
                description="Structural architectural wall piece with socket connectors.",
                required_parameters=["dimensions", "grid_size"],
                default_parameters={"dimensions": [2.0, 3.0, 0.2], "grid_size": 1.0},
                required_capabilities=["modular_assembly", "socket_alignment"],
                supported_targets=["generic", "unreal"],
            ),
            AssetArchetype(
                archetype_id="Building",
                asset_type=AssetType.ARCHITECTURE,
                description="Composite multi-story building assembled from modular elements.",
                required_parameters=["footprint", "floors"],
                default_parameters={"footprint": [10.0, 10.0], "floors": 2},
                required_capabilities=["composite_assembly", "lod_generation"],
                supported_targets=["generic", "unreal"],
            ),
            AssetArchetype(
                archetype_id="Material",
                asset_type=AssetType.MATERIAL,
                description="PBR surface shader declaration with multilayer wear.",
                required_parameters=["base_color", "roughness"],
                default_parameters={"base_color": "#808080", "roughness": 0.5, "metallic": 0.0},
                required_capabilities=["pbr_material_compilation"],
                supported_targets=["generic", "unreal", "blender"],
            ),
            AssetArchetype(
                archetype_id="TextureSet",
                asset_type=AssetType.TEXTURE,
                description="Cohesive PBR texture map bundle.",
                required_parameters=["resolution"],
                default_parameters={"resolution": 2048},
                required_capabilities=["texture_baking", "channel_packing"],
                supported_targets=["generic", "unreal"],
            ),
            AssetArchetype(
                archetype_id="Terrain",
                asset_type=AssetType.ENVIRONMENT,
                description="Heightmap and biome surface terrain tile.",
                required_parameters=["heightmap_resolution", "dimensions"],
                default_parameters={"heightmap_resolution": 1024, "dimensions": [1000.0, 1000.0]},
                required_capabilities=["heightmap_generation", "splatmap_generation"],
                supported_targets=["generic", "unreal"],
            ),
            AssetArchetype(
                archetype_id="OpenWorldRegion",
                asset_type=AssetType.WORLD,
                description="Open world partitioned landscape with biomes and streaming.",
                required_parameters=["cell_size", "region_count"],
                default_parameters={"cell_size": 512.0, "region_count": 4},
                required_capabilities=["world_partitioning", "landscape_streaming"],
                supported_targets=["generic", "unreal"],
            ),
        ]
        for a in standard:
            self.register(a.archetype_id, a, overwrite=True)
