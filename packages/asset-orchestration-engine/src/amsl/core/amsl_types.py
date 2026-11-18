from enum import Enum

class AMSLAssetType(str, Enum):
    PROP = "PROP"
    BUILDING = "BUILDING"
    CHARACTER = "CHARACTER"
    VEHICLE = "VEHICLE"
    WEAPON = "WEAPON"
    FURNITURE = "FURNITURE"
    VEGETATION = "VEGETATION"
    TERRAIN = "TERRAIN"
    ENVIRONMENT = "ENVIRONMENT"
    VFX = "VFX"
    OTHER = "OTHER"

class AMSLAssetPurpose(str, Enum):
    DECORATIVE = "decorative"
    GAMEPLAY = "gameplay"
    ENVIRONMENT = "environment"
    CINEMATIC = "cinematic"
    BACKGROUND = "background"
    INTERACTIVE = "interactive"
    COLLECTIBLE = "collectible"

class DimensionMode(str, Enum):
    ABSOLUTE = "ABSOLUTE"
    RELATIVE = "RELATIVE"
    RANGE = "RANGE"
    APPROXIMATE = "APPROXIMATE"
    UNCONSTRAINED = "UNCONSTRAINED"

class RelationshipType(str, Enum):
    ATTACHED_TO = "ATTACHED_TO"
    ALIGNED_WITH = "ALIGNED_WITH"
    CENTERED_ON = "CENTERED_ON"
    PARENT_OF = "PARENT_OF"
    CHILD_OF = "CHILD_OF"
    ADJACENT_TO = "ADJACENT_TO"
    ABOVE = "ABOVE"
    BELOW = "BELOW"
    INSIDE = "INSIDE"
    OUTSIDE = "OUTSIDE"
    CONNECTED_TO = "CONNECTED_TO"

class StyleFamily(str, Enum):
    MEDIEVAL = "MEDIEVAL"
    MODERN = "MODERN"
    INDUSTRIAL = "INDUSTRIAL"
    SCI_FI = "SCI_FI"
    FANTASY = "FANTASY"
    VICTORIAN = "VICTORIAN"
    RUSTIC = "RUSTIC"
    MILITARY = "MILITARY"
    CARTOON = "CARTOON"
    REALISTIC = "REALISTIC"

class DetailLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    HERO = "HERO"

class MaterialCategory(str, Enum):
    WOOD = "WOOD"
    STONE = "STONE"
    METAL = "METAL"
    GLASS = "GLASS"
    CONCRETE = "CONCRETE"
    FABRIC = "FABRIC"
    LEATHER = "LEATHER"
    CERAMIC = "CERAMIC"
    ORGANIC = "ORGANIC"

class DamageLevel(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    DESTROYED = "DESTROYED"

class CollisionType(str, Enum):
    BOX = "BOX"
    CAPSULE = "CAPSULE"
    CONVEX_HULL = "CONVEX_HULL"
    COMPLEX_MESH = "COMPLEX_MESH"
    NONE = "NONE"

class QualityLevel(str, Enum):
    MOBILE = "MOBILE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    HERO = "HERO"
    CINEMATIC = "CINEMATIC"

class RebuildPolicy(str, Enum):
    NEVER = "NEVER"
    COMPONENT_ONLY = "COMPONENT_ONLY"
    DEPENDENCIES = "DEPENDENCIES"
    FULL_ASSET = "FULL_ASSET"

class ConstraintType(str, Enum):
    HARD = "HARD"
    SOFT = "SOFT"

class ConstraintPriority(str, Enum):
    SYSTEM = "SYSTEM"
    PROJECT = "PROJECT"
    USER_HARD = "USER_HARD"
    USER_SOFT = "USER_SOFT"
    STYLE = "STYLE"
    DEFAULT = "DEFAULT"

class ValidationCategory(str, Enum):
    STRUCTURAL = "STRUCTURAL"
    DIMENSIONAL = "DIMENSIONAL"
    GEOMETRIC = "GEOMETRIC"
    MATERIAL = "MATERIAL"
    VISUAL = "VISUAL"
    GAMEPLAY = "GAMEPLAY"
    PERFORMANCE = "PERFORMANCE"
    REFERENCE = "REFERENCE"
