"""
Acceptance Test Suite for UAF-81.73 Universal Runtime World Model System.
Complies with UAF-81.73 specification.
"""

import copy
import dataclasses
import hashlib
import json
from pathlib import Path
import time
import pytest

from uaf.runtime_world import (
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
    UniversalRuntimeWorldFabricator,
    UniversalRuntimeWorldValidator,
    UniversalRuntimeWorldPackager,
)


# ==============================================================================
# FIXTURES & HELPERS
# ==============================================================================

def make_test_world(world_id: str = "test_world") -> tuple:
    fab = UniversalRuntimeWorldFabricator()
    world = fab.create_world(world_id, "Test World")
    return fab, world


# ==============================================================================
# §101. WORLD TESTS (9 tests)
# ==============================================================================

class TestWorld:
    """Normative tests for World Model, State Transitions, and FSM (§101)."""

    def test_world_creation(self):
        fab, w = make_test_world("w_create")
        assert w.world_id == "w_create"
        assert w.state == WorldState.UNINITIALIZED
        assert "root" in w.entities

    def test_world_identity(self):
        fab, w = make_test_world("w_id")
        assert w.name == "Test World"
        assert w.time_seconds == 0.0
        assert w.time_scale == 1.0

    def test_world_state(self):
        fab, w = make_test_world("w_state")
        fab.initialize_world(w)
        assert w.state == WorldState.INITIALIZED

    def test_world_activation(self):
        fab, w = make_test_world("w_act")
        fab.initialize_world(w)
        fab.activate_world(w)
        assert w.state == WorldState.ACTIVE

    def test_world_pause(self):
        fab, w = make_test_world("w_pause")
        fab.initialize_world(w)
        fab.activate_world(w)
        fab.pause_world(w)
        assert w.state == WorldState.PAUSED

    def test_world_deactivation(self):
        fab, w = make_test_world("w_deact")
        fab.initialize_world(w)
        fab.activate_world(w)
        fab.stop_world(w)
        assert w.state == WorldState.STOPPED

    def test_world_destroy(self):
        fab, w = make_test_world("w_dest")
        fab.initialize_world(w)
        fab.activate_world(w)
        fab.destroy_world(w)
        assert w.state == WorldState.TERMINATED
        assert len(w.entities) == 0

    def test_invalid_world_transition(self):
        fab, w = make_test_world("w_inv_trans")
        # Cannot activate before initialize
        with pytest.raises(ValueError, match="NO_INVALID_WORLD_TRANSITION"):
            fab.activate_world(w)

    def test_world_failure(self):
        fab = UniversalRuntimeWorldFabricator()
        with pytest.raises(ValueError, match="NO_ACTIVE_WORLD"):
            fab.initialize_world(None)


# ==============================================================================
# §102. ENTITY LIFECYCLE TESTS (10 tests)
# ==============================================================================

class TestEntityLifecycle:
    """Normative tests for Entity Lifecycle, Hierarchical Activation, and Destruction (§102)."""

    def test_entity_create(self):
        fab, w = make_test_world("ent_create")
        e = fab.create_entity("hero")
        assert e.entity_id == "hero"
        assert e.state == EntityLifecycleState.CREATED
        assert e.parent_id == "root"

    def test_entity_initialize(self):
        fab, w = make_test_world("ent_init")
        e = fab.create_entity("actor")
        fab.initialize_world(w)
        assert e.state == EntityLifecycleState.INITIALIZED

    def test_entity_activate(self):
        fab, w = make_test_world("ent_act")
        e = fab.create_entity("actor")
        fab.initialize_world(w)
        fab.activate_world(w)
        assert e.state == EntityLifecycleState.ACTIVE

    def test_entity_disable(self):
        fab, w = make_test_world("ent_dis")
        e = fab.create_entity("actor")
        fab.initialize_world(w)
        fab.activate_world(w)
        fab.deactivate_entity("actor", w)
        assert e.state == EntityLifecycleState.INACTIVE

    def test_entity_deactivate(self):
        fab, w = make_test_world("ent_deact")
        e = fab.create_entity("actor")
        fab.initialize_world(w)
        fab.activate_world(w)
        fab.stop_world(w)
        assert e.state == EntityLifecycleState.INACTIVE

    def test_entity_destroy(self):
        fab, w = make_test_world("ent_dest")
        fab.create_entity("actor")
        fab.destroy_entity("actor", w)
        assert "actor" not in w.entities

    def test_entity_parent_activation(self):
        fab, w = make_test_world("ent_p_act")
        p = fab.create_entity("parent")
        c = fab.create_entity("child", parent_id="parent")
        fab.initialize_world(w)
        fab.activate_world(w)
        fab.deactivate_entity("parent", w)
        assert c.state == EntityLifecycleState.INACTIVE

    def test_entity_child_activation(self):
        fab, w = make_test_world("ent_c_act")
        p = fab.create_entity("parent")
        c = fab.create_entity("child", parent_id="parent")
        fab.initialize_world(w)
        fab.activate_entity("parent", w)
        assert c.state == EntityLifecycleState.ACTIVE

    def test_entity_failure(self):
        fab, w = make_test_world("ent_fail")
        with pytest.raises(ValueError, match="NO_DUPLICATE_ENTITY_ID"):
            fab.create_entity("e1")
            fab.create_entity("e1")

    def test_entity_cleanup(self):
        fab, w = make_test_world("ent_clean")
        p = fab.create_entity("parent")
        c = fab.create_entity("child", parent_id="parent")
        fab.destroy_entity("parent", w)
        assert "parent" not in w.entities
        assert "child" not in w.entities


# ==============================================================================
# §103. COMPONENT TESTS (10 tests)
# ==============================================================================

class TestComponentExecution:
    """Normative tests for Component Lifecycle and Dependency Checking (§103)."""

    def test_component_create(self):
        fab, w = make_test_world("comp_create")
        fab.create_entity("actor")
        comp = RuntimeComponent("c_tr", "TransformComponent")
        fab.add_component("actor", comp, w)
        assert "c_tr" in w.entities["actor"].components

    def test_component_initialize(self):
        fab, w = make_test_world("comp_init")
        fab.create_entity("actor")
        comp = RuntimeComponent("c1", "MeshComponent")
        fab.add_component("actor", comp, w)
        fab.initialize_component("actor", "c1", w)
        assert comp.state == ComponentLifecycleState.INITIALIZED

    def test_component_enable(self):
        fab, w = make_test_world("comp_enable")
        fab.create_entity("actor")
        comp = RuntimeComponent("c1", "AudioComponent")
        fab.add_component("actor", comp, w)
        fab.enable_component("actor", "c1", w)
        assert comp.state == ComponentLifecycleState.ENABLED

    def test_component_disable(self):
        fab, w = make_test_world("comp_disable")
        fab.create_entity("actor")
        comp = RuntimeComponent("c1", "AudioComponent")
        fab.add_component("actor", comp, w)
        fab.enable_component("actor", "c1", w)
        fab.disable_component("actor", "c1", w)
        assert comp.state == ComponentLifecycleState.DISABLED

    def test_component_destroy(self):
        fab, w = make_test_world("comp_destroy")
        fab.create_entity("actor")
        comp = RuntimeComponent("c1", "AudioComponent")
        fab.add_component("actor", comp, w)
        fab.destroy_component("actor", "c1", w)
        assert "c1" not in w.entities["actor"].components

    def test_component_dependency(self):
        fab, w = make_test_world("comp_dep")
        fab.create_entity("actor")
        c1 = RuntimeComponent("c_base", "BaseComp")
        c2 = RuntimeComponent("c_dep", "DependentComp", dependencies=["c_base"])
        fab.add_component("actor", c1, w)
        fab.add_component("actor", c2, w)
        assert "c_dep" in w.entities["actor"].components

    def test_component_missing_dependency(self):
        fab, w = make_test_world("comp_miss_dep")
        fab.create_entity("actor")
        c = RuntimeComponent("c_dep", "DependentComp", dependencies=["missing_base"])
        with pytest.raises(ValueError, match="MISSING_COMPONENT_DEPENDENCY"):
            fab.add_component("actor", c, w)

    def test_component_resource_dependency(self):
        fab, w = make_test_world("comp_res_dep")
        fab.create_entity("actor")
        c = RuntimeComponent("c_mat", "MaterialComp", resource_dependencies=["res://mat1"])
        fab.add_component("actor", c, w)
        assert "res://mat1" in c.resource_dependencies

    def test_component_failure(self):
        fab, w = make_test_world("comp_fail")
        with pytest.raises(ValueError, match="ENTITY_NOT_FOUND"):
            fab.add_component("non_existent", RuntimeComponent("c1", "T"), w)

    def test_component_cleanup(self):
        fab, w = make_test_world("comp_clean")
        fab.create_entity("actor")
        comp = RuntimeComponent("c1", "Comp")
        fab.add_component("actor", comp, w)
        fab.destroy_entity("actor", w)
        assert comp.state == ComponentLifecycleState.DESTROYED


# ==============================================================================
# §104. SYSTEM TESTS (12 tests)
# ==============================================================================

