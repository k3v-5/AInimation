"""
UAF-81.82: Domain Models, Vector Mathematics, Enums and Exception Contracts
for Universal Runtime AI, Navigation Mesh, Dynamic Avoidance & Behavior Trees.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
import enum
import hashlib
import json
import math
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple, Union

# Canonical 3D Vector representation
Vec3 = Tuple[float, float, float]


# ==============================================================================
# 1. VECTOR MATHEMATICS & FINITE NUMERIC VALIDATION
# ==============================================================================

def ensure_finite_float(val: float, context: str = "") -> float:
    """Validate that a float value is finite (not NaN, not +Inf, not -Inf)."""
    if math.isnan(val) or math.isinf(val):
        raise AINumericStateError(f"Non-finite float encountered in {context}: {val}")
    return float(val)


def ensure_finite_vec3(v: Sequence[float], context: str = "") -> Vec3:
    """Validate that a 3D vector contains only finite floats."""
    if len(v) != 3:
        raise AINumericStateError(f"Vec3 must have exactly 3 components in {context}, got {len(v)}")
    x, y, z = float(v[0]), float(v[1]), float(v[2])
    if math.isnan(x) or math.isinf(x) or math.isnan(y) or math.isinf(y) or math.isnan(z) or math.isinf(z):
        raise AINumericStateError(f"Non-finite coordinate in Vec3 ({x}, {y}, {z}) in {context}")
    return (x, y, z)


def vec3_add(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def vec3_sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vec3_scale(a: Vec3, s: float) -> Vec3:
    return (a[0] * s, a[1] * s, a[2] * s)


def vec3_dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vec3_cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def vec3_length_sq(a: Vec3) -> float:
    return a[0] * a[0] + a[1] * a[1] + a[2] * a[2]


def vec3_length(a: Vec3) -> float:
    return math.sqrt(vec3_length_sq(a))


def vec3_distance(a: Vec3, b: Vec3) -> float:
    return vec3_length(vec3_sub(a, b))


def vec3_distance_sq(a: Vec3, b: Vec3) -> float:
    return vec3_length_sq(vec3_sub(a, b))


def vec3_normalize(a: Vec3) -> Vec3:
    l = vec3_length(a)
    if l < 1e-12:
        return (0.0, 0.0, 0.0)
    inv = 1.0 / l
    return (a[0] * inv, a[1] * inv, a[2] * inv)


def vec3_lerp(a: Vec3, b: Vec3, t: float) -> Vec3:
    clamped_t = max(0.0, min(1.0, t))
    return (
        a[0] + (b[0] - a[0]) * clamped_t,
        a[1] + (b[1] - a[1]) * clamped_t,
        a[2] + (b[2] - a[2]) * clamped_t,
    )


# ==============================================================================
# 2. ENUMS
# ==============================================================================

class AIRuntimeWorldState(str, enum.Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    DESTROYED = "DESTROYED"


class PathStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    NO_PATH = "NO_PATH"
    INVALID_START = "INVALID_START"
    INVALID_GOAL = "INVALID_GOAL"
    NAVIGATION_UNAVAILABLE = "NAVIGATION_UNAVAILABLE"
    CANCELLED = "CANCELLED"


class NavAreaType(str, enum.Enum):
    GROUND = "GROUND"
    ROAD = "ROAD"
    GRASS = "GRASS"
    WATER = "WATER"
    MUD = "MUD"
    STAIRS = "STAIRS"
    DANGER = "DANGER"
    NO_GO = "NO_GO"
    CUSTOM = "CUSTOM"


class NodeStatus(str, enum.Enum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    ABORTED = "ABORTED"


class ParallelPolicy(str, enum.Enum):
    SUCCESS_ON_ALL = "SUCCESS_ON_ALL"
    SUCCESS_ON_ONE = "SUCCESS_ON_ONE"
    FAIL_ON_ONE = "FAIL_ON_ONE"
    FAIL_ON_ALL = "FAIL_ON_ALL"


class TeamRelation(str, enum.Enum):
    FRIENDLY = "FRIENDLY"
    NEUTRAL = "NEUTRAL"
    HOSTILE = "HOSTILE"
    UNKNOWN = "UNKNOWN"


class AILOD(int, enum.Enum):
    LOD0_FULL = 0
    LOD1_REDUCED_PERCEPTION = 1
    LOD2_SIMPLIFIED_DECISION = 2
    LOD3_STATISTICAL = 3
    LOD4_DORMANT = 4


class AIPriority(int, enum.Enum):
    CRITICAL = 4
    HIGH = 3
    NORMAL = 2
    LOW = 1
    BACKGROUND = 0


# ==============================================================================
# 3. EXCEPTIONS
# ==============================================================================

class AIError(Exception):
    """Base exception for all AI runtime errors."""
    pass


class InvalidNavMesh(AIError):
    """Raised when a NavMesh geometry or topology violates strict contracts."""
    pass


class InvalidNavigationProfile(AIError):
    """Raised when a NavigationProfile is invalid."""
    pass


class PathNotFound(AIError):
    """Raised when pathfinding cannot find a viable route."""
    pass


class NavigationTileUnavailable(AIError):
    """Raised when navigation data for a spatial cell/tile is not resident."""
    pass


class BehaviorTreeInvalid(AIError):
    """Raised when a Behavior Tree definition violates integrity or acyclicity."""
    pass


class BlackboardTypeError(AIError):
    """Raised when accessing or storing incompatible types in a Blackboard."""
    pass


class InvalidTaskState(AIError):
    """Raised when a task enters an illegal lifecycle state."""
    pass


class SensorConfigurationError(AIError):
    """Raised when a perception sensor is misconfigured."""
    pass


class AINumericStateError(AIError):
    """Raised when a NaN or Infinity is detected in positions, velocities or scores."""
    pass


class AISimulationError(AIError):
    """General AI simulation failure."""
    pass


# ==============================================================================
# 4. DOMAIN DATACLASSES
# ==============================================================================

@dataclass(frozen=True)
class AIEntity:
    entity_id: str
    agent_id: str
    position: Vec3
    velocity: Vec3
    radius: float = 0.5
    height: float = 1.8
    navigation_profile: str = "Default"
    team_id: str = "Neutral"
    enabled: bool = True

    def __post_init__(self):
        ensure_finite_vec3(self.position, f"AIEntity({self.entity_id}).position")
        ensure_finite_vec3(self.velocity, f"AIEntity({self.entity_id}).velocity")
        ensure_finite_float(self.radius, "AIEntity.radius")
        ensure_finite_float(self.height, "AIEntity.height")


@dataclass(frozen=True)
class NavigationProfile:
    profile_id: str
    radius: float = 0.5
    height: float = 1.8
    max_slope_degrees: float = 45.0
    max_step_height: float = 0.4
    can_jump: bool = False
    allowed_areas: Tuple[str, ...] = ("GROUND", "ROAD", "GRASS")

    def is_area_allowed(self, area: str) -> bool:
        if area == NavAreaType.NO_GO.value:
            return False
        return area in self.allowed_areas


@dataclass(frozen=True)
class NavPolygon:
    polygon_id: int
    vertices: Tuple[Vec3, ...]
    neighbors: Tuple[int, ...] = ()
    area_type: str = "GROUND"
    traversal_cost: float = 1.0

    def __post_init__(self):
        if len(self.vertices) < 3:
            raise InvalidNavMesh(f"NavPolygon {self.polygon_id} has less than 3 vertices ({len(self.vertices)}).")
        for v in self.vertices:
            ensure_finite_vec3(v, f"NavPolygon({self.polygon_id}).vertex")
        ensure_finite_float(self.traversal_cost, f"NavPolygon({self.polygon_id}).traversal_cost")
        if self.traversal_cost < 0.0:
            raise InvalidNavMesh(f"NavPolygon {self.polygon_id} has negative traversal cost {self.traversal_cost}.")

    def centroid(self) -> Vec3:
        n = len(self.vertices)
        sx = sum(v[0] for v in self.vertices) / n
        sy = sum(v[1] for v in self.vertices) / n
        sz = sum(v[2] for v in self.vertices) / n
        return (sx, sy, sz)


@dataclass(frozen=True)
class Portal:
    left: Vec3
    right: Vec3
    from_poly: int
    to_poly: int


@dataclass(frozen=True)
class PathRequest:
    request_id: int
    agent_id: str
    start: Vec3
    goal: Vec3
    profile_id: str = "Default"
    priority: AIPriority = AIPriority.NORMAL
    requested_tick: int = 0

    def __post_init__(self):
        ensure_finite_vec3(self.start, f"PathRequest({self.request_id}).start")
        ensure_finite_vec3(self.goal, f"PathRequest({self.request_id}).goal")


@dataclass(frozen=True)
class PathResult:
    request_id: int
    status: PathStatus
    polygons: Tuple[int, ...] = ()
    portals: Tuple[Portal, ...] = ()
    points: Tuple[Vec3, ...] = ()
    total_cost: float = 0.0


@dataclass(frozen=True)
class AgentKinematics:
    position: Vec3
    velocity: Vec3
    preferred_velocity: Vec3
    max_speed: float = 5.0
    max_acceleration: float = 10.0
    radius: float = 0.5

    def __post_init__(self):
        ensure_finite_vec3(self.position, "AgentKinematics.position")
        ensure_finite_vec3(self.velocity, "AgentKinematics.velocity")
        ensure_finite_vec3(self.preferred_velocity, "AgentKinematics.preferred_velocity")
        ensure_finite_float(self.max_speed, "AgentKinematics.max_speed")
        ensure_finite_float(self.max_acceleration, "AgentKinematics.max_acceleration")
        ensure_finite_float(self.radius, "AgentKinematics.radius")


@dataclass(frozen=True)
class SoundStimulus:
    source_id: str
    position: Vec3
    intensity: float
    category: str = "GENERIC"
    tick: int = 0

    def __post_init__(self):
        ensure_finite_vec3(self.position, "SoundStimulus.position")
        ensure_finite_float(self.intensity, "SoundStimulus.intensity")


@dataclass(frozen=True)
class DamageStimulus:
    source_id: str
    target_id: str
    amount: float
    position: Vec3
    damage_type: str = "PHYSICAL"
    tick: int = 0

    def __post_init__(self):
        ensure_finite_vec3(self.position, "DamageStimulus.position")
        ensure_finite_float(self.amount, "DamageStimulus.amount")


@dataclass(frozen=True)
class SensoryMemoryEntry:
    stimulus_id: str
    source_id: str
    stimulus_type: str
    position: Vec3
    strength: float
    first_seen_tick: int
    last_seen_tick: int
    confidence: float

    def __post_init__(self):
        ensure_finite_vec3(self.position, "SensoryMemoryEntry.position")
        ensure_finite_float(self.strength, "SensoryMemoryEntry.strength")
        ensure_finite_float(self.confidence, "SensoryMemoryEntry.confidence")


@dataclass(frozen=True)
class AIBudget:
    max_path_requests_per_tick: int = 16
    max_sensor_queries_per_tick: int = 64
    max_bt_nodes_per_tick: int = 500
    max_avoidance_agents: int = 100


@dataclass
class AIMetrics:
    total_path_requests: int = 0
    successful_paths: int = 0
    failed_paths: int = 0
    total_sensor_queries: int = 0
    total_bt_nodes_executed: int = 0
    avoidance_pairs_evaluated: int = 0
    deferred_path_requests: int = 0
    agents_by_lod: Dict[int, int] = field(default_factory=dict)


# ==============================================================================
# 5. DETERMINISTIC RNG
# ==============================================================================

class DeterministicRNG:
    """
    Pure mathematical deterministic pseudo-random number generator.
    Produces strictly bit-exact values across platforms without os entropy.
    """
    def __init__(self, world_seed: int, agent_id: str, tick: int, stream_id: str = "default"):
        key_str = f"{world_seed}:{agent_id}:{tick}:{stream_id}"
        h = hashlib.sha256(key_str.encode("utf-8")).digest()
        # Seed 64-bit integer
        self._state = int.from_bytes(h[:8], byteorder="big")

    def next_u32(self) -> int:
        # Linear Congruential Generator (LCG) with Knuth constants
        self._state = (self._state * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
        return (self._state >> 32) & 0xFFFFFFFF

    def next_float(self) -> float:
        """Returns float in [0.0, 1.0)."""
        return self.next_u32() / 4294967296.0

    def next_range(self, min_val: float, max_val: float) -> float:
        return min_val + (max_val - min_val) * self.next_float()


# ==============================================================================
# 6. CANONICAL SNAPSHOTS & STATE HASH
# ==============================================================================

@dataclass(frozen=True)
class AIAgentSnapshot:
    agent_id: str
    entity_id: str
    lod: int
    position: Vec3
    velocity: Vec3
    current_target_id: Optional[str]
    blackboard_data: Dict[str, Any]
    memory_entries: Dict[str, Dict[str, Any]]
    path_points: Tuple[Vec3, ...]
    bt_status: str
    rng_state: int


@dataclass(frozen=True)
class AISnapshot:
    tick: int
    world_revision: int
    agents: Dict[str, AIAgentSnapshot]
    state_hash: str = ""

    @classmethod
    def create(cls, tick: int, world_revision: int, agents: Dict[str, AIAgentSnapshot]) -> AISnapshot:
        # Build deterministic JSON representation sorted by agent_id ASC
        sorted_agents = []
        for aid in sorted(agents.keys()):
            a = agents[aid]
            sorted_agents.append({
                "agent_id": a.agent_id,
                "entity_id": a.entity_id,
                "lod": a.lod,
                "position": [round(c, 5) for c in a.position],
                "velocity": [round(c, 5) for c in a.velocity],
                "target": a.current_target_id,
                "blackboard": {k: str(v) for k, v in sorted(a.blackboard_data.items())},
                "memory_count": len(a.memory_entries),
                "path_len": len(a.path_points),
                "bt_status": a.bt_status,
                "rng_state": a.rng_state,
            })

        payload = {
            "tick": tick,
            "world_revision": world_revision,
            "agents": sorted_agents,
        }
        raw_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        computed_hash = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()
        return cls(tick=tick, world_revision=world_revision, agents=agents, state_hash=computed_hash)
