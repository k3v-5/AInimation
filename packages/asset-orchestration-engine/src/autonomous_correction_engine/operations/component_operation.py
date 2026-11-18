from typing import Dict, Any, Tuple
from ..core.correction_types import OperationType, ActionAuthorization
from ..core.correction_schema import ParameterChange
from .base_operation import ICorrectionOperation

class ComponentResizeOperation(ICorrectionOperation):
    @property
    def operation_type(self) -> OperationType:
        return OperationType.COMPONENT_RESIZE

    def validate_action(self, action: Any, current_state: Dict[str, Any]) -> Tuple[bool, ActionAuthorization, str]:
        target = getattr(action, "target", "")
        if not target:
            return False, ActionAuthorization.BLOCKED, "MISSING_TARGET_COMPONENT"
        return True, ActionAuthorization.SAFE, "AUTHORIZED"

    def apply_action(self, action: Any, current_state: Dict[str, Any]) -> Tuple[bool, ParameterChange, Dict[str, Any]]:
        target = getattr(action, "target", "component.body")
        delta = getattr(action, "delta", 0.0)

        old_scale = current_state.get(f"{target}.scale", 1.15)
        new_scale = round(old_scale + delta, 4)
        new_scale = max(0.50, min(2.00, new_scale))

        updated_state = dict(current_state)
        updated_state[f"{target}.scale"] = new_scale

        p_change = ParameterChange(
            parameter_id=f"{target}.scale",
            old_value=old_scale,
            new_value=new_scale,
            delta=round(new_scale - old_scale, 4),
            min_value=0.50,
            max_value=2.00
        )
        return True, p_change, updated_state