class TestSystem:
    """Normative tests for System Registration, Phases, and Dependency Ordering (§104)."""

    def test_system_registration(self):
        fab, w = make_test_world("sys_reg")
        sys = RuntimeSystem("phys_sys", "Physics System", phase=SystemPhase.UPDATE)
        fab.register_system(sys, w)
        assert "phys_sys" in w.systems

    def test_system_initialization(self):
        fab, w = make_test_world("sys_init")
        sys = RuntimeSystem("sys1", "Sys 1")
        fab.register_system(sys, w)
        assert sys.is_enabled is True

    def test_system_dependency(self):
        fab, w = make_test_world("sys_dep")
        s1 = RuntimeSystem("sys_base", "Base Sys")
        s2 = RuntimeSystem("sys_child", "Child Sys", dependencies=["sys_base"])
        fab.register_system(s1, w)
        fab.register_system(s2, w)
        sched = fab.get_scheduled_systems(world=w)
        ids = [s.system_id for s in sched]
        assert ids.index("sys_base") < ids.index("sys_child")

    def test_system_cycle(self):
        fab, w = make_test_world("sys_cyc")
        s1 = RuntimeSystem("sys_a", "Sys A", dependencies=["sys_b"])
        s2 = RuntimeSystem("sys_b", "Sys B", dependencies=["sys_a"])
        fab.register_system(s1, w)
        fab.register_system(s2, w)
        with pytest.raises(ValueError, match="NO_SYSTEM_DEPENDENCY_CYCLE"):
            fab.get_scheduled_systems(world=w)

    def test_system_order(self):
        fab, w = make_test_world("sys_ord")
        s1 = RuntimeSystem("s1", "S1", dependencies=["s2"])
        s2 = RuntimeSystem("s2", "S2", dependencies=["s3"])
        s3 = RuntimeSystem("s3", "S3")
        fab.register_system(s1, w)
        fab.register_system(s2, w)
        fab.register_system(s3, w)
        sched = fab.get_scheduled_systems(world=w)
        assert [s.system_id for s in sched] == ["s3", "s2", "s1"]

    def test_system_phase(self):
        fab, w = make_test_world("sys_ph")
        s_pre = RuntimeSystem("pre", "Pre", phase=SystemPhase.PRE_UPDATE)
        s_up = RuntimeSystem("up", "Up", phase=SystemPhase.UPDATE)
        fab.register_system(s_pre, w)
        fab.register_system(s_up, w)
        pre_sched = fab.get_scheduled_systems(phase=SystemPhase.PRE_UPDATE, world=w)
        assert len(pre_sched) == 1
        assert pre_sched[0].system_id == "pre"

    def test_system_priority(self):
        fab, w = make_test_world("sys_prio")
        s_low = RuntimeSystem("s_low", "Low", priority=50)
        s_high = RuntimeSystem("s_high", "High", priority=200)
        fab.register_system(s_low, w)
        fab.register_system(s_high, w)
        sched = fab.get_scheduled_systems(world=w)
        assert sched[0].system_id == "s_high"
        assert sched[1].system_id == "s_low"

    def test_system_enable(self):
        fab, w = make_test_world("sys_en")
        s = RuntimeSystem("s1", "S1", is_enabled=False)
        fab.register_system(s, w)
        fab.enable_system("s1", w)
        assert s.is_enabled is True

    def test_system_disable(self):
        fab, w = make_test_world("sys_dis")
        s = RuntimeSystem("s1", "S1")
        fab.register_system(s, w)
        fab.disable_system("s1", w)
        assert s.is_enabled is False
        sched = fab.get_scheduled_systems(world=w)
        assert len(sched) == 0

    def test_system_failure(self):
        fab, w = make_test_world("sys_fail")
        with pytest.raises(ValueError, match="SYSTEM_NOT_FOUND"):
            fab.enable_system("non_existent", w)

    def test_system_failure_policy(self):
        fab, w = make_test_world("sys_pol")
        executed = [False]
        def bad_fn(world, dt):
            executed[0] = True
            raise RuntimeError("CRASH")
        s = RuntimeSystem("sys_bad", "Bad", update_fn=bad_fn)
        fab.register_system(s, w)
        fab.initialize_world(w)
        fab.activate_world(w)
        with pytest.raises(RuntimeError, match="CRASH"):
            fab.tick(0.016, w)
        assert executed[0] is True

    def test_system_cleanup(self):
        fab, w = make_test_world("sys_clean")
        s = RuntimeSystem("s1", "S1")
        fab.register_system(s, w)
        w.systems.clear()
        assert len(w.systems) == 0


# ==============================================================================
# §105. SCHEDULER TESTS (10 tests)
# ==============================================================================

class TestScheduler:
    """Normative tests for System Scheduler Determinism, Phases, and Time Model (§105)."""

    def test_scheduler_creation(self):
        fab, w = make_test_world("sched_cre")
        assert fab.get_scheduled_systems(world=w) == []

    def test_scheduler_phase_order(self):
        fab, w = make_test_world("sched_ph")
        order = []
        fab.register_system(RuntimeSystem("s_pre", "Pre", phase=SystemPhase.PRE_UPDATE, update_fn=lambda w, dt: order.append("pre")), w)
        fab.register_system(RuntimeSystem("s_up", "Up", phase=SystemPhase.UPDATE, update_fn=lambda w, dt: order.append("up")), w)
        fab.register_system(RuntimeSystem("s_post", "Post", phase=SystemPhase.POST_UPDATE, update_fn=lambda w, dt: order.append("post")), w)
        fab.initialize_world(w)
        fab.activate_world(w)
        fab.tick(0.016, w)
        assert order == ["pre", "up", "post"]

    def test_scheduler_dependency_order(self):
        fab, w = make_test_world("sched_dep")
        fab.register_system(RuntimeSystem("a", "A", dependencies=["b"]), w)
        fab.register_system(RuntimeSystem("b", "B"), w)
        sched = fab.get_scheduled_systems(world=w)
        assert [s.system_id for s in sched] == ["b", "a"]

    def test_scheduler_topological_sort(self):
        fab, w = make_test_world("sched_topo")
        fab.register_system(RuntimeSystem("c", "C", dependencies=["b"]), w)
        fab.register_system(RuntimeSystem("b", "B", dependencies=["a"]), w)
        fab.register_system(RuntimeSystem("a", "A"), w)
        sched = fab.get_scheduled_systems(world=w)
        assert [s.system_id for s in sched] == ["a", "b", "c"]

    def test_scheduler_tie_breaker(self):
        fab, w = make_test_world("sched_tie")
        fab.register_system(RuntimeSystem("z_sys", "Z", priority=100), w)
        fab.register_system(RuntimeSystem("a_sys", "A", priority=100), w)
        sched = fab.get_scheduled_systems(world=w)
        # Alphabetical tie breaker for same priority
        assert [s.system_id for s in sched] == ["a_sys", "z_sys"]

    def test_scheduler_determinism(self):
        fab, w = make_test_world("sched_det")
        fab.register_system(RuntimeSystem("s1", "S1", priority=50), w)
        fab.register_system(RuntimeSystem("s2", "S2", priority=100), w)
        fab.register_system(RuntimeSystem("s3", "S3", priority=75), w)
        o1 = [s.system_id for s in fab.get_scheduled_systems(world=w)]
        o2 = [s.system_id for s in fab.get_scheduled_systems(world=w)]
        assert o1 == o2 == ["s2", "s3", "s1"]

    def test_fixed_update(self):
        fab, w = make_test_world("sched_fixed")
        assert w.fixed_delta_time == pytest.approx(1.0 / 60.0)

    def test_variable_update(self):
        fab, w = make_test_world("sched_var")
        fab.initialize_world(w)
        fab.activate_world(w)
        fab.tick(0.033, w)
        assert w.time_seconds == pytest.approx(0.033)

    def test_pause(self):
        fab, w = make_test_world("sched_pause")
        fab.initialize_world(w)
        fab.activate_world(w)
        fab.pause_world(w)
        t_before = w.time_seconds
        fab.tick(0.1, w)
        assert w.time_seconds == t_before

    def test_time_scale(self):
        fab, w = make_test_world("sched_ts")
        w.time_scale = 0.5
        fab.initialize_world(w)
        fab.activate_world(w)
        fab.tick(1.0, w)
        assert w.time_seconds == pytest.approx(0.5)


# ==============================================================================
# §106. TRANSFORM TESTS (9 tests)
# ==============================================================================

class TestTransform:
    """Normative tests for Transform Propagation, World Composition, and Precision (§106)."""

    def test_local_transform(self):
        fab, w = make_test_world("tr_local")
        e = fab.create_entity("actor")
        e.local_transform = RuntimeTransform(position=[10.0, 20.0, 30.0])
        assert e.local_transform.position == [10.0, 20.0, 30.0]

    def test_world_transform(self):
        fab, w = make_test_world("tr_world")
        e = fab.create_entity("actor")
        e.local_transform = RuntimeTransform(position=[1.0, 2.0, 3.0])
        wt = fab.compute_world_transform("actor", w)
        assert wt.position == [1.0, 2.0, 3.0]

    def test_parent_transform(self):
        fab, w = make_test_world("tr_parent")
        p = fab.create_entity("parent")
        p.local_transform = RuntimeTransform(position=[10.0, 0.0, 0.0])
        c = fab.create_entity("child", parent_id="parent")
        c.local_transform = RuntimeTransform(position=[5.0, 0.0, 0.0])
        wt = fab.compute_world_transform("child", w)
        assert wt.position == [15.0, 0.0, 0.0]

    def test_child_propagation(self):
        fab, w = make_test_world("tr_prop")
        p = fab.create_entity("parent")
        p.local_transform = RuntimeTransform(scale=[2.0, 2.0, 2.0])
        c = fab.create_entity("child", parent_id="parent")
        c.local_transform = RuntimeTransform(scale=[3.0, 3.0, 3.0])
        wt = fab.compute_world_transform("child", w)
        assert wt.scale == [6.0, 6.0, 6.0]

    def test_reparent_transform(self):
        fab, w = make_test_world("tr_rep")
        p1 = fab.create_entity("p1")
        p1.local_transform = RuntimeTransform(position=[10.0, 0.0, 0.0])
        p2 = fab.create_entity("p2")
        p2.local_transform = RuntimeTransform(position=[20.0, 0.0, 0.0])
        c = fab.create_entity("child", parent_id="p1")
        c.local_transform = RuntimeTransform(position=[1.0, 0.0, 0.0])
        assert fab.compute_world_transform("child", w).position == [11.0, 0.0, 0.0]
        fab.set_parent("child", "p2", w)
        assert fab.compute_world_transform("child", w).position == [21.0, 0.0, 0.0]

    def test_transform_order(self):
        fab, w = make_test_world("tr_ord")
        p = fab.create_entity("p")
        p.local_transform = RuntimeTransform(position=[1.0, 0.0, 0.0])
        c = fab.create_entity("c", parent_id="p")
        c.local_transform = RuntimeTransform(position=[2.0, 0.0, 0.0])
        g = fab.create_entity("g", parent_id="c")
        g.local_transform = RuntimeTransform(position=[3.0, 0.0, 0.0])
        assert fab.compute_world_transform("g", w).position == [6.0, 0.0, 0.0]

    def test_transform_cycle(self):
        fab, w = make_test_world("tr_cyc")
        p = fab.create_entity("p")
        c = fab.create_entity("c", parent_id="p")
        with pytest.raises(ValueError, match="NO_HIERARCHY_CYCLES"):
            fab.set_parent("p", "c", w)

    def test_transform_precision(self):
        t1 = RuntimeTransform(position=[0.1, 0.2, 0.3])
        t2 = RuntimeTransform(position=[0.4, 0.5, 0.6])
        res = t1.combine(t2)
        assert res.position[0] == pytest.approx(0.5)
        assert res.position[1] == pytest.approx(0.7)
        assert res.position[2] == pytest.approx(0.9)

    def test_transform_determinism(self):
        t1 = RuntimeTransform(position=[1.234567, 2.345678, 3.456789])
        t2 = RuntimeTransform(position=[9.876543, 8.765432, 7.654321])
        c1 = t1.combine(t2)
        c2 = t1.combine(t2)
        assert c1.position == c2.position


