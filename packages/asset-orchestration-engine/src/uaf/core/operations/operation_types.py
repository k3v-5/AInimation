"""
OperationType enumerates conceptual operation categories in UAF.
UAF-81.0 Section 18.
"""

from enum import Enum


class OperationType(str, Enum):
    GENERATE = "GENERATE"
    TRANSFORM = "TRANSFORM"
    ASSEMBLE = "ASSEMBLE"
    VALIDATE = "VALIDATE"
    OPTIMIZE = "OPTIMIZE"
    PACKAGE = "PACKAGE"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    PUBLISH = "PUBLISH"

    @classmethod
    def from_str(cls, value: str) -> "OperationType":
        normalized = value.strip().upper()
        return cls(normalized)
