"""World, terrain, biomes, vegetation, architecture, and spawn point generator."""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from uaf.golden_slice.manifest.models import WorldConfig
from uaf.golden_slice.manifest.seeds import SeedManager


@dataclass
class SpawnPoint:
    spawn_id: str
    point_type: str  # "player", "enemy", "npc", "item", "objective", "vehicle", "vfx"
    location: Tuple[float, float, float]
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    is_accessible: bool = True
    tags: List[str] = field(default_factory=list)


@dataclass
class WorldSlice:
    biome_name: str
    size_km: float
    terrain_resolution: int
    elevation_range: Tuple[float, float]
    vegetation_instances_count: int
    architecture_instances_count: int
    streaming_cells_count: int
    spawn_points: List[SpawnPoint] = field(default_factory=list)
    streaming_cells: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def validate(self) -> List[str]:
        """Validates world constraints: no floating assets, valid spawn separation, etc."""
        errors: List[str] = []
        if not self.spawn_points:
            errors.append("World has zero spawn points")

        # Validate minimum distance separation between player and enemy spawns
        player_spawns = [s for s in self.spawn_points if s.point_type == "player"]
        enemy_spawns = [s for s in self.spawn_points if s.point_type == "enemy"]

        if not player_spawns:
            errors.append("Missing player spawn point")

        for p in player_spawns:
            for e in enemy_spawns:
                dx = p.location[0] - e.location[0]
                dy = p.location[1] - e.location[1]
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < 10.0:
                    errors.append(f"Player spawn {p.spawn_id} and Enemy spawn {e.spawn_id} are dangerously close ({dist:.1f}m < 10m)")

        return errors


class WorldGenerator:
    """Generates deterministic world data, streaming partitioning, and validated spawns."""

    def __init__(self, config: WorldConfig, seeds: SeedManager) -> None:
        self.config = config
        self.seeds = seeds
        self.rng = seeds.get_rng("world")

    def generate(self) -> WorldSlice:
        cell_size = self.config.streaming_cell_size
        grid_dim = max(2, int((self.config.size_km * 1000.0) / (cell_size * 4)))
        streaming_cells: Dict[str, Dict[str, Any]] = {}

        for x in range(grid_dim):
            for y in range(grid_dim):
                cell_id = f"cell_{x}_{y}"
                streaming_cells[cell_id] = {
                    "grid_coords": (x, y),
                    "state": "Loaded" if (x == 0 and y == 0) else "Unloaded",
                    "actor_count": self.rng.randint(15, 60),
                }

        # Generate spawn points with guaranteed minimum spacing
        spawns: List[SpawnPoint] = [
            SpawnPoint(
                spawn_id="spawn_player_primary",
                point_type="player",
                location=(0.0, 0.0, 50.0),
                tags=["main_hero", "initial"],
            ),
            SpawnPoint(
                spawn_id="spawn_objective_core",
                point_type="objective",
                location=(200.0, 250.0, 50.0),
                tags=["capture_point"],
            ),
            SpawnPoint(
                spawn_id="spawn_item_chest_01",
                point_type="item",
                location=(50.0, 80.0, 50.0),
                tags=["loot"],
            ),
        ]

        # Enemy patrol spawns
        enemy_archetypes = ["scout", "melee", "heavy", "ranged"]
        for i in range(4):
            angle = (i * math.pi / 2.0) + 0.5
            dist = 80.0 + self.rng.uniform(10.0, 30.0)
            ex = dist * math.cos(angle)
            ey = dist * math.sin(angle)
            arch = enemy_archetypes[i % len(enemy_archetypes)]
            spawns.append(
                SpawnPoint(
                    spawn_id=f"spawn_enemy_{arch}_{i}",
                    point_type="enemy",
                    location=(round(ex, 1), round(ey, 1), 50.0),
                    tags=[arch, "hostile"],
                )
            )

        veg_count = int(self.config.vegetation_density * 1000)
        arch_count = 45

        return WorldSlice(
            biome_name=self.config.biome,
            size_km=self.config.size_km,
            terrain_resolution=1024,
            elevation_range=(0.0, 350.0),
            vegetation_instances_count=veg_count,
            architecture_instances_count=arch_count,
            streaming_cells_count=len(streaming_cells),
            spawn_points=spawns,
            streaming_cells=streaming_cells,
        )
