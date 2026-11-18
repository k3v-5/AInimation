"""
UAF-81.89.4: Clustered Particle Lights Manager.
Consolidates thousands of glowing particle sparks and plasma bolts into a budget-compliant set of physical point lights.
"""

from __future__ import annotations

import math
from typing import List, Tuple, Dict, Any
from pydantic import BaseModel, Field
from ..core.contracts import ensure_finite_vec3, clamp_scalar


class EmissiveParticle(BaseModel):
    position: Tuple[float, float, float]
    intensity: float = Field(gt=0.0)
    color: Tuple[float, float, float] = (1.0, 0.8, 0.3)
    radius: float = Field(default=3.0, gt=0.0)


class VirtualPointLight(BaseModel):
    light_id: int
    position: Tuple[float, float, float]
    intensity: float
    color: Tuple[float, float, float]
    radius: float
    particle_count: int


class ParticleLightManager:
    """
    Groups hundreds or thousands of emissive particles into clustered virtual point lights.
    Ensures zero budget overflow in deferred/clustered rendering while preserving dynamic illumination.
    """

    def __init__(self, cluster_cell_size: float = 4.0, max_budget_lights: int = 32) -> None:
        self.cluster_cell_size: float = cluster_cell_size
        self.max_budget_lights: int = max_budget_lights
        self.particles: List[EmissiveParticle] = []

    def clear(self) -> None:
        self.particles.clear()

    def add_particle(
        self,
        position: Tuple[float, float, float],
        intensity: float,
        color: Tuple[float, float, float] = (1.0, 0.8, 0.3),
        radius: float = 3.0,
    ) -> None:
        if intensity > 0.01:
            self.particles.append(
                EmissiveParticle(
                    position=ensure_finite_vec3(position),
                    intensity=intensity,
                    color=color,
                    radius=radius,
                )
            )

    def build_clustered_lights(self) -> List[VirtualPointLight]:
        """
        Clusters emissive particles spatially and consolidates them into virtual point lights.
        Sorted by energy and capped at max_budget_lights.
        """
        if not self.particles:
            return []

        # Spatial hash grid: (cell_x, cell_y, cell_z) -> List[EmissiveParticle]
        clusters: Dict[Tuple[int, int, int], List[EmissiveParticle]] = {}
        inv_size = 1.0 / max(0.1, self.cluster_cell_size)

        for p in self.particles:
            cell_key = (
                int(math.floor(p.position[0] * inv_size)),
                int(math.floor(p.position[1] * inv_size)),
                int(math.floor(p.position[2] * inv_size)),
            )
            if cell_key not in clusters:
                clusters[cell_key] = []
            clusters[cell_key].append(p)

        # Consolidate each cluster into a single virtual point light
        consolidated: List[VirtualPointLight] = []
        light_counter = 0

        for cell_key, p_list in clusters.items():
            total_intensity = sum(p.intensity for p in p_list)
            if total_intensity <= 0.0:
                continue

            # Weighted center of mass for position and color
            sum_x = sum(p.position[0] * p.intensity for p in p_list)
            sum_y = sum(p.position[1] * p.intensity for p in p_list)
            sum_z = sum(p.position[2] * p.intensity for p in p_list)

            avg_pos = (sum_x / total_intensity, sum_y / total_intensity, sum_z / total_intensity)

            sum_r = sum(p.color[0] * p.intensity for p in p_list)
            sum_g = sum(p.color[1] * p.intensity for p in p_list)
            sum_b = sum(p.color[2] * p.intensity for p in p_list)

            avg_col = (
                clamp_scalar(sum_r / total_intensity, 0.0, 1.0),
                clamp_scalar(sum_g / total_intensity, 0.0, 1.0),
                clamp_scalar(sum_b / total_intensity, 0.0, 1.0),
            )

            # Radius expands logarithmically with total intensity
            max_p_radius = max(p.radius for p in p_list)
            combined_radius = max_p_radius * (1.0 + 0.25 * math.log(1.0 + len(p_list)))

            consolidated.append(
                VirtualPointLight(
                    light_id=light_counter,
                    position=ensure_finite_vec3(avg_pos),
                    intensity=total_intensity,
                    color=avg_col,
                    radius=combined_radius,
                    particle_count=len(p_list),
                )
            )
            light_counter += 1

        # Sort by total intensity descending and clamp to budget
        consolidated.sort(key=lambda l: l.intensity, reverse=True)
        return consolidated[: self.max_budget_lights]