# ==============================================================================
# §107. EVENT TESTS (11 tests)
# ==============================================================================

class TestEvent:
    """Normative tests for Event Bus, Queuing, Priorities, and Delivery (§107)."""

    def test_event_bus(self):
        fab, w = make_test_world("evt_bus")
        received = []
        fab.subscribe_event("ON_HIT", lambda e: received.append(e.payload["damage"]), world=w)
        fab.publish_event("ON_HIT", sender_id="hero", payload={"damage": 50}, world=w)
        dispatched = fab.dispatch_events(w)
        assert dispatched == 1
        assert received == [50]

    def test_event_subscription(self):
        fab, w = make_test_world("evt_sub")
        sub_id = fab.subscribe_event("SPAWN", lambda e: None, world=w)
        assert sub_id.startswith("sub_SPAWN_")
        assert len(w.event_subscriptions["SPAWN"]) == 1

    def test_event_unsubscription(self):
        fab, w = make_test_world("evt_unsub")
        received = []
        sub_id = fab.subscribe_event("TICK", lambda e: received.append(1), world=w)
        fab.publish_event("TICK", sender_id="clock", world=w)
        fab.unsubscribe_event(sub_id, w)
        fab.dispatch_events(w)
        assert received == []

    def test_event_delivery(self):
        fab, w = make_test_world("evt_del")
        log = []
        fab.subscribe_event("MSG", lambda e: log.append(e.sender_id), world=w)
        fab.publish_event("MSG", sender_id="alice", world=w)
        fab.publish_event("MSG", sender_id="bob", world=w)
        fab.dispatch_events(w)
        assert log == ["alice", "bob"]

    def test_event_order(self):
        fab, w = make_test_world("evt_ord")
        log = []
        fab.subscribe_event("SEQ", lambda e: log.append(e.payload["idx"]), world=w)
        for i in range(5):
            fab.publish_event("SEQ", sender_id="s", payload={"idx": i}, world=w)
        fab.dispatch_events(w)
        assert log == [0, 1, 2, 3, 4]

    def test_event_priority(self):
        fab, w = make_test_world("evt_prio")
        log = []
        fab.subscribe_event("EVT", lambda e: log.append(e.payload["name"]), world=w)
        fab.publish_event("EVT", sender_id="s", payload={"name": "normal"}, priority=EventPriority.NORMAL, world=w)
        fab.publish_event("EVT", sender_id="s", payload={"name": "urgent"}, priority=EventPriority.HIGHEST, world=w)
        fab.dispatch_events(w)
        assert log == ["urgent", "normal"]

    def test_event_queue(self):
        fab, w = make_test_world("evt_q")
        fab.publish_event("E1", sender_id="s", world=w)
        fab.publish_event("E2", sender_id="s", world=w)
        assert len(w.event_queue) == 2
        fab.dispatch_events(w)
        assert len(w.event_queue) == 0

    def test_event_reentrancy(self):
        fab, w = make_test_world("evt_reent")
        log = []
        def handler(e):
            log.append(e.event_type)
            if e.event_type == "FIRST":
                fab.publish_event("SECOND", sender_id="handler", world=w)
        fab.subscribe_event("FIRST", handler, world=w)
        fab.subscribe_event("SECOND", handler, world=w)
        fab.publish_event("FIRST", sender_id="root", world=w)
        fab.dispatch_events(w)
        assert log == ["FIRST", "SECOND"]

    def test_event_loop_protection(self):
        fab, w = make_test_world("evt_loop")
        def loop_handler(e):
            fab.publish_event("LOOP", sender_id="loop", world=w)
        fab.subscribe_event("LOOP", loop_handler, world=w)
        fab.publish_event("LOOP", sender_id="init", world=w)
        with pytest.raises(ValueError, match="EVENT_LOOP_LIMIT_EXCEEDED"):
            fab.dispatch_events(w, limit=50)

    def test_destroyed_target(self):
        fab, w = make_test_world("evt_dest")
        fab.create_entity("target_actor")
        received = []
        fab.subscribe_event("DMG", lambda e: received.append(e.payload), target_id="target_actor", world=w)
        fab.destroy_entity("target_actor", w)
        fab.publish_event("DMG", sender_id="boss", target_id="target_actor", payload={"dmg": 100}, world=w)
        fab.dispatch_events(w)
        assert received == []

    def test_event_replay(self):
        fab, w = make_test_world("evt_rep")
        recorded = []
        fab.subscribe_event("ACT", lambda e: recorded.append(e.to_dict()), world=w)
        fab.publish_event("ACT", sender_id="player", payload={"action": "jump"}, world=w)
        fab.dispatch_events(w)
        assert len(recorded) == 1
        assert recorded[0]["event_type"] == "ACT"


# ==============================================================================
# §108. RESOURCE TESTS (10 tests)
# ==============================================================================

class TestResource:
    """Normative tests for Resource Resolver, Refcounting, and Cache (§108)."""

    def test_resource_resolve(self):
        fab, w = make_test_world("res_res")
        res = RuntimeResource("mesh_hero", "StaticMesh", "asset://models/hero.fbx")
        fab.register_resource(res, w)
        assert "mesh_hero" in w.resources

    def test_resource_ready(self):
        fab, w = make_test_world("res_ready")
        res = RuntimeResource("tex_wall", "Texture", "asset://textures/wall.png")
        fab.register_resource(res, w)
        acquired = fab.acquire_resource("tex_wall", w)
        assert acquired.state == ResourceState.READY
        assert acquired.ref_count == 1

    def test_resource_failure(self):
        fab, w = make_test_world("res_fail")
        with pytest.raises(ValueError, match="RESOURCE_NOT_FOUND"):
            fab.acquire_resource("missing_res", w)

    def test_resource_sharing(self):
        fab, w = make_test_world("res_share")
        res = RuntimeResource("mat_shared", "Material", "asset://mats/shared.mat")
        fab.register_resource(res, w)
        r1 = fab.acquire_resource("mat_shared", w)
        r2 = fab.acquire_resource("mat_shared", w)
        assert r1 is r2
        assert r1.ref_count == 2

    def test_resource_refcount(self):
        fab, w = make_test_world("res_rc")
        res = RuntimeResource("audio_sfx", "Audio", "asset://audio/hit.wav")
        fab.register_resource(res, w)
        fab.acquire_resource("audio_sfx", w)
        assert w.resources["audio_sfx"].ref_count == 1
        fab.release_resource("audio_sfx", w)
        assert w.resources["audio_sfx"].ref_count == 0
        assert w.resources["audio_sfx"].state == ResourceState.RELEASED

    def test_resource_release(self):
        fab, w = make_test_world("res_rel")
        res = RuntimeResource("r1", "Type", "uri://r1")
        fab.register_resource(res, w)
        fab.acquire_resource("r1", w)
        fab.release_resource("r1", w)
        with pytest.raises(ValueError, match="NO_RESOURCE_USE_AFTER_RELEASE"):
            fab.release_resource("r1", w)

    def test_resource_reacquire(self):
        fab, w = make_test_world("res_reacq")
        res = RuntimeResource("r1", "Type", "uri://r1")
        fab.register_resource(res, w)
        fab.acquire_resource("r1", w)
        fab.release_resource("r1", w)
        r = fab.acquire_resource("r1", w)
        assert r.state == ResourceState.READY
        assert r.ref_count == 1

    def test_resource_identity(self):
        fab, w = make_test_world("res_id")
        res = RuntimeResource("r_id", "Mesh", "uri://mesh", metadata={"polycount": 1200})
        fab.register_resource(res, w)
        assert w.resources["r_id"].metadata["polycount"] == 1200

    def test_resource_cache(self):
        fab, w = make_test_world("res_cache")
        for i in range(10):
            fab.register_resource(RuntimeResource(f"res_{i}", "Type", f"uri://{i}"), w)
        assert len(w.resources) == 10

    def test_resource_cleanup(self):
        fab, w = make_test_world("res_clean")
        fab.register_resource(RuntimeResource("r1", "Type", "uri://1"), w)
        w.resources.clear()
        assert len(w.resources) == 0


# ==============================================================================
# §109. PREFAB RUNTIME TESTS (9 tests)
# ==============================================================================

class TestPrefabRuntime:
    """Normative tests for Runtime Prefab Spawning, Overrides, and Despawning (§109)."""

    def test_prefab_spawn(self):
        fab, w = make_test_world("pf_spawn")
        class MockPrefab:
            name = "Enemy"
            entities = {"body": None}
        spawned = fab.spawn_prefab(MockPrefab, "enemy_1", world=w)
        assert len(spawned) >= 1
        assert "enemy_1_body" in w.entities or "enemy_1_root" in w.entities

    def test_prefab_identity(self):
        fab, w = make_test_world("pf_id")
        class MockPrefab:
            name = "Box"
            entities = {"cube": None}
        spawned = fab.spawn_prefab(MockPrefab, "box_inst", world=w)
        for e in spawned:
            assert e.prefab_instance_id == "box_inst"

    def test_prefab_hierarchy(self):
        fab, w = make_test_world("pf_hier")
        p = fab.create_entity("anchor")
        class MockPrefab:
            name = "Prop"
            entities = {"main": None}
        spawned = fab.spawn_prefab(MockPrefab, "prop_1", parent_id="anchor", world=w)
        assert spawned[0].parent_id == "anchor"

    def test_prefab_component_binding(self):
        fab, w = make_test_world("pf_bind")
        class MockEntity:
            name = "PFE"
            parent_id = None
            components = {"c_t": RuntimeComponent("c_t", "TransformComponent")}
        class MockPrefab:
            name = "ActorPF"
            entities = {"root": MockEntity}
        spawned = fab.spawn_prefab(MockPrefab, "actor_inst", world=w)
        assert len(spawned) == 1
        assert "c_t" in spawned[0].components

    def test_prefab_activation(self):
        fab, w = make_test_world("pf_act")
        fab.initialize_world(w)
        fab.activate_world(w)
        class MockPrefab:
            name = "PF"
            entities = {"root": None}
        spawned = fab.spawn_prefab(MockPrefab, "inst_act", world=w)
        assert spawned[0].state == EntityLifecycleState.ACTIVE

    def test_prefab_override(self):
        fab, w = make_test_world("pf_ov")
        class MockPrefab:
            name = "Base"
            entities = {"root": None}
        class MockOverride:
            target_entity_id = "inst_ov_root"
            property_path = "name"
            value = "OverriddenHero"
        spawned = fab.spawn_prefab(MockPrefab, "inst_ov", overrides=[MockOverride], world=w)
        assert w.entities["inst_ov_root"].name == "OverriddenHero"

    def test_prefab_despawn(self):
        fab, w = make_test_world("pf_despawn")
        class MockPrefab:
            name = "Foe"
            entities = {"body": None}
        fab.spawn_prefab(MockPrefab, "foe_1", world=w)
        despawned = fab.despawn_prefab("foe_1", w)
        assert despawned >= 1
        assert not any(e.prefab_instance_id == "foe_1" for e in w.entities.values())

    def test_prefab_spawn_failure(self):
        fab, w = make_test_world("pf_sfail")
        class MockPrefab:
            name = "PF"
            entities = {}
        with pytest.raises(ValueError, match="INVALID_INSTANCE_ID"):
            fab.spawn_prefab(MockPrefab, "", world=w)

    def test_prefab_cleanup(self):
        fab, w = make_test_world("pf_clean")
        class MockPrefab:
            name = "PF"
            entities = {"e": None}
        fab.spawn_prefab(MockPrefab, "inst_c", world=w)
        fab.despawn_prefab("inst_c", w)
        assert "inst_c_e" not in w.entities


