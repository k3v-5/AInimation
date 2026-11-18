"""
Diagnostic represents a structured diagnostic entry produced during UAF operations.
UAF-81.0 Section 27.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from .severity import DiagnosticSeverity


@dataclass(frozen=True)
class Diagnostic:
    """
    Structured diagnostic message.
    """
    severity: DiagnosticSeverity
    code: str
    message: str
    component: str = "core"
    operation_id: Optional[str] = None
    asset_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    location: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
            "component": self.component,
            "operation_id": self.operation_id,
            "asset_id": self.asset_id,
            "details": self.details,
            "location": self.location,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Diagnostic":
        return cls(
            severity=DiagnosticSeverity(data["severity"]),
            code=data["code"],
            message=data["message"],
            component=data.get("component", "core"),
            operation_id=data.get("operation_id"),
            asset_id=data.get("asset_id"),
            details=data.get("details", {}),
            location=data.get("location"),
            timestamp=float(data.get("timestamp", time.time())),
        )
