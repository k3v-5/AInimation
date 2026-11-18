from typing import Dict, Any, Tuple
from ..core.correction_types import OperationType, ActionAuthorization
from ..core.correction_schema import ParameterChange
from .base_operation import ICorrectionOperation

class ParameterUpdateOperation(ICorrectionOperation):
    @property
    def operation_type(self) -> OperationType:
        return OperationType.PARAMETER_UPDATE

    def validate_action(self, action: Any, current_state: Dict[str, Any]) -> Tuple[bool, ActionAuthorization, str]:
        param_name = getattr(action, "parameter", "")
        if not param_name:
            return False, ActionAuthorization.BLOCKED, "MISSING_PARAMETER_NAME"
        
        delta = getattr(action, "delta", 0.0)
        if abs(delta) > 0.50:
            return True, ActionAuthorization.CONTROLLED, "LARGE_DELTA_REQUIRES_CONTROLLED_STEP"

        return True, ActionAuthorization.SAFE, "AUTHORIZED"

    def apply_action(self, action: Any, current_state: Dict[str, Any]) -> Tuple[bool, ParameterChange, Dict[str, Any]]:
        param_name = getattr(action, "parameter", "geometry_param")
        target = getattr(action, "target", "component.root")
        delta = getattr(action, "delta", 0.0)

        old_val = current_state.get(param_name, 1.15)
        new_val = round(old_val + delta, 4)

        # Clamping
        new_val = max(0.50, min(2.00, new_val))

        updated_state = dict(current_state)
        updated_state[param_name] = new_val
        updated_state[f"{target}.{param_name}"] = new_val

        p_change = ParameterChange(
            parameter_id=param_name,
            old_value=old_val,
            new_value=new_val,
            delta=round(new_val - old_val, 4),
            min_value=0.50,
            max_value=2.00
        )
        return True, p_change, updated_state
