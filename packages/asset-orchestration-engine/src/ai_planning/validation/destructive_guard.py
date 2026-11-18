from enum import Enum
from typing import Tuple, Optional, Dict, Any

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class DestructiveOperationGuard:
    @staticmethod
    def classify_risk(operation_type: str, scope: str = "target") -> RiskLevel:
        if operation_type in ["CLEAR_LEVEL", "DELETE_BLUEPRINT"]:
            return RiskLevel.CRITICAL
        if operation_type in ["DELETE", "DELETE_ACTOR", "REPLACE_ASSET"] and scope == "all":
            return RiskLevel.CRITICAL
        if operation_type in ["DELETE", "DELETE_ACTOR", "MODIFY_SHARED_ASSET"]:
            return RiskLevel.HIGH
        if operation_type in ["ADD_GAMEPLAY_COMPONENT", "MAKE_PICKABLE", "EQUIPPABLE"]:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW
