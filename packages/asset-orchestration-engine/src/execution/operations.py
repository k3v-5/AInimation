from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time

@dataclass
class OperationResult:
    operation_id: str
    success: bool
    status: str # SUCCESS, FAILED, NO_OP
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    error_code: Optional[str] = None

class BaseOperation:
    def __init__(self, operation_id: str, target_id: str, parameters: Dict[str, Any]):
        self.operation_id = operation_id
        self.target_id = target_id
        self.parameters = parameters
        self.timestamp = time.time()

    def validate_preconditions(self, context: Any) -> tuple[bool, Optional[str]]:
        return True, None

    def execute(self, context: Any) -> OperationResult:
        raise NotImplementedError

    def validate_postconditions(self, context: Any) -> tuple[bool, Optional[str]]:
        return True, None
