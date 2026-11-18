"""
UAF Surface Detail Models Package
"""

from .definition import (
    PhysicalMaterialClass,
    SurfaceLayerType,
    SurfaceDetailDefinition,
)
from .textures import (
    SurfaceDetailChannel,
)

__all__ = [
    "PhysicalMaterialClass",
    "SurfaceLayerType",
    "SurfaceDetailDefinition",
    "SurfaceDetailChannel",
]
