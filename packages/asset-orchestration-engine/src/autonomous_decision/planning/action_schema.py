from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class ActionPlan:
    action_id: str
    target: str
    strategy_id: str
    operation_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    expected_improvement: float = 0.10
    risk: float = 0.10
    estimated_cost: float = 1.0
    utility: float = 0.10
    reason: str = ""
