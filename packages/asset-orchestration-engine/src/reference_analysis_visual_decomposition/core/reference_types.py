from enum import Enum

class ReferenceModality(str, Enum):
    CONCEPT_ART = "CONCEPT_ART"
    SCREENSHOT = "SCREENSHOT"
    RENDER = "RENDER"
    PHOTO = "PHOTO"
    DIAGRAM = "DIAGRAM"
    TEXTURE_SWATCH = "TEXTURE_SWATCH"

class CameraPerspective(str, Enum):
    FRONT = "FRONT"
    SIDE = "SIDE"
    TOP = "TOP"
    ISOMETRIC_THREE_QUARTERS = "ISOMETRIC_THREE_QUARTERS"
    PERSPECTIVE_UNKNOWN = "PERSPECTIVE_UNKNOWN"

class ExtractedMaterialType(str, Enum):
    WOOD = "WOOD"
    IRON = "IRON"
    STEEL = "STEEL"
    STONE = "STONE"
    LEATHER = "LEATHER"
    FABRIC = "FABRIC"
    GLASS = "GLASS"
    PLASTIC = "PLASTIC"
    OTHER = "OTHER"

class StyleArchetype(str, Enum):
    STYLIZED = "STYLIZED"
    LOW_POLY = "LOW_POLY"
    SEMI_REALISTIC = "SEMI_REALISTIC"
    PHOTOREALISTIC = "PHOTOREALISTIC"
    HAND_PAINTED = "HAND_PAINTED"

class ConfidenceTier(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNCERTAIN = "UNCERTAIN"

class VisualFeatureImportance(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
