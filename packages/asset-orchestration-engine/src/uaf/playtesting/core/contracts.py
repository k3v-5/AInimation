"""
UAF-81.96: Autonomous Gameplay Playtesting & AI QA Simulation Core Contracts.
Provides Pydantic v2 domain models, enums, telemetry structures and schemas for headless simulation.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class PlaytestArchetype(str, Enum):
    EXPLORER = "EXPLORER"
    SPEEDRUNNER = "SPEEDRUNNER"
    COMBATANT = "COMBATANT"
    NOVICE = "NOVICE"
    COMPLETIONIST = "COMPLETIONIST"


class SimulationOutcome(str, Enum):
    VICTORY = "VICTORY"
    DEATH = "DEATH"
    SOFTLOCK = "SOFTLOCK"
    TIMEOUT = "TIMEOUT"
    ABORTED = "ABORTED"


class SoftlockType(str, Enum):
    KEY_BEHIND_LOCKED_DOOR = "KEY_BEHIND_LOCKED_DOOR"
    DISCONNECTED_ROOM = "DISCONNECTED_ROOM"
    ONE_WAY_TRAP = "ONE_WAY_TRAP"
    RESOURCE_EXHAUSTION_BLOCK = "RESOURCE_EXHAUSTION_BLOCK"
    MISSING_GOAL = "MISSING_GOAL"
    CYCLE_LOCK = "CYCLE_LOCK"


class SoftlockSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    FATAL_SOFTLOCK = "FATAL_SOFTLOCK"


class TelemetryEventType(str, Enum):
    SPAWN = "SPAWN"
    ROOM_ENTER = "ROOM_ENTER"
    ROOM_EXIT = "ROOM_EXIT"
    PICKUP_KEY = "PICKUP_KEY"
    PICKUP_AMMO = "PICKUP_AMMO"
    PICKUP_HEALTH = "PICKUP_HEALTH"
    UNLOCK_DOOR = "UNLOCK_DOOR"
    FIRE_WEAPON = "FIRE_WEAPON"
    HIT_ENEMY = "HIT_ENEMY"
    TAKE_DAMAGE = "TAKE_DAMAGE"
    ENEMY_DEFEATED = "ENEMY_DEFEATED"
    DEATH = "DEATH"
    SOLVE_PUZZLE = "SOLVE_PUZZLE"
    GOAL_REACHED = "GOAL_REACHED"
    STUCK_TIMEOUT = "STUCK_TIMEOUT"


class HeatmapMetric(str, Enum):
    DEATH_DENSITY = "DEATH_DENSITY"
    AMMO_EXPENDITURE = "AMMO_EXPENDITURE"
    DWELL_TIME = "DWELL_TIME"
    DAMAGE_TAKEN = "DAMAGE_TAKEN"
    PATH_TRAVERSAL = "PATH_TRAVERSAL"


class Vector3D(BaseModel):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def to_ue5_cm(self) -> "Vector3D":
        return Vector3D(x=self.x * 100.0, y=self.y * 100.0, z=self.z * 100.0)

    @classmethod
    def from_ue5_cm(cls, x_cm: float, y_cm: float, z_cm: float) -> "Vector3D":
        return cls(x=x_cm * 0.01, y=y_cm * 0.01, z=z_cm * 0.01)

    def distance_to(self, other: "Vector3D") -> float:
        import math
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2)


class AgentStats(BaseModel):
    max_health: float = 100.0
    current_health: float = 100.0
    max_shield: float = 50.0
    current_shield: float = 50.0
    ammo: int = 120
    max_ammo: int = 240
    weapon_damage: float = 25.0
    fire_rate: float = 3.0
    accuracy: float = 0.85
    evasion: float = 0.20
    movement_speed_mps: float = 5.0


class ArchetypeProfile(BaseModel):
    archetype: PlaytestArchetype
    accuracy_mult: float = 1.0
    damage_taken_mult: float = 1.0
    exploration_desire: float = 0.5
    caution_factor: float = 0.5
    speedrun_factor: float = 0.0


class TelemetryEvent(BaseModel):
    event_id: str
    timestamp_s: float
    event_type: TelemetryEventType
    room_id: str
    position: Vector3D
    data: Dict[str, Any] = Field(default_factory=dict)


class EnemySpawn(BaseModel):
    enemy_id: str
    enemy_type: str = "GRUNT"
    health: float = 50.0
    damage: float = 10.0
    fire_rate: float = 1.5
    is_mandatory: bool = True


class DoorConnection(BaseModel):
    source_room_id: str
    target_room_id: str
    is_two_way: bool = True
    required_key_id: Optional[str] = None
    is_locked_initially: bool = False


class RoomSpec(BaseModel):
    room_id: str
    room_name: str = ""
    center_position: Vector3D = Field(default_factory=Vector3D)
    dimensions_m: Vector3D = Field(default_factory=lambda: Vector3D(x=10.0, y=10.0, z=3.0))
    is_start: bool = False
    is_goal: bool = False
    enemies: List[EnemySpawn] = Field(default_factory=list)
    contained_keys: List[str] = Field(default_factory=list)
    health_pickups: int = 0
    ammo_pickups: int = 0
    has_terminal_puzzle: bool = False
    puzzle_id: Optional[str] = None


class PlaytestLevelSpec(BaseModel):
    level_id: str
    level_name: str = ""
    rooms: Dict[str, RoomSpec] = Field(default_factory=dict)
    connections: List[DoorConnection] = Field(default_factory=list)
    seed: int = 42


class SoftlockIncident(BaseModel):
    incident_id: str
    softlock_type: SoftlockType
    severity: SoftlockSeverity
    room_id: str
    description: str
    remediation_hint: str = ""


class DifficultySpikeIncident(BaseModel):
    room_id: str
    player_death_count: int = 0
    survival_rate: float = 1.0
    average_ttk_seconds: float = 0.0
    ammo_exhaustion_rate: float = 0.0
    severity: SoftlockSeverity = SoftlockSeverity.WARNING
    recommendation: str = ""


class HeatmapGrid2D(BaseModel):
    metric: HeatmapMetric
    cell_size_m: float = 2.0
    min_x: float = 0.0
    max_x: float = 100.0
    min_y: float = 0.0
    max_y: float = 100.0
    grid_width: int = 50
    grid_height: int = 50
    cells: List[List[float]] = Field(default_factory=list)
    hotspots: List[Dict[str, Any]] = Field(default_factory=list)


class PlaytestRunResult(BaseModel):
    session_id: str
    archetype: PlaytestArchetype
    outcome: SimulationOutcome
    total_time_s: float
    rooms_visited: List[str]
    keys_collected: List[str]
    enemies_defeated: int
    damage_dealt: float
    damage_taken: float
    ammo_spent: int
    shots_fired: int
    accuracy_achieved: float
    telemetry_events: List[TelemetryEvent] = Field(default_factory=list)


class QASimulationSuiteSummary(BaseModel):
    total_runs: int
    victory_count: int
    death_count: int
    softlock_count: int
    timeout_count: int
    overall_survival_rate: float
    archetype_survival_rates: Dict[PlaytestArchetype, float] = Field(default_factory=dict)
    identified_softlocks: List[SoftlockIncident] = Field(default_factory=list)
    difficulty_spikes: List[DifficultySpikeIncident] = Field(default_factory=list)
    calibrated_successfully: bool = False
