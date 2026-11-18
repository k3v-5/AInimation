"""
Universal Runtime Gameplay World Data Models (UAF-81.79).
Strict dataclasses and enums for ECS entities, components, character/camera controllers,
interactions, triggers, gameplay tags, rules, commands, events, combat/health,
status effects, abilities, cooldowns, timers, transactional inventory, quests,
spawn/despawn, save/load state, snapshots, and deterministic replay.
"""

from __future__ import annotations

import enum
import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Union


def copy_dict_deterministic(data: Any) -> Any:
    """Recursively formats and sorts dictionary structures deterministically."""
    if isinstance(data, dict):
        return {k: copy_dict_deterministic(data[k]) for k in sorted(data.keys())}
    elif isinstance(data, list):
        return [copy_dict_deterministic(item) for item in data]
    elif isinstance(data, tuple):
        return tuple(copy_dict_deterministic(item) for item in data)
    elif isinstance(data, set):
        return sorted([copy_dict_deterministic(item) for item in data], key=lambda x: str(x))
    elif isinstance(data, float):
        if math.isnan(data):
            return "NaN"
        if math.isinf(data):
            return "Infinity" if data > 0 else "-Infinity"
        return round(float(data), 6)
    elif isinstance(data, enum.Enum):
        return data.value
    return data


class GameplayWorldState(str, enum.Enum):
    CREATED = "CREATED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    DESTROYED = "DESTROYED"


