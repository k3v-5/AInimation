"""Task definitions and typed representations for vertical slice generation DAG."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskType(str, Enum):
    WORLD_TERRAIN = "WORLD_TERRAIN"
    WORLD_VEGETATION = "WORLD_VEGETATION"
    WORLD_ARCHITECTURE = "WORLD_ARCHITECTURE"
    WORLD_STREAMING = "WORLD_STREAMING"
    CHARACTER_SKELETON = "CHARACTER_SKELETON"
    CHARACTER_ANIMATION = "CHARACTER_ANIMATION"
    CHARACTER_ANIMBP = "CHARACTER_ANIMBP"
    CHARACTER_PLAYER = "CHARACTER_PLAYER"
    CHARACTER_ENEMY = "CHARACTER_ENEMY"
    AI_BEHAVIOR = "AI_BEHAVIOR"
    GAMEPLAY_COMBAT = "GAMEPLAY_COMBAT"
    GAMEPLAY_INVENTORY = "GAMEPLAY_INVENTORY"
    VFX_NIAGARA = "VFX_NIAGARA"
    AUDIO_SPATIAL = "AUDIO_SPATIAL"
    UI_HUD = "UI_HUD"
    CINEMATIC_SEQUENCER = "CINEMATIC_SEQUENCER"
    NETWORKING_SETUP = "NETWORKING_SETUP"
    PERSISTENCE_SETUP = "PERSISTENCE_SETUP"


@dataclass
class GenerationTask:
    """Represents a single dependency-aware generation unit within the DAG."""
    task_id: str
    task_type: TaskType
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    is_completed: bool = False
    error: Optional[str] = None

    def mark_completed(self, outputs: Optional[Dict[str, Any]] = None) -> None:
        self.is_completed = True
        if outputs:
            self.outputs.update(outputs)

    def mark_failed(self, error: str) -> None:
        self.is_completed = False
        self.error = error
