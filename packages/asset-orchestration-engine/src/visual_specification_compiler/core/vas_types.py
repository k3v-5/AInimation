from enum import Enum

class RequirementClass(str, Enum):
    HARD = "HARD"
    SOFT = "SOFT"
    PREFERENCE = "PREFERENCE"
    INFORMATIONAL = "INFORMATIONAL"

class ValidationMethod(str, Enum):
    NUMERIC = "NUMERIC"
    GEOMETRIC = "GEOMETRIC"
    VISUAL = "VISUAL"
    SEMANTIC = "SEMANTIC"
    MATERIAL = "MATERIAL"
    TOPOLOGICAL = "TOPOLOGICAL"
    STRUCTURAL = "STRUCTURAL"
    ENGINE = "ENGINE"
    MANUAL = "MANUAL"

class RequirementOrigin(str, Enum):
    USER_PROMPT = "USER_PROMPT"
    REFERENCE = "REFERENCE"
    F51_INTENT = "F51_INTENT"
    F54_SEMANTIC = "F54_SEMANTIC"
    F55_REFERENCE = "F55_REFERENCE"
    PROJECT_CONFIG = "PROJECT_CONFIG"
    PREVIOUS_GENERATION = "PREVIOUS_GENERATION"
    DEFAULT = "DEFAULT"

class ContradictionSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AmbiguitySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class InformationState(str, Enum):
    EXPLICIT = "EXPLICIT"
    OBSERVED = "OBSERVED"
    INFERRED = "INFERRED"
    DEFAULTED = "DEFAULTED"
    UNKNOWN = "UNKNOWN"
    CONFLICTED = "CONFLICTED"

class EngineTarget(str, Enum):
    UNREAL_ENGINE_5 = "UNREAL_ENGINE_5"
    UNITY = "UNITY"
    GENERIC = "GENERIC"