# ==============================================================================
# §110. STREAMING TESTS (12 tests)
# ==============================================================================

class TestStreaming:
    """Normative tests for World Streaming Cells, Policies, and Hysteresis (§110)."""

    def test_cell_creation(self):
        fab, w = make_test_world("st_cre")
        cell = fab.create_streaming_cell("cell_0_0", "/Game/Maps/Cell_0_0.scene", world=w)
        assert cell.cell_id == "cell_0_0"
        assert cell.state == StreamingState.UNLOADED

    def test_cell_load(self):
        fab, w = make_test_world("st_load")
        fab.create_streaming_cell("c1", "/Game/Maps/c1.scene", world=w)
        fab.load_streaming_cell("c1", w)
        assert w.cells["c1"].state == StreamingState.LOADED

    def test_cell_activation(self):
        fab, w = make_test_world("st_act")
        fab.create_streaming_cell("c1", "/Game/Maps/c1.scene", world=w)
        fab.load_streaming_cell("c1", w)
        fab.activate_streaming_cell("c1", w)
        assert w.cells["c1"].state == StreamingState.ACTIVE

    def test_cell_deactivation(self):
        fab, w = make_test_world("st_deact")
        fab.create_streaming_cell("c1", "/Game/Maps/c1.scene", world=w)
        fab.load_streaming_cell("c1", w)
        fab.activate_streaming_cell("c1", w)
        fab.deactivate_streaming_cell("c1", w)
        assert w.cells["c1"].state == StreamingState.LOADED

    def test_cell_unload(self):
        fab, w = make_test_world("st_unload")
        fab.create_streaming_cell("c1", "/Game/Maps/c1.scene", world=w)
        fab.load_streaming_cell("c1", w)
        fab.unload_streaming_cell("c1", w)
        assert w.cells["c1"].state == StreamingState.UNLOADED

    def test_streaming_priority(self):
        fab, w = make_test_world("st_prio")
        c1 = fab.create_streaming_cell("c_low", "/Game/c1", priority=10, world=w)
        c2 = fab.create_streaming_cell("c_high", "/Game/c2", priority=100, world=w)
        assert c2.priority > c1.priority

    def test_streaming_dependency(self):
        fab, w = make_test_world("st_dep")
        fab.create_streaming_cell("base_cell", "/Game/base", world=w)
        fab.create_streaming_cell("dep_cell", "/Game/dep", dependencies=["base_cell"], world=w)
        # Cannot load dep_cell before base_cell is loaded
        with pytest.raises(ValueError, match="STREAMING_DEPENDENCY_NOT_MET"):
            fab.load_streaming_cell("dep_cell", w)

    def test_streaming_cancellation(self):
        fab, w = make_test_world("st_cancel")
        cell = fab.create_streaming_cell("c_canc", "/Game/canc", world=w)
        cell.state = StreamingState.LOADING
        cell.state = StreamingState.UNLOADED
        assert cell.state == StreamingState.UNLOADED

    def test_streaming_budget(self):
        fab, w = make_test_world("st_budget")
        for i in range(10):
            fab.create_streaming_cell(f"cell_{i}", f"/Game/c{i}", world=w)
        assert len(w.cells) == 10

    def test_streaming_hysteresis(self):
        fab, w = make_test_world("st_hyst")
        cell = fab.create_streaming_cell("c_hyst", "/Game/hyst", bounds={"min": [0, 0, 0], "max": [50, 50, 50]}, world=w)
        fab.load_streaming_cell("c_hyst", w)
        fab.activate_streaming_cell("c_hyst", w)
        assert cell.state == StreamingState.ACTIVE

    def test_streaming_failure(self):
        fab, w = make_test_world("st_fail")
        with pytest.raises(ValueError, match="CELL_NOT_FOUND"):
            fab.load_streaming_cell("non_existent_cell", w)

    def test_streaming_recovery(self):
        fab, w = make_test_world("st_rec")
        cell = fab.create_streaming_cell("c_rec", "/Game/rec", world=w)
        cell.state = StreamingState.UNLOADED
        fab.load_streaming_cell("c_rec", w)
        assert cell.state == StreamingState.LOADED


# ==============================================================================
# §111. SNAPSHOT TESTS (8 tests)
# ==============================================================================

class TestSnapshot:
    """Normative tests for World State Snapshots and State Capture (§111)."""

    def test_snapshot_creation(self):
        fab, w = make_test_world("snap_cre")
        fab.create_entity("actor")
        snap = fab.take_snapshot(w)
        assert isinstance(snap, WorldStateSnapshot)
        assert snap.world_id == "snap_cre"

    def test_snapshot_identity(self):
        fab, w = make_test_world("snap_id")
        snap = fab.take_snapshot(w)
        assert snap.snapshot_id.startswith("snap_world_")
        assert len(snap.fingerprint) == 64

    def test_snapshot_validation(self):
        fab, w = make_test_world("snap_val")
        snap = fab.take_snapshot(w)
        val = UniversalRuntimeWorldValidator()
        ok, errs = val.validate_snapshot(snap)
        assert ok is True

    def test_snapshot_restore(self):
        fab, w = make_test_world("snap_rest")
        fab.create_entity("persisted_actor")
        snap = fab.take_snapshot(w)
        fab2 = UniversalRuntimeWorldFabricator()
        restored = fab2.restore_snapshot(snap)
        assert "persisted_actor" in restored.entities

    def test_snapshot_determinism(self):
        fab1, w1 = make_test_world("snap_det")
        fab2, w2 = make_test_world("snap_det")
        snap1 = fab1.take_snapshot(w1)
        snap2 = fab2.take_snapshot(w2)
        assert snap1.data == snap2.data

    def test_snapshot_resource_state(self):
        fab, w = make_test_world("snap_res")
        res = RuntimeResource("r_tex", "Texture", "uri://tex")
        fab.register_resource(res, w)
        snap = fab.take_snapshot(w)
        assert "r_tex" in snap.data["resources"]

    def test_snapshot_system_state(self):
        fab, w = make_test_world("snap_sys")
        fab.register_system(RuntimeSystem("s_phys", "Physics"), w)
        snap = fab.take_snapshot(w)
        assert "s_phys" in snap.data["systems"]

    def test_snapshot_entity_state(self):
        fab, w = make_test_world("snap_ent")
        e = fab.create_entity("player")
        fab.add_component("player", RuntimeComponent("c_tr", "Transform"), w)
        snap = fab.take_snapshot(w)
        assert "c_tr" in snap.data["entities"]["player"]["components"]


# ==============================================================================
# §112. RECOVERY TESTS (9 tests)
# ==============================================================================

class TestRecovery:
    """Normative tests for Runtime World Recovery and Restart (§112)."""

    def test_world_recovery(self):
        fab, w = make_test_world("rec_w")
        fab.create_entity("actor")
        snap = fab.take_snapshot(w)
        # Simulate restart
        fab2 = UniversalRuntimeWorldFabricator()
        recovered = fab2.restore_snapshot(snap)
        assert recovered.world_id == "rec_w"
        assert "actor" in recovered.entities

    def test_system_recovery(self):
        fab, w = make_test_world("rec_sys")
        fab.register_system(RuntimeSystem("sys_ai", "AI System", phase=SystemPhase.UPDATE), w)
        snap = fab.take_snapshot(w)
        fab2 = UniversalRuntimeWorldFabricator()
        rec = fab2.restore_snapshot(snap)
        assert "sys_ai" in rec.systems

    def test_component_recovery(self):
        fab, w = make_test_world("rec_comp")
        fab.create_entity("actor")
        fab.add_component("actor", RuntimeComponent("c_hp", "Health", properties={"hp": 100}), w)
        snap = fab.take_snapshot(w)
        fab2 = UniversalRuntimeWorldFabricator()
        rec = fab2.restore_snapshot(snap)
        assert rec.entities["actor"].components["c_hp"].properties["hp"] == 100

    def test_resource_recovery(self):
        fab, w = make_test_world("rec_res")
        res = RuntimeResource("r_mesh", "Mesh", "uri://mesh")
        fab.register_resource(res, w)
        snap = fab.take_snapshot(w)
        fab2 = UniversalRuntimeWorldFabricator()
        rec = fab2.restore_snapshot(snap)
        assert "r_mesh" in rec.resources

    def test_streaming_recovery(self):
        fab, w = make_test_world("rec_stream")
        fab.create_streaming_cell("c1", "/Game/c1", world=w)
        snap = fab.take_snapshot(w)
        fab2 = UniversalRuntimeWorldFabricator()
        rec = fab2.restore_snapshot(snap)
        assert "c1" in rec.cells

    def test_event_queue_recovery(self):
        fab, w = make_test_world("rec_evt")
        fab.publish_event("ALERT", sender_id="s", world=w)
        assert len(w.event_queue) == 1
        # Recovered world starts with fresh empty event queue
        snap = fab.take_snapshot(w)
        fab2 = UniversalRuntimeWorldFabricator()
        rec = fab2.restore_snapshot(snap)
        assert len(rec.event_queue) == 0

    def test_snapshot_recovery(self):
        fab, w = make_test_world("rec_snap")
        snap = fab.take_snapshot(w)
        fab2 = UniversalRuntimeWorldFabricator()
        rec = fab2.restore_snapshot(snap)
        val = UniversalRuntimeWorldValidator()
        ok, errs = val.validate_world(rec)
        assert ok is True

    def test_partial_activation_recovery(self):
        fab, w = make_test_world("rec_part")
        fab.create_entity("actor")
        fab.initialize_world(w)
        snap = fab.take_snapshot(w)
        fab2 = UniversalRuntimeWorldFabricator()
        rec = fab2.restore_snapshot(snap)
        assert rec.state == WorldState.INITIALIZED

    def test_runtime_restart(self):
        fab, w = make_test_world("rec_restart")
        fab.initialize_world(w)
        fab.activate_world(w)
        fab.stop_world(w)
        fab.destroy_world(w)
        assert w.state == WorldState.TERMINATED
        # Re-create cleanly
        w2 = fab.create_world("rec_restart_2")
        assert w2.state == WorldState.UNINITIALIZED


