"""
Universal Runtime Physics Model Definitions (UAF-81.74).
Normative dataclasses, enumerations, and serialization structures for runtime physics.
"""

from __future__ import annotations
import copy
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


class PhysicsWorldState(str, Enum):
    CREATED = "CREATED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    SIMULATING = "SIMULATING"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    DESTROYED = "DESTROYED"


class BodyType(str, Enum):
    STATIC = "STATIC"
    DYNAMIC = "DYNAMIC"
    KINEMATIC = "KINEMATIC"


class CollisionShapeType(str, Enum):
    BOX = "BOX"
    SPHERE = "SPHERE"
    CAPSULE = "CAPSULE"
    CYLINDER = "CYLINDER"
    PLANE = "PLANE"
    CONVEX = "CONVEX"
    TRIANGLE_MESH = "TRIANGLE_MESH"
    HEIGHTFIELD = "HEIGHTFIELD"
    COMPOUND = "COMPOUND"


class MaterialCombinePolicy(str, Enum):
    AVERAGE = "AVERAGE"
    MIN = "MIN"
    MAX = "MAX"
    MULTIPLY = "MULTIPLY"
    CUSTOM = "CUSTOM"


class ConstraintType(str, Enum):
    FIXED = "FIXED"
    DISTANCE = "DISTANCE"
    HINGE = "HINGE"
    SLIDER = "SLIDER"
    SPRING = "SPRING"
    GENERIC = "GENERIC"


class PhysicsEventType(str, Enum):
    CONTACT_BEGIN = "CONTACT_BEGIN"
    CONTACT_STAY = "CONTACT_STAY"
    CONTACT_END = "CONTACT_END"
    TRIGGER_ENTER = "TRIGGER_ENTER"
    TRIGGER_STAY = "TRIGGER_STAY"
    TRIGGER_EXIT = "TRIGGER_EXIT"
    BODY_SLEEP = "BODY_SLEEP"
    BODY_WAKE = "BODY_WAKE"


def copy_dict_deterministic(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: copy_dict_deterministic(v) for k, v in sorted(data.items())}
    elif isinstance(data, list):
        return [copy_dict_deterministic(x) for x in data]
    return copy.deepcopy(data)


@dataclass
class PhysicsMaterial:
    material_id: str
    name: str = "DefaultMaterial"
    friction: float = 0.5
    restitution: float = 0.0
    density: float = 1000.0
    combine_policy: MaterialCombinePolicy = MaterialCombinePolicy.AVERAGE
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "material_id": self.material_id,
            "name": self.name,
            "friction": round(float(self.friction), 6),
            "restitution": round(float(self.restitution), 6),
            "density": round(float(self.density), 6),
            "combine_policy": self.combine_policy.value,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class CollisionShape:
    shape_type: CollisionShapeType
    params: Dict[str, Any] = field(default_factory=dict)
    local_position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    local_rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 1.0])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "shape_type": self.shape_type.value,
            "params": copy_dict_deterministic(self.params),
            "local_position": [round(float(v), 6) for v in self.local_position],
            "local_rotation": [round(float(v), 6) for v in self.local_rotation],
        }


