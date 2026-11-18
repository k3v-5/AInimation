from typing import List, Dict, Any, Set

class PartialBuilder:
    PARAMETER_COMPONENT_MAP = {
        "roof_height": {"roof"},
        "roof_angle": {"roof"},
        "roof_material": {"roof"},
        "window_count": {"windows"},
        "window_size": {"windows"},
        "door_width": {"door"},
        "wall_height": {"walls"},
        "foundation_height": {"foundation"}
    }

    @classmethod
    def get_affected_components(
        cls,
        changed_params: Dict[str, Any],
        all_components: List[str]
    ) -> List[str]:
        affected: Set[str] = set()
        for p in changed_params:
            if p in ["width", "depth", "height"]:
                # Cambios estructurales globales afectan a todos los componentes
                return list(all_components)
            if p in cls.PARAMETER_COMPONENT_MAP:
                affected.update(cls.PARAMETER_COMPONENT_MAP[p])

        return sorted(list(affected)) if affected else list(all_components)
