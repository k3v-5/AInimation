from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

class DecisionStateEnum(str, Enum):
    IDLE = "IDLE"
    ANALYZING = "ANALYZING"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    VALIDATING = "VALIDATING"
    CORRECTING = "CORRECTING"
    REGENERATING = "REGENERATING"
    WAITING_DECISION = "WAITING_DECISION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"

@dataclass
class DecisionState:
    asset_id: str
    asset_version: int = 1
    state: DecisionStateEnum = DecisionStateEnum.IDLE
    current_score: float = 0.0
    previous_score: float = 0.0
    best_score: float = 0.0
    iteration_count: int = 0
    correction_count: int = 0
    regeneration_count: int = 0
    current_strategy: str = ""
    history: List[Dict[str, Any]] = field(default_factory=list)
