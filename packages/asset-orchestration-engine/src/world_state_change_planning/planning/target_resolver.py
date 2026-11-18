from typing import Dict, Any, List, Optional
from ..core.world_schema import AssetState, WorldState

class TargetResolver:
    @staticmethod
    def resolve_target(query: str, world_state: WorldState) -> str:
        # 1. Búsqueda por asset_id exacto
        if query in world_state.assets:
            return query

        # 2. Búsqueda por tipo/categoría
        matches = []
        q_lower = query.lower()
        for asset_id, asset in world_state.assets.items():
            if q_lower in asset_id.lower() or q_lower in asset.asset_type.lower() or "casa" in q_lower:
                matches.append(asset_id)

        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            raise ValueError(f"AMBIGUOUS_TARGET: Multiple assets ({matches}) match target query '{query}'. Explicit asset_id required.")
        else:
            raise ValueError(f"TARGET_NOT_FOUND: No asset in WorldState matches query '{query}'.")

class ConstraintRegistry:
    @staticmethod
    def validate_change_against_constraints(asset: AssetState, property_path: str, new_value: Any) -> bool:
        clean_prop = property_path.lower()
        for locked in asset.locked_properties:
            if locked.lower() == clean_prop or (locked.lower().startswith("roof") and "roof" in clean_prop):
                raise ValueError(f"CONSTRAINT_CONFLICT: Property '{property_path}' is LOCKED by user explicit constraint (Lock: {locked}).")
        return True
