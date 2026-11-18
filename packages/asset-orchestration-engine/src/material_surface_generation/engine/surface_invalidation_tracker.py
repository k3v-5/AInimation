from typing import Dict, Any
from ..core.surface_types import InvalidationState

class SurfaceInvalidationTracker:
    @classmethod
    def handle_geometry_change(cls, current_state: Dict[str, Any]) -> Dict[str, InvalidationState]:
        # Modificar geometría invalida UVs y bakes pero preserva parámetros base de material
        return {
            "geometry": InvalidationState.VALID,
            "materials": InvalidationState.VALID,
            "surface_regions": InvalidationState.VALID,
            "uv_layouts": InvalidationState.STALE,
            "baking_plan": InvalidationState.STALE,
            "texel_density": InvalidationState.STALE
        }

    @classmethod
    def handle_material_change(cls, current_state: Dict[str, Any]) -> Dict[str, InvalidationState]:
        # Modificar material invalida bake pero preserva geometría y UVs
        return {
            "geometry": InvalidationState.VALID,
            "materials": InvalidationState.VALID,
            "surface_regions": InvalidationState.VALID,
            "uv_layouts": InvalidationState.VALID,
            "baking_plan": InvalidationState.STALE,
            "texel_density": InvalidationState.VALID
        }
