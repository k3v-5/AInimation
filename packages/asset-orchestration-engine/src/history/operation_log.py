from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time

@dataclass
class LogEntry:
    timestamp: float
    task_id: str
    asset_id: str
    operation_type: str
    target_id: str
    parameters: Dict[str, Any]
    status: str
    error_message: str = ""

class OperationLog:
    def __init__(self):
        self.entries: List[LogEntry] = []

    def record(self, task_id: str, asset_id: str, operation_type: str, target_id: str, parameters: Dict[str, Any], status: str, error_message: str = ""):
        entry = LogEntry(
            timestamp=time.time(),
            task_id=task_id,
            asset_id=asset_id,
            operation_type=operation_type,
            target_id=target_id,
            parameters=parameters,
            status=status,
            error_message=error_message
        )
        self.entries.append(entry)

    def get_history(self, asset_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if asset_id:
            return [e.__dict__ for e in self.entries if e.asset_id == asset_id]
        return [e.__dict__ for e in self.entries]
