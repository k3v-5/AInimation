from enum import Enum
from typing import Dict, Any
from ..core.correction_plan import OperationType

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RiskAnalyzer:
    @staticmethod
    def analyze_risk(op_type: OperationType, params: Dict[str, Any] = None) -> RiskLevel:
        val = op_type.value if isinstance(op_type, OperationType) else str(op_type)

        if val in ["DELETE_ASSET", "DELETE_SCENE", "CLEAR_SCENE", "REGENERATE_ALL", "RESET_PROJECT"]:
            return RiskLevel.CRITICAL

        if val in ["MODIFY_COMPONENT", "REPLACE_COMPONENT", "REBUILD_COMPONENT", "DELETE_COMPONENT"]:
            return RiskLevel.HIGH

        if val in ["SCALE_OBJECT", "SET_DIMENSIONS", "SET_PIVOT", "APPLY_TRANSFORM", "REGENERATE_UV", "REBUILD_COLLISION"]:
            return RiskLevel.MEDIUM

        return RiskLevel.LOW
