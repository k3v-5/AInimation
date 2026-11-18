from typing import Dict, List, Set

class ParameterImpactGraph:
    IMPACT_MAP: Dict[str, List[str]] = {
        "door_width": ["scale", "navigation", "collision", "interaction"],
        "door_height": ["scale", "collision"],
        "stair_slope": ["traversal", "navigation", "scale"],
        "stair_step_height": ["traversal", "navigation"],
        "stair_width": ["traversal", "navigation", "collision"],
        "ceiling_height": ["scale", "camera", "collision"],
        "corridor_width": ["navigation", "collision"],
        "roof_height": ["visual"], # No afecta gameplay de planta baja
        "roof_angle": ["visual"],
        "window_scale": ["visual"],
        "wall_material": ["appearance"]
    }

    @classmethod
    def get_affected_systems(cls, parameter_name: str) -> List[str]:
        return cls.IMPACT_MAP.get(parameter_name, ["visual", "technical", "gameplay"])
