"""
UAF-81.84.0: VFX Core Contracts, Identifiers, Enums, and Data Models.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
import enum
import hashlib
import json
import math
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple, Union

Vec3 = Tuple[float, float, float]
Vec4 = Tuple[float, float, float, float]
ColorRGBA = Tuple[float, float, float, float]  # (r, g, b, a) normalized 0.0 to 1.0


# ==============================================================================
# 1. NUMERIC SANITY AND ANTI-CHEAT CHECKS
# ==============================================================================

def ensure_finite_float(val: float, context: str = "") -> float:
    """Validate that a float value is finite (not NaN, not +Inf, not -Inf)."""
    if math.isnan(val) or math.isinf(val):
        raise VFXNumericSecurityError(f"Non-finite float detected in {context}: {val}")
    return float(val)


def ensure_finite_vec3(v: Sequence[float], context: str = "") -> Vec3:
    """Validate that a 3D vector contains only finite floats."""
    if len(v) != 3:
        raise VFXNumericSecurityError(f"Vec3 must have 3 coordinates in {context}, got {len(v)}")
    x, y, z = float(v[0]), float(v[1]), float(v[2])
    if math.isnan(x) or math.isinf(x) or math.isnan(y) or math.isinf(y) or math.isnan(z) or math.isinf(z):
        raise VFXNumericSecurityError(f"Non-finite coordinate in Vec3 ({x}, {y}, {z}) in {context}")
    return (x, y, z)


def ensure_finite_vec4(v: Sequence[float], context: str = "") -> Vec4:
    """Validate that a 4D vector contains only finite floats."""
    if len(v) != 4:
        raise VFXNumericSecurityError(f"Vec4 must have 4 coordinates in {context}, got {len(v)}")
    x, y, z, w = float(v[0]), float(v[1]), float(v[2]), float(v[3])
    if any(math.isnan(c) or math.isinf(c) for c in (x, y, z, w)):
        raise VFXNumericSecurityError(f"Non-finite coordinate in Vec4 ({x}, {y}, {z}, {w}) in {context}")
    return (x, y, z, w)


# ==============================================================================
# 2. ENUMS
# ==============================================================================

class DeterminismMode(str, enum.Enum):
    DETERMINISTIC = "DETERMINISTIC"
    PRESENTATION_DETERMINISTIC = "PRESENTATION_DETERMINISTIC"
    NON_DETERMINISTIC_VISUAL = "NON_DETERMINISTIC_VISUAL"


class ParticleLifecycleState(str, enum.Enum):
    SPAWNED = "SPAWNED"
    ACTIVE = "ACTIVE"
    DYING = "DYING"
    DEAD = "DEAD"
    RECYCLED = "RECYCLED"


class SpawnMode(str, enum.Enum):
    RATE = "RATE"
    BURST = "BURST"
    DISTANCE = "DISTANCE"
    EVENT = "EVENT"
    MANUAL = "MANUAL"
    SURFACE = "SURFACE"
    VOLUME = "VOLUME"
    POINT = "POINT"
    CURVE = "CURVE"


class OverflowPolicy(str, enum.Enum):
    DROP_NEW = "DROP_NEW"
    KILL_OLDEST = "KILL_OLDEST"
    KILL_LOWEST_PRIORITY = "KILL_LOWEST_PRIORITY"
    CLAMP = "CLAMP"


class CollisionMode(str, enum.Enum):
    NONE = "NONE"
    PLANE = "PLANE"
    SPHERE = "SPHERE"
    BOX = "BOX"
    CAPSULE = "CAPSULE"
    MESH = "MESH"
    SDF = "SDF"
    WORLD = "WORLD"


class CollisionResponse(str, enum.Enum):
    BOUNCE = "BOUNCE"
    SLIDE = "SLIDE"
    STICK = "STICK"
    KILL = "KILL"
    REFLECT = "REFLECT"
    FRICTION = "FRICTION"


class ConstraintType(str, enum.Enum):
    DISTANCE = "DISTANCE"
    POSITION = "POSITION"
    VELOCITY = "VELOCITY"
    ORIENTATION = "ORIENTATION"
    ATTACHMENT = "ATTACHMENT"
    SPRING = "SPRING"


class RendererType(str, enum.Enum):
    SPRITE = "SPRITE"
    MESH = "MESH"
    RIBBON = "RIBBON"
    TRAIL = "TRAIL"
    BEAM = "BEAM"
    DECAL = "DECAL"
    LIGHT = "LIGHT"


class SpriteFacing(str, enum.Enum):
    BILLBOARD = "BILLBOARD"
    SCREEN_ALIGNED = "SCREEN_ALIGNED"
    VELOCITY_ALIGNED = "VELOCITY_ALIGNED"
    CUSTOM_FACING = "CUSTOM_FACING"


class VFXLOD(str, enum.Enum):
    LOD0 = "LOD0"
    LOD1 = "LOD1"
    LOD2 = "LOD2"
    LOD3 = "LOD3"
    CULLED = "CULLED"


class VFXPriority(int, enum.Enum):
    CRITICAL = 5
    GAMEPLAY = 4
    HIGH = 3
    NORMAL = 2
    LOW = 1
    COSMETIC = 0


class SimulationBackendType(str, enum.Enum):
    REFERENCE = "REFERENCE"
    CPU = "CPU"
    GPU = "GPU"


class UnloadPolicy(str, enum.Enum):
    DESTROY = "DESTROY"
    PAUSE = "PAUSE"
    MIGRATE = "MIGRATE"
    CONTINUE = "CONTINUE"


# ==============================================================================
# 3. EXCEPTIONS
# ==============================================================================

class VFXError(Exception):
    """Base exception for runtime VFX errors."""
    pass


class VFXNumericSecurityError(VFXError):
    """Raised when a NaN or Inf is detected in coordinates, velocities, or lifetimes."""
    pass


class VFXValidationError(VFXError):
    """Raised when an asset, emitter, or module fails schema verification."""
    pass


class VFXBudgetExceededError(VFXError):
    """Raised when hard resource quotas are exceeded without recovery."""
    pass


class VFXGraphCycleError(VFXError):
    """Raised when a cycle is detected in a VFX DAG."""
    pass


class NiagaraBridgeError(VFXError):
    """Raised when an unsupported or invalid Niagara asset translation occurs."""
    pass


# ==============================================================================
# 4. IDENTIFIERS & CORE DATACLASSES
# ==============================================================================

@dataclass(frozen=True, order=True)
class ParticleId:
    emitter_id: str
    index: int
    generation: int = 0

    def __str__(self) -> str:
        return f"P({self.emitter_id}:{self.index}:{self.generation})"


@dataclass(frozen=True)
class ParticleAttribute:
    name: str
    type_name: str  # float, float2, float3, float4, int, uint, bool, color, quat, transform
    default_value: Any = 0.0


@dataclass(frozen=True)
class ParticleSchema:
    attributes: Tuple[ParticleAttribute, ...]

    def get_attribute(self, name: str) -> Optional[ParticleAttribute]:
        for attr in self.attributes:
            if attr.name == name:
                return attr
        return None

    def has_attribute(self, name: str) -> bool:
        return any(a.name == name for a in self.attributes)


# Default canonical particle schema
DEFAULT_PARTICLE_SCHEMA = ParticleSchema(
    attributes=(
        ParticleAttribute("position", "float3", (0.0, 0.0, 0.0)),
        ParticleAttribute("velocity", "float3", (0.0, 0.0, 0.0)),
        ParticleAttribute("acceleration", "float3", (0.0, 0.0, 0.0)),
        ParticleAttribute("age", "float", 0.0),
        ParticleAttribute("lifetime", "float", 1.0),
        ParticleAttribute("size", "float3", (1.0, 1.0, 1.0)),
        ParticleAttribute("rotation", "float3", (0.0, 0.0, 0.0)),
        ParticleAttribute("color", "color", (1.0, 1.0, 1.0, 1.0)),
        ParticleAttribute("alpha", "float", 1.0),
        ParticleAttribute("mass", "float", 1.0),
        ParticleAttribute("scale", "float", 1.0),
        ParticleAttribute("sprite_index", "int", 0),
        ParticleAttribute("mesh_index", "int", 0),
    )
)


@dataclass(frozen=True)
class VFXParameter:
    name: str
    type_name: str
    value: Any


@dataclass(frozen=True)
class VFXMaterialBinding:
    material_id: str
    parameter_mappings: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class VFXBudget:
    max_active_systems: int = 1000
    max_particles: int = 50000
    max_gpu_bytes: int = 64 * 1024 * 1024  # 64 MB
    max_cpu_ms: float = 8.0
    max_gpu_ms: float = 4.0
    max_draw_calls: int = 500
    max_events: int = 2000


@dataclass
class VFXMetrics:
    active_systems: int = 0
    active_emitters: int = 0
    active_particles: int = 0
    spawned_particles: int = 0
    killed_particles: int = 0
    cpu_time_ms: float = 0.0
    gpu_time_ms: float = 0.0
    draw_calls: int = 0
    events_dispatched: int = 0
    culled_systems: int = 0
    pooled_instances: int = 0


@dataclass(frozen=True)
class VFXSnapshot:
    server_tick: int
    world_revision: int
    active_system_count: int
    total_particles: int
    state_hash: str

    @classmethod
    def create(
        cls,
        server_tick: int,
        world_revision: int,
        system_states: Sequence[Dict[str, Any]],
    ) -> VFXSnapshot:
        """Create deterministic state snapshot with canonical SHA-256 hash."""
        sorted_systems = sorted(system_states, key=lambda s: s.get("system_id", ""))
        payload = {
            "server_tick": server_tick,
            "world_revision": world_revision,
            "systems": sorted_systems,
        }
        raw_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        h = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()

        total_parts = sum(s.get("particle_count", 0) for s in system_states)
        return cls(
            server_tick=server_tick,
            world_revision=world_revision,
            active_system_count=len(system_states),
            total_particles=total_parts,
            state_hash=h,
        )