class EntityLifecycleState(str, enum.Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    PENDING_DESPAWN = "PENDING_DESPAWN"
    DESTROYED = "DESTROYED"


class MovementState(str, enum.Enum):
    IDLE = "IDLE"
    MOVING = "MOVING"
    WALKING = "WALKING"
    RUNNING = "RUNNING"
    SPRINTING = "SPRINTING"
    JUMPING = "JUMPING"
    FALLING = "FALLING"
    GROUNDED = "GROUNDED"
    CROUCHING = "CROUCHING"
    DASHING = "DASHING"
    DISABLED = "DISABLED"


class CameraMode(str, enum.Enum):
    FIRST_PERSON = "FIRST_PERSON"
    THIRD_PERSON = "THIRD_PERSON"
    TOP_DOWN = "TOP_DOWN"
    FREE = "FREE"
    SCRIPTED = "SCRIPTED"
    ORBIT = "ORBIT"
    FIXED = "FIXED"


class InteractionState(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    IN_RANGE = "IN_RANGE"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    DISABLED = "DISABLED"


class TriggerState(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    TRIGGERED = "TRIGGERED"
    RESETTING = "RESETTING"


class TriggerEventType(str, enum.Enum):
    ENTER = "ENTER"
    EXIT = "EXIT"
    STAY = "STAY"


class DamageType(str, enum.Enum):
    PHYSICAL = "PHYSICAL"
    FIRE = "FIRE"
    COLD = "COLD"
    ELECTRIC = "ELECTRIC"
    POISON = "POISON"
    TRUE_DAMAGE = "TRUE_DAMAGE"


class CombatState(str, enum.Enum):
    NEUTRAL = "NEUTRAL"
    COMBAT = "COMBAT"
    ATTACKING = "ATTACKING"
    DEFENDING = "DEFENDING"
    STUNNED = "STUNNED"
    DEAD = "DEAD"
    DISABLED = "DISABLED"


class StatusStackingPolicy(str, enum.Enum):
    REPLACE = "REPLACE"
    REFRESH = "REFRESH"
    STACK = "STACK"
    IGNORE = "IGNORE"
    MAX = "MAX"


class AbilityState(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    REQUESTED = "REQUESTED"
    CASTING = "CASTING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    BLOCKED = "BLOCKED"
    READY = "READY"
    ON_COOLDOWN = "ON_COOLDOWN"
    DISABLED = "DISABLED"


class TimerType(str, enum.Enum):
    ONE_SHOT = "ONE_SHOT"
    REPEATING = "REPEATING"
    DELAYED = "DELAYED"


class QuestState(str, enum.Enum):
    INACTIVE = "INACTIVE"
    AVAILABLE = "AVAILABLE"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABANDONED = "ABANDONED"


class ObjectiveState(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    INCOMPLETE = "INCOMPLETE"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class GameplayCommandType(str, enum.Enum):
    MOVE = "MOVE"
    INTERACT = "INTERACT"
    USE_ABILITY = "USE_ABILITY"
    ATTACK = "ATTACK"
    TAKE_DAMAGE = "TAKE_DAMAGE"
    HEAL = "HEAL"
    ADD_ITEM = "ADD_ITEM"
    REMOVE_ITEM = "REMOVE_ITEM"
    START_QUEST = "START_QUEST"
    COMPLETE_OBJECTIVE = "COMPLETE_OBJECTIVE"
    SPAWN = "SPAWN"
    DESPAWN = "DESPAWN"


class GameplayEventType(str, enum.Enum):
    ENTITY_SPAWNED = "ENTITY_SPAWNED"
    ENTITY_DESPAWNED = "ENTITY_DESPAWNED"
    INTERACTION_STARTED = "INTERACTION_STARTED"
    INTERACTION_COMPLETED = "INTERACTION_COMPLETED"
    ABILITY_STARTED = "ABILITY_STARTED"
    ABILITY_COMPLETED = "ABILITY_COMPLETED"
    DAMAGE_APPLIED = "DAMAGE_APPLIED"
    HEALTH_CHANGED = "HEALTH_CHANGED"
    ITEM_ADDED = "ITEM_ADDED"
    ITEM_REMOVED = "ITEM_REMOVED"
    QUEST_STARTED = "QUEST_STARTED"
    OBJECTIVE_COMPLETED = "OBJECTIVE_COMPLETED"
    STATUS_APPLIED = "STATUS_APPLIED"
    STATUS_REMOVED = "STATUS_REMOVED"
    HEALED = "HEALED"
    SHIELD_ABSORBED = "SHIELD_ABSORBED"
    DIED = "DIED"


@dataclass
class GameplayTick:
    tick_index: int = 0
    simulation_time: float = 0.0
    delta_time: float = 0.016

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tick_index": self.tick_index,
            "simulation_time": round(float(self.simulation_time), 6),
            "delta_time": round(float(self.delta_time), 6),
        }


@dataclass
class GameplayTagContainer:
    tags: Set[str] = field(default_factory=set)

    def add(self, tag: str) -> None:
        self.tags.add(tag)

    def remove(self, tag: str) -> None:
        self.tags.discard(tag)

    def has(self, tag: str) -> bool:
        """Returns True if exact tag or any subtag hierarchy matches."""
        for t in self.tags:
            if t == tag or t.startswith(tag + "."):
                return True
        return False

    def has_any(self, tags: Set[str]) -> bool:
        return any(self.has(t) for t in tags)

    def has_all(self, tags: Set[str]) -> bool:
        return all(self.has(t) for t in tags)

    def has_none(self, tags: Set[str]) -> bool:
        return not self.has_any(tags)

    def to_dict(self) -> List[str]:
        return sorted(list(self.tags))


@dataclass
class CharacterControllerComponent:
    controller_id: str
    move_speed: float = 6.0
    run_speed: float = 10.0
    jump_force: float = 8.0
    movement_state: MovementState = MovementState.IDLE
    is_grounded: bool = True
    velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    is_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "controller_id": self.controller_id,
            "move_speed": round(float(self.move_speed), 6),
            "run_speed": round(float(self.run_speed), 6),
            "jump_force": round(float(self.jump_force), 6),
            "movement_state": self.movement_state.value,
            "is_grounded": self.is_grounded,
            "velocity": (round(float(self.velocity[0]), 6), round(float(self.velocity[1]), 6), round(float(self.velocity[2]), 6)),
            "is_enabled": self.is_enabled,
        }


@dataclass
class CameraControllerComponent:
    camera_id: str
    camera_mode: CameraMode = CameraMode.THIRD_PERSON
    target_entity_id: Optional[str] = None
    yaw: float = 0.0
    pitch: float = 0.0
    distance: float = 5.0
    zoom: float = 1.0
    min_pitch: float = -80.0
    max_pitch: float = 80.0
    min_distance: float = 1.0
    max_distance: float = 20.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "camera_id": self.camera_id,
            "camera_mode": self.camera_mode.value,
            "target_entity_id": self.target_entity_id,
            "yaw": round(float(self.yaw), 6),
            "pitch": round(float(self.pitch), 6),
            "distance": round(float(self.distance), 6),
            "zoom": round(float(self.zoom), 6),
            "min_pitch": round(float(self.min_pitch), 6),
            "max_pitch": round(float(self.max_pitch), 6),
            "min_distance": round(float(self.min_distance), 6),
            "max_distance": round(float(self.max_distance), 6),
        }


@dataclass
class InteractableComponent:
    interaction_id: str
    target_entity_id: str
    interaction_type: str = "DEFAULT"
    priority: int = 0
    max_distance: float = 3.0
    conditions: Dict[str, Any] = field(default_factory=dict)
    state: InteractionState = InteractionState.AVAILABLE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interaction_id": self.interaction_id,
            "target_entity_id": self.target_entity_id,
            "interaction_type": self.interaction_type,
            "priority": self.priority,
            "max_distance": round(float(self.max_distance), 6),
            "conditions": copy_dict_deterministic(self.conditions),
            "state": self.state.value,
        }


@dataclass
class TriggerComponent:
    trigger_id: str
    shape: str = "BOX"
    extents: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    state: TriggerState = TriggerState.ACTIVE
    filter_tags: Set[str] = field(default_factory=set)
    inside_entities: Set[str] = field(default_factory=set)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trigger_id": self.trigger_id,
            "shape": self.shape,
            "extents": (round(float(self.extents[0]), 6), round(float(self.extents[1]), 6), round(float(self.extents[2]), 6)),
            "position": (round(float(self.position[0]), 6), round(float(self.position[1]), 6), round(float(self.position[2]), 6)),
            "state": self.state.value,
            "filter_tags": sorted(list(self.filter_tags)),
            "inside_entities": sorted(list(self.inside_entities)),
        }


