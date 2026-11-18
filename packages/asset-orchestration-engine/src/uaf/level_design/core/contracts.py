"""
UAF-81.90: Core Contracts, Spatial Sockets & Mission Models.
Defines modular tile schemas, socket compatibility rules, quest graphs, and pacing phases.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Dict, List, Optional, Tuple, Set
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Direction2D(str, Enum):
    NORTH = "NORTH"
    SOUTH = "SOUTH"
    EAST = "EAST"
    WEST = "WEST"


OPPOSITE_DIR_2D: Dict[Direction2D, Direction2D] = {
    Direction2D.NORTH: Direction2D.SOUTH,
    Direction2D.SOUTH: Direction2D.NORTH,
    Direction2D.EAST: Direction2D.WEST,
    Direction2D.WEST: Direction2D.EAST,
}

DIR_OFFSETS_2D: Dict[Direction2D, Tuple[int, int]] = {
    Direction2D.NORTH: (0, 1),
    Direction2D.SOUTH: (0, -1),
    Direction2D.EAST: (1, 0),
    Direction2D.WEST: (-1, 0),
}


class Direction3D(str, Enum):
    NORTH = "NORTH"
    SOUTH = "SOUTH"
    EAST = "EAST"
    WEST = "WEST"
    UP = "UP"
    DOWN = "DOWN"


OPPOSITE_DIR_3D: Dict[Direction3D, Direction3D] = {
    Direction3D.NORTH: Direction3D.SOUTH,
    Direction3D.SOUTH: Direction3D.NORTH,
    Direction3D.EAST: Direction3D.WEST,
    Direction3D.WEST: Direction3D.EAST,
    Direction3D.UP: Direction3D.DOWN,
    Direction3D.DOWN: Direction3D.UP,
}

DIR_OFFSETS_3D: Dict[Direction3D, Tuple[int, int, int]] = {
    Direction3D.NORTH: (0, 1, 0),
    Direction3D.SOUTH: (0, -1, 0),
    Direction3D.EAST: (1, 0, 0),
    Direction3D.WEST: (-1, 0, 0),
    Direction3D.UP: (0, 0, 1),
    Direction3D.DOWN: (0, 0, -1),
}


class SocketType(str, Enum):
    WALL = "WALL"
    DOOR = "DOOR"
    CORRIDOR = "CORRIDOR"
    OPEN = "OPEN"
    VENT = "VENT"
    WINDOW = "WINDOW"


def are_sockets_compatible(sock_a: SocketType, sock_b: SocketType) -> bool:
    """
    Evaluates socket compatibility between two adjacent cell faces.
    WALL only connects to WALL; DOOR connects to DOOR; OPEN connects to OPEN, etc.
    """
    return sock_a == sock_b


class RoomType(str, Enum):
    CORRIDOR = "CORRIDOR"
    ROOM = "ROOM"
    HUB = "HUB"
    ARENA = "ARENA"
    DEAD_END = "DEAD_END"
    ENTRANCE = "ENTRANCE"
    EXIT = "EXIT"
    SECRET_VAULT = "SECRET_VAULT"
    ELEVATOR = "ELEVATOR"


class ObjectiveType(str, Enum):
    ELIMINATE_TARGET = "ELIMINATE_TARGET"
    COLLECT_ITEM = "COLLECT_ITEM"
    HACK_TERMINAL = "HACK_TERMINAL"
    DEFEND_AREA = "DEFEND_AREA"
    SURVIVE_WAVE = "SURVIVE_WAVE"
    ESCORT_VIP = "ESCORT_VIP"
    REACH_EXTRACTION = "REACH_EXTRACTION"


class ObjectiveState(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DependencyType(str, Enum):
    ALL_REQUIRED = "ALL_REQUIRED"  # AND logic
    ANY_REQUIRED = "ANY_REQUIRED"  # OR logic


class PacingPhase(str, Enum):
    CALM = "CALM"
    BUILDUP = "BUILDUP"
    PEAK = "PEAK"
    SUSTAINED_PEAK = "SUSTAINED_PEAK"
    COOLDOWN = "COOLDOWN"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class ModularTileDefinition(BaseModel):
    tile_id: str
    name: str
    room_type: RoomType = RoomType.ROOM
    sockets_2d: Dict[Direction2D, SocketType] = Field(default_factory=dict)
    sockets_3d: Dict[Direction3D, SocketType] = Field(default_factory=dict)
    weight: float = Field(default=1.0, gt=0.0, description="Selection probability weight in WFC")
    size_meters: float = Field(default=4.0, gt=0.0)
    mesh_path: str = ""

    def get_socket_2d(self, direction: Direction2D) -> SocketType:
        return self.sockets_2d.get(direction, SocketType.WALL)

    def get_socket_3d(self, direction: Direction3D) -> SocketType:
        return self.sockets_3d.get(direction, SocketType.WALL)


class PlacedTile(BaseModel):
    tile_id: str
    x: int
    y: int
    z: int = 0
    room_type: RoomType
    world_pos: Tuple[float, float, float]
    rotation_deg: float = 0.0


class PlayerStressMetric(BaseModel):
    health_ratio: float = Field(default=1.0, ge=0.0, le=1.0)
    ammo_ratio: float = Field(default=1.0, ge=0.0, le=1.0)
    active_enemies: int = Field(default=0, ge=0)
    damage_received_rate: float = Field(default=0.0, ge=0.0)

    def compute_stress_score(self) -> float:
        """
        Computes composite stress score in [0.0, 1.0].
        Weights: 35% missing health, 25% missing ammo, 25% active enemy density, 15% damage spike rate.
        """
        w_health = 0.35 * (1.0 - self.health_ratio)
        w_ammo = 0.25 * (1.0 - self.ammo_ratio)
        w_enemies = 0.25 * min(1.0, self.active_enemies / 6.0)
        w_damage = 0.15 * min(1.0, self.damage_received_rate / 25.0)

        score = w_health + w_ammo + w_enemies + w_damage
        return max(0.0, min(1.0, score))


class PacingDecision(BaseModel):
    current_phase: PacingPhase
    stress_score: float
    spawn_multiplier: float
    recommended_archetype: str
    music_intensity: float