@dataclass
class Collider:
    collider_id: str
    body_id: str
    shape: CollisionShape
    material: Optional[PhysicsMaterial] = None
    is_trigger: bool = False
    layer: int = 1
    mask: int = 0xFFFFFFFF
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "collider_id": self.collider_id,
            "body_id": self.body_id,
            "shape": self.shape.to_dict(),
            "material": self.material.to_dict() if self.material else None,
            "is_trigger": self.is_trigger,
            "layer": self.layer,
            "mask": self.mask,
            "enabled": self.enabled,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class PhysicsBody:
    body_id: str
    entity_id: str
    body_type: BodyType = BodyType.DYNAMIC
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 1.0])
    linear_velocity: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    angular_velocity: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    mass: float = 1.0
    inverse_mass: float = 1.0
    linear_damping: float = 0.01
    angular_damping: float = 0.05
    gravity_scale: float = 1.0
    enabled: bool = True
    is_sleeping: bool = False
    sleep_timer: float = 0.0
    colliders: Dict[str, Collider] = field(default_factory=dict)
    forces: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    torques: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.body_type == BodyType.STATIC:
            self.mass = 0.0
            self.inverse_mass = 0.0
        elif self.mass > 0.0:
            self.inverse_mass = 1.0 / self.mass
        else:
            self.inverse_mass = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "body_id": self.body_id,
            "entity_id": self.entity_id,
            "body_type": self.body_type.value,
            "position": [round(float(v), 6) for v in self.position],
            "rotation": [round(float(v), 6) for v in self.rotation],
            "linear_velocity": [round(float(v), 6) for v in self.linear_velocity],
            "angular_velocity": [round(float(v), 6) for v in self.angular_velocity],
            "mass": round(float(self.mass), 6),
            "inverse_mass": round(float(self.inverse_mass), 6),
            "linear_damping": round(float(self.linear_damping), 6),
            "angular_damping": round(float(self.angular_damping), 6),
            "gravity_scale": round(float(self.gravity_scale), 6),
            "enabled": self.enabled,
            "is_sleeping": self.is_sleeping,
            "sleep_timer": round(float(self.sleep_timer), 6),
            "colliders": {cid: c.to_dict() for cid, c in sorted(self.colliders.items())},
            "forces": [round(float(v), 6) for v in self.forces],
            "torques": [round(float(v), 6) for v in self.torques],
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class PhysicsConstraint:
    constraint_id: str
    constraint_type: ConstraintType
    body_a_id: str
    body_b_id: str
    anchor_a: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    anchor_b: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    limits: Dict[str, float] = field(default_factory=dict)
    stiffness: float = 1.0
    damping: float = 0.1
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "constraint_id": self.constraint_id,
            "constraint_type": self.constraint_type.value,
            "body_a_id": self.body_a_id,
            "body_b_id": self.body_b_id,
            "anchor_a": [round(float(v), 6) for v in self.anchor_a],
            "anchor_b": [round(float(v), 6) for v in self.anchor_b],
            "limits": {k: round(float(v), 6) for k, v in sorted(self.limits.items())},
            "stiffness": round(float(self.stiffness), 6),
            "damping": round(float(self.damping), 6),
            "enabled": self.enabled,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class CharacterController:
    controller_id: str
    entity_id: str
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    velocity: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    is_grounded: bool = False
    ground_normal: List[float] = field(default_factory=lambda: [0.0, 1.0, 0.0])
    slope_limit: float = 45.0
    step_offset: float = 0.3
    height: float = 1.8
    radius: float = 0.3
    gravity_scale: float = 1.0
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "controller_id": self.controller_id,
            "entity_id": self.entity_id,
            "position": [round(float(v), 6) for v in self.position],
            "velocity": [round(float(v), 6) for v in self.velocity],
            "is_grounded": self.is_grounded,
            "ground_normal": [round(float(v), 6) for v in self.ground_normal],
            "slope_limit": round(float(self.slope_limit), 6),
            "step_offset": round(float(self.step_offset), 6),
            "height": round(float(self.height), 6),
            "radius": round(float(self.radius), 6),
            "gravity_scale": round(float(self.gravity_scale), 6),
            "enabled": self.enabled,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class ContactPoint:
    point: List[float]
    normal: List[float]
    penetration: float
    impulse: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "point": [round(float(v), 6) for v in self.point],
            "normal": [round(float(v), 6) for v in self.normal],
            "penetration": round(float(self.penetration), 6),
            "impulse": round(float(self.impulse), 6),
        }


@dataclass
class ContactManifold:
    body_a_id: str
    body_b_id: str
    collider_a_id: str
    collider_b_id: str
    points: List[ContactPoint] = field(default_factory=list)
    normal: List[float] = field(default_factory=lambda: [0.0, 1.0, 0.0])
    penetration: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "body_a_id": self.body_a_id,
            "body_b_id": self.body_b_id,
            "collider_a_id": self.collider_a_id,
            "collider_b_id": self.collider_b_id,
            "points": [p.to_dict() for p in self.points],
            "normal": [round(float(v), 6) for v in self.normal],
            "penetration": round(float(self.penetration), 6),
        }


@dataclass
class RaycastHit:
    hit: bool = False
    distance: float = 0.0
    point: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    normal: List[float] = field(default_factory=lambda: [0.0, 1.0, 0.0])
    collider_id: str = ""
    body_id: str = ""
    entity_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hit": self.hit,
            "distance": round(float(self.distance), 6),
            "point": [round(float(v), 6) for v in self.point],
            "normal": [round(float(v), 6) for v in self.normal],
            "collider_id": self.collider_id,
            "body_id": self.body_id,
            "entity_id": self.entity_id,
        }


@dataclass
class OverlapHit:
    hit: bool = False
    collider_id: str = ""
    body_id: str = ""
    entity_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hit": self.hit,
            "collider_id": self.collider_id,
            "body_id": self.body_id,
            "entity_id": self.entity_id,
        }


@dataclass
class SweepHit:
    hit: bool = False
    distance: float = 0.0
    point: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    normal: List[float] = field(default_factory=lambda: [0.0, 1.0, 0.0])
    collider_id: str = ""
    body_id: str = ""
    entity_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hit": self.hit,
            "distance": round(float(self.distance), 6),
            "point": [round(float(v), 6) for v in self.point],
            "normal": [round(float(v), 6) for v in self.normal],
            "collider_id": self.collider_id,
            "body_id": self.body_id,
            "entity_id": self.entity_id,
        }


