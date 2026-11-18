"""
UAF-81.89.5: Non-linear Optical Distortion and Chromatic Dispersion.
Models refractive shockwaves with wavelength-dependent chromatic refraction and heat mirages.
"""

from __future__ import annotations

import math
from typing import List, Tuple
from pydantic import BaseModel, Field
from ..core.contracts import clamp_scalar


class RefractiveShockwave(BaseModel):
    center: Tuple[float, float] = (0.5, 0.5) # Normalized screen coords [0, 1]
    radius: float = Field(default=0.1, ge=0.0)
    thickness: float = Field(default=0.04, gt=0.0)
    strength: float = Field(default=0.05)
    dispersion_factor: float = Field(default=0.15, ge=0.0, description="RGB index of refraction spread")
    lifetime: float = Field(default=1.0, gt=0.0)
    max_lifetime: float = Field(default=1.0, gt=0.0)


class OpticalDistortionBuffer:
    """
    Manages screen-space refractive disturbances with chromatic aberration.
    Computes distinct (du, dv) UV offsets for Red, Green, and Blue color channels.
    """

    def __init__(self) -> None:
        self.shockwaves: List[RefractiveShockwave] = []

    def add_shockwave(
        self,
        center: Tuple[float, float],
        initial_radius: float = 0.05,
        thickness: float = 0.04,
        strength: float = 0.06,
        dispersion_factor: float = 0.2,
        lifetime: float = 1.0,
    ) -> None:
        self.shockwaves.append(
            RefractiveShockwave(
                center=center,
                radius=initial_radius,
                thickness=thickness,
                strength=strength,
                dispersion_factor=dispersion_factor,
                lifetime=lifetime,
                max_lifetime=lifetime,
            )
        )

    def update(self, dt: float, expansion_rate: float = 0.8) -> None:
        """Expands wavefront radius and decays lifetime."""
        i = 0
        while i < len(self.shockwaves):
            wave = self.shockwaves[i]
            wave.lifetime -= dt
            if wave.lifetime <= 0.0:
                self.shockwaves.pop(i)
                continue

            wave.radius += expansion_rate * dt
            # Strength decays with lifetime
            fade = wave.lifetime / wave.max_lifetime
            wave.strength *= fade
            i += 1

    def sample_screen_distortion(
        self,
        u: float,
        v: float,
    ) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
        """
        Samples chromatic UV distortion at (u, v).
        Returns ((du_r, dv_r), (du_g, dv_g), (du_b, dv_b)).
        """
        offset_r = [0.0, 0.0]
        offset_g = [0.0, 0.0]
        offset_b = [0.0, 0.0]

        for wave in self.shockwaves:
            cx, cy = wave.center
            dx = u - cx
            dy = v - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= 0.0001:
                continue

            # Distance to the wavefront crest
            delta = abs(dist - wave.radius)
            if delta < wave.thickness:
                # Smooth sinusoidal wave profile: -sin(pi * delta / thickness)
                factor = -math.sin(math.pi * (delta / wave.thickness)) * wave.strength
                dir_x = dx / dist
                dir_y = dy / dist

                # Wavelength indices: Red refracts less, Blue refracts more
                disp = wave.dispersion_factor
                n_r = 1.0 - disp * 0.5
                n_g = 1.0
                n_b = 1.0 + disp * 0.5

                offset_r[0] += dir_x * factor * n_r
                offset_r[1] += dir_y * factor * n_r

                offset_g[0] += dir_x * factor * n_g
                offset_g[1] += dir_y * factor * n_g

                offset_b[0] += dir_x * factor * n_b
                offset_b[1] += dir_y * factor * n_b

        return (
            (offset_r[0], offset_r[1]),
            (offset_g[0], offset_g[1]),
            (offset_b[0], offset_b[1]),
        )
