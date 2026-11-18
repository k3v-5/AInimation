"""
Universal Runtime Scene Streaming & World Partitioning — Models & Definition (UAF-81.81).
Normative domain models, compact frozen CellKeys, cell state machines, bounding boxes,
streaming plans, memory budgets, observer kinematics, and deterministic snapshots.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import math
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union


def copy_dict_deterministic(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively sort dictionary keys for canonical serialization."""
    out = {}
    for k in sorted(data.keys()):
        v = data[k]
        if isinstance(v, dict):
            out[k] = copy_dict_deterministic(v)
        elif isinstance(v, list):
            out[k] = [
                copy_dict_deterministic(item) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            out[k] = v
    return out


# ==============================================================================
# EXCEPTIONS
# ==============================================================================

class StreamingError(Exception):
    """Base exception for runtime scene streaming system."""
    pass


class InvalidCellStateTransitionError(StreamingError):
    """Raised when an illegal state transition is attempted on a cell."""
    def __init__(self, key: Any, from_state: Any, to_state: Any, reason: str = ""):
        super().__init__(
            f"Invalid cell state transition for {key}: '{from_state}' -> '{to_state}'. {reason}".strip()
        )
        self.key = key
        self.from_state = from_state
        self.to_state = to_state


class BudgetExceededError(StreamingError):
    """Raised when an operation would violate strict memory/cell count budgets."""
    pass


class CellNotFoundError(StreamingError):
    """Raised when a requested cell is not registered in the spatial grid."""
    pass


# ==============================================================================
# ENUMS
# ==============================================================================

class CellState(str, Enum):
    UNLOADED = "UNLOADED"
    LOADING = "LOADING"
    LOADED = "LOADED"
    ACTIVE = "ACTIVE"
    UNLOADING = "UNLOADING"


class HLODLevel(str, Enum):
    LOD0 = "LOD0"                      # Full raw cell detail
    LOD1 = "LOD1"                      # Simplified geometry
    LOD2 = "LOD2"                      # Clustered HLOD proxy
    LOD3_IMPOSTOR = "LOD3_IMPOSTOR"    # Ultra-low-cost far impostor


class EvictionReason(str, Enum):
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    DISTANCE_FAR = "DISTANCE_FAR"
    OCCLUDED = "OCCLUDED"
    MANUAL_REQUEST = "MANUAL_REQUEST"
    THRASHING_PREVENTION = "THRASHING_PREVENTION"


class StreamingWorldState(str, Enum):
    CREATED = "CREATED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    DESTROYED = "DESTROYED"


# ==============================================================================
# SPATIAL KEYS & BOUNDS
# ==============================================================================

@dataclass(frozen=True, order=True)
class CellKey:
    level: int
    x: int
    y: int
    z: int

    def to_string(self) -> str:
        return f"C_{self.level}_{self.x}_{self.y}_{self.z}"

    def to_list(self) -> List[int]:
        return [self.level, self.x, self.y, self.z]

    @classmethod
    def from_list(cls, data: List[int]) -> CellKey:
        return cls(level=int(data[0]), x=int(data[1]), y=int(data[2]), z=int(data[3]))

    @classmethod
    def from_string(cls, s: str) -> CellKey:
        parts = s.split("_")
        if len(parts) == 5 and parts[0] == "C":
            return cls(int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4]))
        raise ValueError(f"Invalid CellKey string format: {s}")


@dataclass
class CellBounds:
    min_corner: Tuple[float, float, float]
    max_corner: Tuple[float, float, float]

    def center(self) -> Tuple[float, float, float]:
        return (
            (self.min_corner[0] + self.max_corner[0]) * 0.5,
            (self.min_corner[1] + self.max_corner[1]) * 0.5,
            (self.min_corner[2] + self.max_corner[2]) * 0.5,
        )

    def extents(self) -> Tuple[float, float, float]:
        return (
            (self.max_corner[0] - self.min_corner[0]) * 0.5,
            (self.max_corner[1] - self.min_corner[1]) * 0.5,
            (self.max_corner[2] - self.min_corner[2]) * 0.5,
        )

    def size(self) -> Tuple[float, float, float]:
        return (
            self.max_corner[0] - self.min_corner[0],
            self.max_corner[1] - self.min_corner[1],
            self.max_corner[2] - self.min_corner[2],
        )

    def contains_point(self, p: Tuple[float, float, float]) -> bool:
        return (
            self.min_corner[0] <= p[0] <= self.max_corner[0]
            and self.min_corner[1] <= p[1] <= self.max_corner[1]
            and self.min_corner[2] <= p[2] <= self.max_corner[2]
        )

    def closest_distance_to_point(self, p: Tuple[float, float, float]) -> float:
        """Calculate minimum Euclidean distance from a point to this AABB."""
        dx = max(0.0, self.min_corner[0] - p[0], p[0] - self.max_corner[0])
        dy = max(0.0, self.min_corner[1] - p[1], p[1] - self.max_corner[1])
        dz = max(0.0, self.min_corner[2] - p[2], p[2] - self.max_corner[2])
        return math.sqrt(dx * dx + dy * dy + dz * dz)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_corner": [round(float(c), 6) for c in self.min_corner],
            "max_corner": [round(float(c), 6) for c in self.max_corner],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CellBounds:
        min_c = tuple(data["min_corner"])
        max_c = tuple(data["max_corner"])
        return cls(min_corner=(min_c[0], min_c[1], min_c[2]), max_corner=(max_c[0], max_c[1], max_c[2]))


# ==============================================================================
# RESOURCES & DEFINITIONS
# ==============================================================================

@dataclass
class CellResourceDescriptor:
    resource_id: str
    resource_type: str
    ram_bytes: int = 0
    vram_bytes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "ram_bytes": self.ram_bytes,
            "vram_bytes": self.vram_bytes,
        }


