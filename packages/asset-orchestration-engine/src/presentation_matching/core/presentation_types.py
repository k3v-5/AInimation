from enum import Enum

class ProjectionType(str, Enum):
    PERSPECTIVE = "PERSPECTIVE"
    ORTHOGRAPHIC = "ORTHOGRAPHIC"

class CompositionAlignment(str, Enum):
    CENTER = "CENTER"
    RULE_OF_THIRDS = "RULE_OF_THIRDS"
    CUSTOM = "CUSTOM"
    REFERENCE_MATCH = "REFERENCE_MATCH"

class LightType(str, Enum):
    POINT = "POINT"
    AREA = "AREA"
    SUN = "SUN"
    SPOT = "SPOT"
    ENVIRONMENT = "ENVIRONMENT"

class BackgroundType(str, Enum):
    SOLID = "SOLID"
    GRADIENT = "GRADIENT"
    WORLD = "WORLD"
    TRANSPARENT = "TRANSPARENT"
    ENVIRONMENT = "ENVIRONMENT"

class ViewTransformType(str, Enum):
    FILMIC = "Filmic"
    AGX = "AgX"
    STANDARD = "Standard"
    RAW = "Raw"

class PresentationViewAngle(str, Enum):
    FRONT = "FRONT"
    THREE_QUARTER = "THREE_QUARTER"
    SIDE = "SIDE"
    TOP = "TOP"
    ISOMETRIC = "ISOMETRIC"
    CUSTOM = "CUSTOM"

class InferenceConfidenceLevel(str, Enum):
    KNOWN = "KNOWN"
    ESTIMATED = "ESTIMATED"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"

class PresentationValidationSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
