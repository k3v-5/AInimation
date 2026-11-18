"""Audio bridge for sound waves, sound cues, and attenuation."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class AudioBridgePayload:
    asset_id: str
    semantic_name: str
    is_cue: bool = False
    volume_multiplier: float = 1.0
    pitch_multiplier: float = 1.0
    is_looping: bool = False
    attenuation_inner_radius: float = 400.0
    attenuation_falloff_distance: float = 3600.0
    is_spatialized: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "semantic_name": self.semantic_name,
            "is_cue": self.is_cue,
            "volume_multiplier": self.volume_multiplier,
            "pitch_multiplier": self.pitch_multiplier,
            "is_looping": self.is_looping,
            "attenuation_inner_radius": self.attenuation_inner_radius,
            "attenuation_falloff_distance": self.attenuation_falloff_distance,
            "is_spatialized": self.is_spatialized,
            "metadata": self.metadata,
        }
