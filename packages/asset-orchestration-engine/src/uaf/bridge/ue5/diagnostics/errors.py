"""Normalized UE5 bridge error definitions and contextual error envelopes."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class UE5ErrorCode(str, Enum):
    UE5_IMPORT_ERROR = "UE5_IMPORT_ERROR"
    UE5_ASSET_ERROR = "UE5_ASSET_ERROR"
    UE5_RUNTIME_ERROR = "UE5_RUNTIME_ERROR"
    UE5_SHADER_ERROR = "UE5_SHADER_ERROR"
    UE5_NIAGARA_ERROR = "UE5_NIAGARA_ERROR"
    UE5_REFERENCE_ERROR = "UE5_REFERENCE_ERROR"
    UE5_CONNECTION_ERROR = "UE5_CONNECTION_ERROR"
    UE5_PERMISSION_DENIED = "UE5_PERMISSION_DENIED"


@dataclass
class UE5ErrorContext:
    """Rich operational context captured alongside a bridge error."""
    error_code: UE5ErrorCode
    message: str
    uaf_object_id: Optional[str] = None
    ue5_path: Optional[str] = None
    operation: Optional[str] = None
    revision: Optional[int] = None
    transaction_id: Optional[str] = None
    frame: int = 0
    state_hash: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "uaf_object_id": self.uaf_object_id,
            "ue5_path": self.ue5_path,
            "operation": self.operation,
            "revision": self.revision,
            "transaction_id": self.transaction_id,
            "frame": self.frame,
            "state_hash": self.state_hash,
            "details": self.details,
        }


class UE5BridgeError(Exception):
    """Base exception for all LiveLink and bridge interoperability errors."""

    def __init__(self, message: str, context: Optional[UE5ErrorContext] = None) -> None:
        super().__init__(message)
        self.context = context or UE5ErrorContext(
            error_code=UE5ErrorCode.UE5_RUNTIME_ERROR,
            message=message,
        )
