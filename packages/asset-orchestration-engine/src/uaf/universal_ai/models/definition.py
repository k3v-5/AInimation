"""
Universal AI Models & Definitions for UAF-81.57.
Covers Agents, Senses, Memory, Targeting, FSM, Behavior Trees, Utility AI, GOAP,
Actions, Navigation, Crowd, Formations, Combat, Daily Schedules, Replay, and Simulation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple, Callable
import math
from ...core.hashing.canonical_hasher import CanonicalHasher


# --- SECTION 7: AGENT TYPES ---
class AgentType(Enum):
    PLAYER_PROXY = "PLAYER_PROXY"
    NPC = "NPC"
    ANIMAL = "ANIMAL"
    CREATURE = "CREATURE"
    CROWD_AGENT = "CROWD_AGENT"
    VEHICLE_AGENT = "VEHICLE_AGENT"
    COMPANION = "COMPANION"
    ENEMY = "ENEMY"
    BOSS = "BOSS"
    CUSTOM = "CUSTOM"


# --- SECTION 9: AGENT LIFECYCLE ---
class AgentLifecycleState(Enum):
    SPAWNING = "SPAWNING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    SUSPENDED = "SUSPENDED"
    DESPAWNING = "DESPAWNING"
    DEAD = "DEAD"
    PERSISTED = "PERSISTED"


# --- SECTION 8: AGENT STATE ---
@dataclass
class AgentState:
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    acceleration: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    health: float = 100.0
    max_health: float = 100.0
    stamina: float = 100.0
    current_action: str = "IDLE"
    current_goal: str = "SURVIVE"
    current_target: Optional[str] = None
    current_location: str = "WORLD_ROOT"
    alert_level: float = 0.0  # 0..1
    simulation_level: int = 0  # LOD 0..4

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": [round(v, 4) for v in self.position],
            "rotation": [round(v, 4) for v in self.rotation],
            "velocity": [round(v, 4) for v in self.velocity],
            "acceleration": [round(v, 4) for v in self.acceleration],
            "health": round(self.health, 2),
            "max_health": round(self.max_health, 2),
            "stamina": round(self.stamina, 2),
            "current_action": self.current_action,
            "current_goal": self.current_goal,
            "current_target": self.current_target,
            "current_location": self.current_location,
            "alert_level": round(self.alert_level, 2),
            "simulation_level": self.simulation_level,
        }


# --- SECTION 20, 21: AI RANDOM STREAM ---
@dataclass
class AIRandomStream:
    seed: int = 42
    _counter: int = 0

    def next_float(self) -> float:
        self._counter += 1
        val = (self._counter * 2654435761 + self.seed) & 0xFFFFFFFF
        return (val % 100000) / 100000.0

    def next_range(self, min_val: float, max_val: float) -> float:
        return min_val + self.next_float() * (max_val - min_val)

    def next_int(self, min_val: int, max_val: int) -> int:
        f = self.next_float()
        return min_val + int(f * (max_val - min_val + 1))



# --- SECTION 6: AGENT PROFILE ---
@dataclass
class AgentProfile:
    profile_id: str
    agent_type: AgentType = AgentType.NPC
    movement_speed: float = 400.0
    senses: List[str] = field(default_factory=lambda: ["VISION", "HEARING", "PROXIMITY"])
    intelligence_model: str = "HYBRID"
    combat_profile: str = "STANDARD"
    interaction_profile: str = "FRIENDLY"
    needs_enabled: bool = True
    social_enabled: bool = True
    schedule_enabled: bool = True
    simulation_lod: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "agent_type": self.agent_type.value,
            "movement_speed": self.movement_speed,
            "senses": list(self.senses),
            "intelligence_model": self.intelligence_model,
            "combat_profile": self.combat_profile,
            "interaction_profile": self.interaction_profile,
            "needs_enabled": self.needs_enabled,
            "social_enabled": self.social_enabled,
            "schedule_enabled": self.schedule_enabled,
            "simulation_lod": self.simulation_lod,
        }


# --- SECTION 23: SENSES ---
class SenseType(Enum):
    VISION = "VISION"
    HEARING = "HEARING"
    SMELL = "SMELL"
    TOUCH = "TOUCH"
    PROXIMITY = "PROXIMITY"
    WORLD_QUERY = "WORLD_QUERY"
    CUSTOM = "CUSTOM"


# --- SECTION 31: PERCEPTION FILTERS ---
class PerceptionFilter(Enum):
    ALLY = "ALLY"
    ENEMY = "ENEMY"
    NEUTRAL = "NEUTRAL"
    ANIMAL = "ANIMAL"
    PLAYER = "PLAYER"
    OBJECT = "OBJECT"
    ENVIRONMENT = "ENVIRONMENT"
    CUSTOM = "CUSTOM"


# --- SECTION 25: PERCEPTION EVENT ---
@dataclass
class PerceptionEvent:
    source_agent_id: str
    target_id: str
    sense: SenseType = SenseType.VISION
    confidence: float = 1.0  # 0..1
    distance: float = 500.0
    direction: Tuple[float, float, float] = (1.0, 0.0, 0.0)
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_agent_id": self.source_agent_id,
            "target_id": self.target_id,
            "sense": self.sense.value,
            "confidence": round(self.confidence, 4),
            "distance": round(self.distance, 2),
            "direction": [round(v, 4) for v in self.direction],
            "timestamp": self.timestamp,
        }


# --- SECTION 27, 28: HEARING & SOUND EVENT ---
@dataclass
class HearingProfile:
    range: float = 2000.0
    attenuation: float = 0.5
    occlusion_factor: float = 0.8


@dataclass
class AISoundEvent:
    position: Tuple[float, float, float]
    volume: float = 1.0
    category: str = "FOOTSTEP"
    source: str = "UNKNOWN"
    timestamp: float = 0.0


# --- SECTION 35, 36: MEMORY TYPES & RECORD ---
class MemoryType(Enum):
    SHORT_TERM = "SHORT_TERM"
    LONG_TERM = "LONG_TERM"
    SPATIAL = "SPATIAL"
    SOCIAL = "SOCIAL"
    THREAT = "THREAT"
    TASK = "TASK"
    EPISODIC = "EPISODIC"
    CUSTOM = "CUSTOM"


@dataclass
class MemoryRecord:
    memory_id: str
    mem_type: MemoryType = MemoryType.SHORT_TERM
    subject: str = "UNKNOWN"
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    timestamp: float = 0.0
    confidence: float = 1.0
    importance: float = 1.0
    expiration: float = 60.0

    def is_expired(self, current_time: float) -> bool:
        return (current_time - self.timestamp) > self.expiration

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "mem_type": self.mem_type.value,
            "subject": self.subject,
            "location": list(self.location),
            "timestamp": self.timestamp,
            "confidence": round(self.confidence, 3),
            "importance": round(self.importance, 3),
            "expiration": self.expiration,
        }


@dataclass
class AIMemory:
    records: Dict[str, MemoryRecord] = field(default_factory=dict)
    capacity: int = 100
    decay_rate: float = 0.05

    def add_record(self, record: MemoryRecord) -> None:
        if len(self.records) >= self.capacity:
            # Evict lowest importance
            least_important = min(self.records.values(), key=lambda r: r.importance)
            self.records.pop(least_important.memory_id, None)
        self.records[record.memory_id] = record

    def get_records_by_type(self, m_type: MemoryType) -> List[MemoryRecord]:
        return [r for r in self.records.values() if r.mem_type == m_type]

    def decay_memories(self, current_time: float) -> None:
        expired = [rid for rid, r in self.records.items() if r.is_expired(current_time)]
        for rid in expired:
            self.records.pop(rid, None)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capacity": self.capacity,
            "record_count": len(self.records),
            "records": [r.to_dict() for r in self.records.values()],
        }


# --- SECTION 43: TARGET LOCK MODE ---
class TargetLockMode(Enum):
    LOCKED = "LOCKED"
    SOFT_LOCK = "SOFT_LOCK"
    NO_LOCK = "NO_LOCK"


# --- SECTION 42: TARGET SCORE ---
@dataclass
class TargetScore:
    target_id: str
    score: float = 0.0
    distance: float = 0.0
    visibility: bool = True
    threat_level: float = 0.0


# --- SECTION 47, 48: FSM ---
@dataclass
class StateDefinition:
    state_id: str
    name: str
    on_enter_action: Optional[str] = None
    on_exit_action: Optional[str] = None


@dataclass
class StateTransition:
    source_state: str
    target_state: str
    condition: str
    priority: int = 1
    cooldown: float = 0.0


@dataclass
class FSMDefinition:
    fsm_id: str
    initial_state: str
    states: Dict[str, StateDefinition] = field(default_factory=dict)
    transitions: List[StateTransition] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fsm_id": self.fsm_id,
            "initial_state": self.initial_state,
            "state_count": len(self.states),
            "transition_count": len(self.transitions),
        }


# --- SECTION 51: BEHAVIOR TREE ---
class BTNodeType(Enum):
    SEQUENCE = "SEQUENCE"
    SELECTOR = "SELECTOR"
    PARALLEL = "PARALLEL"
    DECORATOR = "DECORATOR"
    CONDITION = "CONDITION"
    ACTION = "ACTION"
    WAIT = "WAIT"
    REPEAT = "REPEAT"
    RANDOM_SELECTOR = "RANDOM_SELECTOR"
    UTILITY_SELECTOR = "UTILITY_SELECTOR"


class BTNodeStatus(Enum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    ABORTED = "ABORTED"


class BTAbortMode(Enum):
    SELF = "SELF"
    LOWER_PRIORITY = "LOWER_PRIORITY"
    BOTH = "BOTH"
    NONE = "NONE"


@dataclass
class BehaviorNode:
    node_id: str
    node_type: BTNodeType
    children: List[str] = field(default_factory=list)
    action_name: Optional[str] = None
    condition_name: Optional[str] = None
    abort_mode: BTAbortMode = BTAbortMode.NONE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "children": list(self.children),
            "action_name": self.action_name,
            "abort_mode": self.abort_mode.value,
        }


@dataclass
class BehaviorTree:
    tree_id: str
    root_node_id: str
    nodes: Dict[str, BehaviorNode] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tree_id": self.tree_id,
            "root_node_id": self.root_node_id,
            "node_count": len(self.nodes),
        }


# --- SECTION 55, 56, 57: UTILITY AI ---
class UtilityCurveType(Enum):
    LINEAR = "LINEAR"
    QUADRATIC = "QUADRATIC"
    EXPONENTIAL = "EXPONENTIAL"
    LOGISTIC = "LOGISTIC"
    CUSTOM = "CUSTOM"


@dataclass
class UtilityConsideration:
    name: str
    curve_type: UtilityCurveType = UtilityCurveType.LINEAR
    weight: float = 1.0

    def evaluate(self, input_val: float) -> float:
        # Clamped 0..1
        val = max(0.0, min(1.0, input_val))
        if self.curve_type == UtilityCurveType.LINEAR:
            return val * self.weight
        elif self.curve_type == UtilityCurveType.QUADRATIC:
            return (val ** 2) * self.weight
        elif self.curve_type == UtilityCurveType.EXPONENTIAL:
            return (math.exp(val) / math.e) * self.weight
        elif self.curve_type == UtilityCurveType.LOGISTIC:
            return (1.0 / (1.0 + math.exp(-10.0 * (val - 0.5)))) * self.weight
        return val * self.weight


@dataclass
class UtilityAction:
    action_id: str
    considerations: List[UtilityConsideration] = field(default_factory=list)
    weight: float = 1.0
    priority: int = 1
    cooldown: float = 0.0

    def calculate_utility(self, inputs: Dict[str, float]) -> float:
        if not self.considerations:
            return self.weight
        total = 1.0
        for c in self.considerations:
            in_val = inputs.get(c.name, 0.5)
            score = c.evaluate(in_val)
            total *= score
        return total * self.weight


# --- SECTION 58, 59, 60: GOAP ---
@dataclass(frozen=True)
class WorldFact:
    key: str
    value: Any


@dataclass
class GOAPAction:
    action_id: str
    preconditions: Dict[str, Any] = field(default_factory=dict)
    effects: Dict[str, Any] = field(default_factory=dict)
    cost: float = 1.0
    duration: float = 1.0


@dataclass
class GOAPGoal:
    goal_id: str
    desired_state: Dict[str, Any] = field(default_factory=dict)
    priority: float = 1.0


@dataclass
class ActionPlan:
    goal_id: str
    actions: List[GOAPAction] = field(default_factory=list)
    total_cost: float = 0.0
    is_valid: bool = True


# --- SECTION 64, 65: ACTIONS ---
class AIActionType(Enum):
    MOVE = "MOVE"
    LOOK = "LOOK"
    WAIT = "WAIT"
    INTERACT = "INTERACT"
    PICKUP = "PICKUP"
    DROP = "DROP"
    USE = "USE"
    TALK = "TALK"
    ATTACK = "ATTACK"
    DEFEND = "DEFEND"
    FLEE = "FLEE"
    FOLLOW = "FOLLOW"
    GUARD = "GUARD"
    SEARCH = "SEARCH"
    SLEEP = "SLEEP"
    EAT = "EAT"
    DRINK = "DRINK"
    WORK = "WORK"
    CUSTOM = "CUSTOM"


class AIActionState(Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    INTERRUPTED = "INTERRUPTED"


@dataclass
class AIAction:
    action_id: str
    action_type: AIActionType
    target_id: Optional[str] = None
    target_pos: Optional[Tuple[float, float, float]] = None
    priority: int = 1
    state: AIActionState = AIActionState.QUEUED
    duration: float = 1.0
    elapsed: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "target_id": self.target_id,
            "priority": self.priority,
            "state": self.state.value,
        }


# --- SECTION 69, 70: MOVEMENT ---
class AIMovementMode(Enum):
    WALK = "WALK"
    RUN = "RUN"
    SPRINT = "SPRINT"
    CROUCH = "CROUCH"
    CRAWL = "CRAWL"
    CLIMB = "CLIMB"
    SWIM = "SWIM"
    FLY = "FLY"
    DRIVE = "DRIVE"
    CUSTOM = "CUSTOM"


@dataclass
class AIMovementProfile:
    speed: float = 400.0
    acceleration: float = 800.0
    deceleration: float = 1200.0
    turn_rate: float = 360.0
    radius: float = 40.0
    height: float = 180.0
    step_height: float = 45.0
    slope_limit: float = 45.0


# --- SECTION 72, 73, 74: PATHFINDING ---
class PathfindingAlgorithm(Enum):
    A_STAR = "A_STAR"
    DIJKSTRA = "DIJKSTRA"
    FLOW_FIELD = "FLOW_FIELD"
    NAVMESH_QUERY = "NAVMESH_QUERY"
    GRID = "GRID"
    CUSTOM = "CUSTOM"


class PathStatus(Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    INVALID = "INVALID"


@dataclass
class PathResult:
    status: PathStatus = PathStatus.SUCCESS
    waypoints: List[Tuple[float, float, float]] = field(default_factory=list)
    cost: float = 0.0
    distance: float = 0.0
    estimated_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "waypoint_count": len(self.waypoints),
            "distance": round(self.distance, 2),
            "estimated_time": round(self.estimated_time, 2),
        }


@dataclass
class DynamicObstacle:
    obstacle_id: str
    position: Tuple[float, float, float]
    radius: float = 50.0
    is_active: bool = True


# --- SECTION 80, 86: CROWD & FORMATIONS ---
class CrowdGroupType(Enum):
    PEDESTRIAN = "PEDESTRIAN"
    CIVILIAN = "CIVILIAN"
    MILITARY = "MILITARY"
    ANIMAL = "ANIMAL"
    EMERGENCY = "EMERGENCY"
    CUSTOM = "CUSTOM"


@dataclass
class CrowdAgent:
    agent_id: str
    position: Tuple[float, float, float]
    velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    desired_velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    radius: float = 40.0
    priority: int = 1
    group_type: CrowdGroupType = CrowdGroupType.PEDESTRIAN


class FormationType(Enum):
    LINE = "LINE"
    COLUMN = "COLUMN"
    WEDGE = "WEDGE"
    CIRCLE = "CIRCLE"
    SQUARE = "SQUARE"
    CUSTOM = "CUSTOM"


@dataclass
class FormationMember:
    agent_id: str
    slot_index: int
    offset: Tuple[float, float, float]
    role: str = "SOLDIER"


@dataclass
class FormationDefinition:
    formation_id: str
    formation_type: FormationType = FormationType.LINE
    spacing: float = 150.0
    members: List[FormationMember] = field(default_factory=list)


# --- SECTION 90, 93: SOCIAL & FACTIONS ---
class FactionType(Enum):
    ALLY = "ALLY"
    FRIENDLY = "FRIENDLY"
    NEUTRAL = "NEUTRAL"
    SUSPICIOUS = "SUSPICIOUS"
    HOSTILE = "HOSTILE"


@dataclass
class Relationship:
    source: str
    target: str
    affinity: float = 0.5  # 0..1
    trust: float = 0.5     # 0..1
    fear: float = 0.0      # 0..1
    respect: float = 0.5   # 0..1
    familiarity: float = 0.1 # 0..1
    faction_relation: FactionType = FactionType.NEUTRAL


@dataclass
class FactionDefinition:
    faction_id: str
    name: str
    default_relation: FactionType = FactionType.NEUTRAL
    relationships: Dict[str, FactionType] = field(default_factory=dict)


# --- SECTION 96, 97: COMMUNICATION ---
class AICommunicationType(Enum):
    SPEECH = "SPEECH"
    SIGNAL = "SIGNAL"
    RADIO = "RADIO"
    GESTURE = "GESTURE"
    ALERT = "ALERT"
    CUSTOM = "CUSTOM"


@dataclass
class AICommunicationMessage:
    message_id: str
    source: str
    target: str
    channel: AICommunicationType = AICommunicationType.SPEECH
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    timestamp: float = 0.0


# --- SECTION 101, 103: SQUAD & GROUPS ---
class GroupRole(Enum):
    LEADER = "LEADER"
    FOLLOWER = "FOLLOWER"
    SCOUT = "SCOUT"
    SUPPORT = "SUPPORT"
    ATTACKER = "ATTACKER"
    DEFENDER = "DEFENDER"
    MEDIC = "MEDIC"
    CIVILIAN = "CIVILIAN"
    CUSTOM = "CUSTOM"


@dataclass
class SquadDefinition:
    squad_id: str
    leader_id: str
    member_ids: List[str] = field(default_factory=list)
    formation: FormationType = FormationType.WEDGE
    shared_target: Optional[str] = None


# --- SECTION 105, 107, 109: COMBAT & COVER ---
class AICombatState(Enum):
    IDLE = "IDLE"
    ALERT = "ALERT"
    SEARCHING = "SEARCHING"
    ENGAGING = "ENGAGING"
    DEFENDING = "DEFENDING"
    RETREATING = "RETREATING"
    DEAD = "DEAD"


class CombatRangeType(Enum):
    MELEE = "MELEE"
    SHORT = "SHORT"
    MEDIUM = "MEDIUM"
    LONG = "LONG"


@dataclass
class CoverPoint:
    cover_id: str
    position: Tuple[float, float, float]
    normal: Tuple[float, float, float]
    height: float = 120.0
    protection_score: float = 0.8
    is_occupied: bool = False


# --- SECTION 115, 116: INTERACTION ---
class AIInteractionType(Enum):
    TALK = "TALK"
    OPEN = "OPEN"
    CLOSE = "CLOSE"
    USE = "USE"
    PICKUP = "PICKUP"
    DROP = "DROP"
    ACTIVATE = "ACTIVATE"
    SIT = "SIT"
    SLEEP = "SLEEP"
    WORK = "WORK"
    TRADE = "TRADE"
    CUSTOM = "CUSTOM"


@dataclass
class InteractableDefinition:
    interactable_id: str
    interaction_type: AIInteractionType = AIInteractionType.USE
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    interaction_radius: float = 200.0
    is_reserved: bool = False
    reserved_by: Optional[str] = None


# --- SECTION 121: NEEDS ---
class NeedType(Enum):
    HUNGER = "HUNGER"
    THIRST = "THIRST"
    ENERGY = "ENERGY"
    SAFETY = "SAFETY"
    SOCIAL = "SOCIAL"
    COMFORT = "COMFORT"
    CURIOSITY = "CURIOSITY"
    CUSTOM = "CUSTOM"


@dataclass
class NeedsProfile:
    hunger: float = 0.0   # 0..1 (1.0 = starving)
    thirst: float = 0.0   # 0..1 (1.0 = dehydrated)
    energy: float = 1.0   # 0..1 (0.0 = exhausted)
    safety: float = 1.0   # 0..1 (0.0 = terrified)
    social: float = 0.5

    def update_decay(self, dt: float) -> None:
        self.hunger = min(1.0, self.hunger + (0.005 * dt))
        self.thirst = min(1.0, self.thirst + (0.01 * dt))
        self.energy = max(0.0, self.energy - (0.002 * dt))


# --- SECTION 131, 134: SCHEDULE & DAILY ROUTINE ---
@dataclass
class ScheduleEntry:
    start_time: float  # hours 0..24
    end_time: float
    activity: str      # WAKE, EAT, WORK, SOCIAL, REST, SLEEP
    location: str
    priority: int = 1


@dataclass
class DailySchedule:
    schedule_id: str
    entries: List[ScheduleEntry] = field(default_factory=list)

    def get_current_entry(self, time_of_day: float) -> Optional[ScheduleEntry]:
        for e in self.entries:
            if e.start_time <= time_of_day < e.end_time:
                return e
        return None


# --- SECTION 137, 139: EVENT BUS ---
class AIEventType(Enum):
    SPAWN = "SPAWN"
    DESPAWN = "DESPAWN"
    DAMAGE = "DAMAGE"
    DEATH = "DEATH"
    SOUND = "SOUND"
    VISUAL = "VISUAL"
    INTERACTION = "INTERACTION"
    QUEST = "QUEST"
    WEATHER = "WEATHER"
    TIME = "TIME"
    WORLD_CHANGE = "WORLD_CHANGE"
    ALERT = "ALERT"
    CUSTOM = "CUSTOM"


class AIEventPriority(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


@dataclass
class AIEvent:
    event_type: AIEventType
    sender_id: str
    priority: AIEventPriority = AIEventPriority.NORMAL
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0


# --- SECTION 141, 145: SAVE STATE & REPLAY ---
@dataclass
class AISaveState:
    agent_id: str
    transform: Tuple[float, float, float]
    state: AgentState
    needs: NeedsProfile
    timestamp: float = 0.0
    schema_version: str = "1.0.0"


@dataclass
class SimulationReplay:
    replay_id: str
    initial_seed: int
    inputs: List[Dict[str, Any]] = field(default_factory=list)
    recorded_events: List[Dict[str, Any]] = field(default_factory=list)
    total_ticks: int = 0
    final_hash: str = ""


# --- SECTION 150: AI LOD ---
class AISimulationLOD(Enum):
    LOD0_FULL = "LOD0_FULL"
    LOD1_REDUCED = "LOD1_REDUCED"
    LOD2_BACKGROUND = "LOD2_BACKGROUND"
    LOD3_ABSTRACT = "LOD3_ABSTRACT"
    LOD4_FROZEN = "LOD4_FROZEN"


# --- SECTION 158: ABSTRACT AGENT ---
@dataclass
class AbstractAgentState:
    group_id: str
    population: int = 100
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    activity: str = "WORKING"
    resource_level: float = 1.0


# --- SECTION 162, 165, 167: BUDGETS & DIAGNOSTICS ---
@dataclass
class AIPerformanceBudget:
    max_active_agents: int = 1000
    max_full_agents: int = 100
    max_tick_time_ms: float = 16.67


@dataclass
class AIPerformanceReport:
    perception_time_ms: float = 0.0
    decision_time_ms: float = 0.0
    behavior_time_ms: float = 0.0
    pathfinding_time_ms: float = 0.0
    movement_time_ms: float = 0.0
    combat_time_ms: float = 0.0
    crowd_time_ms: float = 0.0
    total_tick_time_ms: float = 0.0


@dataclass
class AIDiagnosticReport:
    agent_count: int = 0
    active_count: int = 0
    path_failures: int = 0
    deadlocks_detected: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# --- SECTION 173: AI QUERIES ---
class AIQueryType(Enum):
    NEAREST_AGENT = "NEAREST_AGENT"
    VISIBLE_TARGETS = "VISIBLE_TARGETS"
    THREATS = "THREATS"
    ALLIES = "ALLIES"
    COVER = "COVER"
    SAFE_LOCATION = "SAFE_LOCATION"
    PATH = "PATH"
    INTERACTABLES = "INTERACTABLES"
    POPULATION = "POPULATION"


@dataclass
class AIQuery:
    query_type: AIQueryType
    origin: Tuple[float, float, float]
    radius: float = 2000.0
    filter_tag: Optional[str] = None


# --- SECTION 183: TERRITORY ---
@dataclass
class TerritoryDefinition:
    territory_id: str
    center: Tuple[float, float, float]
    radius: float = 5000.0
    owner_faction: str = "WILD_ANIMALS"
    threat_level: float = 0.5


# --- SECTION 4: AI AGENT COMPLETE ---
@dataclass
class AIAgent:
    agent_id: str
    profile: AgentProfile
    state: AgentState = field(default_factory=AgentState)
    lifecycle: AgentLifecycleState = AgentLifecycleState.ACTIVE
    memory: AIMemory = field(default_factory=AIMemory)
    needs: NeedsProfile = field(default_factory=NeedsProfile)
    schedule: Optional[DailySchedule] = None
    fsm: Optional[FSMDefinition] = None
    behavior_tree: Optional[BehaviorTree] = None
    current_fsm_state: Optional[str] = None
    target_lock: TargetLockMode = TargetLockMode.NO_LOCK
    faction: str = "NEUTRAL"
    current_action_obj: Optional[AIAction] = None

    def is_alive(self) -> bool:
        return self.lifecycle != AgentLifecycleState.DEAD and self.state.health > 0.0

    def apply_damage(self, amount: float) -> None:
        self.state.health = max(0.0, self.state.health - amount)
        if self.state.health <= 0.0:
            self.lifecycle = AgentLifecycleState.DEAD

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "profile": self.profile.to_dict(),
            "state": self.state.to_dict(),
            "lifecycle": self.lifecycle.value,
            "memory": self.memory.to_dict(),
            "faction": self.faction,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIAgent":
        prof_data = data.get("profile", {})
        prof = AgentProfile(
            profile_id=prof_data.get("profile_id", "DEFAULT"),
            agent_type=AgentType(prof_data.get("agent_type", "NPC")),
            movement_speed=prof_data.get("movement_speed", 400.0),
        )
        st_data = data.get("state", {})
        st = AgentState(
            position=tuple(st_data.get("position", (0.0, 0.0, 0.0))),
            rotation=tuple(st_data.get("rotation", (0.0, 0.0, 0.0))),
            velocity=tuple(st_data.get("velocity", (0.0, 0.0, 0.0))),
            health=st_data.get("health", 100.0),
            max_health=st_data.get("max_health", 100.0),
            stamina=st_data.get("stamina", 100.0),
        )
        return cls(
            agent_id=data["agent_id"],
            profile=prof,
            state=st,
            lifecycle=AgentLifecycleState(data.get("lifecycle", "ACTIVE")),
            faction=data.get("faction", "NEUTRAL"),
        )



# --- SECTION 2, 236: TOP-LEVEL SIMULATION DEFINITION & SNAPSHOT ---
@dataclass
class SimulationSnapshot:
    simulation_hash: str
    tick: int
    world_hash: str
    active_agents: int
    total_agents: int
    event_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation_hash": self.simulation_hash,
            "tick": self.tick,
            "world_hash": self.world_hash,
            "active_agents": self.active_agents,
            "total_agents": self.total_agents,
            "event_count": self.event_count,
        }


@dataclass
class SimulationDefinition:
    simulation_id: str
    seed: int = 54321
    world_hash: str = "WORLD_SNAPSHOT_HASH"
    agents: List[AIAgent] = field(default_factory=list)
    squads: List[SquadDefinition] = field(default_factory=list)
    factions: List[FactionDefinition] = field(default_factory=list)
    cover_points: List[CoverPoint] = field(default_factory=list)
    interactables: List[InteractableDefinition] = field(default_factory=list)
    territories: List[TerritoryDefinition] = field(default_factory=list)
    current_tick: int = 0
    simulation_version: str = "1.0.0"

    @property
    def simulation_hash(self) -> str:
        payload = {
            "simulation_id": self.simulation_id,
            "seed": self.seed,
            "world_hash": self.world_hash,
            "agent_count": len(self.agents),
            "squad_count": len(self.squads),
            "faction_count": len(self.factions),
            "current_tick": self.current_tick,
            "simulation_version": self.simulation_version,
        }
        return CanonicalHasher.compute_hash(payload)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "seed": self.seed,
            "world_hash": self.world_hash,
            "agent_count": len(self.agents),
            "squad_count": len(self.squads),
            "current_tick": self.current_tick,
            "simulation_hash": self.simulation_hash,
        }
