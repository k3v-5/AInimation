"""
Domain error model for UAF with explicit recoverability and serializability.
UAF-81.0 Sections 29, 30, 31.
"""

from typing import Dict, Any, Optional


class UAFError(Exception):
    """
    Base structured domain exception for Universal Asset Factory.
    """
    def __init__(
        self,
        message: str,
        code: str = "UAF_ERROR",
        operation_id: Optional[str] = None,
        asset_id: Optional[str] = None,
        phase: str = "execution",
        recoverable: bool = False,
        retryable: bool = False,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.operation_id = operation_id
        self.asset_id = asset_id
        self.phase = phase
        self.recoverable = recoverable
        self.retryable = retryable
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.__class__.__name__,
            "code": self.code,
            "message": self.message,
            "operation_id": self.operation_id,
            "asset_id": self.asset_id,
            "phase": self.phase,
            "recoverable": self.recoverable,
            "retryable": self.retryable,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UAFError":
        return cls(
            message=data.get("message", "Unknown UAF Error"),
            code=data.get("code", "UAF_ERROR"),
            operation_id=data.get("operation_id"),
            asset_id=data.get("asset_id"),
            phase=data.get("phase", "execution"),
            recoverable=bool(data.get("recoverable", False)),
            retryable=bool(data.get("retryable", False)),
            details=data.get("details", {}),
        )


class SpecificationError(UAFError):
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("code", "SPECIFICATION_ERROR")
        kwargs.setdefault("recoverable", True)
        super().__init__(message, **kwargs)


class ConfigurationError(UAFError):
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("code", "CONFIGURATION_ERROR")
        kwargs.setdefault("recoverable", True)
        super().__init__(message, **kwargs)


class CapabilityError(UAFError):
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("code", "CAPABILITY_ERROR")
        super().__init__(message, **kwargs)


class GenerationError(UAFError):
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("code", "GENERATION_ERROR")
        kwargs.setdefault("retryable", True)
        super().__init__(message, **kwargs)


class ValidationError(UAFError):
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("code", "VALIDATION_ERROR")
        super().__init__(message, **kwargs)


class ArtifactError(UAFError):
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("code", "ARTIFACT_ERROR")
        super().__init__(message, **kwargs)


class PersistenceError(UAFError):
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("code", "PERSISTENCE_ERROR")
        kwargs.setdefault("retryable", True)
        super().__init__(message, **kwargs)


class PackagingError(UAFError):
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("code", "PACKAGING_ERROR")
        super().__init__(message, **kwargs)


class PermissionError(UAFError):
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("code", "PERMISSION_ERROR")
        super().__init__(message, **kwargs)


class ResourceError(UAFError):
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("code", "RESOURCE_ERROR")
        kwargs.setdefault("recoverable", True)
        kwargs.setdefault("retryable", True)
        super().__init__(message, **kwargs)


class ExternalProcessError(UAFError):
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("code", "EXTERNAL_PROCESS_ERROR")
        kwargs.setdefault("retryable", True)
        super().__init__(message, **kwargs)


class RecoveryError(UAFError):
    def __init__(self, message: str, **kwargs):
        kwargs.setdefault("code", "RECOVERY_ERROR")
        super().__init__(message, **kwargs)