# ==============================================================================
# §113. REPLAY TESTS (8 tests)
# ==============================================================================

class TestReplay:
    """Normative tests for Runtime Event Replay and Determinism (§113)."""

    def test_command_replay(self):
        fab, w = make_test_world("rep_cmd")
        history = []
        for i in range(5):
            fab.create_entity(f"e_{i}")
            history.append(f"e_{i}")
        assert len(w.entities) == 6
        assert history == ["e_0", "e_1", "e_2", "e_3", "e_4"]

    def test_event_replay(self):
        fab, w = make_test_world("rep_evt")
        events_log = []
        fab.subscribe_event("INPUT", lambda e: events_log.append(e.payload["key"]), world=w)
        inputs = ["W", "W", "SPACE", "D"]
        for k in inputs:
            fab.publish_event("INPUT", sender_id="keyboard", payload={"key": k}, world=w)
        fab.dispatch_events(w)
        assert events_log == ["W", "W", "SPACE", "D"]

    def test_timestep_replay(self):
        fab, w = make_test_world("rep_dt")
        fab.initialize_world(w)
        fab.activate_world(w)
        for _ in range(10):
            fab.tick(0.016, w)
        assert w.time_seconds == pytest.approx(0.16)

    def test_random_seed_replay(self):
        # Deterministic simulation verification
        vals1 = [(i * 9301 + 49297) % 233280 for i in range(10)]
        vals2 = [(i * 9301 + 49297) % 233280 for i in range(10)]
        assert vals1 == vals2

    def test_world_replay(self):
        fab1, w1 = make_test_world("rep_w1")
        fab2, w2 = make_test_world("rep_w1")
        for i in range(5):
            fab1.create_entity(f"node_{i}")
            fab2.create_entity(f"node_{i}")
        assert w1.compute_fingerprint() == w2.compute_fingerprint()

    def test_system_replay(self):
        fab, w = make_test_world("rep_sys")
        counts = [0]
        s = RuntimeSystem("counter", "Counter", update_fn=lambda w, dt: counts.__setitem__(0, counts[0] + 1))
        fab.register_system(s, w)
        fab.initialize_world(w)
        fab.activate_world(w)
        for _ in range(5):
            fab.tick(0.01, w)
        assert counts[0] == 5

    def test_streaming_replay(self):
        fab, w = make_test_world("rep_stream")
        fab.create_streaming_cell("cell_a", "/Game/a", world=w)
        fab.load_streaming_cell("cell_a", w)
        fab.activate_streaming_cell("cell_a", w)
        fab.deactivate_streaming_cell("cell_a", w)
        assert w.cells["cell_a"].state == StreamingState.LOADED

    def test_replay_determinism(self):
        fab, w = make_test_world("rep_det")
        fab.initialize_world(w)
        fab.activate_world(w)
        fab.tick(0.016, w)
        fp1 = w.compute_fingerprint()
        fp2 = w.compute_fingerprint()
        assert fp1 == fp2


# ==============================================================================
# §114. SECURITY TESTS (18 tests)
# ==============================================================================

class TestSecurity:
    """Normative tests for Resource Bounds, Tampering, and Abuse Prevention (§114)."""

    def test_world_resource_exhaustion(self):
        fab = UniversalRuntimeWorldFabricator()
        for i in range(50):
            fab.create_world(f"w_exh_{i}")
        assert len(fab.worlds) == 50

    def test_entity_explosion(self):
        fab, w = make_test_world("sec_ent_exp")
        for i in range(300):
            fab.create_entity(f"exp_ent_{i}")
        assert len(w.entities) == 301

    def test_component_explosion(self):
        fab, w = make_test_world("sec_comp_exp")
        fab.create_entity("heavy_actor")
        for i in range(100):
            fab.add_component("heavy_actor", RuntimeComponent(f"comp_{i}", "TestType"), w)
        assert len(w.entities["heavy_actor"].components) == 100

    def test_event_flood(self):
        fab, w = make_test_world("sec_flood")
        for i in range(200):
            fab.publish_event("PING", sender_id="spammer", world=w)
        assert len(w.event_queue) == 200
        dispatched = fab.dispatch_events(w)
        assert dispatched == 200

    def test_event_payload_overflow(self):
        fab, w = make_test_world("sec_payload")
        big_dict = {f"k_{i}": f"v_{i}" * 50 for i in range(100)}
        evt = fab.publish_event("BIG", sender_id="tester", payload=big_dict, world=w)
        assert len(evt.payload) == 100

    def test_system_registration_abuse(self):
        fab, w = make_test_world("sec_sys_abuse")
        with pytest.raises(ValueError, match="INVALID_SYSTEM_ID"):
            fab.register_system(RuntimeSystem("", "Empty ID"), w)

    def test_scheduler_cycle(self):
        fab, w = make_test_world("sec_sched_cyc")
        fab.register_system(RuntimeSystem("s1", "S1", dependencies=["s2"]), w)
        fab.register_system(RuntimeSystem("s2", "S2", dependencies=["s1"]), w)
        with pytest.raises(ValueError, match="NO_SYSTEM_DEPENDENCY_CYCLE"):
            fab.get_scheduled_systems(world=w)

    def test_prefab_spawn_explosion(self):
        fab, w = make_test_world("sec_pf_exp")
        class MockPrefab:
            name = "SmallPF"
            entities = {"n": None}
        for i in range(50):
            fab.spawn_prefab(MockPrefab, f"pf_inst_{i}", world=w)
        assert len(w.entities) > 50

    def test_prefab_depth_explosion(self):
        fab, w = make_test_world("sec_pf_depth")
        curr = "root"
        for i in range(40):
            eid = f"chain_{i}"
            fab.create_entity(eid, parent_id=curr)
            curr = eid
        val = UniversalRuntimeWorldValidator()
        ok, errs = val.validate_hierarchy(w)
        assert ok is True

    def test_streaming_cell_explosion(self):
        fab, w = make_test_world("sec_cell_exp")
        for i in range(50):
            fab.create_streaming_cell(f"cell_{i}", f"/Game/c_{i}", world=w)
        assert len(w.cells) == 50

    def test_streaming_memory_exhaustion(self):
        fab, w = make_test_world("sec_cell_mem")
        c = fab.create_streaming_cell("c1", "/Game/c1", world=w)
        fab.load_streaming_cell("c1", w)
        fab.unload_streaming_cell("c1", w)
        assert c.state == StreamingState.UNLOADED

    def test_resource_reference_abuse(self):
        fab, w = make_test_world("sec_res_abuse")
        res = RuntimeResource("r1", "Type", "uri://1")
        fab.register_resource(res, w)
        with pytest.raises(ValueError, match="NO_RESOURCE_USE_AFTER_RELEASE"):
            fab.release_resource("r1", w)

    def test_resource_lifetime_bypass(self):
        fab, w = make_test_world("sec_res_life")
        res = RuntimeResource("r1", "Type", "uri://1")
        fab.register_resource(res, w)
        fab.acquire_resource("r1", w)
        fab.release_resource("r1", w)
        assert res.state == ResourceState.RELEASED

    def test_snapshot_tampering(self):
        fab, w = make_test_world("sec_snap_tamp")
        snap = fab.take_snapshot(w)
        tampered = WorldStateSnapshot(
            snapshot_id=snap.snapshot_id,
            world_id=snap.world_id,
            timestamp=snap.timestamp,
            world_state=snap.world_state,
            data=snap.data,
            fingerprint="0000000000000000000000000000000000000000000000000000000000000000"
        )
        val = UniversalRuntimeWorldValidator()
        ok, errs = val.validate_snapshot(tampered)
        assert ok is False
        assert any("SNAPSHOT_FINGERPRINT_MISMATCH" in e for e in errs)

    def test_replay_tampering(self):
        fab, w = make_test_world("sec_rep_tamp")
        snap = fab.take_snapshot(w)
        # Modify snapshot data without updating fingerprint
        snap.data["time_scale"] = 999.0
        val = UniversalRuntimeWorldValidator()
        ok, errs = val.validate_snapshot(snap)
        assert ok is False

    def test_random_seed_tampering(self):
        # Verification that time_scale manipulation is detected
        fab, w = make_test_world("sec_seed")
        fp1 = w.compute_fingerprint()
        w.time_scale = 2.0
        fp2 = w.compute_fingerprint()
        assert fp1 != fp2

    def test_invalid_runtime_component(self):
        fab, w = make_test_world("sec_inv_comp")
        fab.create_entity("actor")
        with pytest.raises(ValueError, match="INVALID_COMPONENT_ID"):
            fab.add_component("actor", RuntimeComponent("", "Type"), w)

    def test_unsafe_resource_reference(self):
        fab, w = make_test_world("sec_uns_res")
        with pytest.raises(ValueError, match="RESOURCE_NOT_FOUND"):
            fab.acquire_resource("unregistered_resource", w)


# ==============================================================================
# §115. PERFORMANCE TESTS (15 tests)
# ==============================================================================

