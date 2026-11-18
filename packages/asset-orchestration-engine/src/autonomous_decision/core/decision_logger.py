import time
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class DecisionLogEntry:
    decision_id: str
    asset_id: str
    iteration: int
    selected_action: str
    rejected_actions: List[str]
    reason: str
    utility: float
    score_before: float
    score_after: float
    timestamp: float = field(default_factory=time.time)

class DecisionLogger:
    def __init__(self):
        self.logs: List[DecisionLogEntry] = []

    def log(self, entry: DecisionLogEntry):
        self.logs.append(entry)
