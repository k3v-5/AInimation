"""
UAF-81.84: Management layer exports.
"""

from .lod_culling import VFXLODManager, VFXLODProfile
from .pool_budget import VFXBudgetManager, VFXPool

__all__ = [
    "VFXBudgetManager",
    "VFXLODManager",
    "VFXLODProfile",
    "VFXPool",
]
