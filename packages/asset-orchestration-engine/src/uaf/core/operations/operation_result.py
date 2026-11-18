"""
OperationResult captures the complete outcome of an executed operation.
UAF-81.0 Section 21.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .operation_status import OperationStatus


@dataclass
class OperationResult:
    """
    Result container holding produced artifacts, metrics, and diagnostics.
    """
    operation_id: str
    status: OperationStatus
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    diagnostics: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    duration_seconds: float = 0.0
    error: Optional[Dict[str, Any]] = None

    @property
    def is_success(self) -> bool:
        return self.status == OperationStatus.SUCCEEDED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation_id": self.operation_id,
            "status": self.status.value,
            "artifacts": self.artifacts,
            "diagnostics": self.diagnostics,
            "metrics": self.metrics,
            "duration_seconds": self.duration_seconds,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OperationResult":
        return cls(
            operation_id=data["operation_id"],
            status=OperationStatus(data["status"]),
            artifacts=data.get("artifacts", []),
            diagnostics=data.get("diagnostics", []),
            metrics=data.get("metrics", {}),
            duration_seconds=float(data.get("duration_seconds", 0.0)),
            error=data.get("error"),
        )
