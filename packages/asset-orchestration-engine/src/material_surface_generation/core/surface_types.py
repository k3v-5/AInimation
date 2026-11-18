from enum import Enum

class SurfaceTypeTag(str, Enum):
    METAL = "METAL"
    PAINTED_METAL = "PAINTED_METAL"
    RAW_METAL = "RAW_METAL"
    WOOD = "WOOD"
    STONE = "STONE"
    CONCRETE = "CONCRETE"
    PLASTIC = "PLASTIC"
    RUBBER = "RUBBER"
    GLASS = "GLASS"
    CERAMIC = "CERAMIC"
    FABRIC = "FABRIC"
    LEATHER = "LEATHER"
    SKIN = "SKIN"
    ORGANIC = "ORGANIC"
    LIQUID = "LIQUID"
    EMISSIVE = "EMISSIVE"
    CUSTOM = "CUSTOM"

class ShaderModelType(str, Enum):
    DEFAULT_LIT = "DEFAULT_LIT"
    SUBSURFACE = "SUBSURFACE"
    CLEAR_COAT = "CLEAR_COAT"
    TWO_SIDED_FOLIAGE = "TWO_SIDED_FOLIAGE"
    UNLIT = "UNLIT"

class ColorSpaceType(str, Enum):
    SRGB = "sRGB"
    LINEAR = "Linear"
    NON_COLOR = "Non-Color"

class UVUnwrapMethod(str, Enum):
    SMART = "SMART"
    ANGLE_BASED = "ANGLE_BASED"
    CONFORMAL = "CONFORMAL"
    BOX = "BOX"
    CYLINDRICAL = "CYLINDRICAL"
    PLANAR = "PLANAR"
    CUSTOM = "CUSTOM"
    UDIM = "UDIM"
    PROCEDURAL = "PROCEDURAL"

class BakeChannelType(str, Enum):
    NORMAL = "NORMAL"
    AO = "AO"
    CURVATURE = "CURVATURE"
    POSITION = "POSITION"
    THICKNESS = "THICKNESS"
    ORM = "ORM"
    ID_MASK = "ID_MASK"

class AttributeSemanticName(str, Enum):
    AO = "AO"
    WEAR = "WEAR"
    DUST = "DUST"
    MASK = "MASK"
    BLEND = "BLEND"
    DAMAGE = "DAMAGE"
    CUSTOM = "CUSTOM"

class InvalidationState(str, Enum):
    VALID = "VALID"
    STALE = "STALE"
    INVALID = "INVALID"

class SurfaceValidationSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
