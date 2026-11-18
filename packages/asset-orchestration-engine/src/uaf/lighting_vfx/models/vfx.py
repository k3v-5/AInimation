"""
VFXEffectType and VFXEffectDefinition models.
UAF-81.25 Sections 28, 29, 30, 31, 32, 33, 35, 36.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any


class VFXEffectType(str, Enum):
    NIAGARA_PARTICLE = "NIAGARA_PARTICLE"
    WEATHER_RAIN = "WEATHER_RAIN"
    WEATHER_SNOW = "WEATHER_SNOW"
    FIRE = "FIRE"
    SMOKE = "SMOKE"
    DUST = "DUST"
    EXPLOSION = "EXPLOSION"
    ENERGY = "ENERGY"
    AMBIENT_DUST = "AMBIENT_DUST"


@dataclass
class VFXEffectDefinition:
    effect_id: str
    effect_type: VFXEffectType
    max_particles: int = 1000
    spawn_rate: float = 50.0
    lifetime_seconds: float = 3.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "effect_id": self.effect_id,
            "effect_type": self.effect_type.value,
            "max_particles": self.max_particles,
            "spawn_rate": self.spawn_rate,
            "lifetime_seconds": self.lifetime_seconds,
        }
