"""
WorldBuildFabricationPlatform manufactures canonical Golden Worlds matching Section 153.
UAF-81.40 Sections 153, 149.
"""

from typing import Tuple, List, Dict, Any
from ..models.definition import (
    WorldBuildSpecification,
    WorldScaleProfile40,
    RegionType40,
    WorldDimensions40,
)


class WorldBuildFabricationPlatform:
    """
    Synthesizes complete, production-grade procedural worlds, maps, landscapes, and partitions for Unreal Engine.
    """

    @classmethod
    def build_golden_small_world(cls, world_id: str = "World_Gold_Small") -> Tuple[WorldBuildSpecification, str, str]:
        """1. GOLDEN_SMALL_WORLD (Section 153: 1000x1000m, contained arena world)."""
        dims = WorldDimensions40(width_m=1000.0, length_m=1000.0, height_m=100.0)
        spec = WorldBuildSpecification(world_id, WorldScaleProfile40.SMALL, RegionType40.RURAL, dims, cell_count=1, has_world_partition=False, has_hydrology=False, road_count=1)
        return spec, f"/Game/Worlds/{world_id}/Level_{world_id}", f"/Game/Worlds/{world_id}/Partition/WP_{world_id}"

    @classmethod
    def build_golden_forest_world(cls, world_id: str = "World_Gold_Forest") -> Tuple[WorldBuildSpecification, str, str]:
        """2. GOLDEN_FOREST_WORLD (Section 153: 2000x2000m, temperate forest canopy, winding river)."""
        dims = WorldDimensions40(width_m=2000.0, length_m=2000.0, height_m=250.0)
        spec = WorldBuildSpecification(world_id, WorldScaleProfile40.MEDIUM, RegionType40.FOREST, dims, cell_count=4, has_world_partition=True, has_hydrology=True, road_count=2)
        return spec, f"/Game/Worlds/{world_id}/Level_{world_id}", f"/Game/Worlds/{world_id}/Partition/WP_{world_id}"

    @classmethod
    def build_golden_desert_world(cls, world_id: str = "World_Gold_Desert") -> Tuple[WorldBuildSpecification, str, str]:
        """3. GOLDEN_DESERT_WORLD (Section 153: 4000x4000m, arid dunes, highway network, oasis)."""
        dims = WorldDimensions40(width_m=4000.0, length_m=4000.0, height_m=350.0)
        spec = WorldBuildSpecification(world_id, WorldScaleProfile40.LARGE, RegionType40.DESERT, dims, cell_count=16, has_world_partition=True, has_hydrology=True, road_count=4)
        return spec, f"/Game/Worlds/{world_id}/Level_{world_id}", f"/Game/Worlds/{world_id}/Partition/WP_{world_id}"

    @classmethod
    def build_golden_industrial_world(cls, world_id: str = "World_Gold_Industrial") -> Tuple[WorldBuildSpecification, str, str]:
        """4. GOLDEN_INDUSTRIAL_WORLD (Section 153: 2500x2500m, heavy manufacturing sector, paved roads)."""
        dims = WorldDimensions40(width_m=2500.0, length_m=2500.0, height_m=180.0)
        spec = WorldBuildSpecification(world_id, WorldScaleProfile40.MEDIUM, RegionType40.INDUSTRIAL, dims, cell_count=6, has_world_partition=True, has_hydrology=False, road_count=6)
        return spec, f"/Game/Worlds/{world_id}/Level_{world_id}", f"/Game/Worlds/{world_id}/Partition/WP_{world_id}"

    @classmethod
    def build_golden_urban_world(cls, world_id: str = "World_Gold_Urban") -> Tuple[WorldBuildSpecification, str, str]:
        """5. GOLDEN_URBAN_WORLD (Section 153: 3000x3000m, city blocks, grid streets, multi-building clusters)."""
        dims = WorldDimensions40(width_m=3000.0, length_m=3000.0, height_m=220.0)
        spec = WorldBuildSpecification(world_id, WorldScaleProfile40.LARGE, RegionType40.URBAN, dims, cell_count=9, has_world_partition=True, has_hydrology=False, road_count=12)
        return spec, f"/Game/Worlds/{world_id}/Level_{world_id}", f"/Game/Worlds/{world_id}/Partition/WP_{world_id}"

    @classmethod
    def build_golden_mountain_world(cls, world_id: str = "World_Gold_Mountain") -> Tuple[WorldBuildSpecification, str, str]:
        """6. GOLDEN_MOUNTAIN_WORLD (Section 153: 4000x4000m, alpine ridges, steep cliffs, mountain passes)."""
        dims = WorldDimensions40(width_m=4000.0, length_m=4000.0, height_m=1200.0)
        spec = WorldBuildSpecification(world_id, WorldScaleProfile40.LARGE, RegionType40.MOUNTAIN, dims, cell_count=16, has_world_partition=True, has_hydrology=True, road_count=3)
        return spec, f"/Game/Worlds/{world_id}/Level_{world_id}", f"/Game/Worlds/{world_id}/Partition/WP_{world_id}"

    @classmethod
    def build_golden_sci_fi_world(cls, world_id: str = "World_Gold_SciFi") -> Tuple[WorldBuildSpecification, str, str]:
        """7. GOLDEN_SCI_FI_WORLD (Section 153: 3000x3000m, extraterrestrial outpost, landing pads, energy conduits)."""
        dims = WorldDimensions40(width_m=3000.0, length_m=3000.0, height_m=400.0)
        spec = WorldBuildSpecification(world_id, WorldScaleProfile40.LARGE, RegionType40.CUSTOM, dims, cell_count=9, has_world_partition=True, has_hydrology=False, road_count=5)
        return spec, f"/Game/Worlds/{world_id}/Level_{world_id}", f"/Game/Worlds/{world_id}/Partition/WP_{world_id}"

    @classmethod
    def build_golden_combat_world(cls, world_id: str = "World_Gold_Combat") -> Tuple[WorldBuildSpecification, str, str]:
        """8. GOLDEN_COMBAT_WORLD (Section 153: 1500x1500m, balanced cover positions, spawn symmetry, tactical choke points)."""
        dims = WorldDimensions40(width_m=1500.0, length_m=1500.0, height_m=120.0)
        spec = WorldBuildSpecification(world_id, WorldScaleProfile40.MEDIUM, RegionType40.MILITARY, dims, cell_count=2, has_world_partition=True, has_hydrology=False, road_count=3)
        return spec, f"/Game/Worlds/{world_id}/Level_{world_id}", f"/Game/Worlds/{world_id}/Partition/WP_{world_id}"