@dataclass
class HealthComponent:
    current_health: float = 100.0
    max_health: float = 100.0
    min_health: float = 0.0
    current_shield: float = 0.0
    max_shield: float = 50.0
    is_invulnerable: bool = False
    is_dead: bool = False
    regeneration_rate: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_health": round(float(self.current_health), 6),
            "max_health": round(float(self.max_health), 6),
            "min_health": round(float(self.min_health), 6),
            "current_shield": round(float(self.current_shield), 6),
            "max_shield": round(float(self.max_shield), 6),
            "is_invulnerable": self.is_invulnerable,
            "is_dead": self.is_dead,
            "regeneration_rate": round(float(self.regeneration_rate), 6),
        }


@dataclass
class DamageRequest:
    request_id: str
    source_entity_id: str
    target_entity_id: str
    raw_damage: float
    damage_type: DamageType = DamageType.PHYSICAL
    modifiers: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "source_entity_id": self.source_entity_id,
            "target_entity_id": self.target_entity_id,
            "raw_damage": round(float(self.raw_damage), 6),
            "damage_type": self.damage_type.value,
            "modifiers": {k: round(float(v), 6) for k, v in sorted(self.modifiers.items())},
        }


@dataclass
class DamageResult:
    request_id: str
    source_entity_id: str
    target_entity_id: str
    raw_damage: float
    mitigated_damage: float
    shield_absorbed: float
    health_damage: float
    final_health: float
    is_killed: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "source_entity_id": self.source_entity_id,
            "target_entity_id": self.target_entity_id,
            "raw_damage": round(float(self.raw_damage), 6),
            "mitigated_damage": round(float(self.mitigated_damage), 6),
            "shield_absorbed": round(float(self.shield_absorbed), 6),
            "health_damage": round(float(self.health_damage), 6),
            "final_health": round(float(self.final_health), 6),
            "is_killed": self.is_killed,
        }


