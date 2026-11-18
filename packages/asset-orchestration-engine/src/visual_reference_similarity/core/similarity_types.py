from enum import Enum

class ReferenceType(str, Enum):
    IMAGE = "IMAGE"
    PHOTO = "PHOTO"
    CONCEPT_ART = "CONCEPT_ART"
    CONCEPT_SHEET = "CONCEPT_SHEET"
    SCREENSHOT = "SCREENSHOT"
    RENDER = "RENDER"
    MODEL = "MODEL"
    VIDEO_FRAME = "VIDEO_FRAME"
    STYLE_BOARD = "STYLE_BOARD"

class ReferencePriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class ReferenceCategory(str, Enum):
    STRUCTURE = "STRUCTURE"
    SILHOUETTE = "SILHOUETTE"
    STYLE = "STYLE"
    MATERIAL = "MATERIAL"
    COLOR = "COLOR"
    DETAIL = "DETAIL"
    PROPORTION = "PROPORTION"
    COMPOSITION = "COMPOSITION"

class EvaluationStatus(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    NOT_EVALUATED = "NOT_EVALUATED"

class DifferenceType(str, Enum):
    MISSING = "MISSING"
    EXTRA = "EXTRA"
    WRONG_SHAPE = "WRONG_SHAPE"
    WRONG_SIZE = "WRONG_SIZE"
    WRONG_POSITION = "WRONG_POSITION"
    WRONG_COUNT = "WRONG_COUNT"
    WRONG_COLOR = "WRONG_COLOR"
    WRONG_MATERIAL = "WRONG_MATERIAL"
    WRONG_STYLE = "WRONG_STYLE"
    WRONG_DETAIL = "WRONG_DETAIL"

class DifferenceSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class CorrectionPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class ViewDirection(str, Enum):
    FRONT = "FRONT"
    BACK = "BACK"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    THREE_QUARTER = "THREE_QUARTER"
