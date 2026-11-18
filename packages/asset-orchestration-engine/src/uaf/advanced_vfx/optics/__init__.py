"""
UAF-81.89: Optics and dielectric breakdown exports.
"""

from .dielectric_trees import LightningSegment, LightningBolt, DielectricBreakdownSolver
from .optical_distortion import RefractiveShockwave, OpticalDistortionBuffer

__all__ = [
    "LightningSegment",
    "LightningBolt",
    "DielectricBreakdownSolver",
    "RefractiveShockwave",
    "OpticalDistortionBuffer",
]
