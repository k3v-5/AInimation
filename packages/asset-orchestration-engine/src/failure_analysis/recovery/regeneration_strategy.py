from typing import List, Set

class RegenerationStrategy:
    """Calculates surgical boundary of components requiring regeneration without destroying valid parts."""

    @staticmethod
    def compute_boundary(failed_component: str, all_components: List[str]) -> List[str]:
        # Minimal boundary: only regenerate the failed component and its direct dependents
        if failed_component.upper() == "MATERIALS":
            return ["Materials", "Shaders"]
        if failed_component.upper() == "UV":
            return ["UV", "Materials"]
        if failed_component.upper() == "LOD":
            return ["LOD1", "LOD2", "LOD3"]
        if failed_component.upper() == "COLLISION":
            return ["UCX_Collision"]
        return [failed_component]