@dataclass
class PhysicsEvent:
    event_type: PhysicsEventType
    body_a_id: str
    body_b_id: str = ""
    collider_a_id: str = ""
    collider_b_id: str = ""
    timestamp: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "body_a_id": self.body_a_id,
            "body_b_id": self.body_b_id,
            "collider_a_id": self.collider_a_id,
            "collider_b_id": self.collider_b_id,
            "timestamp": round(float(self.timestamp), 6),
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class PhysicsSimulationSettings:
    gravity: List[float] = field(default_factory=lambda: [0.0, -9.81, 0.0])
    fixed_delta_time: float = 1.0 / 60.0
    solver_iterations: int = 8
    velocity_iterations: int = 8
    position_iterations: int = 4
    sleep_linear_threshold: float = 0.01
    sleep_angular_threshold: float = 0.01
    sleep_time_threshold: float = 0.5
    continuous_collision: bool = False
    max_substeps: int = 4
    max_bodies: int = 10000
    max_colliders: int = 20000
    max_constraints: int = 5000
    max_query_distance: float = 1000.0
    max_linear_velocity: float = 100.0
    max_angular_velocity: float = 50.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gravity": [round(float(v), 6) for v in self.gravity],
            "fixed_delta_time": round(float(self.fixed_delta_time), 6),
            "solver_iterations": self.solver_iterations,
            "velocity_iterations": self.velocity_iterations,
            "position_iterations": self.position_iterations,
            "sleep_linear_threshold": round(float(self.sleep_linear_threshold), 6),
            "sleep_angular_threshold": round(float(self.sleep_angular_threshold), 6),
            "sleep_time_threshold": round(float(self.sleep_time_threshold), 6),
            "continuous_collision": self.continuous_collision,
            "max_substeps": self.max_substeps,
            "max_bodies": self.max_bodies,
            "max_colliders": self.max_colliders,
            "max_constraints": self.max_constraints,
            "max_query_distance": round(float(self.max_query_distance), 6),
            "max_linear_velocity": round(float(self.max_linear_velocity), 6),
            "max_angular_velocity": round(float(self.max_angular_velocity), 6),
        }


@dataclass
class PhysicsWorld:
    physics_world_id: str
    runtime_world_id: str = ""
    state: PhysicsWorldState = PhysicsWorldState.CREATED
    settings: PhysicsSimulationSettings = field(default_factory=PhysicsSimulationSettings)
    bodies: Dict[str, PhysicsBody] = field(default_factory=dict)
    colliders: Dict[str, Collider] = field(default_factory=dict)
    constraints: Dict[str, PhysicsConstraint] = field(default_factory=dict)
    character_controllers: Dict[str, CharacterController] = field(default_factory=dict)
    materials: Dict[str, PhysicsMaterial] = field(default_factory=dict)
    collision_matrix: Dict[int, int] = field(default_factory=dict)
    event_queue: List[PhysicsEvent] = field(default_factory=list)
    time_seconds: float = 0.0
    time_accumulator: float = 0.0
    frame_index: int = 0
    destroyed_body_ids: Set[str] = field(default_factory=set)
    destroyed_collider_ids: Set[str] = field(default_factory=set)
    content_fingerprint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "physics_world_id": self.physics_world_id,
            "runtime_world_id": self.runtime_world_id,
            "state": self.state.value,
            "settings": self.settings.to_dict(),
            "time_seconds": round(float(self.time_seconds), 6),
            "frame_index": self.frame_index,
            "bodies": {bid: b.to_dict() for bid, b in sorted(self.bodies.items())},
            "colliders": {cid: c.to_dict() for cid, c in sorted(self.colliders.items())},
            "constraints": {cid: c.to_dict() for cid, c in sorted(self.constraints.items())},
            "character_controllers": {cid: c.to_dict() for cid, c in sorted(self.character_controllers.items())},
            "materials": {mid: m.to_dict() for mid, m in sorted(self.materials.items())},
        }

    def compute_fingerprint(self) -> str:
        data = self.to_dict()
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def __post_init__(self):
        if not self.content_fingerprint:
            self.content_fingerprint = self.compute_fingerprint()


@dataclass
class PhysicsSnapshot:
    snapshot_id: str
    physics_world_id: str
    frame_index: int
    timestamp: float
    world_data: Dict[str, Any]
    content_fingerprint: str = ""

    def __post_init__(self):
        if not self.content_fingerprint:
            serialized = json.dumps(self.world_data, sort_keys=True)
            self.content_fingerprint = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "physics_world_id": self.physics_world_id,
            "frame_index": self.frame_index,
            "timestamp": round(float(self.timestamp), 6),
            "content_fingerprint": self.content_fingerprint,
            "world_data": copy_dict_deterministic(self.world_data),
        }


@dataclass
class PhysicsReplayCommand:
    frame_index: int
    command_type: str
    target_id: str
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_index": self.frame_index,
            "command_type": self.command_type,
            "target_id": self.target_id,
            "parameters": copy_dict_deterministic(self.parameters),
        }


@dataclass
class PhysicsReplay:
    replay_id: str
    initial_snapshot: PhysicsSnapshot
    commands: List[PhysicsReplayCommand] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "replay_id": self.replay_id,
            "initial_snapshot": self.initial_snapshot.to_dict(),
            "commands": [cmd.to_dict() for cmd in self.commands],
        }
