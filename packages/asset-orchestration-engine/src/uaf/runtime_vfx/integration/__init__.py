"""
UAF-81.84: Integration layer exports.
"""

from .gameplay import GameplayVFXBridge, VFXAttachment
from .world_integration import StreamingCellVFXTracker

__all__ = [
    "GameplayVFXBridge",
    "StreamingCellVFXTracker",
    "VFXAttachment",
]
