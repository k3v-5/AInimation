from typing import Dict, Any, List, Tuple
from .correction_plan import OperationType

class OperationRegistry:
    PROHIBITED_OPERATIONS = {
        "DELETE_ASSET", "DELETE_SCENE", "CLEAR_SCENE",
        "REBUILD_ALL", "REGENERATE_ALL", "RESET_PROJECT"
    }

    @classmethod
    def is_prohibited(cls, op_type_str: str) -> bool:
        return op_type_str.upper() in cls.PROHIBITED_OPERATIONS

    @classmethod
    def validate_operation_parameters(cls, op_type: OperationType, params: Dict[str, Any]) -> Tuple[bool, str]:
        if cls.is_prohibited(op_type.value):
            return False, f"PROHIBITED_OPERATION: Operation '{op_type.value}' is strictly forbidden by default."

        if op_type == OperationType.SET_DIMENSIONS:
            if not any(k in params for k in ["dimensions", "length", "width", "height", "x", "y", "z"]):
                return False, "INVALID_PARAMETERS: SET_DIMENSIONS requires dimension values."

        elif op_type in [OperationType.CHANGE_METALLIC, OperationType.CHANGE_ROUGHNESS]:
            val = params.get("value")
            if val is None or not (0.0 <= float(val) <= 1.0):
                return False, f"INVALID_PARAMETERS: {op_type.value} requires a float value between 0.0 and 1.0."

        elif op_type == OperationType.SCALE_OBJECT:
            factor = params.get("factor") or params.get("scale")
            if factor is None or float(factor) <= 0.0:
                return False, "INVALID_PARAMETERS: SCALE_OBJECT requires a positive scale factor."

        return True, ""
