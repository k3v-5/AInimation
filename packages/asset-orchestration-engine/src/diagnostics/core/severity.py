from enum import Enum

class FailureSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"

    @classmethod
    def from_context(cls, error_text: str, is_blocking: bool = False, is_critical_dimension: bool = False) -> "FailureSeverity":
        txt = error_text.upper()
        if "FATAL" in txt or "CORRUPTED" in txt:
            return cls.FATAL
        if is_blocking or is_critical_dimension or "CRITICAL" in txt or "CRASH" in txt:
            return cls.CRITICAL
        if "ERROR" in txt or "FAIL" in txt or "DENIED" in txt:
            return cls.ERROR
        if "WARNING" in txt or "DEPRECATED" in txt:
            return cls.WARNING
        return cls.INFO
