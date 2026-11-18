"""
UAF-81.89: Fluid simulation exports.
"""

from .grid2d import EulerianFluidGrid2D
from .grid3d import EulerianFluidGrid3D
from .smoke_fire import SmokeFireSolver

__all__ = [
    "EulerianFluidGrid2D",
    "EulerianFluidGrid3D",
    "SmokeFireSolver",
]
