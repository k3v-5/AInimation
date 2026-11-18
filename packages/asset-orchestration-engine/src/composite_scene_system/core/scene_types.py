from enum import Enum

class SceneType(str, Enum):
    VILLAGE = "VILLAGE"
    CITY_BLOCK = "CITY_BLOCK"
    ROOM = "ROOM"
    BUILDING = "BUILDING"
    DUNGEON = "DUNGEON"
    FOREST = "FOREST"
    ROAD = "ROAD"
    COURTYARD = "COURTYARD"
    BATTLEFIELD = "BATTLEFIELD"
    MARKET = "MARKET"
    PORT = "PORT"
    FORTRESS = "FORTRESS"

class ConstraintPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class SpatialRelationType(str, Enum):
    CONTAINS = "CONTAINS"
    ATTACHED_TO = "ATTACHED_TO"
    ALIGNED_WITH = "ALIGNED_WITH"
    NEAR = "NEAR"
    CONNECTED_TO = "CONNECTED_TO"
    FACING = "FACING"
    SUPPORTS = "SUPPORTS"
    BLOCKS = "BLOCKS"

class PlanningStage(str, Enum):
    PLANNING = "PLANNING"
    BLOCKOUT = "BLOCKOUT"
    MACRO = "MACRO"
    MESO = "MESO"
    MICRO = "MICRO"
    VALIDATION = "VALIDATION"
    COMPLETED = "COMPLETED"

class SceneState(str, Enum):
    PLANNED = "PLANNED"
    BLOCKED = "BLOCKED"
    BUILDING = "BUILDING"
    PARTIAL = "PARTIAL"
    VALIDATING = "VALIDATING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"

class LockState(str, Enum):
    UNLOCKED = "UNLOCKED"
    LOCKED = "LOCKED"
    PROTECTED = "PROTECTED"
    MANUAL_OVERRIDE = "MANUAL_OVERRIDE"

class CollisionSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"
