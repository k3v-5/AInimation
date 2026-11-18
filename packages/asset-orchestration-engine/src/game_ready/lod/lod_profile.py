from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class LODLevelConfig:
    level: int
    screen_size: float
    reduction_ratio: float # 1.0 = 100%, 0.5 = 50%, etc.
    max_triangles: int
    max_visual_deviation: float = 0.03

@dataclass
class GameReadyLODProfile:
    name: str = "DEFAULT_GAME_ASSET"
    levels: Dict[int, LODLevelConfig] = field(default_factory=lambda: {
        0: LODLevelConfig(level=0, screen_size=1.0, reduction_ratio=1.0, max_triangles=10000, max_visual_deviation=0.00),
        1: LODLevelConfig(level=1, screen_size=0.5, reduction_ratio=0.5, max_triangles=5000, max_visual_deviation=0.04),
        2: LODLevelConfig(level=2, screen_size=0.2, reduction_ratio=0.25, max_triangles=2000, max_visual_deviation=0.06),
        3: LODLevelConfig(level=3, screen_size=0.05, reduction_ratio=0.10, max_triangles=800, max_visual_deviation=0.08)
    })
