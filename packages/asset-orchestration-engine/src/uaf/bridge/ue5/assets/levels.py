"""Level and World hierarchy container bridge."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class LevelBridgePayload:
    level_id: str
    level_name: str
    is_world_partition: bool = True
    sublevels: List[str] = field(default_factory=list)
    data_layers: List[str] = field(default_factory=list)
    hlod_layers: List[str] = field(default_factory=list)
    default_game_mode: str = "GameModeBase"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level_id": self.level_id,
            "level_name": self.level_name,
            "is_world_partition": self.is_world_partition,
            "sublevels": self.sublevels,
            "data_layers": self.data_layers,
            "hlod_layers": self.hlod_layers,
            "default_game_mode": self.default_game_mode,
            "metadata": self.metadata,
        }
