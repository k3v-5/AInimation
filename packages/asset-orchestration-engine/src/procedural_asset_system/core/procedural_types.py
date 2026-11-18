from enum import Enum

class PrimitiveType(str, Enum):
    BOX = "BOX"
    CYLINDER = "CYLINDER"
    PLANE = "PLANE"
    WEDGE = "WEDGE"
    ARCH = "ARCH"
    BEAM = "BEAM"
    PANEL = "PANEL"
    FRAME = "FRAME"
    STAIR = "STAIR"
    ROOF_SECTION = "ROOF_SECTION"

class OperationType(str, Enum):
    CREATE_PRIMITIVE = "CREATE_PRIMITIVE"
    MOVE = "MOVE"
    ROTATE = "ROTATE"
    SCALE = "SCALE"
    BOOLEAN = "BOOLEAN"
    EXTRUDE = "EXTRUDE"
    BEVEL = "BEVEL"

class QualityLevel(str, Enum):
    BLOCKOUT = "BLOCKOUT"
    GAMEPLAY = "GAMEPLAY"
    FINAL = "FINAL"
    CINEMATIC = "CINEMATIC"

class ConstructionPass(str, Enum):
    STRUCTURAL = "STRUCTURAL"
    FUNCTIONAL = "FUNCTIONAL"
    DETAIL = "DETAIL"
    SURFACE = "SURFACE"
    FINAL = "FINAL"

class RoofStyle(str, Enum):
    GABLE = "GABLE"
    HIP = "HIP"
    SHED = "SHED"
    FLAT = "FLAT"
    MANSARD = "MANSARD"
    THATCH = "THATCH"

class OpeningType(str, Enum):
    DOOR = "DOOR"
    WINDOW = "WINDOW"
    ARCHWAY = "ARCHWAY"
