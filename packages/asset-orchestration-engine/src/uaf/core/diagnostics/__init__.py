"""
UAF Core Diagnostics Package
"""

from .severity import DiagnosticSeverity
from .diagnostic import Diagnostic
from .errors import (
    UAFError,
    SpecificationError,
    ConfigurationError,
    CapabilityError,
    GenerationError,
    ValidationError,
    ArtifactError,
    PersistenceError,
    PackagingError,
    PermissionError,
    ResourceError,
    ExternalProcessError,
    RecoveryError,
)
from .metrics import OperationMetrics

__all__ = [
    "DiagnosticSeverity",
    "Diagnostic",
    "UAFError",
    "SpecificationError",
    "ConfigurationError",
    "CapabilityError",
    "GenerationError",
    "ValidationError",
    "ArtifactError",
    "PersistenceError",
    "PackagingError",
    "PermissionError",
    "ResourceError",
    "ExternalProcessError",
    "RecoveryError",
    "OperationMetrics",
]
