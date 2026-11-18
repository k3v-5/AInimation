"""
UAF-81.89: Environment interaction exports.
"""

from .surface_persistence import PersistentSurfaceManager
from .foliage_interaction import FoliageInteractionBuffer

__all__ = [
    "PersistentSurfaceManager",
    "FoliageInteractionBuffer",
]