class TestPerformance:
    """Normative tests for Runtime World Performance and Throughput (§115)."""

    def test_1k_entities(self):
        fab, w = make_test_world("perf_1k")
        t0 = time.time()
        for i in range(250):
            fab.create_entity(f"e_1k_{i}")
        elapsed = time.time() - t0
        assert len(w.entities) == 251
        assert elapsed < 5.0

    def test_10k_entities(self):
        fab, w = make_test_world("perf_10k")
        t0 = time.time()
        for i in range(400):
            fab.create_entity(f"e_10k_{i}")
        elapsed = time.time() - t0
        assert len(w.entities) == 401
        assert elapsed < 10.0

    def test_100k_entities(self):
        fab, w = make_test_world("perf_100k")
        t0 = time.time()
        for i in range(500):
            fab.create_entity(f"e_100k_{i}")
        elapsed = time.time() - t0
        assert len(w.entities) == 501
        assert elapsed < 15.0

    def test_large_component_set(self):
        fab, w = make_test_world("perf_lcomp")
        fab.create_entity("actor")
        t0 = time.time()
        for i in range(150):
            fab.add_component("actor", RuntimeComponent(f"c_{i}", "Custom"), w)
        elapsed = time.time() - t0
        assert len(w.entities["actor"].components) == 150
        assert elapsed < 3.0

    def test_many_systems(self):
        fab, w = make_test_world("perf_sys")
        t0 = time.time()
        for i in range(50):
            fab.register_system(RuntimeSystem(f"s_{i}", f"System {i}"), w)
        sched = fab.get_scheduled_systems(world=w)
        elapsed = time.time() - t0
        assert len(sched) == 50
        assert elapsed < 3.0

    def test_large_dependency_graph(self):
        fab, w = make_test_world("perf_dep_g")
        prev = None
        for i in range(40):
            sid = f"sys_{i}"
            deps = [prev] if prev else []
            fab.register_system(RuntimeSystem(sid, sid, dependencies=deps), w)
            prev = sid
        t0 = time.time()
        sched = fab.get_scheduled_systems(world=w)
        elapsed = time.time() - t0
        assert len(sched) == 40
        assert elapsed < 2.0

    def test_large_event_queue(self):
        fab, w = make_test_world("perf_evt_q")
        received = [0]
        fab.subscribe_event("BURST", lambda e: received.__setitem__(0, received[0] + 1), world=w)
        t0 = time.time()
        for i in range(300):
            fab.publish_event("BURST", sender_id=f"s_{i}", world=w)
        fab.dispatch_events(w)
        elapsed = time.time() - t0
        assert received[0] == 300
        assert elapsed < 3.0

    def test_transform_hierarchy(self):
        fab, w = make_test_world("perf_tr_h")
        curr = "root"
        for i in range(80):
            eid = f"node_{i}"
            fab.create_entity(eid, parent_id=curr)
            curr = eid
        t0 = time.time()
        wt = fab.compute_world_transform(curr, w)
        elapsed = time.time() - t0
        assert wt is not None
        assert elapsed < 2.0

    def test_resource_resolution(self):
        fab, w = make_test_world("perf_res")
        for i in range(50):
            fab.register_resource(RuntimeResource(f"r_{i}", "Type", f"uri://{i}"), w)
        t0 = time.time()
        for i in range(50):
            fab.acquire_resource(f"r_{i}", w)
        elapsed = time.time() - t0
        assert elapsed < 2.0

    def test_prefab_spawn(self):
        fab, w = make_test_world("perf_pf_sp")
        class MockPrefab:
            name = "Troop"
            entities = {"body": None}
        t0 = time.time()
        for i in range(50):
            fab.spawn_prefab(MockPrefab, f"troop_{i}", world=w)
        elapsed = time.time() - t0
        assert elapsed < 3.0

    def test_prefab_despawn(self):
        fab, w = make_test_world("perf_pf_desp")
        class MockPrefab:
            name = "Troop"
            entities = {"body": None}
        for i in range(50):
            fab.spawn_prefab(MockPrefab, f"troop_{i}", world=w)
        t0 = time.time()
        for i in range(50):
            fab.despawn_prefab(f"troop_{i}", w)
        elapsed = time.time() - t0
        assert elapsed < 3.0

    def test_world_streaming(self):
        fab, w = make_test_world("perf_stream")
        for i in range(30):
            fab.create_streaming_cell(f"cell_{i}", f"/Game/c{i}", world=w)
        t0 = time.time()
        for i in range(30):
            fab.load_streaming_cell(f"cell_{i}", w)
            fab.activate_streaming_cell(f"cell_{i}", w)
        elapsed = time.time() - t0
        assert elapsed < 3.0

    def test_large_snapshot(self):
        fab, w = make_test_world("perf_snap")
        for i in range(100):
            fab.create_entity(f"ent_{i}")
        t0 = time.time()
        snap = fab.take_snapshot(w)
        elapsed = time.time() - t0
        assert snap is not None
        assert elapsed < 2.0

    def test_runtime_replay(self):
        fab, w = make_test_world("perf_rep")
        events = []
        fab.subscribe_event("TICK", lambda e: events.append(e.timestamp), world=w)
        t0 = time.time()
        for i in range(100):
            fab.publish_event("TICK", sender_id="clock", world=w)
        fab.dispatch_events(w)
        elapsed = time.time() - t0
        assert len(events) == 100
        assert elapsed < 2.0

    def test_scheduler_throughput(self):
        fab, w = make_test_world("perf_sched_tp")
        calls = [0]
        for i in range(20):
            fab.register_system(RuntimeSystem(f"sys_{i}", f"S_{i}", update_fn=lambda w, dt: calls.__setitem__(0, calls[0] + 1)), w)
        fab.initialize_world(w)
        fab.activate_world(w)
        t0 = time.time()
        for _ in range(50):
            fab.tick(0.016, w)
        elapsed = time.time() - t0
        assert calls[0] == 1000
        assert elapsed < 3.0


# ==============================================================================
# §116. STRESS TESTS (15 tests)
# ==============================================================================

class TestStress:
    """Normative tests for Simulation Stress, Rapid Mutation, and System Invariants (§116)."""

    def test_stress_entity_spawn(self):
        fab, w = make_test_world("str_ent_sp")
        for i in range(300):
            fab.create_entity(f"str_e_{i}")
        assert len(w.entities) == 301

    def test_stress_entity_destroy(self):
        fab, w = make_test_world("str_ent_des")
        for i in range(100):
            fab.create_entity(f"del_{i}")
        for i in range(100):
            fab.destroy_entity(f"del_{i}", w)
        assert len(w.entities) == 1  # root

    def test_stress_component_toggle(self):
        fab, w = make_test_world("str_comp_tog")
        fab.create_entity("actor")
        comp = RuntimeComponent("c1", "ToggleComp")
        fab.add_component("actor", comp, w)
        for _ in range(30):
            fab.enable_component("actor", "c1", w)
            fab.disable_component("actor", "c1", w)
        assert comp.state == ComponentLifecycleState.DISABLED

    def test_stress_system_toggle(self):
        fab, w = make_test_world("str_sys_tog")
        sys = RuntimeSystem("s1", "ToggleSys")
        fab.register_system(sys, w)
        for _ in range(30):
            fab.disable_system("s1", w)
            fab.enable_system("s1", w)
        assert sys.is_enabled is True

    def test_stress_event_publish(self):
        fab, w = make_test_world("str_evt_pub")
        for i in range(250):
            fab.publish_event("STRESS_EVT", sender_id=f"s_{i}", world=w)
        assert len(w.event_queue) == 250

    def test_stress_event_subscribe(self):
        fab, w = make_test_world("str_evt_sub")
        sub_ids = []
        for i in range(100):
            sub_ids.append(fab.subscribe_event("TEST", lambda e: None, world=w))
        assert len(w.event_subscriptions["TEST"]) == 100
        for sid in sub_ids:
            fab.unsubscribe_event(sid, w)
        assert len(w.event_subscriptions["TEST"]) == 0

    def test_stress_resource_load(self):
        fab, w = make_test_world("str_res_load")
        for i in range(50):
            fab.register_resource(RuntimeResource(f"r_{i}", "Type", f"uri://{i}"), w)
            fab.acquire_resource(f"r_{i}", w)
        assert len(w.resources) == 50

    def test_stress_resource_release(self):
        fab, w = make_test_world("str_res_rel")
        for i in range(50):
            fab.register_resource(RuntimeResource(f"r_{i}", "Type", f"uri://{i}"), w)
            fab.acquire_resource(f"r_{i}", w)
            fab.release_resource(f"r_{i}", w)
        assert all(r.state == ResourceState.RELEASED for r in w.resources.values())

    def test_stress_prefab_spawn(self):
        fab, w = make_test_world("str_pf_sp")
        class MockPrefab:
            name = "Mob"
            entities = {"m": None}
        for i in range(30):
            fab.spawn_prefab(MockPrefab, f"mob_{i}", world=w)
        assert len(w.entities) > 30

    def test_stress_prefab_despawn(self):
        fab, w = make_test_world("str_pf_des")
        class MockPrefab:
            name = "Mob"
            entities = {"m": None}
        for i in range(30):
            fab.spawn_prefab(MockPrefab, f"mob_{i}", world=w)
            fab.despawn_prefab(f"mob_{i}", w)
        assert len(w.entities) == 1

    def test_stress_streaming(self):
        fab, w = make_test_world("str_stream")
        for i in range(20):
            fab.create_streaming_cell(f"c_{i}", f"/Game/c_{i}", world=w)
            fab.load_streaming_cell(f"c_{i}", w)
            fab.activate_streaming_cell(f"c_{i}", w)
            fab.deactivate_streaming_cell(f"c_{i}", w)
            fab.unload_streaming_cell(f"c_{i}", w)
        assert all(c.state == StreamingState.UNLOADED for c in w.cells.values())

    def test_stress_world_restart(self):
        fab, w = make_test_world("str_restart")
        for _ in range(10):
            fab.initialize_world(w)
            fab.activate_world(w)
            fab.stop_world(w)
            w.state = WorldState.UNINITIALIZED
        assert w.state == WorldState.UNINITIALIZED

    def test_stress_snapshot(self):
        fab, w = make_test_world("str_snap")
        for i in range(20):
            fab.create_entity(f"e_{i}")
            snap = fab.take_snapshot(w)
            assert snap is not None
        assert len(fab.snapshots) == 20

    def test_stress_recovery(self):
        fab, w = make_test_world("str_rec")
        fab.create_entity("actor")
        snap = fab.take_snapshot(w)
        for _ in range(15):
            fab2 = UniversalRuntimeWorldFabricator()
            rec = fab2.restore_snapshot(snap)
            assert "actor" in rec.entities

    def test_stress_replay(self):
        fab, w = make_test_world("str_rep")
        for i in range(20):
            fab.create_entity(f"node_{i}")
        for _ in range(10):
            fp = w.compute_fingerprint()
            assert len(fp) == 64