@dataclass
class StatusEffect:
    effect_id: str
    name: str
    source_entity_id: str
    target_entity_id: str
    duration: float = 5.0
    elapsed: float = 0.0
    magnitude: float = 10.0
    tick_interval: float = 1.0
    time_since_tick: float = 0.0
    stacks: int = 1
    max_stacks: int = 5
    policy: StatusStackingPolicy = StatusStackingPolicy.REFRESH
    is_expired: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "effect_id": self.effect_id,
            "name": self.name,
            "source_entity_id": self.source_entity_id,
            "target_entity_id": self.target_entity_id,
            "duration": round(float(self.duration), 6),
            "elapsed": round(float(self.elapsed), 6),
            "magnitude": round(float(self.magnitude), 6),
            "tick_interval": round(float(self.tick_interval), 6),
            "time_since_tick": round(float(self.time_since_tick), 6),
            "stacks": self.stacks,
            "max_stacks": self.max_stacks,
            "policy": self.policy.value,
            "is_expired": self.is_expired,
        }


@dataclass
class AbilityDefinition:
    ability_id: str
    name: str
    cooldown: float = 2.0
    cast_time: float = 0.0
    resource_cost: float = 10.0
    required_tags: Set[str] = field(default_factory=set)
    blocked_tags: Set[str] = field(default_factory=set)
    state: AbilityState = AbilityState.AVAILABLE
    remaining_cooldown: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ability_id": self.ability_id,
            "name": self.name,
            "cooldown": round(float(self.cooldown), 6),
            "cast_time": round(float(self.cast_time), 6),
            "resource_cost": round(float(self.resource_cost), 6),
            "required_tags": sorted(list(self.required_tags)),
            "blocked_tags": sorted(list(self.blocked_tags)),
            "state": self.state.value,
            "remaining_cooldown": round(float(self.remaining_cooldown), 6),
        }


@dataclass
class GameplayTimer:
    timer_id: str
    duration: float = 1.0
    elapsed: float = 0.0
    timer_type: TimerType = TimerType.ONE_SHOT
    is_active: bool = True
    is_completed: bool = False
    callback_event: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timer_id": self.timer_id,
            "duration": round(float(self.duration), 6),
            "elapsed": round(float(self.elapsed), 6),
            "timer_type": self.timer_type.value,
            "is_active": self.is_active,
            "is_completed": self.is_completed,
            "callback_event": self.callback_event,
        }


@dataclass
class InventorySlot:
    slot_id: int
    item_id: str = ""
    quantity: int = 0
    max_stack: int = 99
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "slot_id": self.slot_id,
            "item_id": self.item_id,
            "quantity": self.quantity,
            "max_stack": self.max_stack,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class InventoryComponent:
    inventory_id: str
    max_slots: int = 20
    slots: Dict[int, InventorySlot] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inventory_id": self.inventory_id,
            "max_slots": self.max_slots,
            "slots": {str(k): v.to_dict() for k, v in sorted(self.slots.items())},
        }


@dataclass
class QuestObjective:
    objective_id: str
    description: str = ""
    target_count: int = 1
    current_count: int = 0
    state: ObjectiveState = ObjectiveState.PENDING
    is_mandatory: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "objective_id": self.objective_id,
            "description": self.description,
            "target_count": self.target_count,
            "current_count": self.current_count,
            "state": self.state.value,
            "is_mandatory": self.is_mandatory,
        }


