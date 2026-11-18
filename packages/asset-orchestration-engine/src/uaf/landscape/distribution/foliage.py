"""
UAF-81.91: Poisson-Disk Foliage Distribution & UE5 PCG Substrate.
Distributes natural vegetation, trees, and geological scatter using Bridson's
blue-noise sampling constrained by biome, slope, altitude, and clearance corridors.
"""

from __future__ import annotations

import math
import random
from typing import Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

from uaf.landscape.core.contracts import (
    BiomeType,
    RoadPath,
    Heightfield2D,
)
from uaf.landscape.ecology.biomes import WhittakerBiomeClassifier, ClimateMap


class FoliageInstance(BaseModel):
    """Represents a scattered tree, rock, or vegetation actor."""
    instance_id: str
    asset_type: str  # "TREE", "ROCK", "BUSH"
    mesh_path: str
    world_pos: Tuple[float, float, float]  # [X, Y, Z] in Unreal cm
    rotation_deg: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # [Pitch, Yaw, Roll]
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    biome: BiomeType


class PoissonDiskSampler2D:
    """
    Fast 2D Poisson-Disk sampling using Bridson's algorithm.
    Guarantees that no two sample points are closer than min_dist_m.
    """

    def __init__(self, min_dist_m: float = 6.0, k_candidates: int = 30, seed: int = 42):
        self.min_dist = min_dist_m
        self.k = k_candidates
        self.rng = random.Random(seed)

    def sample(self, width_m: float, height_m: float) -> List[Tuple[float, float]]:
        """Generates 2D coordinates in [0, width_m] x [0, height_m]."""
        cell_size = self.min_dist / math.sqrt(2.0)
        grid_w = int(math.ceil(width_m / cell_size))
        grid_h = int(math.ceil(height_m / cell_size))

        grid: List[List[Optional[Tuple[float, float]]]] = [
            [None for _ in range(grid_w)] for _ in range(grid_h)
        ]

        active_list: List[Tuple[float, float]] = []
        samples: List[Tuple[float, float]] = []

        # Initial point
        p0 = (self.rng.uniform(0.0, width_m), self.rng.uniform(0.0, height_m))
        samples.append(p0)
        active_list.append(p0)

        g0_x = int(p0[0] / cell_size)
        g0_y = int(p0[1] / cell_size)
        grid[g0_y][g0_x] = p0

        while active_list:
            idx = self.rng.randint(0, len(active_list) - 1)
            px, py = active_list[idx]
            found = False

            for _ in range(self.k):
                angle = self.rng.uniform(0.0, 2.0 * math.pi)
                radius = self.rng.uniform(self.min_dist, 2.0 * self.min_dist)
                cand_x = px + math.cos(angle) * radius
                cand_y = py + math.sin(angle) * radius

                if not (0.0 <= cand_x < width_m and 0.0 <= cand_y < height_m):
                    continue

                cg_x = int(cand_x / cell_size)
                cg_y = int(cand_y / cell_size)

                # Check neighborhood
                too_close = False
                for ox in (-2, -1, 0, 1, 2):
                    for oy in (-2, -1, 0, 1, 2):
                        nx, ny = cg_x + ox, cg_y + oy
                        if 0 <= nx < grid_w and 0 <= ny < grid_h:
                            neighbor = grid[ny][nx]
                            if neighbor is not None:
                                dist = math.hypot(cand_x - neighbor[0], cand_y - neighbor[1])
                                if dist < self.min_dist:
                                    too_close = True
                                    break
                    if too_close:
                        break

                if not too_close:
                    pt = (cand_x, cand_y)
                    samples.append(pt)
                    active_list.append(pt)
                    grid[cg_y][cg_x] = pt
                    found = True
                    break

            if not found:
                active_list.pop(idx)

        return samples


