"""
Volumetric Lighting Raymarching & In-Scattering for UAF-81.85.
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Tuple

from .core import VolumetricQuality, ensure_finite_scalar, ensure_finite_vec3
from .lights import Light


@dataclass
class VolumetricSystem:
    """
    Simulates volumetric light shaft scattering and participate media in-scattering.
    """
    quality: VolumetricQuality = VolumetricQuality.MEDIUM
    scattering_coefficient: float = 0.05       # (1/m)
    absorption_coefficient: float = 0.01       # (1/m)
    phase_g: float = 0.6                       # Henyey-Greenstein forward factor
    max_distance: float = 100.0                # Raymarch cutoff distance
    noise_scale: float = 0.1
    noise_speed: float = 1.0

    def __post_init__(self) -> None:
        self.scattering_coefficient = max(0.0, ensure_finite_scalar(self.scattering_coefficient, "scattering_coefficient", 0.05))
        self.absorption_coefficient = max(0.0, ensure_finite_scalar(self.absorption_coefficient, "absorption_coefficient", 0.01))
        self.phase_g = max(-0.99, min(0.99, ensure_finite_scalar(self.phase_g, "phase_g", 0.6)))
        self.max_distance = max(1.0, ensure_finite_scalar(self.max_distance, "max_distance", 100.0))

    def _get_step_count(self) -> int:
        if self.quality == VolumetricQuality.OFF:
            return 0
        elif self.quality == VolumetricQuality.LOW:
            return 8
        elif self.quality == VolumetricQuality.MEDIUM:
            return 16
        else:
            return 32

    def evaluate_volumetric_inscattering(
        self,
        ray_origin: Tuple[float, float, float],
        ray_dir: Tuple[float, float, float],
        ray_length: float,
        lights: List[Light]
    ) -> Tuple[float, float, float]:
        """
        Raymarches along ray to accumulate volumetric lighting.
        """
        steps = self._get_step_count()
        if steps == 0 or not lights:
            return (0.0, 0.0, 0.0)

        march_dist = min(self.max_distance, ray_length)
        step_size = march_dist / float(steps)

        total_r = 0.0
        total_g = 0.0
        total_b = 0.0
        extinction = self.scattering_coefficient + self.absorption_coefficient

        for s in range(steps):
            t = (s + 0.5) * step_size
            sample_pos = (
                ray_origin[0] + ray_dir[0] * t,
                ray_origin[1] + ray_dir[1] * t,
                ray_origin[2] + ray_dir[2] * t,
            )

            # Transmittance from camera to sample point
            transmittance = math.exp(-extinction * t)

            # Sum light contributions at sample point
            for light in lights:
                if not light.visibility or not light.affect_volumetrics:
                    continue

                lx = light.position[0] - sample_pos[0]
                ly = light.position[1] - sample_pos[1]
                lz = light.position[2] - sample_pos[2]
                dist_sq = lx * lx + ly * ly + lz * lz
                dist = math.sqrt(dist_sq)

                if dist > light.range or dist < 1e-4:
                    continue

                inv_dist = 1.0 / dist
                light_dir = (lx * inv_dist, ly * inv_dist, lz * inv_dist)

                # Henyey-Greenstein phase
                cos_theta = -(ray_dir[0] * light_dir[0] + ray_dir[1] * light_dir[1] + ray_dir[2] * light_dir[2])
                denom = 1.0 + self.phase_g * self.phase_g - 2.0 * self.phase_g * cos_theta
                phase = (1.0 - self.phase_g * self.phase_g) / max(1e-4, 4.0 * math.pi * (denom ** 1.5))

                # Attenuation
                att = max(0.0, 1.0 - (dist / light.range)) ** light.falloff_exponent
                eff_color = light.get_effective_color()
                flux = (light.intensity * 0.0001) * att * phase * light.volumetric_scattering_intensity

                total_r += eff_color[0] * flux * transmittance * step_size
                total_g += eff_color[1] * flux * transmittance * step_size
                total_b += eff_color[2] * flux * transmittance * step_size

        return (round(total_r, 6), round(total_g, 6), round(total_b, 6))