@dataclass
class QuestDefinition:
    quest_id: str
    title: str = ""
    state: QuestState = QuestState.INACTIVE
    objectives: Dict[str, QuestObjective] = field(default_factory=dict)
    rewards: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "quest_id": self.quest_id,
            "title": self.title,
            "state": self.state.value,
            "objectives": {k: o.to_dict() for k, o in sorted(self.objectives.items())},
            "rewards": copy_dict_deterministic(self.rewards),
        }


@dataclass
class GameplayRule:
    rule_id: str
    priority: int = 0
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    effects: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "priority": self.priority,
            "conditions": copy_dict_deterministic(self.conditions),
            "effects": copy_dict_deterministic(self.effects),
        }


@dataclass
class GameplayCommand:
    command_id: str
    command_type: GameplayCommandType
    target_entity_id: str
    source_entity_id: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command_id": self.command_id,
            "command_type": self.command_type.value,
            "target_entity_id": self.target_entity_id,
            "source_entity_id": self.source_entity_id,
            "payload": copy_dict_deterministic(self.payload),
            "timestamp": round(float(self.timestamp), 6),
        }


@dataclass
class GameplayEvent:
    event_id: str
    event_type: GameplayEventType
    target_entity_id: str
    source_entity_id: str = ""
    sequence_number: int = 0
    timestamp: float = 0.0
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "target_entity_id": self.target_entity_id,
            "source_entity_id": self.source_entity_id,
            "sequence_number": self.sequence_number,
            "timestamp": round(float(self.timestamp), 6),
            "payload": copy_dict_deterministic(self.payload),
        }


@dataclass
class Entity:
    entity_id: str
    name: str = ""
    state: EntityLifecycleState = EntityLifecycleState.ACTIVE
    tags: GameplayTagContainer = field(default_factory=GameplayTagContainer)
    components: Dict[str, Any] = field(default_factory=dict)
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        comp_dict = {}
        for k, c in sorted(self.components.items()):
            if hasattr(c, "to_dict"):
                comp_dict[k] = c.to_dict()
            else:
                comp_dict[k] = copy_dict_deterministic(c)
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "state": self.state.value,
            "tags": self.tags.to_dict(),
            "components": comp_dict,
            "position": (round(float(self.position[0]), 6), round(float(self.position[1]), 6), round(float(self.position[2]), 6)),
            "rotation": (round(float(self.rotation[0]), 6), round(float(self.rotation[1]), 6), round(float(self.rotation[2]), 6)),
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class SpawnRequest:
    spawn_id: str
    definition_id: str
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    owner_entity_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spawn_id": self.spawn_id,
            "definition_id": self.definition_id,
            "position": (round(float(self.position[0]), 6), round(float(self.position[1]), 6), round(float(self.position[2]), 6)),
            "rotation": (round(float(self.rotation[0]), 6), round(float(self.rotation[1]), 6), round(float(self.rotation[2]), 6)),
            "owner_entity_id": self.owner_entity_id,
        }


@dataclass
class DespawnRequest:
    despawn_id: str
    entity_id: str
    reason: str = "DEFAULT"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "despawn_id": self.despawn_id,
            "entity_id": self.entity_id,
            "reason": self.reason,
        }


@dataclass
class SaveState:
    save_id: str
    version: int = 1
    timestamp: float = 0.0
    gameplay_world_id: str = ""
    entities_data: Dict[str, Any] = field(default_factory=dict)
    inventory_data: Dict[str, Any] = field(default_factory=dict)
    quest_data: Dict[str, Any] = field(default_factory=dict)
    cooldowns_data: Dict[str, Any] = field(default_factory=dict)
    flags: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "save_id": self.save_id,
            "version": self.version,
            "timestamp": round(float(self.timestamp), 6),
            "gameplay_world_id": self.gameplay_world_id,
            "entities_data": copy_dict_deterministic(self.entities_data),
            "inventory_data": copy_dict_deterministic(self.inventory_data),
            "quest_data": copy_dict_deterministic(self.quest_data),
            "cooldowns_data": copy_dict_deterministic(self.cooldowns_data),
            "flags": copy_dict_deterministic(self.flags),
        }