class PCGFoliageDistributor:
    """
    Applies ecological rules and physical constraints to scatter foliage and rock assets
    over a terrain heightfield.
    """

    BIOME_MESHES: Dict[BiomeType, Dict[str, List[str]]] = {
        BiomeType.CONIFEROUS_FOREST: {
            "TREE": ["/Game/Megascans/Foliage/Pine_01.Pine_01", "/Game/Megascans/Foliage/Spruce_02.Spruce_02"],
            "ROCK": ["/Game/Megascans/Rocks/Granite_Boulder_01.Granite_Boulder_01"],
        },
        BiomeType.TEMPERATE_FOREST: {
            "TREE": ["/Game/Megascans/Foliage/Oak_01.Oak_01", "/Game/Megascans/Foliage/Birch_03.Birch_03"],
            "ROCK": ["/Game/Megascans/Rocks/Limestone_Rock_02.Limestone_Rock_02"],
        },
        BiomeType.GRASSLAND: {
            "TREE": ["/Game/Megascans/Foliage/Acacia_01.Acacia_01"],
            "ROCK": ["/Game/Megascans/Rocks/Fieldstone_01.Fieldstone_01"],
        },
        BiomeType.ALPINE: {
            "TREE": [],  # Above tree line
            "ROCK": ["/Game/Megascans/Rocks/Alpine_Slate_01.Alpine_Slate_01", "/Game/Megascans/Rocks/Cliff_Shard_04.Cliff_Shard_04"],
        },
        BiomeType.TUNDRA: {
            "TREE": [],
            "ROCK": ["/Game/Megascans/Rocks/Permafrost_Stone_01.Permafrost_Stone_01"],
        },
        BiomeType.DESERT: {
            "TREE": ["/Game/Megascans/Foliage/Desert_Palm_01.Desert_Palm_01"],
            "ROCK": ["/Game/Megascans/Rocks/Sandstone_Crag_01.Sandstone_Crag_01"],
        },
        BiomeType.WETLAND: {
            "TREE": ["/Game/Megascans/Foliage/Willow_01.Willow_01"],
            "ROCK": ["/Game/Megascans/Rocks/Mossy_Boulder_01.Mossy_Boulder_01"],
        },
    }

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)

    def distribute_foliage(
        self,
        heightfield: Heightfield2D,
        climate: ClimateMap,
        roads: Optional[List[RoadPath]] = None,
        min_tree_spacing_m: float = 7.0,
        max_tree_slope_deg: float = 28.0,
        tree_line_altitude_m: float = 1200.0,
    ) -> List[FoliageInstance]:
        """
        Generates non-overlapping foliage instances across the heightfield
        obeying ecological rules, slope thresholds, and road clearances.
        """
        w, h = heightfield.width, heightfield.height
        total_w_m = w * heightfield.meters_per_cell
        total_h_m = h * heightfield.meters_per_cell

        # 1. Poisson-disk candidate points
        sampler = PoissonDiskSampler2D(min_dist_m=min_tree_spacing_m, seed=self.seed)
        candidate_points = sampler.sample(total_w_m, total_h_m)

        instances: List[FoliageInstance] = []
        inst_idx = 0

        # Build clearance zone for roads
        road_clearance_boxes: List[Tuple[float, float, float]] = []  # (world_x, world_y, radius)
        if roads:
            for road in roads:
                for node in road.nodes:
                    road_clearance_boxes.append((node.world_pos[0], node.world_pos[1], node.width_cm * 0.7))

        for px_m, py_m in candidate_points:
            # Map meters to grid cells
            gx = int(px_m / heightfield.meters_per_cell)
            gy = int(py_m / heightfield.meters_per_cell)

            if not (0 <= gx < w and 0 <= gy < h):
                continue

            world_x, world_y, world_z = heightfield.get_world_coords_cm(gx, gy)
            slope = heightfield.compute_slope_angle_deg(gx, gy)
            alt_m = heightfield.get_world_elevation_meters(gx, gy)

            # Check road clearance
            in_road_corridor = False
            for rx, ry, r_clear in road_clearance_boxes:
                if math.hypot(world_x - rx, world_y - ry) < r_clear:
                    in_road_corridor = True
                    break

            if in_road_corridor:
                continue

            temp = climate.temperature[gy][gx]
            precip = climate.precipitation[gy][gx]
            biome = WhittakerBiomeClassifier.classify(temp, precip, alt_m)

            # Determine whether to place tree or rock
            biome_dict = self.BIOME_MESHES.get(biome, {})
            tree_meshes = biome_dict.get("TREE", [])
            rock_meshes = biome_dict.get("ROCK", [])

            is_tree = (slope <= max_tree_slope_deg) and (alt_m < tree_line_altitude_m) and bool(tree_meshes)

            if is_tree and tree_meshes:
                mesh = self.rng.choice(tree_meshes)
                asset_type = "TREE"
                scale_val = self.rng.uniform(0.85, 1.25)
                scale = (scale_val, scale_val, scale_val * self.rng.uniform(0.9, 1.15))
            elif rock_meshes:
                mesh = self.rng.choice(rock_meshes)
                asset_type = "ROCK"
                scale_val = self.rng.uniform(0.7, 1.6)
                scale = (scale_val, scale_val, scale_val)
            else:
                continue

            yaw = self.rng.uniform(0.0, 360.0)
            pitch = self.rng.uniform(-2.0, 2.0)
            roll = self.rng.uniform(-2.0, 2.0)

            instances.append(
                FoliageInstance(
                    instance_id=f"Foliage_{inst_idx}",
                    asset_type=asset_type,
                    mesh_path=mesh,
                    world_pos=(round(world_x, 2), round(world_y, 2), round(world_z, 2)),
                    rotation_deg=(round(pitch, 1), round(yaw, 1), round(roll, 1)),
                    scale=(round(scale[0], 2), round(scale[1], 2), round(scale[2], 2)),
                    biome=biome,
                )
            )
            inst_idx += 1

        return instances
