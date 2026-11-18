from typing import Dict, Any, Tuple

class ParameterConstraintSolver:
    @staticmethod
    def validate_and_solve(params: Dict[str, Any]) -> Tuple[bool, str]:
        # 1. Comprobar que las dimensiones sean positivas
        for k in ["total_length", "blade_length", "blade_width", "blade_thickness", "guard_width", "handle_length"]:
            if k in params and params[k] <= 0:
                return False, f"PARAMETER_CONSTRAINT_VIOLATION: {k} must be > 0 (got {params[k]})."

        # 2. Restricción relacional: la hoja debe ser más larga que la empuñadura
        b_len = params.get("blade_length", 0.90)
        h_len = params.get("handle_length", 0.22)
        if b_len <= h_len:
            return False, f"RELATIONAL_CONSTRAINT_VIOLATION: blade_length ({b_len:.2f}) must be > handle_length ({h_len:.2f})."

        # 3. Restricción de ratio: anchura de hoja razonable
        b_w = params.get("blade_width", 0.05)
        if b_w > b_len * 0.40:
            return False, f"RATIO_CONSTRAINT_VIOLATION: blade_width ({b_w:.2f}) is too large for blade_length ({b_len:.2f})."

        return True, "Constraints satisfied."