@dataclass
class GameplaySnapshot:
    snapshot_id: str
    gameplay_world_id: str
    state: str
    tick_index: int
    simulation_time: float
    entities: Dict[str, Dict[str, Any]]
    quests: Dict[str, Dict[str, Any]]
    abilities: Dict[str, Dict[str, Any]]
    timers: Dict[str, Dict[str, Any]]
    fingerprint: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "gameplay_world_id": self.gameplay_world_id,
            "state": self.state,
            "tick_index": self.tick_index,
            "simulation_time": round(float(self.simulation_time), 6),
            "entities": {k: copy_dict_deterministic(v) for k, v in sorted(self.entities.items())},
            "quests": {k: copy_dict_deterministic(v) for k, v in sorted(self.quests.items())},
            "abilities": {k: copy_dict_deterministic(v) for k, v in sorted(self.abilities.items())},
            "timers": {k: copy_dict_deterministic(v) for k, v in sorted(self.timers.items())},
            "fingerprint": self.fingerprint,
        }


@dataclass
class GameplayWorldSettings:
    max_entities: int = 10000
    max_components_per_entity: int = 64
    max_commands_per_tick: int = 1000
    max_events_per_tick: int = 1000
    max_timers: int = 500
    max_rules: int = 200
    max_items_per_inventory: int = 500

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_entities": self.max_entities,
            "max_components_per_entity": self.max_components_per_entity,
            "max_commands_per_tick": self.max_commands_per_tick,
            "max_events_per_tick": self.max_events_per_tick,
            "max_timers": self.max_timers,
            "max_rules": self.max_rules,
            "max_items_per_inventory": self.max_items_per_inventory,
        }


@dataclass
class GameplayWorld:
    gameplay_world_id: str
    runtime_world_id: str = "runtime_world_default"
    state: GameplayWorldState = GameplayWorldState.CREATED
    settings: GameplayWorldSettings = field(default_factory=GameplayWorldSettings)
    tick: GameplayTick = field(default_factory=GameplayTick)
    entities: Dict[str, Entity] = field(default_factory=dict)
    rules: Dict[str, GameplayRule] = field(default_factory=dict)
    abilities: Dict[str, AbilityDefinition] = field(default_factory=dict)
    quests: Dict[str, QuestDefinition] = field(default_factory=dict)
    timers: Dict[str, GameplayTimer] = field(default_factory=dict)
    command_queue: List[GameplayCommand] = field(default_factory=list)
    event_queue: List[GameplayEvent] = field(default_factory=list)
    event_history: List[GameplayEvent] = field(default_factory=list)
    event_sequence_counter: int = 0
    spawn_counter: int = 0

    def compute_fingerprint(self) -> str:
        """Computes deterministic SHA-256 fingerprint of the logical gameplay state."""
        canonical = self.to_dict()
        serialized = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gameplay_world_id": self.gameplay_world_id,
            "runtime_world_id": self.runtime_world_id,
            "state": self.state.value,
            "settings": self.settings.to_dict(),
            "tick": self.tick.to_dict(),
            "entities": {k: e.to_dict() for k, e in sorted(self.entities.items())},
            "rules": {k: r.to_dict() for k, r in sorted(self.rules.items())},
            "abilities": {k: a.to_dict() for k, a in sorted(self.abilities.items())},
            "quests": {k: q.to_dict() for k, q in sorted(self.quests.items())},
            "timers": {k: t.to_dict() for k, t in sorted(self.timers.items())},
            "event_sequence_counter": self.event_sequence_counter,
            "spawn_counter": self.spawn_counter,
        }
