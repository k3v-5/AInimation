"""
UAF-81.84: Emitter layer exports.
"""

from .emitter import EmitterConfig, SpawnConfig, VFXEmitter
from .particle import Particle

__all__ = [
    "EmitterConfig",
    "Particle",
    "SpawnConfig",
    "VFXEmitter",
]
