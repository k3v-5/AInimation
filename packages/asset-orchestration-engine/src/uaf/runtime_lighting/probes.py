"""
Irradiance & Reflection Probes, Light Probe Grid for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .core import ProbeId, ensure_finite_scalar, ensure_finite_vec3


@dataclass
class IrradianceProbe:
    """
    Spherical Harmonic (SH) Irradiance Probe capturing diffuse indirect light at a point.
    Uses standard 3-band L2 Spherical Harmonics (9 RGB coefficients).
    """
    probe_id: ProbeId
    position: Tuple[float, float, float]
    # 9 SH coefficients for RGB (each element is (r, g, b))
    sh_coefficients: List[Tuple[float, float, float]] = field(
        default_factory=lambda: [(0.1, 0.1, 0.1)] + [(0.0, 0.0, 0.0)] * 8
    )
    cell_id: Optional[str] = None

    def __post_init__(self) -> None:
        self.position = ensure_finite_vec3(self.position, "position")
        if len(self.sh_coefficients) != 9:
            self.sh_coefficients = [(0.1, 0.1, 0.1)] + [(0.0, 0.0, 0.0)] * 8

    def evaluate_direction(self, normal: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """
        Evaluates irradiance in direction 'normal' using L0 and L1 SH components.
        """
        nx, ny, nz = normal
        # L0
        c0 = 0.282095
        # L1
        c1 = 0.488603
        r = self.sh_coefficients[0][0] * c0 + (self.sh_coefficients[1][0] * ny + self.sh_coefficients[2][0] * nz + self.sh_coefficients[3][0] * nx) * c1
        g = self.sh_coefficients[0][1] * c0 + (self.sh_coefficients[1][1] * ny + self.sh_coefficients[2][1] * nz + self.sh_coefficients[3][1] * nx) * c1
        b = self.sh_coefficients[0][2] * c0 + (self.sh_coefficients[1][2] * ny + self.sh_coefficients[2][2] * nz + self.sh_coefficients[3][2] * nx) * c1
        return (max(0.0, r), max(0.0, g), max(0.0, b))


@dataclass
class ReflectionProbe:
    """
    Specular Reflection Probe storing high-frequency reflections and cubemap data.
    """
    probe_id: ProbeId
    position: Tuple[float, float, float]
    radius: float = 10.0
    box_bounds: Optional[Tuple[float, float, float]] = None  # Half-extents if box projection
    intensity: float = 1.0
    resolution: int = 256
    cell_id: Optional[str] = None

    def __post_init__(self) -> None:
        self.position = ensure_finite_vec3(self.position, "position")
        self.radius = max(0.1, ensure_finite_scalar(self.radius, "radius", 10.0))
        self.intensity = max(0.0, ensure_finite_scalar(self.intensity, "intensity", 1.0))
        self.resolution = max(64, min(2048, int(ensure_finite_scalar(self.resolution, "resolution", 256))))


class LightProbeGrid:
    """
    3D regular grid of irradiance probes with trilinear interpolation.
    """

    def __init__(
        self,
        origin: Tuple[float, float, float] = (-50.0, 0.0, -50.0),
        spacing: float = 5.0,
        grid_dims: Tuple[int, int, int] = (21, 5, 21),  # (dim_x, dim_y, dim_z)
    ) -> None:
        self.origin = origin
        self.spacing = max(0.5, spacing)
        self.dims = (max(1, grid_dims[0]), max(1, grid_dims[1]), max(1, grid_dims[2]))
        self.probes: Dict[Tuple[int, int, int], IrradianceProbe] = {}
        self._populate_grid()

    def _populate_grid(self) -> None:
        idx = 0
        for z in range(self.dims[2]):
            for y in range(self.dims[1]):
                for x in range(self.dims[0]):
                    pos = (
                        self.origin[0] + x * self.spacing,
                        self.origin[1] + y * self.spacing,
                        self.origin[2] + z * self.spacing,
                    )
                    probe = IrradianceProbe(
                        probe_id=ProbeId(f"grid_probe_{idx}"),
                        position=pos,
                        sh_coefficients=[(0.05, 0.05, 0.06)] + [(0.0, 0.0, 0.0)] * 8
                    )
                    self.probes[(x, y, z)] = probe
                    idx += 1

    def sample_irradiance(
        self,
        world_pos: Tuple[float, float, float],
        normal: Tuple[float, float, float]
    ) -> Tuple[float, float, float]:
        """
        Samples irradiance at world_pos via nearest probe interpolation.
        """
        gx = int(round((world_pos[0] - self.origin[0]) / self.spacing))
        gy = int(round((world_pos[1] - self.origin[1]) / self.spacing))
        gz = int(round((world_pos[2] - self.origin[2]) / self.spacing))

        # Clamp to bounds
        gx = max(0, min(self.dims[0] - 1, gx))
        gy = max(0, min(self.dims[1] - 1, gy))
        gz = max(0, min(self.dims[2] - 1, gz))

        probe = self.probes.get((gx, gy, gz))
        if probe is None:
            return (0.05, 0.05, 0.05)
        return probe.evaluate_direction(normal)
