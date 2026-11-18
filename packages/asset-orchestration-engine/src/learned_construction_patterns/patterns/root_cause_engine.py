from typing import Dict, Any, List, Tuple
from ..core.memory_types import ProblemSignature

class RootCauseEngine:
    ROOT_CAUSE_MAP: Dict[str, List[Tuple[str, float, float]]] = {
        # Signature -> list of (parameter_name, confidence, expected_improvement)
        "ROOF_TOO_LOW": [("roof_height", 0.92, 0.18), ("roof_angle", 0.65, 0.08)],
        "ROOF_TOO_HIGH": [("roof_height", 0.90, -0.15), ("roof_angle", 0.60, -0.06)],
        "WINDOWS_TOO_SMALL": [("window_scale", 0.88, 0.25), ("window_count", 0.45, 1.0)],
        "WINDOWS_TOO_LARGE": [("window_scale", 0.85, -0.20)],
        "BODY_TOO_WIDE": [("width", 0.85, -0.20), ("depth", 0.70, -0.15)],
        "BODY_TOO_NARROW": [("width", 0.85, 0.20), ("depth", 0.70, 0.15)]
    }

    @classmethod
    def get_likely_root_causes(cls, problem_signature: str) -> List[Tuple[str, float, float]]:
        return cls.ROOT_CAUSE_MAP.get(problem_signature, [("general_scale", 0.50, 0.10)])
