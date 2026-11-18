import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..core.permission_manager import AuthorizationStatus

@dataclass
class AuditRecord:
    record_id: str
    timestamp: float = field(default_factory=time.time)
    agent_id: str = ""
    task_id: str = ""
    orchestration_id: str = ""
    tool_id: Optional[str] = None
    capability_id: Optional[str] = None
    resource_id: Optional[str] = None
    operation: Optional[str] = None
    status: AuthorizationStatus = AuthorizationStatus.DENIED
    reason: str = ""
    sanitized_input: Dict[str, Any] = field(default_factory=dict)
    sanitized_output: Dict[str, Any] = field(default_factory=dict)
    execution_duration: float = 0.0

class AuditLogger:
    """Immutable audit logging facility with secret sanitization."""
    SENSITIVE_KEYS = {"password", "secret", "token", "api_key", "credential", "auth_token", "private_key"}

    def __init__(self):
        self._records: List[AuditRecord] = []

    def sanitize_payload(self, data: Any) -> Any:
        if isinstance(data, dict):
            clean = {}
            for k, v in data.items():
                if any(sens in k.lower() for sens in self.SENSITIVE_KEYS):
                    clean[k] = "[REDACTED_SECRET]"
                else:
                    clean[k] = self.sanitize_payload(v)
            return clean
        elif isinstance(data, list):
            return [self.sanitize_payload(item) for item in data]
        return data

    def log_decision(self, record: AuditRecord):
        record.sanitized_input = self.sanitize_payload(record.sanitized_input)
        record.sanitized_output = self.sanitize_payload(record.sanitized_output)
        self._records.append(record)

    def list_records(self, agent_id: Optional[str] = None) -> List[AuditRecord]:
        if agent_id:
            return [r for r in self._records if r.agent_id == agent_id]
        return list(self._records)
