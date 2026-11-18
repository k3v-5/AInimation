from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class CorrectiveAction:
    action_id: str
    failure_id: str
    action_type: str
    target: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    risk_level: str = "LOW"
    required_capabilities: List[str] = field(default_factory=list)
    expected_effect: str = ""
    validation_requirements: List[str] = field(default_factory=list)
    rollback_strategy: str = "RESTORE_PRE_CORRECTION_SNAPSHOT"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "failure_id": self.failure_id,
            "action_type": self.action_type,
            "target": self.target,
            "parameters": self.parameters,
            "risk_level": self.risk_level,
            "required_capabilities": self.required_capabilities,
            "expected_effect": self.expected_effect,
            "validation_requirements": self.validation_requirements,
            "rollback_strategy": self.rollback_strategy
        }
