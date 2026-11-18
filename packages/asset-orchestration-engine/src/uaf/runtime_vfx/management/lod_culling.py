"""
UAF-81.84.7: VFX Level of Detail (LOD) and Spatial/Distance Culling.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

from ..math.operators import vec3_length, vec3_sub
from ..models.definition import Vec3, VFXLOD, VFXPriority


@dataclass(frozen=True)
class VFXLODProfile:
    """Distance thresholds for LOD transitions."""
    lod0_max_distance: float = 20.0
    lod1_max_distance: float = 50.0
    lod2_max_distance: float = 100.0
    lod3_max_distance: float = 200.0
    cull_distance: float = 300.0


class VFXLODManager:
    """Computes LOD levels and culling state based on camera distance and priority."""

    def __init__(self, default_profile: VFXLODProfile | None = None):
        self.profile = default_profile or VFXLODProfile()

    def evaluate_lod(
        self,
        effect_position: Vec3,
        camera_position: Vec3,
        priority: VFXPriority = VFXPriority.NORMAL,
    ) -> VFXLOD:
        """Evaluate LOD level based on distance to camera and effect priority."""
        # Critical gameplay effects are never culled by distance
        dist = vec3_length(vec3_sub(effect_position, camera_position))

        if priority == VFXPriority.CRITICAL:
            if dist <= self.profile.lod1_max_distance:
                return VFXLOD.LOD0
            return VFXLOD.LOD1

        if dist > self.profile.cull_distance:
            return VFXLOD.CULLED
        if dist > self.profile.lod2_max_distance:
            return VFXLOD.LOD3
        if dist > self.profile.lod1_max_distance:
            return VFXLOD.LOD2
        if dist > self.profile.lod0_max_distance:
            return VFXLOD.LOD1
        return VFXLOD.LOD0

    @staticmethod
    def get_spawn_multiplier(lod: VFXLOD) -> float:
        """Get particle spawn count multiplier based on LOD."""
        if lod == VFXLOD.LOD0:
            return 1.0
        elif lod == VFXLOD.LOD1:
            return 0.75
        elif lod == VFXLOD.LOD2:
            return 0.50
        elif lod == VFXLOD.LOD3:
            return 0.25
        return 0.0  # CULLED