@dataclass
class CellDefinition:
    key: CellKey
    bounds: CellBounds
    resources: List[CellResourceDescriptor] = field(default_factory=list)
    entity_count: int = 0
    hlod_parent_key: Optional[CellKey] = None
    is_critical: bool = False
    data_layer: str = "Default"

    def total_ram_bytes(self) -> int:
        return sum(r.ram_bytes for r in self.resources)

    def total_vram_bytes(self) -> int:
        return sum(r.vram_bytes for r in self.resources)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key.to_list(),
            "bounds": self.bounds.to_dict(),
            "resources": [r.to_dict() for r in self.resources],
            "entity_count": self.entity_count,
            "hlod_parent_key": self.hlod_parent_key.to_list() if self.hlod_parent_key else None,
            "is_critical": self.is_critical,
            "data_layer": self.data_layer,
        }


# ==============================================================================
# SNAPSHOTS & CANONICAL STATE
# ==============================================================================

@dataclass(frozen=True)
class CellSnapshot:
    key: CellKey
    state: CellState
    lod: int = 0
    resident: bool = False
    visible: bool = False
    entity_count: int = 0
    ram_bytes: int = 0
    vram_bytes: int = 0
    revision: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key.to_list(),
            "state": self.state.value,
            "lod": self.lod,
            "resident": self.resident,
            "visible": self.visible,
            "entity_count": self.entity_count,
            "ram_bytes": self.ram_bytes,
            "vram_bytes": self.vram_bytes,
            "revision": self.revision,
        }


# ==============================================================================
# OBSERVER & BUDGET
# ==============================================================================

@dataclass
class ObserverState:
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    forward: Tuple[float, float, float] = (0.0, 0.0, 1.0)
    fov_degrees: float = 90.0
    view_distance: float = 500.0

    def speed(self) -> float:
        vx, vy, vz = self.velocity
        return math.sqrt(vx * vx + vy * vy + vz * vz)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": [round(float(p), 6) for p in self.position],
            "velocity": [round(float(v), 6) for v in self.velocity],
            "forward": [round(float(f), 6) for f in self.forward],
            "fov_degrees": round(float(self.fov_degrees), 6),
            "view_distance": round(float(self.view_distance), 6),
        }


@dataclass(frozen=True)
class StreamingBudget:
    ram_bytes: int = 512 * 1024 * 1024       # 512 MB
    vram_bytes: int = 1024 * 1024 * 1024     # 1024 MB
    max_loaded_cells: int = 64
    max_active_cells: int = 16
    max_loads_per_tick: int = 4
    max_unloads_per_tick: int = 8

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ram_bytes": self.ram_bytes,
            "vram_bytes": self.vram_bytes,
            "max_loaded_cells": self.max_loaded_cells,
            "max_active_cells": self.max_active_cells,
            "max_loads_per_tick": self.max_loads_per_tick,
            "max_unloads_per_tick": self.max_unloads_per_tick,
        }


@dataclass
class StreamingPlan:
    loads: List[CellKey] = field(default_factory=list)
    activations: List[CellKey] = field(default_factory=list)
    deactivations: List[CellKey] = field(default_factory=list)
    unloads: List[CellKey] = field(default_factory=list)
    hlod_transitions: Dict[CellKey, int] = field(default_factory=dict)

    def is_empty(self) -> bool:
        return (
            not self.loads
            and not self.activations
            and not self.deactivations
            and not self.unloads
            and not self.hlod_transitions
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loads": [k.to_list() for k in self.loads],
            "activations": [k.to_list() for k in self.activations],
            "deactivations": [k.to_list() for k in self.deactivations],
            "unloads": [k.to_list() for k in self.unloads],
            "hlod_transitions": {k.to_string(): v for k, v in sorted(self.hlod_transitions.items(), key=lambda x: x[0].to_string())},
        }


@dataclass
class StreamingMetrics:
    resident_cells_count: int = 0
    active_cells_count: int = 0
    current_ram_bytes: int = 0
    current_vram_bytes: int = 0
    budget_violations_count: int = 0
    total_evictions_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resident_cells_count": self.resident_cells_count,
            "active_cells_count": self.active_cells_count,
            "current_ram_bytes": self.current_ram_bytes,
            "current_vram_bytes": self.current_vram_bytes,
            "budget_violations_count": self.budget_violations_count,
            "total_evictions_count": self.total_evictions_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
        }


# ==============================================================================
# GLOBAL STREAMING SNAPSHOT (SHA-256 HASH)
# ==============================================================================

@dataclass
class StreamingSnapshot:
    snapshot_id: str
    timestamp: float
    world_revision: int
    scheduler_revision: int
    cell_snapshots: Dict[str, Dict[str, Any]]
    budget_metrics: Dict[str, Any]
    active_keys: List[List[int]]
    state_hash: str = ""

    def compute_hash(self) -> str:
        """Compute 100% deterministic SHA-256 hash without timestamps or pointers."""
        canonical = {
            "world_revision": self.world_revision,
            "scheduler_revision": self.scheduler_revision,
            "cell_snapshots": {k: v for k, v in sorted(self.cell_snapshots.items())},
            "budget_metrics": copy_dict_deterministic(self.budget_metrics),
            "active_keys": sorted(self.active_keys),
        }
        encoded = json.dumps(canonical, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def __post_init__(self):
        if not self.state_hash:
            self.state_hash = self.compute_hash()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": round(float(self.timestamp), 6),
            "world_revision": self.world_revision,
            "scheduler_revision": self.scheduler_revision,
            "cell_snapshots": self.cell_snapshots,
            "budget_metrics": self.budget_metrics,
            "active_keys": self.active_keys,
            "state_hash": self.state_hash,
        }