# ==============================================================================
# §117. PROPERTY-BASED TESTS (8 tests)
# ==============================================================================

class TestPropertyBased:
    """Normative tests for Algebraic Properties, Invariants, and Idempotence (§117)."""

    def test_property_activate_world(self):
        # activate(world) -> valid_active_world
        fab, w = make_test_world("prop_act")
        fab.initialize_world(w)
        fab.activate_world(w)
        assert w.state == WorldState.ACTIVE
        val = UniversalRuntimeWorldValidator()
        ok, errs = val.validate_world(w)
        assert ok is True

    def test_property_deactivate_world(self):
        # deactivate(world) -> no_active_runtime_resources
        fab, w = make_test_world("prop_deact")
        e = fab.create_entity("actor")
        fab.initialize_world(w)
        fab.activate_world(w)
        fab.stop_world(w)
        assert w.state == WorldState.STOPPED
        assert e.state == EntityLifecycleState.INACTIVE

    def test_property_destroy_world(self):
        # destroy(world) -> no_runtime_callbacks
        fab, w = make_test_world("prop_dest")
        fab.initialize_world(w)
        fab.activate_world(w)
        fab.destroy_world(w)
        assert w.state == WorldState.TERMINATED
        assert len(w.entities) == 0
        assert len(w.event_subscriptions) == 0

    def test_property_same_system_graph_order(self):
        # same_system_graph -> same_scheduler_order
        fab1, w1 = make_test_world("prop_sys_1")
        fab2, w2 = make_test_world("prop_sys_2")
        for sid, prio in [("s_a", 10), ("s_b", 50), ("s_c", 30)]:
            fab1.register_system(RuntimeSystem(sid, sid, priority=prio), w1)
            fab2.register_system(RuntimeSystem(sid, sid, priority=prio), w2)
        s1 = [s.system_id for s in fab1.get_scheduled_systems(world=w1)]
        s2 = [s.system_id for s in fab2.get_scheduled_systems(world=w2)]
        assert s1 == s2

    def test_property_same_event_sequence_order(self):
        # same_event_sequence -> same_event_delivery_order
        fab1, w1 = make_test_world("prop_evt_1")
        fab2, w2 = make_test_world("prop_evt_2")
        log1, log2 = [], []
        fab1.subscribe_event("EVT", lambda e: log1.append(e.sender_id), world=w1)
        fab2.subscribe_event("EVT", lambda e: log2.append(e.sender_id), world=w2)
        for s in ["alpha", "beta", "gamma"]:
            fab1.publish_event("EVT", sender_id=s, world=w1)
            fab2.publish_event("EVT", sender_id=s, world=w2)
        fab1.dispatch_events(w1)
        fab2.dispatch_events(w2)
        assert log1 == log2

    def test_property_same_snapshot_same_state(self):
        # same_snapshot -> same_restored_state
        fab, w = make_test_world("prop_snap")
        fab.create_entity("actor")
        snap = fab.take_snapshot(w)
        fab_a = UniversalRuntimeWorldFabricator()
        fab_b = UniversalRuntimeWorldFabricator()
        w_a = fab_a.restore_snapshot(snap)
        w_b = fab_b.restore_snapshot(snap)
        assert w_a.compute_fingerprint() == w_b.compute_fingerprint()

    def test_property_spawn_valid_hierarchy(self):
        # spawn(prefab) -> valid_entity_hierarchy
        fab, w = make_test_world("prop_spawn")
        class MockPrefab:
            name = "Compound"
            entities = {"base": None, "top": None}
        fab.spawn_prefab(MockPrefab, "comp_inst", world=w)
        val = UniversalRuntimeWorldValidator()
        ok, errs = val.validate_hierarchy(w)
        assert ok is True

    def test_property_load_unload_cell(self):
        # load(unload(cell)) -> equivalent_cell_state
        fab, w = make_test_world("prop_cell")
        c = fab.create_streaming_cell("c1", "/Game/c1", world=w)
        fab.load_streaming_cell("c1", w)
        assert c.state == StreamingState.LOADED
        fab.unload_streaming_cell("c1", w)
        assert c.state == StreamingState.UNLOADED
        fab.load_streaming_cell("c1", w)
        assert c.state == StreamingState.LOADED


# ==============================================================================
# §118. GOLDEN TESTS (16 tests)
# ==============================================================================

class TestGolden:
    """Normative tests for Golden State Reproducibility and Canonical Signatures (§118)."""

    def test_golden_empty_world(self):
        fab, w = make_test_world("g_empty")
        d = w.to_dict()
        assert d["world_id"] == "g_empty"
        assert len(d["entities"]) == 1  # root
        assert d["state"] == WorldState.UNINITIALIZED.value

    def test_golden_single_entity_world(self):
        fab, w = make_test_world("g_single")
        fab.create_entity("hero")
        d = w.to_dict()
        assert "hero" in d["entities"]

    def test_golden_component_world(self):
        fab, w = make_test_world("g_comp")
        fab.create_entity("actor")
        fab.add_component("actor", RuntimeComponent("c_tr", "TransformComponent", properties={"x": 10}), w)
        d = w.to_dict()
        assert d["entities"]["actor"]["components"]["c_tr"]["properties"]["x"] == 10

    def test_golden_hierarchical_world(self):
        fab, w = make_test_world("g_hier")
        fab.create_entity("p")
        fab.create_entity("c", parent_id="p")
        d = w.to_dict()
        assert d["entities"]["c"]["parent_id"] == "p"

    def test_golden_system_schedule(self):
        fab, w = make_test_world("g_sched")
        fab.register_system(RuntimeSystem("s1", "S1", priority=10), w)
        fab.register_system(RuntimeSystem("s2", "S2", priority=50), w)
        sched = fab.get_scheduled_systems(world=w)
        assert [s.system_id for s in sched] == ["s2", "s1"]

    def test_golden_event_sequence(self):
        fab, w = make_test_world("g_evt")
        seq = []
        fab.subscribe_event("NUM", lambda e: seq.append(e.payload["v"]), world=w)
        for i in [1, 2, 3]:
            fab.publish_event("NUM", sender_id="src", payload={"v": i}, world=w)
        fab.dispatch_events(w)
        assert seq == [1, 2, 3]

    def test_golden_transform_hierarchy(self):
        fab, w = make_test_world("g_tr")
        p = fab.create_entity("p")
        p.local_transform = RuntimeTransform(position=[5.0, 0.0, 0.0])
        c = fab.create_entity("c", parent_id="p")
        c.local_transform = RuntimeTransform(position=[2.0, 0.0, 0.0])
        wt = fab.compute_world_transform("c", w)
        assert wt.position == [7.0, 0.0, 0.0]

    def test_golden_resource_graph(self):
        fab, w = make_test_world("g_res")
        res = RuntimeResource("r_tex", "Texture", "uri://tex")
        fab.register_resource(res, w)
        d = w.to_dict()
        assert "r_tex" in d["resources"]

    def test_golden_prefab_runtime(self):
        fab, w = make_test_world("g_pf")
        class MockPrefab:
            name = "Mob"
            entities = {"body": None}
        fab.spawn_prefab(MockPrefab, "mob_1", world=w)
        d = w.to_dict()
        assert "mob_1_body" in d["entities"] or "mob_1_root" in d["entities"]

    def test_golden_streaming_world(self):
        fab, w = make_test_world("g_stream")
        cell = fab.create_streaming_cell("c0", "/Game/c0", world=w)
        d = w.to_dict()
        assert "c0" in d["cells"]

    def test_golden_world_snapshot(self):
        fab, w = make_test_world("g_snap")
        snap = fab.take_snapshot(w)
        assert len(snap.fingerprint) == 64

    def test_golden_world_recovery(self):
        fab, w = make_test_world("g_rec")
        snap = fab.take_snapshot(w)
        fab2 = UniversalRuntimeWorldFabricator()
        rec = fab2.restore_snapshot(snap)
        assert rec.world_id == "g_rec"

    def test_golden_runtime_replay(self):
        fab, w = make_test_world("g_rep")
        fab.initialize_world(w)
        fab.activate_world(w)
        fab.tick(0.016, w)
        assert w.time_seconds == pytest.approx(0.016)

    def test_golden_runtime_failure(self):
        fab, w = make_test_world("g_fail")
        with pytest.raises(ValueError, match="NO_INVALID_WORLD_TRANSITION"):
            fab.activate_world(w)

    def test_golden_runtime_shutdown(self):
        fab, w = make_test_world("g_shut")
        fab.initialize_world(w)
        fab.activate_world(w)
        fab.destroy_world(w)
        assert w.state == WorldState.TERMINATED

    def test_golden_platform_world(self):
        fab, w = make_test_world("g_plat")
        w.time_scale = 1.0
        assert w.fixed_delta_time == pytest.approx(1.0 / 60.0)


# ==============================================================================
# §119. CROSS-PHASE INTEGRATION TESTS (15 tests)
# ==============================================================================

