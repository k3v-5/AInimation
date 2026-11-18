"""
DiagnosticSeverity enumeration.
UAF-81.0 Section 28.
"""

from enum import Enum


class DiagnosticSeverity(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
