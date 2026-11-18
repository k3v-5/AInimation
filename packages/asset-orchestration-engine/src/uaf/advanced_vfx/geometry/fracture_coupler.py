"""
UAF-81.89.2: Geometry Fracture & Voronoi Destruction VFX Coupler.
Generates directional debris, dust clouds, and edge sparks along freshly exposed fracture planes.
"""

from __future__ import annotations

import math
import random
from typing import List, Tuple
from pydantic import BaseModel, Field
from ..core.contracts import ensure_finite_vec3


class FractureChunk(BaseModel):
    chunk_id: int
    centroid: Tuple[float, float, float]
    normal: Tuple[float, float, float]
    volume: float = Field(default=1.0, gt=0.0)
    linear_impulse: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    angular_impulse: Tuple[float, float, float] = (0.0, 0.0, 0.0)


class FractureDebrisParticle(BaseModel):
    position: Tuple[float, float, float]
    velocity: Tuple[float, float, float]
    lifetime: float
    size: float
    is_dust: bool


class FractureVFXCoupler:
    """
    Couples physical destruction events (Voronoi slicing, Chaos breakdown) to particle systems.
    """

    def __init__(self, base_debris_speed: float = 12.0, base_dust_speed: float = 2.5) -> None:
        self.base_debris_speed: float = base_debris_speed
        self.base_dust_speed: float = base_dust_speed

    def generate_fracture_vfx(
        self,
        chunks: List[FractureChunk],
        debris_per_chunk: int = 5,
        dust_per_chunk: int = 15,
        seed: int = 42,
    ) -> List[FractureDebrisParticle]:
        """
        Emits debris and volumetric dust particles from fracture facets.
        """
        rng = random.Random(seed)
        particles: List[FractureDebrisParticle] = []

        for chunk in chunks:
            cx, cy, cz = chunk.centroid
            nx, ny, nz = chunk.normal
            ix, iy, iz = chunk.linear_impulse

            # 1. Emit solid debris along chunk normal + impulse
            for _ in range(debris_per_chunk):
                # Small spatial jitter around centroid
                pos = (
                    cx + (rng.random() - 0.5) * 0.2,
                    cy + (rng.random() - 0.5) * 0.2,
                    cz + (rng.random() - 0.5) * 0.2,
                )

                # Velocity along normal with conical cone spread
                spread_x = rng.gauss(0.0, 0.3)
                spread_y = rng.gauss(0.0, 0.3)
                spread_z = rng.gauss(0.0, 0.3)

                speed = self.base_debris_speed * (0.8 + 0.4 * rng.random())
                vel = (
                    (nx + spread_x) * speed + ix * 0.5,
                    (ny + spread_y) * speed + iy * 0.5,
                    (nz + spread_z) * speed + iz * 0.5,
                )

                particles.append(
                    FractureDebrisParticle(
                        position=ensure_finite_vec3(pos),
                        velocity=ensure_finite_vec3(vel),
                        lifetime=rng.uniform(1.5, 3.5),
                        size=rng.uniform(0.05, 0.25),
                        is_dust=False,
                    )
                )

            # 2. Emit volumetric lingering dust clouds
            for _ in range(dust_per_chunk):
                pos = (
                    cx + (rng.random() - 0.5) * 0.4,
                    cy + (rng.random() - 0.5) * 0.4,
                    cz + (rng.random() - 0.5) * 0.4,
                )

                dust_speed = self.base_dust_speed * rng.random()
                vel = (
                    rng.gauss(0.0, 0.5) * dust_speed + nx * 0.5,
                    rng.uniform(0.2, 1.0) * dust_speed,  # Slight upward drift
                    rng.gauss(0.0, 0.5) * dust_speed + nz * 0.5,
                )

                particles.append(
                    FractureDebrisParticle(
                        position=ensure_finite_vec3(pos),
                        velocity=ensure_finite_vec3(vel),
                        lifetime=rng.uniform(3.0, 6.0),
                        size=rng.uniform(0.5, 1.8),
                        is_dust=True,
                    )
                )

        return particles