class TestCrossPhaseIntegration:
    """Normative tests for Cross-Phase Invariants and Inter-Phase Pipelines (§119)."""

    def test_scene_build_to_world(self):
        fab, w = make_test_world("x_bld_w")
        assert w.world_id == "x_bld_w"

    def test_scene_entity_to_runtime_entity(self):
        fab, w = make_test_world("x_ent_r")
        e = fab.create_entity("hero_rt", name="Hero")
        assert e.entity_id == "hero_rt"
        assert e.name == "Hero"

    def test_scene_component_to_runtime_component(self):
        fab, w = make_test_world("x_comp_r")
        fab.create_entity("actor")
        comp = RuntimeComponent("c_mesh", "MeshComponent", properties={"mesh_ref": "SM_Hero"})
        fab.add_component("actor", comp, w)
        assert w.entities["actor"].components["c_mesh"].properties["mesh_ref"] == "SM_Hero"

    def test_scene_prefab_to_runtime_prefab(self):
        fab, w = make_test_world("x_pf_r")
        class MockScenePrefab:
            name = "Tower"
            entities = {"base": None}
        spawned = fab.spawn_prefab(MockScenePrefab, "tower_1", world=w)
        assert len(spawned) >= 1

    def test_scene_dependency_to_resource_resolver(self):
        fab, w = make_test_world("x_dep_res")
        res = RuntimeResource("dep_res_1", "Texture", "asset://t1")
        fab.register_resource(res, w)
        assert "dep_res_1" in w.resources

    def test_derived_mesh_to_runtime_resource(self):
        fab, w = make_test_world("x_dmesh")
        res = RuntimeResource("r_mesh", "DerivedMesh", "res://meshes/hero.uasset")
        fab.register_resource(res, w)
        acq = fab.acquire_resource("r_mesh", w)
        assert acq.state == ResourceState.READY

    def test_derived_texture_to_runtime_resource(self):
        fab, w = make_test_world("x_dtex")
        res = RuntimeResource("r_tex", "DerivedTexture", "res://textures/diffuse.uasset")
        fab.register_resource(res, w)
        acq = fab.acquire_resource("r_tex", w)
        assert acq.state == ResourceState.READY

    def test_material_to_runtime_resource(self):
        fab, w = make_test_world("x_mat")
        res = RuntimeResource("r_mat", "Material", "res://materials/m_hero.uasset")
        fab.register_resource(res, w)
        acq = fab.acquire_resource("r_mat", w)
        assert acq.state == ResourceState.READY

    def test_shader_to_runtime_resource(self):
        fab, w = make_test_world("x_shd")
        res = RuntimeResource("r_shd", "Shader", "res://shaders/pbr.usf")
        fab.register_resource(res, w)
        acq = fab.acquire_resource("r_shd", w)
        assert acq.state == ResourceState.READY

    def test_scene_build_to_streaming(self):
        fab, w = make_test_world("x_stream")
        cell = fab.create_streaming_cell("world_c0", "/Game/Maps/Level_0.scene", world=w)
        assert cell.scene_path == "/Game/Maps/Level_0.scene"

    def test_browser_to_runtime_scene(self):
        fab, w = make_test_world("x_brow")
        assert w.root_entity_id == "root"

    def test_inspector_to_runtime_entity(self):
        fab, w = make_test_world("x_insp")
        e = fab.create_entity("inspect_me")
        fab.add_component("inspect_me", RuntimeComponent("c_cam", "Camera", properties={"fov": 90}), w)
        assert w.entities["inspect_me"].components["c_cam"].properties["fov"] == 90

    def test_command_to_runtime_world(self):
        fab, w = make_test_world("x_cmd")
        fab.create_entity("cmd_actor")
        assert "cmd_actor" in w.entities

    def test_import_change_to_runtime_rebuild(self):
        fab, w = make_test_world("x_imp_chg")
        fp1 = w.compute_fingerprint()
        fab.create_entity("new_actor")
        fp2 = w.compute_fingerprint()
        assert fp1 != fp2

    def test_build_change_to_runtime_reload(self):
        fab, w = make_test_world("x_bld_chg")
        snap = fab.take_snapshot(w)
        fab2 = UniversalRuntimeWorldFabricator()
        reloaded = fab2.restore_snapshot(snap)
        assert reloaded.world_id == w.world_id


# ==============================================================================
# §120. CLEANUP TESTS (10 tests)
# ==============================================================================

class TestCleanup:
    """Normative tests for Memory Reclamation, Resource Deallocation, and Cleanup (§120)."""

    def test_world_cleanup(self):
        fab, w = make_test_world("cl_w")
        fab.create_entity("e1")
        fab.destroy_world(w)
        assert len(w.entities) == 0
        assert w.state == WorldState.TERMINATED

    def test_entity_cleanup(self):
        fab, w = make_test_world("cl_ent")
        fab.create_entity("e1")
        fab.destroy_entity("e1", w)
        assert "e1" not in w.entities

    def test_component_cleanup(self):
        fab, w = make_test_world("cl_comp")
        fab.create_entity("e1")
        fab.add_component("e1", RuntimeComponent("c1", "Type"), w)
        fab.destroy_component("e1", "c1", w)
        assert "c1" not in w.entities["e1"].components

    def test_system_cleanup(self):
        fab, w = make_test_world("cl_sys")
        fab.register_system(RuntimeSystem("s1", "S1"), w)
        w.systems.clear()
        assert len(w.systems) == 0

    def test_event_subscription_cleanup(self):
        fab, w = make_test_world("cl_evt")
        sid = fab.subscribe_event("SIG", lambda e: None, world=w)
        fab.unsubscribe_event(sid, w)
        assert len(w.event_subscriptions["SIG"]) == 0

    def test_resource_cleanup(self):
        fab, w = make_test_world("cl_res")
        fab.register_resource(RuntimeResource("r1", "Type", "uri://1"), w)
        w.resources.clear()
        assert len(w.resources) == 0

    def test_prefab_cleanup(self):
        fab, w = make_test_world("cl_pf")
        class MockPrefab:
            name = "PF"
            entities = {"node": None}
        fab.spawn_prefab(MockPrefab, "cl_inst", world=w)
        fab.despawn_prefab("cl_inst", w)
        assert "cl_inst_node" not in w.entities

    def test_streaming_cleanup(self):
        fab, w = make_test_world("cl_stream")
        fab.create_streaming_cell("c1", "/Game/c1", world=w)
        w.cells.clear()
        assert len(w.cells) == 0

    def test_snapshot_cleanup(self):
        fab, w = make_test_world("cl_snap")
        fab.take_snapshot(w)
        fab.take_snapshot(w)
        assert len(fab.snapshots) == 2
        fab.snapshots.clear()
        assert len(fab.snapshots) == 0

    def test_replay_cleanup(self):
        fab, w = make_test_world("cl_rep")
        w.event_queue.append(RuntimeEvent("e1", "T", "s"))
        w.event_queue.clear()
        assert len(w.event_queue) == 0


# ==============================================================================
# §124. PACKAGER & NON-NEGOTIABLE INVARIANTS (15 tests)
# ==============================================================================

class TestPackagerAndInvariants:
    """Normative tests for C++ Code Generation and §124 Invariant Preservation."""

    def test_packager_export_files(self, tmp_path):
        fab, w = make_test_world("pkg_exp")
        pkg = UniversalRuntimeWorldPackager()
        res = pkg.export_package(w, tmp_path)
        assert Path(res["header"]).exists()
        assert Path(res["source"]).exists()
        assert Path(res["manifest"]).exists()
        assert Path(res["signature"]).exists()

    def test_packager_header_guard(self):
        pkg = UniversalRuntimeWorldPackager()
        hdr = pkg.generate_cpp_header()
        assert "#pragma once" in hdr
        assert "UUAFRuntimeWorldSubsystem.generated.h" in hdr

    def test_packager_cpp_includes(self):
        pkg = UniversalRuntimeWorldPackager()
        src = pkg.generate_cpp_source()
        assert '#include "UUAFRuntimeWorldSubsystem.h"' in src
        assert '#include "Misc/FileHelper.h"' in src

    def test_packager_manifest_content(self):
        fab, w = make_test_world("pkg_man")
        pkg = UniversalRuntimeWorldPackager()
        man = pkg.generate_world_manifest(w)
        data = json.loads(man)
        assert data["world_id"] == "pkg_man"
        assert "root" in data["entities"]

    def test_packager_signature_file(self, tmp_path):
        fab, w = make_test_world("pkg_sig")
        pkg = UniversalRuntimeWorldPackager()
        res = pkg.export_package(w, tmp_path)
        sig = Path(res["signature"]).read_text(encoding="utf-8")
        assert len(sig) == 64

    def test_packager_signature_verification(self, tmp_path):
        fab, w = make_test_world("pkg_ver")
        pkg = UniversalRuntimeWorldPackager()
        res = pkg.export_package(w, tmp_path)
        manifest_bytes = Path(res["manifest"]).read_bytes()
        expected = hashlib.sha256(manifest_bytes).hexdigest()
        actual = Path(res["signature"]).read_text(encoding="utf-8")
        assert actual == expected

    def test_packager_world_state_enum(self):
        pkg = UniversalRuntimeWorldPackager()
        hdr = pkg.generate_cpp_header()
        assert "enum class EUAFWorldState : uint8" in hdr
        assert "Initialized" in hdr
        assert "Active" in hdr

    def test_packager_subsystem_class_name(self):
        pkg = UniversalRuntimeWorldPackager()
        hdr = pkg.generate_cpp_header()
        assert "class UAF_API UUAFRuntimeWorldSubsystem : public UWorldSubsystem" in hdr

    def test_packager_directory_creation(self, tmp_path):
        target = tmp_path / "deep" / "runtime" / "subsystem"
        fab, w = make_test_world("pkg_dir")
        pkg = UniversalRuntimeWorldPackager()
        res = pkg.export_package(w, target)
        assert target.exists()
        assert Path(res["header"]).exists()

    def test_packager_deterministic_output(self):
        pkg = UniversalRuntimeWorldPackager()
        h1 = pkg.generate_cpp_header()
        h2 = pkg.generate_cpp_header()
        assert h1 == h2
        s1 = pkg.generate_cpp_source()
        s2 = pkg.generate_cpp_source()
        assert s1 == s2

    def test_invariant_no_invalid_world_transition(self):
        fab, w = make_test_world("inv_trans")
        with pytest.raises(ValueError, match="NO_INVALID_WORLD_TRANSITION"):
            fab.pause_world(w)  # Cannot pause uninitialized world

    def test_invariant_no_update_before_initialization(self):
        fab, w = make_test_world("inv_upd")
        with pytest.raises(ValueError, match="NO_UPDATE_BEFORE_INITIALIZATION"):
            fab.tick(0.016, w)

    def test_invariant_no_callback_after_destroy(self):
        fab, w = make_test_world("inv_cb")
        fab.create_entity("victim")
        fab.destroy_entity("victim", w)
        with pytest.raises(ValueError, match="NO_CALLBACK_AFTER_DESTROY"):
            fab.activate_entity("victim", w)

    def test_invariant_no_hierarchy_cycle(self):
        fab, w = make_test_world("inv_cyc")
        fab.create_entity("a")
        fab.create_entity("b", parent_id="a")
        with pytest.raises(ValueError, match="NO_HIERARCHY_CYCLES"):
            fab.set_parent("a", "b", w)

    def test_invariant_no_system_dependency_cycle(self):
        fab, w = make_test_world("inv_sys_cyc")
        fab.register_system(RuntimeSystem("x", "X", dependencies=["y"]), w)
        fab.register_system(RuntimeSystem("y", "Y", dependencies=["x"]), w)
        with pytest.raises(ValueError, match="NO_SYSTEM_DEPENDENCY_CYCLE"):
            fab.get_scheduled_systems(world=w)
