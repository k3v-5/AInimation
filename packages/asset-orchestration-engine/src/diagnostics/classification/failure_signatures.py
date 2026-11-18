from dataclasses import dataclass
from ..core.failure_types import FailureType
from ..core.severity import FailureSeverity

@dataclass
class FailureSignature:
    signature_id: str
    failure_type: FailureType
    error_code: str
    normalized_pattern: str
    severity: FailureSeverity
    recoverability: bool = True

    def matches(self, message: str) -> bool:
        return self.normalized_pattern.lower() in message.lower()
