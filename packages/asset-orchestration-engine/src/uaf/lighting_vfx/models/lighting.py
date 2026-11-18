"""
LightType25, LightMobility, LightRole, and LightSourceDefinition models.
UAF-81.25 Sections 4, 5, 6, 7, 10, 15, 17, 18.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class LightType25(str, Enum):
    POINT = "POINT"
    SPOT = "SPOT"
    RECT = "RECT"
    DIRECTIONAL = "DIRECTIONAL"
    AREA = "AREA"
    EMISSIVE_SOURCE = "EMISSIVE_SOURCE"
    CUSTOM = "CUSTOM"


class LightMobility(str, Enum):
    STATIC = "STATIC"
    STATIONARY = "STATIONARY"
    MOVABLE = "MOVABLE"


class LightRole(str, Enum):
    KEY = "KEY"
    FILL = "FILL"
    RIM = "RIM"
    AMBIENT = "AMBIENT"
    PRACTICAL = "PRACTICAL"
    ACCENT = "ACCENT"
    WARNING = "WARNING"
    OBJECTIVE = "OBJECTIVE"
    COMBAT = "COMBAT"
    CINEMATIC = "CINEMATIC"


@dataclass
class LightSourceDefinition:
    light_id: str
    light_type: LightType25
    mobility: LightMobility
    role: LightRole
    intensity_lux: float = 5000.0
    color_temperature_k: float = 6500.0
    shadow_enabled: bool = True
    position_xyz: List[float] = field(default_factory=lambda: [0.0, 0.0, 300.0])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "light_id": self.light_id,
            "light_type": self.light_type.value,
            "mobility": self.mobility.value,
            "role": self.role.value,
            "intensity_lux": self.intensity_lux,
            "color_temperature_k": self.color_temperature_k,
            "shadow_enabled": self.shadow_enabled,
            "position_xyz": self.position_xyz,
        }
