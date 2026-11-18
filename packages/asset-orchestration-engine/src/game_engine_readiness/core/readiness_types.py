from enum import Enum

class ReadinessStatus(str, Enum):
    READY = "READY"
    READY_WITH_WARNINGS = "READY_WITH_WARNINGS"
    NOT_READY = "NOT_READY"
    FAILED = "FAILED"

class EngineTarget(str, Enum):
    UNREAL_ENGINE_5 = "UNREAL_ENGINE_5"
    UNREAL_ENGINE_4 = "UNREAL_ENGINE_4"
    GENERIC_REALTIME = "GENERIC_REALTIME"

class ValidationSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    BLOCKER = "BLOCKER"

class PivotMode(str, Enum):
    BASE = "BASE"
    CENTER = "CENTER"
    ORIGIN = "ORIGIN"
    CUSTOM = "CUSTOM"
    COMPONENT_DEFINED = "COMPONENT_DEFINED"

class CoordinateSystem(str, Enum):
    Z_UP_LEFT_HANDED = "Z_UP_LEFT_HANDED"   # Unreal Engine standard
    Z_UP_RIGHT_HANDED = "Z_UP_RIGHT_HANDED" # Blender standard
    Y_UP_RIGHT_HANDED = "Y_UP_RIGHT_HANDED" # Maya / Unity standard

class NaniteReadinessState(str, Enum):
    NANITE_READY = "NANITE_READY"
    NANITE_NOT_RECOMMENDED = "NANITE_NOT_RECOMMENDED"
    NANITE_UNSUPPORTED = "NANITE_UNSUPPORTED"
    NANITE_CONFIGURATION_REQUIRED = "NANITE_CONFIGURATION_REQUIRED"
