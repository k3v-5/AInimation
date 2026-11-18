"""
PresentationDefinition25 model.
UAF-81.25 Sections 3, 4, 131, 132.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from .lighting import LightSourceDefinition
from .atmosphere import SkyAtmosphereProfile
from .vfx import VFXEffectDefinition
from ...core.hashing.canonical_hasher import CanonicalHasher


@dataclass
class PresentationDefinition25:
    presentation_id: str
    sky_atmosphere: SkyAtmosphereProfile = field(default_factory=SkyAtmosphereProfile)
    lights: List[LightSourceDefinition] = field(default_factory=list)
    vfx_effects: List[VFXEffectDefinition] = field(default_factory=list)
    seed: int = 42

    @property
    def definition_hash(self) -> str:
        return CanonicalHasher.compute_hash(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "presentation_id": self.presentation_id,
            "sky_atmosphere": self.sky_atmosphere.to_dict(),
            "lights": [lt.to_dict() for lt in self.lights],
            "vfx_effects": [vx.to_dict() for vx in self.vfx_effects],
            "seed": self.seed,
        }
