"""
Universal Runtime World Model Definition.
Complies with UAF-81.73 specification.
"""

from __future__ import annotations
import copy
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


class WorldState(str, Enum):
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    INITIALIZED = "INITIALIZED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    TERMINATED = "TERMINATED"


class EntityLifecycleState(str, Enum):
    CREATED = "CREATED"
    INITIALIZED = "INITIALIZED"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DESTROYED = "DESTROYED"


class ComponentLifecycleState(str, Enum):
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZED = "INITIALIZED"
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    DESTROYED = "DESTROYED"


class SystemPhase(str, Enum):
    PRE_UPDATE = "PRE_UPDATE"
    UPDATE = "UPDATE"
    POST_UPDATE = "POST_UPDATE"
    RENDER = "RENDER"
    CLEANUP = "CLEANUP"


class StreamingState(str, Enum):
    UNLOADED = "UNLOADED"
    LOADING = "LOADING"
    LOADED = "LOADED"
    ACTIVE = "ACTIVE"
    UNLOADING = "UNLOADING"


class ResourceState(str, Enum):
    UNLOADED = "UNLOADED"
    LOADING = "LOADING"
    READY = "READY"
    FAILED = "FAILED"
    RELEASED = "RELEASED"


class EventPriority(int, Enum):
    HIGHEST = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    LOWEST = 4


def copy_dict_deterministic(data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        return data
    return {k: copy_dict_deterministic(v) if isinstance(v, dict) else v for k, v in sorted(data.items())}


@dataclass
class RuntimeTransform:
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    scale: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])

    def combine(self, other: RuntimeTransform) -> RuntimeTransform:
        return RuntimeTransform(
            position=[self.position[i] + other.position[i] for i in range(3)],
            rotation=[self.rotation[i] + other.rotation[i] for i in range(3)],
            scale=[self.scale[i] * other.scale[i] for i in range(3)],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": list(self.position),
            "rotation": list(self.rotation),
            "scale": list(self.scale),
        }


@dataclass
class RuntimeComponent:
    component_id: str
    component_type: str
    state: ComponentLifecycleState = ComponentLifecycleState.UNINITIALIZED
    properties: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    resource_dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_id": self.component_id,
            "component_type": self.component_type,
            "state": self.state.value,
            "properties": copy_dict_deterministic(self.properties),
            "dependencies": sorted(list(self.dependencies)),
            "resource_dependencies": sorted(list(self.resource_dependencies)),
        }


@dataclass
class RuntimeEntity:
    entity_id: str
    name: str = "RuntimeEntity"
    state: EntityLifecycleState = EntityLifecycleState.CREATED
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    components: Dict[str, RuntimeComponent] = field(default_factory=dict)
    local_transform: RuntimeTransform = field(default_factory=RuntimeTransform)
    world_transform: RuntimeTransform = field(default_factory=RuntimeTransform)
    prefab_instance_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "state": self.state.value,
            "parent_id": self.parent_id,
            "children_ids": list(self.children_ids),
            "components": {cid: c.to_dict() for cid, c in sorted(self.components.items())},
            "local_transform": self.local_transform.to_dict(),
            "world_transform": self.world_transform.to_dict(),
            "prefab_instance_id": self.prefab_instance_id,
            "tags": sorted(list(self.tags)),
        }


@dataclass
class RuntimeSystem:
    system_id: str
    name: str
    phase: SystemPhase = SystemPhase.UPDATE
    priority: int = 100
    dependencies: List[str] = field(default_factory=list)
    is_enabled: bool = True
    update_fn: Optional[Callable[[Any, float], None]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "system_id": self.system_id,
            "name": self.name,
            "phase": self.phase.value,
            "priority": self.priority,
            "dependencies": sorted(list(self.dependencies)),
            "is_enabled": self.is_enabled,
        }


@dataclass
class RuntimeEvent:
    event_id: str
    event_type: str
    sender_id: str
    target_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "sender_id": self.sender_id,
            "target_id": self.target_id,
            "payload": copy_dict_deterministic(self.payload),
            "priority": self.priority.value,
            "timestamp": self.timestamp,
        }


@dataclass
class EventSubscription:
    subscription_id: str
    event_type: str
    callback: Callable[[RuntimeEvent], None]
    priority: EventPriority = EventPriority.NORMAL
    target_id: Optional[str] = None


@dataclass
class RuntimeResource:
    resource_id: str
    resource_type: str
    uri: str
    state: ResourceState = ResourceState.UNLOADED
    ref_count: int = 0
    data: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "uri": self.uri,
            "state": self.state.value,
            "ref_count": self.ref_count,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class StreamingCell:
    cell_id: str
    scene_path: str
    state: StreamingState = StreamingState.UNLOADED
    bounds: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)
    entity_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cell_id": self.cell_id,
            "scene_path": self.scene_path,
            "state": self.state.value,
            "bounds": copy_dict_deterministic(self.bounds),
            "priority": self.priority,
            "dependencies": sorted(list(self.dependencies)),
            "entity_ids": sorted(list(self.entity_ids)),
        }


@dataclass
class RuntimeWorld:
    world_id: str
    name: str = "World"
    state: WorldState = WorldState.UNINITIALIZED
    time_seconds: float = 0.0
    time_scale: float = 1.0
    fixed_delta_time: float = 1.0 / 60.0
    entities: Dict[str, RuntimeEntity] = field(default_factory=dict)
    root_entity_id: str = "root"
    systems: Dict[str, RuntimeSystem] = field(default_factory=dict)
    resources: Dict[str, RuntimeResource] = field(default_factory=dict)
    cells: Dict[str, StreamingCell] = field(default_factory=dict)
    event_queue: List[RuntimeEvent] = field(default_factory=list)
    event_subscriptions: Dict[str, List[EventSubscription]] = field(default_factory=dict)
    destroyed_entity_ids: Set[str] = field(default_factory=set)
    content_fingerprint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "world_id": self.world_id,
            "name": self.name,
            "state": self.state.value,
            "time_seconds": self.time_seconds,
            "time_scale": self.time_scale,
            "fixed_delta_time": self.fixed_delta_time,
            "root_entity_id": self.root_entity_id,
            "entities": {eid: e.to_dict() for eid, e in sorted(self.entities.items())},
            "systems": {sid: s.to_dict() for sid, s in sorted(self.systems.items())},
            "resources": {rid: r.to_dict() for rid, r in sorted(self.resources.items())},
            "cells": {cid: c.to_dict() for cid, c in sorted(self.cells.items())},
        }

    def compute_fingerprint(self) -> str:
        data = self.to_dict()
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def __post_init__(self):
        if not self.content_fingerprint:
            self.content_fingerprint = self.compute_fingerprint()


@dataclass
class WorldStateSnapshot:
    snapshot_id: str
    world_id: str
    timestamp: float
    world_state: str
    data: Dict[str, Any]
    fingerprint: str = ""

    def compute_fingerprint(self) -> str:
        payload = f"{self.snapshot_id}:{self.world_id}:{self.timestamp}:{self.world_state}:{json.dumps(self.data, sort_keys=True)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def __post_init__(self):
        if not self.fingerprint:
            self.fingerprint = self.compute_fingerprint()
