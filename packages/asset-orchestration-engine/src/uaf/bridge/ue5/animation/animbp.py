"""Animation Blueprint state machine, blend tree, and variable synchronization."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class AnimBPBridgePayload:
    anim_bp_id: str
    target_skeleton_id: str
    current_state_name: str = "Idle"
    blend_weight: float = 1.0
    variables: Dict[str, Any] = field(default_factory=dict)
    active_montages: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "anim_bp_id": self.anim_bp_id,
            "target_skeleton_id": self.target_skeleton_id,
            "current_state_name": self.current_state_name,
            "blend_weight": self.blend_weight,
            "variables": self.variables,
            "active_montages": self.active_montages,
        }
