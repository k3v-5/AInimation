import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class CorrectiveAction:
    action_id: str
    failure_id: str
    action_type: str
    target: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    risk_level: str = "LOW"
    required_capabilities: List[str] = field(default_factory=lambda: ["CAP_GEOMETRY", "CAP_BLENDER"])
    expected_effect: str = "RESTORE_VALID_STATE"
    validation_requirements: List[str] = field(default_factory=lambda: ["F75_BENCHMARK"])
    rollback_strategy: str = "RESTORE_CHECKPOINT"
    created_at: float = field(default_factory=time.time)

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
            "rollback_strategy": self.rollback_strategy,
            "created_at": self.created_at
        }
