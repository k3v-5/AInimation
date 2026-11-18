"""
Fog Systems (Linear, Exponential, Exponential Height) for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Tuple

from .core import FogType, ensure_finite_scalar, ensure_finite_vec3


@dataclass
class FogSystem:
    """
    Universal Fog System modeling height-attenuated and volumetric fog.
    """
    fog_type: FogType = FogType.EXPONENTIAL_HEIGHT
    density: float = 0.02                       # Sea-level base extinction coefficient (1/m)
    height_falloff: float = 0.05                # Exponential falloff rate with altitude (1/m)
    height: float = 0.0                         # Base height reference (meters)
    start_distance: float = 0.0                 # Distance before fog starts (meters)
    cutoff_distance: float = 5000.0             # Max distance fog is rendered
    albedo: Tuple[float, float, float] = (0.6, 0.7, 0.8) # In-scattering color
    directional_inscattering_exponent: float = 4.0
    directional_inscattering_start_distance: float = 100.0

    def __post_init__(self) -> None:
        self.density = max(0.0, ensure_finite_scalar(self.density, "density", 0.02))
        self.height_falloff = max(0.0001, ensure_finite_scalar(self.height_falloff, "height_falloff", 0.05))
        self.height = ensure_finite_scalar(self.height, "height", 0.0)
        self.start_distance = max(0.0, ensure_finite_scalar(self.start_distance, "start_distance", 0.0))
        self.cutoff_distance = max(self.start_distance + 1.0, ensure_finite_scalar(self.cutoff_distance, "cutoff_distance", 5000.0))
        self.albedo = ensure_finite_vec3(self.albedo, "albedo", (0.6, 0.7, 0.8))

    def evaluate_optical_depth(
        self,
        ray_origin: Tuple[float, float, float],
        ray_dir: Tuple[float, float, float],
        ray_length: float
    ) -> float:
        """
        Analytically integrates exponential height fog optical depth along ray.
        rho(z) = density * exp(-falloff * (z - height))
        """
        length = max(0.0, min(self.cutoff_distance, ray_length - self.start_distance))
        if length <= 0.0 or self.density <= 0.0:
            return 0.0

        z0 = ray_origin[1] - self.height
        dz = ray_dir[1]

        if abs(dz) < 1e-5:
            # Horizontal ray
            density_at_z = self.density * math.exp(-self.height_falloff * max(-100.0, z0))
            return density_at_z * length

        # Analytical integration along slanted ray
        z1 = z0 + dz * length
        exp_z0 = math.exp(-self.height_falloff * z0)
        exp_z1 = math.exp(-self.height_falloff * z1)
        depth = (self.density / (self.height_falloff * dz)) * (exp_z0 - exp_z1)
        return max(0.0, depth)

    def evaluate_fog_factor(
        self,
        ray_origin: Tuple[float, float, float],
        ray_dir: Tuple[float, float, float],
        ray_length: float
    ) -> Tuple[float, Tuple[float, float, float]]:
        """
        Returns (transmission, inscattered_color).
        transmission = exp(-optical_depth).
        inscattered_color = albedo * (1.0 - transmission).
        """
        opt_depth = self.evaluate_optical_depth(ray_origin, ray_dir, ray_length)
        transmission = math.exp(-opt_depth)
        inscatter_weight = 1.0 - transmission
        inscatter = (
            round(self.albedo[0] * inscatter_weight, 6),
            round(self.albedo[1] * inscatter_weight, 6),
            round(self.albedo[2] * inscatter_weight, 6),
        )
        return (round(transmission, 6), inscatter)
