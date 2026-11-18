from enum import Enum
from .risk_analyzer import RiskLevel

class ExecutionMode(str, Enum):
    SAFE = "SAFE"
    BALANCED = "BALANCED"
    AUTONOMOUS = "AUTONOMOUS"

class OperationPermissionManager:
    @staticmethod
    def is_permitted(risk: RiskLevel, mode: ExecutionMode = ExecutionMode.BALANCED) -> bool:
        if risk == RiskLevel.CRITICAL:
            return False # Prohibido en todos los modos autónomos sin confirmación humana directa

        if mode == ExecutionMode.SAFE:
            return risk == RiskLevel.LOW

        if mode == ExecutionMode.BALANCED:
            return risk in [RiskLevel.LOW, RiskLevel.MEDIUM]

        if mode == ExecutionMode.AUTONOMOUS:
            return risk in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH]

        return False
