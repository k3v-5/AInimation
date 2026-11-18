from typing import Dict, Any, Tuple

class LibraryConstraintEngine:
    PARAMETER_BOUNDS: Dict[str, Tuple[float, float]] = {
        "blade_length": (0.30, 2.50),
        "blade_width": (0.01, 0.25),
        "blade_thickness": (0.005, 0.08),
        "guard_width": (0.05, 0.50),
        "handle_length": (0.10, 0.60)
    }

    @classmethod
    def validate_constraints(cls, params: Dict[str, Any]) -> Tuple[bool, str]:
        # 1. Bounds check
        for p_name, val in params.items():
            if p_name in cls.PARAMETER_BOUNDS and isinstance(val, (int, float)):
                min_v, max_v = cls.PARAMETER_BOUNDS[p_name]
                if val < min_v or val > max_v:
                    return False, f"PARAMETER_OUT_OF_RANGE: {p_name}={val} is outside allowed range [{min_v}, {max_v}]."

        # 2. Relational check
        b_len = params.get("blade_length", 0.90)
        h_len = params.get("handle_length", 0.22)
        if b_len <= h_len:
            return False, f"RELATIONAL_CONSTRAINT_VIOLATION: blade_length ({b_len:.2f}) must be > handle_length ({h_len:.2f})."

        return True, "Constraints valid."
