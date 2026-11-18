"""
Wave Function Collapse (WFC) modular interior generation solvers and presets.
"""

from uaf.level_design.wfc.solver2d import WaveFunctionCollapse2D, WFCContradictionError
from uaf.level_design.wfc.solver3d import WaveFunctionCollapse3D
from uaf.level_design.wfc.presets import (
    create_scifi_interior_catalog_2d,
    create_scifi_multilevel_catalog_3d,
)

__all__ = [
    "WaveFunctionCollapse2D",
    "WaveFunctionCollapse3D",
    "WFCContradictionError",
    "create_scifi_interior_catalog_2d",
    "create_scifi_multilevel_catalog_3d",
]
