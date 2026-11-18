from typing import Dict, Any, Tuple, List
from ..core.parametric_schema import ParametricAssetDefinition

class ParameterConstraintSolver:
    @staticmethod
    def validate_constraints(
        definition: ParametricAssetDefinition,
        parameters: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        errors = []

        # 1. Validar rangos individuales
        for p_name, val in parameters.items():
            if p_name in definition.parameters and isinstance(val, (int, float)):
                p_def = definition.parameters[p_name]
                if p_def.min_value is not None and val < p_def.min_value:
                    errors.append(f"CONSTRAINT_VIOLATION: Parameter '{p_name}' value {val} is below minimum {p_def.min_value}.")
                if p_def.max_value is not None and val > p_def.max_value:
                    errors.append(f"CONSTRAINT_VIOLATION: Parameter '{p_name}' value {val} exceeds maximum {p_def.max_value}.")

        # 2. Validar restricciones cruzadas (Cross-Parameter Constraints)
        roof_h = parameters.get("roof_height")
        total_h = parameters.get("height")
        if roof_h is not None and total_h is not None:
            if roof_h >= total_h:
                errors.append(f"CROSS_PARAMETER_VIOLATION: roof_height ({roof_h}m) must be strictly less than total height ({total_h}m).")

        return len(errors) == 0, errors
