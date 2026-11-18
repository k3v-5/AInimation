from enum import Enum

class ActorType(str, Enum):
    PLAYER = "PLAYER"
    NPC_SMALL = "NPC_SMALL"
    NPC_MEDIUM = "NPC_MEDIUM"
    NPC_LARGE = "NPC_LARGE"
    VEHICLE = "VEHICLE"

class InteractionType(str, Enum):
    USE = "USE"
    OPEN = "OPEN"
    CLOSE = "CLOSE"
    ENTER = "ENTER"
    EXIT = "EXIT"
    PICKUP = "PICKUP"
    CLIMB = "CLIMB"
    SIT = "SIT"
    ACTIVATE = "ACTIVATE"
    ATTACK = "ATTACK"

class CollisionLayer(str, Enum):
    WORLD = "WORLD"
    PLAYER = "PLAYER"
    NPC = "NPC"
    VEHICLE = "VEHICLE"
    PROJECTILE = "PROJECTILE"
    INTERACTION = "INTERACTION"
    TRIGGER = "TRIGGER"

class CollisionPurpose(str, Enum):
    PHYSICAL = "PHYSICAL"
    NAVIGATION = "NAVIGATION"
    INTERACTION = "INTERACTION"
    DAMAGE = "DAMAGE"
    TRIGGER = "TRIGGER"

class SurfaceWalkability(str, Enum):
    WALKABLE = "WALKABLE"
    NON_WALKABLE = "NON_WALKABLE"
    CONDITIONAL = "CONDITIONAL"

class TraversalType(str, Enum):
    WALK = "WALK"
    RUN = "RUN"
    JUMP = "JUMP"
    CLIMB = "CLIMB"
    CROUCH = "CROUCH"

class GameplayTag(str, Enum):
    INTERACTABLE = "INTERACTABLE"
    NAVIGABLE = "NAVIGABLE"
    CLIMBABLE = "CLIMBABLE"
    ENTERABLE = "ENTERABLE"
    COVER = "COVER"
    SPAWNABLE = "SPAWNABLE"
    QUEST_RELEVANT = "QUEST_RELEVANT"

class GameplaySeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    PASS = "PASS"
