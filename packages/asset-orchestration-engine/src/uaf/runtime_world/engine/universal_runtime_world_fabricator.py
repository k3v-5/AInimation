"""
Universal Runtime World Fabricator and Simulation Engine.
Complies with UAF-81.73 specification.
"""

from __future__ import annotations
import copy
import hashlib
import json
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from uaf.runtime_world.models.definition import (
    WorldState,
    EntityLifecycleState,
    ComponentLifecycleState,
    SystemPhase,
    StreamingState,
    ResourceState,
    EventPriority,
    RuntimeTransform,
    RuntimeComponent,
    RuntimeEntity,
    RuntimeSystem,
    RuntimeEvent,
    EventSubscription,
    RuntimeResource,
    StreamingCell,
    RuntimeWorld,
    WorldStateSnapshot,
)


class UniversalRuntimeWorldFabricator:
    """Core fabricator and execution engine for runtime worlds, lifecycle, scheduling, and events."""

    def __init__(self):
        self.worlds: Dict[str, RuntimeWorld] = {}
        self.active_world: Optional[RuntimeWorld] = None
        self._sub_counter: int = 0
        self._event_counter: int = 0
        self.snapshots: List[WorldStateSnapshot] = []

    # --------------------------------------------------------------------------
    # 1. World Management & Finite State Machine
    # --------------------------------------------------------------------------

    def create_world(self, world_id: str, name: str = "World") -> RuntimeWorld:
        if not world_id or not world_id.strip():
            raise ValueError("INVALID_WORLD_ID: World ID cannot be empty.")
        if world_id in self.worlds:
            raise ValueError(f"DUPLICATE_WORLD_ID: World '{world_id}' already exists.")

        world = RuntimeWorld(world_id=world_id, name=name, state=WorldState.UNINITIALIZED)
        # Root entity
        root_entity = RuntimeEntity(
            entity_id="root",
            name="WorldRoot",
            state=EntityLifecycleState.INITIALIZED,
            parent_id=None
        )
        world.entities["root"] = root_entity
        world.root_entity_id = "root"

        self.worlds[world_id] = world
        self.active_world = world
        return world

    def get_world(self, world_id: str) -> Optional[RuntimeWorld]:
        return self.worlds.get(world_id)

    def initialize_world(self, world: Optional[RuntimeWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state != WorldState.UNINITIALIZED:
            raise ValueError(f"NO_INVALID_WORLD_TRANSITION: Cannot initialize world from state '{target.state.value}'.")

        target.state = WorldState.INITIALIZING
        # Initialize entities and components
        for ent in target.entities.values():
            if ent.state == EntityLifecycleState.CREATED:
                ent.state = EntityLifecycleState.INITIALIZED
            for comp in ent.components.values():
                if comp.state == ComponentLifecycleState.UNINITIALIZED:
                    comp.state = ComponentLifecycleState.INITIALIZED

        target.state = WorldState.INITIALIZED
        target.content_fingerprint = target.compute_fingerprint()

    def activate_world(self, world: Optional[RuntimeWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state not in (WorldState.INITIALIZED, WorldState.PAUSED):
            raise ValueError(f"NO_INVALID_WORLD_TRANSITION: Cannot activate world from state '{target.state.value}'.")

        target.state = WorldState.ACTIVE
        for ent in target.entities.values():
            if ent.state in (EntityLifecycleState.INITIALIZED, EntityLifecycleState.INACTIVE):
                ent.state = EntityLifecycleState.ACTIVE
            for comp in ent.components.values():
                if comp.state in (ComponentLifecycleState.INITIALIZED, ComponentLifecycleState.DISABLED):
                    comp.state = ComponentLifecycleState.ENABLED

        target.content_fingerprint = target.compute_fingerprint()

    def pause_world(self, world: Optional[RuntimeWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state != WorldState.ACTIVE:
            raise ValueError(f"NO_INVALID_WORLD_TRANSITION: Cannot pause world from state '{target.state.value}'.")
        target.state = WorldState.PAUSED

    def stop_world(self, world: Optional[RuntimeWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state not in (WorldState.ACTIVE, WorldState.PAUSED):
            raise ValueError(f"NO_INVALID_WORLD_TRANSITION: Cannot stop world from state '{target.state.value}'.")

        for ent in target.entities.values():
            if ent.state == EntityLifecycleState.ACTIVE:
                ent.state = EntityLifecycleState.INACTIVE
            for comp in ent.components.values():
                if comp.state == ComponentLifecycleState.ENABLED:
                    comp.state = ComponentLifecycleState.DISABLED

        target.state = WorldState.STOPPED

    def destroy_world(self, world: Optional[RuntimeWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        # Destroy all components and entities
        for ent in target.entities.values():
            for comp in ent.components.values():
                comp.state = ComponentLifecycleState.DESTROYED
            ent.state = EntityLifecycleState.DESTROYED

        target.entities.clear()
        target.systems.clear()
        target.resources.clear()
        target.event_queue.clear()
        target.event_subscriptions.clear()
        target.cells.clear()
        target.state = WorldState.TERMINATED

    # --------------------------------------------------------------------------
    # 2. Entity Management & Lifecycle
    # --------------------------------------------------------------------------

    def create_entity(
        self,
        entity_id: str,
        name: str = "RuntimeEntity",
        parent_id: Optional[str] = None,
        world: Optional[RuntimeWorld] = None
    ) -> RuntimeEntity:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if not entity_id or not entity_id.strip():
            raise ValueError("INVALID_ENTITY_ID: Entity ID cannot be empty.")
        if entity_id in target.entities:
            raise ValueError(f"NO_DUPLICATE_ENTITY_ID: Entity '{entity_id}' already exists.")

        effective_parent = parent_id or target.root_entity_id
        if effective_parent and effective_parent not in target.entities:
            raise ValueError(f"PARENT_NOT_FOUND: Parent '{effective_parent}' does not exist.")

        ent = RuntimeEntity(
            entity_id=entity_id,
            name=name,
            state=EntityLifecycleState.ACTIVE if target.state == WorldState.ACTIVE else EntityLifecycleState.CREATED,
            parent_id=effective_parent
        )
        target.entities[entity_id] = ent

        if effective_parent:
            parent = target.entities[effective_parent]
            if entity_id not in parent.children_ids:
                parent.children_ids.append(entity_id)

        return ent

    def activate_entity(self, entity_id: str, world: Optional[RuntimeWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if entity_id in getattr(target, "destroyed_entity_ids", set()):
            raise ValueError(f"NO_CALLBACK_AFTER_DESTROY: Entity '{entity_id}' is destroyed.")
        if entity_id not in target.entities:
            raise ValueError("ENTITY_NOT_FOUND")

        ent = target.entities[entity_id]
        if ent.state == EntityLifecycleState.DESTROYED:
            raise ValueError(f"NO_CALLBACK_AFTER_DESTROY: Entity '{entity_id}' is destroyed.")

        ent.state = EntityLifecycleState.ACTIVE
        for comp in ent.components.values():
            if comp.state != ComponentLifecycleState.DESTROYED:
                comp.state = ComponentLifecycleState.ENABLED

        for cid in ent.children_ids:
            if cid in target.entities:
                self.activate_entity(cid, target)

    def deactivate_entity(self, entity_id: str, world: Optional[RuntimeWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if entity_id in getattr(target, "destroyed_entity_ids", set()):
            raise ValueError(f"NO_CALLBACK_AFTER_DESTROY: Entity '{entity_id}' is destroyed.")
        if entity_id not in target.entities:
            raise ValueError("ENTITY_NOT_FOUND")

        ent = target.entities[entity_id]
        if ent.state == EntityLifecycleState.DESTROYED:
            raise ValueError("NO_CALLBACK_AFTER_DESTROY")

        ent.state = EntityLifecycleState.INACTIVE
        for comp in ent.components.values():
            if comp.state == ComponentLifecycleState.ENABLED:
                comp.state = ComponentLifecycleState.DISABLED

        for cid in ent.children_ids:
            if cid in target.entities:
                self.deactivate_entity(cid, target)

    def destroy_entity(self, entity_id: str, world: Optional[RuntimeWorld] = None) -> None:
        target = world or self.active_world
        if not target or entity_id not in target.entities:
            raise ValueError("ENTITY_NOT_FOUND")
        if entity_id == target.root_entity_id:
            raise ValueError("CANNOT_DESTROY_ROOT")

        ent = target.entities[entity_id]
        # Recursively destroy children first
        for cid in list(ent.children_ids):
            if cid in target.entities:
                self.destroy_entity(cid, target)

        # Destroy components
        for comp in ent.components.values():
            comp.state = ComponentLifecycleState.DESTROYED

        # Remove from parent
        if ent.parent_id and ent.parent_id in target.entities:
            p = target.entities[ent.parent_id]
            if entity_id in p.children_ids:
                p.children_ids.remove(entity_id)

        ent.state = EntityLifecycleState.DESTROYED
        if hasattr(target, "destroyed_entity_ids"):
            target.destroyed_entity_ids.add(entity_id)
        del target.entities[entity_id]

    def set_parent(
        self,
        child_id: str,
        new_parent_id: Optional[str],
        world: Optional[RuntimeWorld] = None
    ) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if child_id not in target.entities:
            raise ValueError(f"ENTITY_NOT_FOUND: '{child_id}'")
        if child_id == target.root_entity_id:
            raise ValueError("ROOT_CANNOT_BE_REPARENTED")
        if child_id == new_parent_id:
            raise ValueError("SELF_PARENTING_PROHIBITED")

        if new_parent_id is not None:
            if new_parent_id not in target.entities:
                raise ValueError(f"PARENT_NOT_FOUND: '{new_parent_id}'")
            curr: Optional[str] = new_parent_id
            while curr:
                if curr == child_id:
                    raise ValueError(f"NO_HIERARCHY_CYCLES: Reparenting creates cycle with '{child_id}'.")
                curr = target.entities[curr].parent_id

        child = target.entities[child_id]
        old_parent_id = child.parent_id
        if old_parent_id and old_parent_id in target.entities:
            op = target.entities[old_parent_id]
            if child_id in op.children_ids:
                op.children_ids.remove(child_id)

        child.parent_id = new_parent_id
        if new_parent_id and new_parent_id in target.entities:
            np = target.entities[new_parent_id]
            if child_id not in np.children_ids:
                np.children_ids.append(child_id)

    def compute_world_transform(
        self,
        entity_id: str,
        world: Optional[RuntimeWorld] = None
    ) -> RuntimeTransform:
        target = world or self.active_world
        if not target or entity_id not in target.entities:
            raise ValueError("ENTITY_NOT_FOUND")

        lineage: List[str] = []
        curr: Optional[str] = entity_id
        visited: Set[str] = set()
        while curr:
            if curr in visited:
                raise ValueError("NO_HIERARCHY_CYCLES")
            visited.add(curr)
            lineage.append(curr)
            curr = target.entities[curr].parent_id

        lineage.reverse()
        accum = RuntimeTransform()
        for eid in lineage:
            accum = accum.combine(target.entities[eid].local_transform)

        target.entities[entity_id].world_transform = accum
        return accum

    # --------------------------------------------------------------------------
    # 3. Component Management & Lifecycle
    # --------------------------------------------------------------------------

    def add_component(
        self,
        entity_id: str,
        component: RuntimeComponent,
        world: Optional[RuntimeWorld] = None
    ) -> None:
        target = world or self.active_world
        if not target or entity_id not in target.entities:
            raise ValueError("ENTITY_NOT_FOUND")
        if not component.component_id or not component.component_id.strip():
            raise ValueError("INVALID_COMPONENT_ID")

        ent = target.entities[entity_id]
        if ent.state == EntityLifecycleState.DESTROYED:
            raise ValueError("NO_CALLBACK_AFTER_DESTROY")

        # Validate dependencies
        for dep in component.dependencies:
            if dep not in ent.components:
                raise ValueError(f"MISSING_COMPONENT_DEPENDENCY: Component '{component.component_id}' requires '{dep}'.")

        if ent.state == EntityLifecycleState.ACTIVE:
            component.state = ComponentLifecycleState.ENABLED
        elif ent.state == EntityLifecycleState.INITIALIZED:
            component.state = ComponentLifecycleState.INITIALIZED
        else:
            component.state = ComponentLifecycleState.UNINITIALIZED

        ent.components[component.component_id] = component

    def initialize_component(
        self,
        entity_id: str,
        component_id: str,
        world: Optional[RuntimeWorld] = None
    ) -> None:
        target = world or self.active_world
        if not target or entity_id not in target.entities:
            raise ValueError("ENTITY_NOT_FOUND")
        ent = target.entities[entity_id]
        if component_id not in ent.components:
            raise ValueError("COMPONENT_NOT_FOUND")

        c = ent.components[component_id]
        if c.state == ComponentLifecycleState.DESTROYED:
            raise ValueError("NO_CALLBACK_AFTER_DESTROY")
        c.state = ComponentLifecycleState.INITIALIZED

    def enable_component(
        self,
        entity_id: str,
        component_id: str,
        world: Optional[RuntimeWorld] = None
    ) -> None:
        target = world or self.active_world
        if not target or entity_id not in target.entities:
            raise ValueError("ENTITY_NOT_FOUND")
        ent = target.entities[entity_id]
        if component_id not in ent.components:
            raise ValueError("COMPONENT_NOT_FOUND")

        c = ent.components[component_id]
        if c.state == ComponentLifecycleState.DESTROYED:
            raise ValueError("NO_CALLBACK_AFTER_DESTROY")
        c.state = ComponentLifecycleState.ENABLED

    def disable_component(
        self,
        entity_id: str,
        component_id: str,
        world: Optional[RuntimeWorld] = None
    ) -> None:
        target = world or self.active_world
        if not target or entity_id not in target.entities:
            raise ValueError("ENTITY_NOT_FOUND")
        ent = target.entities[entity_id]
        if component_id not in ent.components:
            raise ValueError("COMPONENT_NOT_FOUND")

        c = ent.components[component_id]
        if c.state == ComponentLifecycleState.DESTROYED:
            raise ValueError("NO_CALLBACK_AFTER_DESTROY")
        c.state = ComponentLifecycleState.DISABLED

    def destroy_component(
        self,
        entity_id: str,
        component_id: str,
        world: Optional[RuntimeWorld] = None
    ) -> None:
        target = world or self.active_world
        if not target or entity_id not in target.entities:
            raise ValueError("ENTITY_NOT_FOUND")
        ent = target.entities[entity_id]
        if component_id not in ent.components:
            raise ValueError("COMPONENT_NOT_FOUND")

        c = ent.components[component_id]
        c.state = ComponentLifecycleState.DESTROYED
        del ent.components[component_id]

    # --------------------------------------------------------------------------
    # 4. System Scheduler & Execution
    # --------------------------------------------------------------------------

    def register_system(
        self,
        system: RuntimeSystem,
        world: Optional[RuntimeWorld] = None
    ) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if not system.system_id or not system.system_id.strip():
            raise ValueError("INVALID_SYSTEM_ID")

        target.systems[system.system_id] = system

    def enable_system(self, system_id: str, world: Optional[RuntimeWorld] = None) -> None:
        target = world or self.active_world
        if not target or system_id not in target.systems:
            raise ValueError("SYSTEM_NOT_FOUND")
        target.systems[system_id].is_enabled = True

    def disable_system(self, system_id: str, world: Optional[RuntimeWorld] = None) -> None:
        target = world or self.active_world
        if not target or system_id not in target.systems:
            raise ValueError("SYSTEM_NOT_FOUND")
        target.systems[system_id].is_enabled = False

    def get_scheduled_systems(
        self,
        phase: Optional[SystemPhase] = None,
        world: Optional[RuntimeWorld] = None
    ) -> List[RuntimeSystem]:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        candidates = [
            s for s in target.systems.values()
            if s.is_enabled and (phase is None or s.phase == phase)
        ]

        # Check for cycles and build topological order
        # Kahn's algorithm with deterministic tie-breaking (priority desc, system_id asc)
        graph: Dict[str, List[str]] = {s.system_id: [] for s in candidates}
        in_degree: Dict[str, int] = {s.system_id: 0 for s in candidates}
        cand_map = {s.system_id: s for s in candidates}

        for s in candidates:
            for dep_id in s.dependencies:
                if dep_id in cand_map:
                    # dep_id must run before s
                    graph[dep_id].append(s.system_id)
                    in_degree[s.system_id] += 1

        # Queue contains systems with 0 in-degree
        # Priority queue emulation: sort by (-priority, system_id)
        ready = [sid for sid, deg in in_degree.items() if deg == 0]
        ready.sort(key=lambda x: (-cand_map[x].priority, x))

        ordered: List[RuntimeSystem] = []
        while ready:
            curr_id = ready.pop(0)
            ordered.append(cand_map[curr_id])

            for neighbor in graph[curr_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    ready.append(neighbor)
            ready.sort(key=lambda x: (-cand_map[x].priority, x))

        if len(ordered) < len(candidates):
            raise ValueError("NO_SYSTEM_DEPENDENCY_CYCLE: Dependency cycle detected among systems.")

        return ordered

    # --------------------------------------------------------------------------
    # 5. Event Bus
    # --------------------------------------------------------------------------

    def subscribe_event(
        self,
        event_type: str,
        callback: Callable[[RuntimeEvent], None],
        priority: EventPriority = EventPriority.NORMAL,
        target_id: Optional[str] = None,
        world: Optional[RuntimeWorld] = None
    ) -> str:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        self._sub_counter += 1
        sub_id = f"sub_{event_type}_{self._sub_counter}"
        sub = EventSubscription(
            subscription_id=sub_id,
            event_type=event_type,
            callback=callback,
            priority=priority,
            target_id=target_id
        )
        if event_type not in target.event_subscriptions:
            target.event_subscriptions[event_type] = []
        target.event_subscriptions[event_type].append(sub)
        return sub_id

    def unsubscribe_event(self, subscription_id: str, world: Optional[RuntimeWorld] = None) -> bool:
        target = world or self.active_world
        if not target:
            return False

        found = False
        for et, subs in target.event_subscriptions.items():
            before = len(subs)
            target.event_subscriptions[et] = [s for s in subs if s.subscription_id != subscription_id]
            if len(target.event_subscriptions[et]) < before:
                found = True
        return found

    def publish_event(
        self,
        event_type: str,
        sender_id: str,
        payload: Optional[Dict[str, Any]] = None,
        target_id: Optional[str] = None,
        priority: EventPriority = EventPriority.NORMAL,
        world: Optional[RuntimeWorld] = None
    ) -> RuntimeEvent:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        self._event_counter += 1
        event = RuntimeEvent(
            event_id=f"evt_{self._event_counter}",
            event_type=event_type,
            sender_id=sender_id,
            target_id=target_id,
            payload=payload or {},
            priority=priority,
            timestamp=target.time_seconds
        )
        target.event_queue.append(event)
        return event

    def dispatch_events(self, world: Optional[RuntimeWorld] = None, limit: int = 1000) -> int:
        target = world or self.active_world
        if not target:
            return 0

        # Sort queue deterministically by priority, timestamp, and event_id
        target.event_queue.sort(key=lambda e: (e.priority.value, e.timestamp, e.event_id))
        count = 0

        while target.event_queue:
            if count >= limit:
                raise ValueError("EVENT_LOOP_LIMIT_EXCEEDED: Event loop limit exceeded during dispatch.")

            evt = target.event_queue.pop(0)
            count += 1

            # Disallow delivery to destroyed targets
            if evt.target_id:
                if evt.target_id in target.entities and target.entities[evt.target_id].state == EntityLifecycleState.DESTROYED:
                    continue
                if evt.target_id not in target.entities and evt.target_id != "broadcast":
                    continue

            subs = list(target.event_subscriptions.get(evt.event_type, []))
            # Sort subscriptions by priority asc, subscription_id asc
            subs.sort(key=lambda s: (s.priority.value, s.subscription_id))
            for sub in subs:
                if sub.target_id is None or sub.target_id == evt.target_id:
                    sub.callback(evt)

        return count

    # --------------------------------------------------------------------------
    # 6. Resource Resolution
    # --------------------------------------------------------------------------

    def register_resource(
        self,
        resource: RuntimeResource,
        world: Optional[RuntimeWorld] = None
    ) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        target.resources[resource.resource_id] = resource

    def acquire_resource(
        self,
        resource_id: str,
        world: Optional[RuntimeWorld] = None
    ) -> RuntimeResource:
        target = world or self.active_world
        if not target or resource_id not in target.resources:
            raise ValueError(f"RESOURCE_NOT_FOUND: '{resource_id}'")

        res = target.resources[resource_id]
        res.ref_count += 1
        res.state = ResourceState.READY
        return res

    def release_resource(
        self,
        resource_id: str,
        world: Optional[RuntimeWorld] = None
    ) -> None:
        target = world or self.active_world
        if not target or resource_id not in target.resources:
            raise ValueError("RESOURCE_NOT_FOUND")

        res = target.resources[resource_id]
        if res.ref_count <= 0 or res.state == ResourceState.RELEASED:
            raise ValueError("NO_RESOURCE_USE_AFTER_RELEASE: Resource already released or ref count is zero.")

        res.ref_count -= 1
        if res.ref_count == 0:
            res.state = ResourceState.RELEASED

    # --------------------------------------------------------------------------
    # 7. Prefab Runtime Instantiation
    # --------------------------------------------------------------------------

    def spawn_prefab(
        self,
        prefab: Any,
        instance_id: str,
        parent_id: Optional[str] = None,
        overrides: Optional[List[Any]] = None,
        world: Optional[RuntimeWorld] = None
    ) -> List[RuntimeEntity]:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if not instance_id or not instance_id.strip():
            raise ValueError("INVALID_INSTANCE_ID")

        spawned: List[RuntimeEntity] = []
        eff_parent = parent_id or target.root_entity_id
        if eff_parent and eff_parent not in target.entities:
            raise ValueError("PARENT_NOT_FOUND")

        # Spawn entities from prefab
        entities_to_spawn = getattr(prefab, "entities", {})
        if not entities_to_spawn:
            # Fallback single entity
            root_eid = f"{instance_id}_root"
            ent = self.create_entity(root_eid, name=getattr(prefab, "name", "PrefabRoot"), parent_id=eff_parent, world=target)
            ent.prefab_instance_id = instance_id
            spawned.append(ent)
            return spawned

        id_map: Dict[str, str] = {}
        for orig_id in entities_to_spawn:
            id_map[orig_id] = f"{instance_id}_{orig_id}"

        for orig_id, pe in entities_to_spawn.items():
            new_id = id_map[orig_id]
            p_orig = getattr(pe, "parent_id", None)
            new_parent = id_map.get(p_orig, eff_parent) if p_orig else eff_parent
            ent = self.create_entity(new_id, name=getattr(pe, "name", "Entity"), parent_id=new_parent, world=target)
            ent.prefab_instance_id = instance_id

            # Cloned components
            comps = getattr(pe, "components", {})
            for cid, c in (comps.items() if isinstance(comps, dict) else []):
                new_comp = RuntimeComponent(
                    component_id=cid,
                    component_type=getattr(c, "component_type", "CUSTOM").value if hasattr(getattr(c, "component_type", None), "value") else str(getattr(c, "component_type", "CUSTOM")),
                    properties=copy.deepcopy(getattr(c, "properties", {}))
                )
                self.add_component(new_id, new_comp, target)

            spawned.append(ent)

        # Apply runtime overrides if any
        if overrides:
            for ov in overrides:
                target_eid = getattr(ov, "target_entity_id", None)
                if target_eid in target.entities:
                    prop_path = getattr(ov, "property_path", None)
                    val = getattr(ov, "value", None)
                    if prop_path == "name" and val:
                        target.entities[target_eid].name = str(val)

        return spawned

    def despawn_prefab(
        self,
        instance_id: str,
        world: Optional[RuntimeWorld] = None
    ) -> int:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        matching = [eid for eid, e in target.entities.items() if e.prefab_instance_id == instance_id]
        for eid in matching:
            if eid in target.entities:
                self.destroy_entity(eid, target)
        return len(matching)

    # --------------------------------------------------------------------------
    # 8. World Streaming
    # --------------------------------------------------------------------------

    def create_streaming_cell(
        self,
        cell_id: str,
        scene_path: str,
        bounds: Optional[Dict[str, Any]] = None,
        priority: int = 0,
        dependencies: Optional[List[str]] = None,
        world: Optional[RuntimeWorld] = None
    ) -> StreamingCell:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if not cell_id or not cell_id.strip():
            raise ValueError("INVALID_CELL_ID")

        cell = StreamingCell(
            cell_id=cell_id,
            scene_path=scene_path,
            bounds=bounds or {"min": [0, 0, 0], "max": [100, 100, 100]},
            priority=priority,
            dependencies=dependencies or []
        )
        target.cells[cell_id] = cell
        return cell

    def load_streaming_cell(self, cell_id: str, world: Optional[RuntimeWorld] = None) -> None:
        target = world or self.active_world
        if not target or cell_id not in target.cells:
            raise ValueError("CELL_NOT_FOUND")

        cell = target.cells[cell_id]
        cell.state = StreamingState.LOADING
        # Check dependencies
        for dep in cell.dependencies:
            if dep in target.cells and target.cells[dep].state not in (StreamingState.LOADED, StreamingState.ACTIVE):
                raise ValueError(f"STREAMING_DEPENDENCY_NOT_MET: '{dep}'")

        cell.state = StreamingState.LOADED

    def activate_streaming_cell(self, cell_id: str, world: Optional[RuntimeWorld] = None) -> None:
        target = world or self.active_world
        if not target or cell_id not in target.cells:
            raise ValueError("CELL_NOT_FOUND")

        cell = target.cells[cell_id]
        if cell.state != StreamingState.LOADED:
            raise ValueError("CANNOT_ACTIVATE_UNLOADED_CELL")

        cell.state = StreamingState.ACTIVE
        for eid in cell.entity_ids:
            if eid in target.entities:
                self.activate_entity(eid, target)

    def deactivate_streaming_cell(self, cell_id: str, world: Optional[RuntimeWorld] = None) -> None:
        target = world or self.active_world
        if not target or cell_id not in target.cells:
            raise ValueError("CELL_NOT_FOUND")

        cell = target.cells[cell_id]
        if cell.state == StreamingState.ACTIVE:
            cell.state = StreamingState.LOADED
            for eid in cell.entity_ids:
                if eid in target.entities:
                    self.deactivate_entity(eid, target)

    def unload_streaming_cell(self, cell_id: str, world: Optional[RuntimeWorld] = None) -> None:
        target = world or self.active_world
        if not target or cell_id not in target.cells:
            raise ValueError("CELL_NOT_FOUND")

        cell = target.cells[cell_id]
        if cell.state == StreamingState.ACTIVE:
            self.deactivate_streaming_cell(cell_id, target)

        cell.state = StreamingState.UNLOADING
        for eid in list(cell.entity_ids):
            if eid in target.entities:
                self.destroy_entity(eid, target)
        cell.entity_ids.clear()
        cell.state = StreamingState.UNLOADED

    # --------------------------------------------------------------------------
    # 9. Simulation Tick & Snapshots
    # --------------------------------------------------------------------------

    def tick(self, dt: float, world: Optional[RuntimeWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state == WorldState.UNINITIALIZED:
            raise ValueError("NO_UPDATE_BEFORE_INITIALIZATION")
        if target.state != WorldState.ACTIVE:
            return

        scaled_dt = dt * target.time_scale
        target.time_seconds += scaled_dt

        # Execute scheduled systems phase by phase
        for phase in [
            SystemPhase.PRE_UPDATE,
            SystemPhase.UPDATE,
            SystemPhase.POST_UPDATE,
            SystemPhase.RENDER,
            SystemPhase.CLEANUP,
        ]:
            systems = self.get_scheduled_systems(phase=phase, world=target)
            for sys in systems:
                if sys.update_fn:
                    sys.update_fn(target, scaled_dt)

        # Dispatch events accumulated during tick
        self.dispatch_events(target)

    def take_snapshot(self, world: Optional[RuntimeWorld] = None) -> WorldStateSnapshot:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        snap_id = f"snap_world_{int(time.time() * 1000)}_{len(self.snapshots)}"
        snap = WorldStateSnapshot(
            snapshot_id=snap_id,
            world_id=target.world_id,
            timestamp=target.time_seconds,
            world_state=target.state.value,
            data=target.to_dict()
        )
        self.snapshots.append(snap)
        return snap

    def restore_snapshot(
        self,
        snapshot: WorldStateSnapshot,
        world: Optional[RuntimeWorld] = None
    ) -> RuntimeWorld:
        data = snapshot.data
        world_id = snapshot.world_id

        restored = RuntimeWorld(
            world_id=world_id,
            name=data.get("name", "World"),
            state=WorldState(snapshot.world_state),
            time_seconds=snapshot.timestamp,
            time_scale=data.get("time_scale", 1.0),
            fixed_delta_time=data.get("fixed_delta_time", 1.0 / 60.0),
            root_entity_id=data.get("root_entity_id", "root")
        )

        # Entities
        for eid, ed in data.get("entities", {}).items():
            components = {
                cid: RuntimeComponent(
                    component_id=cd["component_id"],
                    component_type=cd["component_type"],
                    state=ComponentLifecycleState(cd["state"]),
                    properties=cd.get("properties", {}),
                    dependencies=cd.get("dependencies", []),
                    resource_dependencies=cd.get("resource_dependencies", [])
                )
                for cid, cd in ed.get("components", {}).items()
            }
            lt = ed.get("local_transform", {})
            wt = ed.get("world_transform", {})
            ent = RuntimeEntity(
                entity_id=ed["entity_id"],
                name=ed.get("name", "RuntimeEntity"),
                state=EntityLifecycleState(ed["state"]),
                parent_id=ed.get("parent_id"),
                children_ids=ed.get("children_ids", []),
                components=components,
                local_transform=RuntimeTransform(lt.get("position", [0, 0, 0]), lt.get("rotation", [0, 0, 0]), lt.get("scale", [1, 1, 1])),
                world_transform=RuntimeTransform(wt.get("position", [0, 0, 0]), wt.get("rotation", [0, 0, 0]), wt.get("scale", [1, 1, 1])),
                prefab_instance_id=ed.get("prefab_instance_id"),
                tags=ed.get("tags", [])
            )
            restored.entities[eid] = ent

        # Systems
        for sid, sd in data.get("systems", {}).items():
            restored.systems[sid] = RuntimeSystem(
                system_id=sd["system_id"],
                name=sd.get("name", "System"),
                phase=SystemPhase(sd["phase"]),
                priority=sd.get("priority", 100),
                dependencies=sd.get("dependencies", []),
                is_enabled=sd.get("is_enabled", True)
            )

        # Resources
        for rid, rd in data.get("resources", {}).items():
            restored.resources[rid] = RuntimeResource(
                resource_id=rd["resource_id"],
                resource_type=rd["resource_type"],
                uri=rd["uri"],
                state=ResourceState(rd["state"]),
                ref_count=rd.get("ref_count", 0),
                metadata=rd.get("metadata", {})
            )

        # Cells
        for cid, cld in data.get("cells", {}).items():
            restored.cells[cid] = StreamingCell(
                cell_id=cld["cell_id"],
                scene_path=cld["scene_path"],
                state=StreamingState(cld["state"]),
                bounds=cld.get("bounds", {}),
                priority=cld.get("priority", 0),
                dependencies=cld.get("dependencies", []),
                entity_ids=cld.get("entity_ids", [])
            )

        restored.content_fingerprint = restored.compute_fingerprint()
        self.worlds[world_id] = restored
        self.active_world = restored
        return restored
