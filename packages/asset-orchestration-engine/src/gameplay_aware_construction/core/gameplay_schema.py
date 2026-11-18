import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .gameplay_types import (
    ActorType, InteractionType, CollisionLayer, CollisionPurpose,
    SurfaceWalkability, TraversalType, GameplayTag, GameplaySeverity
)

@dataclass
class ActorProfile:
    actor_type: ActorType = ActorType.PLAYER
    height: float = 1.80 # metros
    width: float = 0.60  # metros
    clearance: float = 0.80 # espacio mínimo de paso
    step_height: float = 0.35 # altura máxima de escalón
    max_slope: float = 40.0 # grados de pendiente máxima

@dataclass
class InteractionPoint:
    point_id: str
    interaction_type: InteractionType
    position: Tuple[float, float, float]
    activation_radius: float = 1.50
    required_clearance: float = 0.80
    is_blocked: bool = False

@dataclass
class GameplayCollisionProfile:
    layer: CollisionLayer = CollisionLayer.WORLD
    purpose: CollisionPurpose = CollisionPurpose.PHYSICAL
    strategy: str = "BOX"
    extents: Tuple[float, float, float] = (1.0, 1.0, 1.0)

CollisionProfile = GameplayCollisionProfile

@dataclass
class SpawnPoint:
    spawn_id: str
    actor_type: ActorType = ActorType.PLAYER
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    is_valid_ground: bool = True
    is_inside_geometry: bool = False
    has_clearance: bool = True

@dataclass
class StairDefinition:
    step_count: int = 12
    step_height: float = 0.18 # m
    step_depth: float = 0.28  # m
    width: float = 1.00       # m
    slope: float = 32.7       # grados (atan(0.18/0.28))

@dataclass
class DoorGameplayDefinition:
    door_id: str
    width: float = 0.90   # m
    height: float = 2.10  # m
    clearance: float = 0.90 # m
    is_locked: bool = False
    open_space_clear: bool = True

@dataclass
class GameplayContract:
    asset_id: str
    provided_interactions: List[InteractionType] = field(default_factory=list)
    tags: List[GameplayTag] = field(default_factory=list)
    minimum_door_width: float = 0.80
    minimum_ceiling_height: float = 2.40

@dataclass
class GameplayValidationReport:
    asset_id: str
    scale_status: GameplaySeverity = GameplaySeverity.PASS
    collision_status: GameplaySeverity = GameplaySeverity.PASS
    navigation_status: GameplaySeverity = GameplaySeverity.PASS
    interaction_status: GameplaySeverity = GameplaySeverity.PASS
    traversal_status: GameplaySeverity = GameplaySeverity.PASS
    spawn_status: GameplaySeverity = GameplaySeverity.PASS
    critical_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    gameplay_score: float = 1.00
    is_valid: bool = True

@dataclass
class GameplaySpecification:
    spec_id: str
    primary_actor: ActorProfile = field(default_factory=ActorProfile)
    required_tags: List[GameplayTag] = field(default_factory=list)
    required_interactions: List[InteractionType] = field(default_factory=list)
