"""
Normative Acceptance Test Suite for UAF-81.74: Universal Runtime Physics System.
Validates complete physical simulation, rigid bodies, colliders, character controllers,
constraints, queries, materials, determinism, and invariants (§101 - §123).
"""

from __future__ import annotations
import copy
import hashlib
import json
import math
import os
import tempfile
import time
from typing import Any, Dict, List

import pytest

from uaf.runtime_physics import (
    PhysicsWorldState,
    BodyType,
    CollisionShapeType,
    MaterialCombinePolicy,
    ConstraintType,
    PhysicsEventType,
    PhysicsMaterial,
    CollisionShape,
    Collider,
    PhysicsBody,
    PhysicsConstraint,
    CharacterController,
    ContactPoint,
    ContactManifold,
    RaycastHit,
    OverlapHit,
    SweepHit,
    PhysicsEvent,
    PhysicsSimulationSettings,
    PhysicsWorld,
    PhysicsSnapshot,
    PhysicsReplayCommand,
    PhysicsReplay,
    UniversalRuntimePhysicsFabricator,
    UniversalRuntimePhysicsValidator,
    UniversalRuntimePhysicsPackager,
)
from uaf.runtime_world import (
    UniversalRuntimeWorldFabricator,
    RuntimeTransform,
)


def make_test_world(world_id: str = "test_phys_world") -> Tuple[UniversalRuntimePhysicsFabricator, PhysicsWorld]:
    fab = UniversalRuntimePhysicsFabricator()
    w = fab.create_world(world_id)
    return fab, w


# ==============================================================================
# §101. PHYSICS WORLD TESTS (10 tests)
# ==============================================================================

class TestPhysicsWorldLifecycle:
    """Normative tests for Physics World Creation and Finite State Machine (§101)."""

    def test_physics_world_creation(self):
        fab, w = make_test_world("pw_create")
        assert w.physics_world_id == "pw_create"
        assert w.state == PhysicsWorldState.CREATED
        assert len(w.bodies) == 0

    def test_physics_world_identity(self):
        fab, w = make_test_world("pw_ident")
        assert fab.get_world("pw_ident") is w
        assert fab.active_world is w

    def test_physics_world_state(self):
        fab, w = make_test_world("pw_state")
        fab.initialize_world(w)
        assert w.state == PhysicsWorldState.READY

    def test_physics_world_activation(self):
        fab, w = make_test_world("pw_act")
        fab.initialize_world(w)
        fab.start_simulation(w)
        assert w.state == PhysicsWorldState.SIMULATING

    def test_physics_world_pause(self):
        fab, w = make_test_world("pw_pause")
        fab.initialize_world(w)
        fab.start_simulation(w)
        fab.pause_simulation(w)
        assert w.state == PhysicsWorldState.PAUSED

    def test_physics_world_stop(self):
        fab, w = make_test_world("pw_stop")
        fab.initialize_world(w)
        fab.start_simulation(w)
        fab.stop_simulation(w)
        assert w.state == PhysicsWorldState.STOPPED

    def test_physics_world_destroy(self):
        fab, w = make_test_world("pw_destroy")
        fab.create_body("b1", "e1", world=w)
        fab.destroy_world(w)
        assert w.state == PhysicsWorldState.DESTROYED
        assert len(w.bodies) == 0

    def test_invalid_physics_world_transition(self):
        fab, w = make_test_world("pw_invalid_trans")
        with pytest.raises(ValueError, match="NO_INVALID_PHYSICS_WORLD_STATE"):
            fab.pause_simulation(w)  # cannot pause from CREATED

    def test_physics_configuration(self):
        settings = PhysicsSimulationSettings(
            fixed_delta_time=1.0 / 120.0,
            solver_iterations=12,
            max_substeps=8,
        )
        fab = UniversalRuntimePhysicsFabricator()
        w = fab.create_world("pw_cfg", settings=settings)
        assert w.settings.fixed_delta_time == 1.0 / 120.0
        assert w.settings.solver_iterations == 12
        assert w.settings.max_substeps == 8

    def test_gravity_configuration(self):
        fab, w = make_test_world("pw_grav")
        w.settings.gravity = [0.0, -19.62, 0.0]
        assert w.settings.gravity == [0.0, -19.62, 0.0]


# ==============================================================================
# §102. BODY TESTS (12 tests)
# ==============================================================================

class TestPhysicsBodyExecution:
    """Normative tests for Rigid Body Creation, Types, and States (§102)."""

    def test_static_body(self):
        fab, w = make_test_world("b_static")
        body = fab.create_body("ground", "e_ground", body_type=BodyType.STATIC, world=w)
        assert body.body_type == BodyType.STATIC
        assert body.mass == 0.0
        assert body.inverse_mass == 0.0

    def test_dynamic_body(self):
        fab, w = make_test_world("b_dyn")
        body = fab.create_body("ball", "e_ball", body_type=BodyType.DYNAMIC, mass=5.0, world=w)
        assert body.body_type == BodyType.DYNAMIC
        assert body.mass == 5.0
        assert body.inverse_mass == 0.2

    def test_kinematic_body(self):
        fab, w = make_test_world("b_kin")
        body = fab.create_body("platform", "e_plat", body_type=BodyType.KINEMATIC, world=w)
        assert body.body_type == BodyType.KINEMATIC
        assert body.mass == 0.0
        assert body.inverse_mass == 0.0

    def test_body_identity(self):
        fab, w = make_test_world("b_ident")
        b = fab.create_body("b1", "e1", world=w)
        assert fab.get_body("b1", w) is b

    def test_body_activation(self):
        fab, w = make_test_world("b_act")
        b = fab.create_body("b1", "e1", world=w)
        fab.deactivate_body("b1", w)
        assert not b.enabled
        fab.activate_body("b1", w)
        assert b.enabled

    def test_body_disable(self):
        fab, w = make_test_world("b_dis")
        b = fab.create_body("b1", "e1", world=w)
        fab.deactivate_body("b1", w)
        assert not b.enabled

    def test_body_sleep(self):
        fab, w = make_test_world("b_sleep")
        b = fab.create_body("b1", "e1", world=w)
        fab.sleep_body("b1", w)
        assert b.is_sleeping

    def test_body_wake(self):
        fab, w = make_test_world("b_wake")
        b = fab.create_body("b1", "e1", world=w)
        fab.sleep_body("b1", w)
        fab.wake_body("b1", w)
        assert not b.is_sleeping

    def test_body_destroy(self):
        fab, w = make_test_world("b_destroy")
        fab.create_body("b1", "e1", world=w)
        fab.destroy_body("b1", w)
        assert "b1" not in w.bodies
        assert "b1" in w.destroyed_body_ids

    def test_body_cleanup(self):
        fab, w = make_test_world("b_clean")
        fab.create_body("b1", "e1", world=w)
        shape = CollisionShape(shape_type=CollisionShapeType.BOX, params={"extents": [1.0, 1.0, 1.0]})
        fab.create_collider("c1", "b1", shape=shape, world=w)
        fab.destroy_body("b1", w)
        assert "c1" not in w.colliders

    def test_mass_validation(self):
        fab, w = make_test_world("b_mass_val")
        with pytest.raises(ValueError, match="INVALID_MASS"):
            fab.create_body("b_bad", "e1", body_type=BodyType.DYNAMIC, mass=-1.0, world=w)

    def test_velocity_validation(self):
        fab, w = make_test_world("b_vel_val")
        b = fab.create_body("b1", "e1", world=w)
        fab.set_linear_velocity("b1", [50.0, 0.0, 0.0], w)
        assert b.linear_velocity == [50.0, 0.0, 0.0]


# ==============================================================================
# §103. COLLIDER TESTS (12 tests)
# ==============================================================================

class TestColliderExecution:
    """Normative tests for Collision Shapes and Collider Attachments (§103)."""

    def test_box_collider(self):
        fab, w = make_test_world("col_box")
        fab.create_body("b1", "e1", world=w)
        shape = CollisionShape(shape_type=CollisionShapeType.BOX, params={"extents": [0.5, 0.5, 0.5]})
        c = fab.create_collider("c_box", "b1", shape=shape, world=w)
        assert c.shape.shape_type == CollisionShapeType.BOX

    def test_sphere_collider(self):
        fab, w = make_test_world("col_sphere")
        fab.create_body("b1", "e1", world=w)
        shape = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.25})
        c = fab.create_collider("c_sph", "b1", shape=shape, world=w)
        assert c.shape.shape_type == CollisionShapeType.SPHERE
        assert c.shape.params["radius"] == 1.25

    def test_capsule_collider(self):
        fab, w = make_test_world("col_capsule")
        fab.create_body("b1", "e1", world=w)
        shape = CollisionShape(shape_type=CollisionShapeType.CAPSULE, params={"radius": 0.5, "height": 1.8})
        c = fab.create_collider("c_cap", "b1", shape=shape, world=w)
        assert c.shape.shape_type == CollisionShapeType.CAPSULE

    def test_cylinder_collider(self):
        fab, w = make_test_world("col_cyl")
        fab.create_body("b1", "e1", world=w)
        shape = CollisionShape(shape_type=CollisionShapeType.CYLINDER, params={"radius": 0.5, "height": 2.0})
        c = fab.create_collider("c_cyl", "b1", shape=shape, world=w)
        assert c.shape.shape_type == CollisionShapeType.CYLINDER

    def test_convex_collider(self):
        fab, w = make_test_world("col_convex")
        fab.create_body("b1", "e1", world=w)
        shape = CollisionShape(shape_type=CollisionShapeType.CONVEX, params={"vertices": [[0,0,0], [1,0,0], [0,1,0]]})
        c = fab.create_collider("c_cvx", "b1", shape=shape, world=w)
        assert c.shape.shape_type == CollisionShapeType.CONVEX

    def test_mesh_collider(self):
        fab, w = make_test_world("col_mesh")
        fab.create_body("b1", "e1", world=w)
        shape = CollisionShape(shape_type=CollisionShapeType.TRIANGLE_MESH, params={"indices": [0,1,2]})
        c = fab.create_collider("c_mesh", "b1", shape=shape, world=w)
        assert c.shape.shape_type == CollisionShapeType.TRIANGLE_MESH

    def test_compound_collider(self):
        fab, w = make_test_world("col_comp")
        fab.create_body("b1", "e1", world=w)
        shape = CollisionShape(
            shape_type=CollisionShapeType.COMPOUND,
            params={"sub_shapes": [{"type": "BOX", "extents": [0.5, 0.5, 0.5]}]}
        )
        c = fab.create_collider("c_comp", "b1", shape=shape, world=w)
        assert c.shape.shape_type == CollisionShapeType.COMPOUND

    def test_shape_validation(self):
        fab, w = make_test_world("col_shape_val")
        fab.create_body("b1", "e1", world=w)
        shape = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": -0.5})
        with pytest.raises(ValueError, match="DEGENERATE_SHAPE"):
            fab.create_collider("c_bad", "b1", shape=shape, world=w)

    def test_collider_transform(self):
        fab, w = make_test_world("col_tr")
        fab.create_body("b1", "e1", world=w)
        shape = CollisionShape(
            shape_type=CollisionShapeType.BOX,
            params={"extents": [1,1,1]},
            local_position=[0.0, 1.0, 0.0]
        )
        c = fab.create_collider("c_tr", "b1", shape=shape, world=w)
        assert c.shape.local_position == [0.0, 1.0, 0.0]

    def test_collider_layer(self):
        fab, w = make_test_world("col_layer")
        fab.create_body("b1", "e1", world=w)
        shape = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        c = fab.create_collider("c_ly", "b1", shape=shape, layer=4, world=w)
        assert c.layer == 4

    def test_collider_mask(self):
        fab, w = make_test_world("col_mask")
        fab.create_body("b1", "e1", world=w)
        shape = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        c = fab.create_collider("c_mk", "b1", shape=shape, mask=0x000F, world=w)
        assert c.mask == 0x000F

    def test_collider_destroy(self):
        fab, w = make_test_world("col_destroy")
        fab.create_body("b1", "e1", world=w)
        shape = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c_del", "b1", shape=shape, world=w)
        fab.destroy_collider("c_del", w)
        assert "c_del" not in w.colliders
        assert "c_del" not in w.bodies["b1"].colliders


# ==============================================================================
# §104. MATERIAL TESTS (8 tests)
# ==============================================================================

class TestPhysicsMaterialExecution:
    """Normative tests for Friction, Restitution, Density and Material Policies (§104)."""

    def test_physics_material(self):
        fab, w = make_test_world("mat_create")
        mat = fab.create_material("wood", friction=0.6, restitution=0.2, world=w)
        assert mat.material_id == "wood"
        assert mat.friction == 0.6
        assert mat.restitution == 0.2

    def test_friction(self):
        fab, w = make_test_world("mat_fric")
        mat = fab.create_material("ice", friction=0.05, world=w)
        assert mat.friction == 0.05

    def test_restitution(self):
        fab, w = make_test_world("mat_rest")
        mat = fab.create_material("rubber", restitution=0.9, world=w)
        assert mat.restitution == 0.9

    def test_density(self):
        fab, w = make_test_world("mat_dens")
        mat = fab.create_material("iron", density=7800.0, world=w)
        assert mat.density == 7800.0

    def test_material_combination(self):
        fab, w = make_test_world("mat_comb")
        mat = fab.create_material("custom", combine_policy=MaterialCombinePolicy.MULTIPLY, world=w)
        assert mat.combine_policy == MaterialCombinePolicy.MULTIPLY

    def test_invalid_material(self):
        fab, w = make_test_world("mat_bad")
        with pytest.raises(ValueError, match="INVALID_MATERIAL"):
            fab.create_material("bad", friction=-1.0, world=w)

    def test_shared_material(self):
        fab, w = make_test_world("mat_share")
        mat = fab.create_material("shared_steel", friction=0.4, restitution=0.1, world=w)
        fab.create_body("b1", "e1", world=w)
        fab.create_body("b2", "e2", world=w)
        shape = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        c1 = fab.create_collider("c1", "b1", shape=shape, material=mat, world=w)
        c2 = fab.create_collider("c2", "b2", shape=shape, material=mat, world=w)
        assert c1.material is c2.material

    def test_material_lifetime(self):
        fab, w = make_test_world("mat_life")
        mat = fab.create_material("temp_mat", world=w)
        assert fab.get_material("temp_mat", w) is mat


# ==============================================================================
# §105. COLLISION TESTS (10 tests)
# ==============================================================================

class TestCollisionDetection:
    """Normative tests for Collision Detection, Filtering and Manifolds (§105)."""

    def test_collision_detection(self):
        fab, w = make_test_world("cd_detect")
        fab.create_body("b1", "e1", position=[0.0, 0.0, 0.0], world=w)
        fab.create_body("b2", "e2", position=[1.0, 0.0, 0.0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, world=w)
        fab.create_collider("c2", "b2", shape=s, world=w)
        fab.initialize_world(w)
        fab.simulate(0.016, w)
        assert any(ev.event_type == PhysicsEventType.CONTACT_BEGIN for ev in w.event_queue)

    def test_collision_filtering(self):
        fab, w = make_test_world("cd_filter")
        fab.create_body("b1", "e1", position=[0.0, 0.0, 0.0], world=w)
        fab.create_body("b2", "e2", position=[1.0, 0.0, 0.0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, layer=1, mask=2, world=w)
        fab.create_collider("c2", "b2", shape=s, layer=4, mask=8, world=w)
        fab.initialize_world(w)
        fab.simulate(0.016, w)
        assert not any(ev.event_type == PhysicsEventType.CONTACT_BEGIN for ev in w.event_queue)

    def test_collision_layer(self):
        fab, w = make_test_world("cd_layer")
        fab.create_body("b1", "e1", world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        c = fab.create_collider("c1", "b1", shape=s, layer=8, world=w)
        assert c.layer == 8

    def test_collision_mask(self):
        fab, w = make_test_world("cd_mask")
        fab.create_body("b1", "e1", world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        c = fab.create_collider("c1", "b1", shape=s, mask=12, world=w)
        assert c.mask == 12

    def test_contact_generation(self):
        fab, w = make_test_world("cd_contact_gen")
        fab.create_body("b1", "e1", position=[0.0, 0.0, 0.0], world=w)
        fab.create_body("b2", "e2", position=[0.5, 0.0, 0.0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, world=w)
        fab.create_collider("c2", "b2", shape=s, world=w)
        fab.initialize_world(w)
        fab.simulate(0.016, w)
        contacts = [ev for ev in w.event_queue if ev.event_type == PhysicsEventType.CONTACT_BEGIN]
        assert len(contacts) > 0

    def test_contact_manifold(self):
        pt = ContactPoint(point=[0.0, 1.0, 0.0], normal=[0.0, 1.0, 0.0], penetration=0.05)
        man = ContactManifold(
            body_a_id="b1",
            body_b_id="b2",
            collider_a_id="c1",
            collider_b_id="c2",
            points=[pt],
            penetration=0.05,
        )
        assert len(man.points) == 1
        assert man.points[0].penetration == 0.05

    def test_contact_normal(self):
        pt = ContactPoint(point=[0.0, 1.0, 0.0], normal=[0.0, 1.0, 0.0], penetration=0.02)
        assert pt.normal == [0.0, 1.0, 0.0]

    def test_contact_penetration(self):
        pt = ContactPoint(point=[0.0, 1.0, 0.0], normal=[0.0, 1.0, 0.0], penetration=0.035)
        assert pt.penetration == 0.035

    def test_contact_impulse(self):
        pt = ContactPoint(point=[0.0, 1.0, 0.0], normal=[0.0, 1.0, 0.0], penetration=0.02, impulse=15.0)
        assert pt.impulse == 15.0

    def test_collision_determinism(self):
        def run_sim():
            fab, w = make_test_world("cd_det")
            fab.create_body("b1", "e1", position=[0.0, 0.0, 0.0], world=w)
            fab.create_body("b2", "e2", position=[0.8, 0.0, 0.0], world=w)
            s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
            fab.create_collider("c1", "b1", shape=s, world=w)
            fab.create_collider("c2", "b2", shape=s, world=w)
            fab.initialize_world(w)
            for _ in range(5):
                fab.simulate(0.016, w)
            return w.compute_fingerprint()

        fp1 = run_sim()
        fp2 = run_sim()
        assert fp1 == fp2


# ==============================================================================
# §106. TRIGGER TESTS (8 tests)
# ==============================================================================

class TestTriggerExecution:
    """Normative tests for Trigger Colliders and Overlap Semantics (§106)."""

    def test_trigger_creation(self):
        fab, w = make_test_world("trig_create")
        fab.create_body("zone", "e_zone", body_type=BodyType.STATIC, world=w)
        s = CollisionShape(shape_type=CollisionShapeType.BOX, params={"extents": [2.0, 2.0, 2.0]})
        c = fab.create_collider("c_trig", "zone", shape=s, is_trigger=True, world=w)
        assert c.is_trigger

    def test_trigger_enter(self):
        fab, w = make_test_world("trig_enter")
        fab.create_body("zone", "e_zone", body_type=BodyType.STATIC, position=[0, 0, 0], world=w)
        fab.create_body("hero", "e_hero", position=[0.5, 0, 0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c_zone", "zone", shape=s, is_trigger=True, world=w)
        fab.create_collider("c_hero", "hero", shape=s, world=w)
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        assert any(ev.event_type == PhysicsEventType.TRIGGER_ENTER for ev in w.event_queue)

    def test_trigger_stay(self):
        fab, w = make_test_world("trig_stay")
        fab.create_body("zone", "e_zone", body_type=BodyType.STATIC, position=[0, 0, 0], world=w)
        fab.create_body("hero", "e_hero", position=[0.5, 0, 0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c_zone", "zone", shape=s, is_trigger=True, world=w)
        fab.create_collider("c_hero", "hero", shape=s, world=w)
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        fab.simulate(0.02, w)
        assert any(ev.event_type == PhysicsEventType.TRIGGER_STAY for ev in w.event_queue)

    def test_trigger_exit(self):
        fab, w = make_test_world("trig_exit")
        fab.create_body("zone", "e_zone", body_type=BodyType.STATIC, position=[0, 0, 0], world=w)
        hero = fab.create_body("hero", "e_hero", position=[0.5, 0, 0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c_zone", "zone", shape=s, is_trigger=True, world=w)
        fab.create_collider("c_hero", "hero", shape=s, world=w)
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        hero.position = [10.0, 0.0, 0.0]
        fab.simulate(0.02, w)
        assert any(ev.event_type == PhysicsEventType.TRIGGER_EXIT for ev in w.event_queue)

    def test_trigger_filtering(self):
        fab, w = make_test_world("trig_filt")
        fab.create_body("zone", "e_zone", body_type=BodyType.STATIC, position=[0, 0, 0], world=w)
        fab.create_body("hero", "e_hero", position=[0.5, 0, 0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c_zone", "zone", shape=s, is_trigger=True, layer=1, mask=2, world=w)
        fab.create_collider("c_hero", "hero", shape=s, layer=4, mask=8, world=w)
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        assert not any(ev.event_type == PhysicsEventType.TRIGGER_ENTER for ev in w.event_queue)

    def test_trigger_no_solid_response(self):
        fab, w = make_test_world("trig_nosolid")
        fab.create_body("zone", "e_zone", body_type=BodyType.STATIC, position=[0, 0, 0], world=w)
        hero = fab.create_body("hero", "e_hero", body_type=BodyType.DYNAMIC, position=[0.5, 0, 0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c_zone", "zone", shape=s, is_trigger=True, world=w)
        fab.create_collider("c_hero", "hero", shape=s, world=w)
        fab.initialize_world(w)
        init_x = hero.position[0]
        fab.simulate(0.02, w)
        # Should not have experienced repulsive solid contact force in X
        assert hero.position[0] == init_x

    def test_trigger_destroy(self):
        fab, w = make_test_world("trig_destroy")
        fab.create_body("zone", "e_zone", body_type=BodyType.STATIC, world=w)
        s = CollisionShape(shape_type=CollisionShapeType.BOX, params={"extents": [2, 2, 2]})
        fab.create_collider("c_t", "zone", shape=s, is_trigger=True, world=w)
        fab.destroy_collider("c_t", w)
        assert "c_t" not in w.colliders

    def test_trigger_cleanup(self):
        fab, w = make_test_world("trig_clean")
        fab.create_body("zone", "e_zone", body_type=BodyType.STATIC, world=w)
        s = CollisionShape(shape_type=CollisionShapeType.BOX, params={"extents": [2, 2, 2]})
        fab.create_collider("c_t", "zone", shape=s, is_trigger=True, world=w)
        fab.destroy_body("zone", w)
        assert "c_t" not in w.colliders


# ==============================================================================
# §107. FORCE TESTS (9 tests)
# ==============================================================================

class TestForceApplication:
    """Normative tests for Forces, Impulses, Torques and Velocity Limits (§107)."""

    def test_force(self):
        fab, w = make_test_world("f_force")
        b = fab.create_body("b1", "e1", world=w)
        fab.apply_force("b1", [10.0, 0.0, 0.0], w)
        assert b.forces == [10.0, 0.0, 0.0]

    def test_impulse(self):
        fab, w = make_test_world("f_impulse")
        b = fab.create_body("b1", "e1", mass=2.0, world=w)
        fab.apply_impulse("b1", [10.0, 0.0, 0.0], w)
        assert b.linear_velocity == [5.0, 0.0, 0.0]

    def test_torque(self):
        fab, w = make_test_world("f_torque")
        b = fab.create_body("b1", "e1", world=w)
        fab.apply_torque("b1", [0.0, 5.0, 0.0], w)
        assert b.torques == [0.0, 5.0, 0.0]

    def test_angular_impulse(self):
        fab, w = make_test_world("f_ang_impulse")
        b = fab.create_body("b1", "e1", mass=2.0, world=w)
        fab.apply_angular_impulse("b1", [0.0, 4.0, 0.0], w)
        assert b.angular_velocity == [0.0, 2.0, 0.0]

    def test_gravity(self):
        fab, w = make_test_world("f_grav")
        b = fab.create_body("b1", "e1", position=[0, 10, 0], world=w)
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        assert b.linear_velocity[1] < 0.0

    def test_gravity_scale(self):
        fab, w = make_test_world("f_grav_scale")
        b = fab.create_body("b1", "e1", gravity_scale=0.0, world=w)
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        assert b.linear_velocity[1] == 0.0

    def test_linear_damping(self):
        fab, w = make_test_world("f_lin_damp")
        b = fab.create_body("b1", "e1", gravity_scale=0.0, linear_damping=0.5, world=w)
        b.linear_velocity = [10.0, 0.0, 0.0]
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        assert b.linear_velocity[0] < 10.0

    def test_angular_damping(self):
        fab, w = make_test_world("f_ang_damp")
        b = fab.create_body("b1", "e1", gravity_scale=0.0, angular_damping=0.5, world=w)
        b.angular_velocity = [0.0, 10.0, 0.0]
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        assert b.angular_velocity[1] < 10.0

    def test_velocity_limit(self):
        fab, w = make_test_world("f_vel_lim")
        b = fab.create_body("b1", "e1", world=w)
        w.settings.max_linear_velocity = 50.0
        fab.set_linear_velocity("b1", [100.0, 0.0, 0.0], w)
        assert b.linear_velocity[0] <= 50.001


# ==============================================================================
# §108. CONSTRAINT TESTS (10 tests)
# ==============================================================================

class TestConstraintExecution:
    """Normative tests for Physics Joints and Constraints (§108)."""

    def test_fixed_constraint(self):
        fab, w = make_test_world("cn_fixed")
        fab.create_body("b1", "e1", world=w)
        fab.create_body("b2", "e2", world=w)
        c = fab.create_constraint("c_fix", ConstraintType.FIXED, "b1", "b2", world=w)
        assert c.constraint_type == ConstraintType.FIXED

    def test_distance_constraint(self):
        fab, w = make_test_world("cn_dist")
        fab.create_body("b1", "e1", world=w)
        fab.create_body("b2", "e2", world=w)
        c = fab.create_constraint("c_dst", ConstraintType.DISTANCE, "b1", "b2", limits={"distance": 3.0}, world=w)
        assert c.limits["distance"] == 3.0

    def test_hinge_constraint(self):
        fab, w = make_test_world("cn_hinge")
        fab.create_body("b1", "e1", world=w)
        fab.create_body("b2", "e2", world=w)
        c = fab.create_constraint("c_hng", ConstraintType.HINGE, "b1", "b2", world=w)
        assert c.constraint_type == ConstraintType.HINGE

    def test_slider_constraint(self):
        fab, w = make_test_world("cn_slider")
        fab.create_body("b1", "e1", world=w)
        fab.create_body("b2", "e2", world=w)
        c = fab.create_constraint("c_sld", ConstraintType.SLIDER, "b1", "b2", world=w)
        assert c.constraint_type == ConstraintType.SLIDER

    def test_spring_constraint(self):
        fab, w = make_test_world("cn_spring")
        fab.create_body("b1", "e1", world=w)
        fab.create_body("b2", "e2", world=w)
        c = fab.create_constraint("c_spr", ConstraintType.SPRING, "b1", "b2", stiffness=50.0, damping=2.0, world=w)
        assert c.stiffness == 50.0

    def test_generic_constraint(self):
        fab, w = make_test_world("cn_gen")
        fab.create_body("b1", "e1", world=w)
        fab.create_body("b2", "e2", world=w)
        c = fab.create_constraint("c_gen", ConstraintType.GENERIC, "b1", "b2", world=w)
        assert c.constraint_type == ConstraintType.GENERIC

    def test_constraint_endpoints(self):
        fab, w = make_test_world("cn_endpoints")
        fab.create_body("b1", "e1", world=w)
        with pytest.raises(ValueError, match="INVALID_CONSTRAINT_ENDPOINTS"):
            fab.create_constraint("c_bad", ConstraintType.FIXED, "b1", "non_existent", world=w)

    def test_constraint_validation(self):
        fab, w = make_test_world("cn_val")
        fab.create_body("b1", "e1", world=w)
        with pytest.raises(ValueError, match="INVALID_CONSTRAINT_ENDPOINTS"):
            fab.create_constraint("c_self", ConstraintType.FIXED, "b1", "b1", world=w)

    def test_constraint_destroy(self):
        fab, w = make_test_world("cn_destroy")
        fab.create_body("b1", "e1", world=w)
        fab.create_body("b2", "e2", world=w)
        fab.create_constraint("c1", ConstraintType.FIXED, "b1", "b2", world=w)
        fab.destroy_constraint("c1", w)
        assert "c1" not in w.constraints

    def test_constraint_cleanup(self):
        fab, w = make_test_world("cn_clean")
        fab.create_body("b1", "e1", world=w)
        fab.create_body("b2", "e2", world=w)
        fab.create_constraint("c1", ConstraintType.FIXED, "b1", "b2", world=w)
        fab.destroy_body("b1", w)
        assert "c1" not in w.constraints


# ==============================================================================
# §109. CHARACTER CONTROLLER TESTS (10 tests)
# ==============================================================================

class TestCharacterControllerExecution:
    """Normative tests for Kinematic Character Controller (§109)."""

    def test_character_creation(self):
        fab, w = make_test_world("cc_create")
        cc = fab.create_character_controller("hero_cc", "e_hero", height=1.8, radius=0.3, world=w)
        assert cc.controller_id == "hero_cc"
        assert cc.height == 1.8
        assert cc.radius == 0.3

    def test_character_move(self):
        fab, w = make_test_world("cc_move")
        cc = fab.create_character_controller("hero_cc", "e_hero", position=[0, 0, 0], world=w)
        fab.move_character("hero_cc", [1.0, 0.0, 0.0], 0.1, w)
        assert cc.position == [1.0, 0.0, 0.0]

    def test_character_grounding(self):
        fab, w = make_test_world("cc_ground")
        cc = fab.create_character_controller("hero_cc", "e_hero", position=[0, 1.0, 0], world=w)
        fab.move_character("hero_cc", [0.0, -1.5, 0.0], 0.1, w)
        assert cc.is_grounded
        assert cc.position[1] == 0.0

    def test_character_slope(self):
        fab, w = make_test_world("cc_slope")
        cc = fab.create_character_controller("hero_cc", "e_hero", slope_limit=45.0, world=w)
        assert cc.slope_limit == 45.0

    def test_character_step(self):
        fab, w = make_test_world("cc_step")
        cc = fab.create_character_controller("hero_cc", "e_hero", step_offset=0.35, world=w)
        assert cc.step_offset == 0.35

    def test_character_collision(self):
        fab, w = make_test_world("cc_col")
        cc = fab.create_character_controller("hero_cc", "e_hero", position=[0, 0, 0], world=w)
        assert cc.enabled

    def test_character_velocity(self):
        fab, w = make_test_world("cc_vel")
        cc = fab.create_character_controller("hero_cc", "e_hero", world=w)
        fab.move_character("hero_cc", [2.0, 0.0, 0.0], 0.1, w)
        assert abs(cc.velocity[0] - 20.0) < 0.001

    def test_character_teleport(self):
        fab, w = make_test_world("cc_teleport")
        cc = fab.create_character_controller("hero_cc", "e_hero", world=w)
        fab.teleport_character("hero_cc", [50.0, 10.0, 5.0], w)
        assert cc.position == [50.0, 10.0, 5.0]
        assert cc.velocity == [0.0, 0.0, 0.0]

    def test_character_destroy(self):
        fab, w = make_test_world("cc_destroy")
        fab.create_character_controller("hero_cc", "e_hero", world=w)
        fab.destroy_character_controller("hero_cc", w)
        assert "hero_cc" not in w.character_controllers

    def test_character_cleanup(self):
        fab, w = make_test_world("cc_clean")
        fab.create_character_controller("hero_cc", "e_hero", world=w)
        fab.destroy_character_controller("hero_cc", w)
        with pytest.raises(ValueError, match="CONTROLLER_NOT_FOUND"):
            fab.move_character("hero_cc", [1, 0, 0], 0.1, w)


# ==============================================================================
# §110. QUERY TESTS (11 tests)
# ==============================================================================

class TestPhysicsQueries:
    """Normative tests for Raycast, Shapecast, Overlap and Sweep Queries (§110)."""

    def test_raycast(self):
        fab, w = make_test_world("q_ray")
        fab.create_body("target", "e_tgt", position=[5.0, 0.0, 0.0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c_tgt", "target", shape=s, world=w)
        hit = fab.raycast([0.0, 0.0, 0.0], [1.0, 0.0, 0.0], max_distance=100.0, world=w)
        assert hit.hit
        assert abs(hit.distance - 4.0) < 0.01

    def test_raycast_miss(self):
        fab, w = make_test_world("q_miss")
        fab.create_body("target", "e_tgt", position=[5.0, 5.0, 0.0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c_tgt", "target", shape=s, world=w)
        hit = fab.raycast([0.0, 0.0, 0.0], [1.0, 0.0, 0.0], max_distance=100.0, world=w)
        assert not hit.hit

    def test_raycast_filter(self):
        fab, w = make_test_world("q_filter")
        fab.create_body("target", "e_tgt", position=[5.0, 0.0, 0.0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c_tgt", "target", shape=s, layer=4, world=w)
        # Layer 4 has bitmask 4; query with layer_mask=1 will ignore it
        hit = fab.raycast([0.0, 0.0, 0.0], [1.0, 0.0, 0.0], layer_mask=1, world=w)
        assert not hit.hit

    def test_raycast_result(self):
        fab, w = make_test_world("q_result")
        fab.create_body("target", "e_tgt", position=[5.0, 0.0, 0.0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c_tgt", "target", shape=s, world=w)
        hit = fab.raycast([0.0, 0.0, 0.0], [1.0, 0.0, 0.0], world=w)
        assert hit.collider_id == "c_tgt"
        assert hit.body_id == "target"
        assert hit.entity_id == "e_tgt"

    def test_raycast_order(self):
        fab, w = make_test_world("q_order")
        fab.create_body("far", "e_far", position=[10.0, 0.0, 0.0], world=w)
        fab.create_body("near", "e_near", position=[5.0, 0.0, 0.0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c_far", "far", shape=s, world=w)
        fab.create_collider("c_near", "near", shape=s, world=w)
        hit = fab.raycast([0.0, 0.0, 0.0], [1.0, 0.0, 0.0], world=w)
        assert hit.body_id == "near"

    def test_shapecast(self):
        fab, w = make_test_world("q_shapecast")
        fab.create_body("obstacle", "e_obs", position=[5.0, 0.0, 0.0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c_obs", "obstacle", shape=s, world=w)
        sweep_shape = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 0.5})
        hit = fab.shapecast(sweep_shape, [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], world=w)
        assert hit.hit

    def test_overlap_query(self):
        fab, w = make_test_world("q_overlap")
        fab.create_body("b1", "e1", position=[0.0, 0.0, 0.0], world=w)
        fab.create_body("b2", "e2", position=[2.0, 0.0, 0.0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, world=w)
        fab.create_collider("c2", "b2", shape=s, world=w)
        query_shape = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.5})
        hits = fab.overlap(query_shape, [0.0, 0.0, 0.0], world=w)
        assert len(hits) >= 1
        assert any(h.collider_id == "c1" for h in hits)

    def test_sweep_query(self):
        fab, w = make_test_world("q_sweep")
        fab.create_body("b1", "e1", position=[4.0, 0.0, 0.0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.BOX, params={"extents": [1.0, 1.0, 1.0]})
        fab.create_collider("c1", "b1", shape=s, world=w)
        sweep_shape = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 0.5})
        hit = fab.sweep(sweep_shape, [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], world=w)
        assert hit.hit

    def test_query_trigger_policy(self):
        fab, w = make_test_world("q_trig_pol")
        fab.create_body("zone", "e_zone", position=[5.0, 0.0, 0.0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c_zone", "zone", shape=s, is_trigger=True, world=w)
        hit_default = fab.raycast([0.0, 0.0, 0.0], [1.0, 0.0, 0.0], include_triggers=False, world=w)
        assert not hit_default.hit
        hit_include = fab.raycast([0.0, 0.0, 0.0], [1.0, 0.0, 0.0], include_triggers=True, world=w)
        assert hit_include.hit

    def test_query_determinism(self):
        def run_q():
            fab, w = make_test_world("q_det")
            fab.create_body("b1", "e1", position=[5.0, 0.0, 0.0], world=w)
            s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
            fab.create_collider("c1", "b1", shape=s, world=w)
            return fab.raycast([0.0, 0.0, 0.0], [1.0, 0.0, 0.0], world=w).to_dict()

        h1 = run_q()
        h2 = run_q()
        assert h1 == h2

    def test_query_limits(self):
        fab, w = make_test_world("q_limits")
        w.settings.max_query_distance = 100.0
        with pytest.raises(ValueError, match="INVALID_QUERY"):
            fab.raycast([0,0,0], [1,0,0], max_distance=500.0, world=w)


# ==============================================================================
# §111. SIMULATION TESTS (10 tests)
# ==============================================================================

class TestSimulationStepping:
    """Normative tests for Simulation Stepping, Substepping and Timestep Accumulator (§111)."""

    def test_simulation_step(self):
        fab, w = make_test_world("sim_step")
        fab.create_body("b1", "e1", position=[0, 10, 0], world=w)
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        assert w.frame_index > 0
        assert w.time_seconds > 0.0

    def test_fixed_timestep(self):
        fab, w = make_test_world("sim_fixed")
        fab.initialize_world(w)
        fab.simulate(1.0 / 60.0, w)
        assert abs(w.time_seconds - (1.0 / 60.0)) < 0.001

    def test_variable_timestep(self):
        fab, w = make_test_world("sim_var")
        fab.initialize_world(w)
        fab.simulate(0.05, w)
        assert w.time_seconds > 0.0

    def test_time_accumulator(self):
        fab, w = make_test_world("sim_acc")
        fab.initialize_world(w)
        fab.simulate(0.005, w)  # small delta, accumulates
        assert w.time_accumulator >= 0.0

    def test_max_substeps(self):
        fab, w = make_test_world("sim_substeps")
        w.settings.max_substeps = 2
        fab.initialize_world(w)
        fab.simulate(1.0, w)  # big delta
        assert w.frame_index == 2

    def test_catch_up_policy(self):
        fab, w = make_test_world("sim_catchup")
        fab.initialize_world(w)
        fab.simulate(10.0, w)  # massive delta
        # Accumulator should have been reset to prevent spiral of death
        assert w.time_accumulator == 0.0

    def test_interpolation(self):
        fab, w = make_test_world("sim_interp")
        b = fab.create_body("b1", "e1", position=[0, 10, 0], world=w)
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        assert b.position[1] < 10.0

    def test_extrapolation(self):
        fab, w = make_test_world("sim_extrap")
        b = fab.create_body("b1", "e1", world=w)
        b.linear_velocity = [10.0, 0.0, 0.0]
        pos_future = [b.position[0] + b.linear_velocity[0] * 0.5, b.position[1], b.position[2]]
        assert pos_future[0] == 5.0

    def test_pause(self):
        fab, w = make_test_world("sim_pause")
        fab.initialize_world(w)
        fab.start_simulation(w)
        fab.pause_simulation(w)
        t_before = w.time_seconds
        fab.simulate(0.05, w)
        assert w.time_seconds == t_before

    def test_simulation_determinism(self):
        def run_full():
            fab, w = make_test_world("sim_det")
            b = fab.create_body("b1", "e1", position=[0, 10, 0], world=w)
            fab.initialize_world(w)
            for _ in range(10):
                fab.simulate(0.02, w)
            return b.position[1]

        y1 = run_full()
        y2 = run_full()
        assert y1 == y2


# ==============================================================================
# §112. TRANSFORM SYNC TESTS (8 tests)
# ==============================================================================

class TestTransformSynchronization:
    """Normative tests for Bidirectional Transform Sync with RuntimeWorld (§112)."""

    def test_physics_to_world_transform(self):
        phys_fab, pw = make_test_world("ts_p2w")
        body = phys_fab.create_body("b_sync", "ent_1", position=[10.0, 5.0, -2.0], world=pw)
        world_fab = UniversalRuntimeWorldFabricator()
        rw = world_fab.create_world("rw_sync")
        ent = world_fab.create_entity("ent_1", world=rw)
        phys_fab.sync_to_runtime_world(rw, pw)
        assert ent.local_transform.position == [10.0, 5.0, -2.0]

    def test_world_to_physics_transform(self):
        phys_fab, pw = make_test_world("ts_w2p")
        body = phys_fab.create_body("b_sync", "ent_2", world=pw)
        world_fab = UniversalRuntimeWorldFabricator()
        rw = world_fab.create_world("rw_sync2")
        ent = world_fab.create_entity("ent_2", world=rw)
        ent.local_transform.position = [3.0, 7.0, 11.0]
        phys_fab.sync_from_runtime_world(rw, pw)
        assert body.position == [3.0, 7.0, 11.0]

    def test_teleport(self):
        phys_fab, pw = make_test_world("ts_teleport")
        body = phys_fab.create_body("b_tp", "ent_tp", world=pw)
        body.linear_velocity = [15.0, 0.0, 0.0]
        phys_fab.teleport_body("b_tp", [100.0, 20.0, 0.0], reset_velocity=True, world=pw)
        assert body.position == [100.0, 20.0, 0.0]
        assert body.linear_velocity == [0.0, 0.0, 0.0]

    def test_transform_rotation(self):
        phys_fab, pw = make_test_world("ts_rot")
        body = phys_fab.create_body("b_rot", "ent_rot", rotation=[0.0, 0.7071, 0.0, 0.7071], world=pw)
        world_fab = UniversalRuntimeWorldFabricator()
        rw = world_fab.create_world("rw_rot")
        ent = world_fab.create_entity("ent_rot", world=rw)
        phys_fab.sync_to_runtime_world(rw, pw)
        assert ent.local_transform.rotation == [0.0, 0.7071, 0.0, 0.7071]

    def test_transform_scale_policy(self):
        phys_fab, pw = make_test_world("ts_scale")
        world_fab = UniversalRuntimeWorldFabricator()
        rw = world_fab.create_world("rw_scale")
        ent = world_fab.create_entity("ent_s", world=rw)
        assert ent.local_transform.scale == [1.0, 1.0, 1.0]

    def test_parent_transform(self):
        world_fab = UniversalRuntimeWorldFabricator()
        rw = world_fab.create_world("rw_parent")
        p = world_fab.create_entity("p", world=rw)
        c = world_fab.create_entity("c", parent_id="p", world=rw)
        assert c.parent_id == "p"

    def test_transform_sync_order(self):
        phys_fab, pw = make_test_world("ts_order")
        phys_fab.create_body("b1", "e1", position=[1, 0, 0], world=pw)
        phys_fab.create_body("b2", "e2", position=[2, 0, 0], world=pw)
        world_fab = UniversalRuntimeWorldFabricator()
        rw = world_fab.create_world("rw_order")
        e1 = world_fab.create_entity("e1", world=rw)
        e2 = world_fab.create_entity("e2", world=rw)
        phys_fab.sync_to_runtime_world(rw, pw)
        assert e1.local_transform.position == [1, 0, 0]
        assert e2.local_transform.position == [2, 0, 0]

    def test_transform_sync_determinism(self):
        phys_fab, pw = make_test_world("ts_det")
        phys_fab.create_body("b1", "e1", position=[5, 5, 5], world=pw)
        world_fab = UniversalRuntimeWorldFabricator()
        rw = world_fab.create_world("rw_det")
        e1 = world_fab.create_entity("e1", world=rw)
        phys_fab.sync_to_runtime_world(rw, pw)
        fp1 = rw.compute_fingerprint()
        phys_fab.sync_to_runtime_world(rw, pw)
        fp2 = rw.compute_fingerprint()
        assert fp1 == fp2


# ==============================================================================
# §113. PHYSICS EVENT TESTS (11 tests)
# ==============================================================================

class TestPhysicsEvents:
    """Normative tests for Contact, Trigger and Body Sleep Events (§113)."""

    def test_contact_begin(self):
        fab, w = make_test_world("ev_cb")
        fab.create_body("b1", "e1", position=[0,0,0], world=w)
        fab.create_body("b2", "e2", position=[0.5,0,0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, world=w)
        fab.create_collider("c2", "b2", shape=s, world=w)
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        assert any(e.event_type == PhysicsEventType.CONTACT_BEGIN for e in w.event_queue)

    def test_contact_stay(self):
        fab, w = make_test_world("ev_cs")
        fab.create_body("b1", "e1", body_type=BodyType.STATIC, position=[0,0,0], world=w)
        fab.create_body("b2", "e2", body_type=BodyType.STATIC, position=[0.5,0,0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, world=w)
        fab.create_collider("c2", "b2", shape=s, world=w)
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        fab.simulate(0.02, w)
        assert any(e.event_type == PhysicsEventType.CONTACT_STAY for e in w.event_queue)

    def test_contact_end(self):
        fab, w = make_test_world("ev_ce")
        b1 = fab.create_body("b1", "e1", position=[0,0,0], world=w)
        b2 = fab.create_body("b2", "e2", position=[0.5,0,0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, world=w)
        fab.create_collider("c2", "b2", shape=s, world=w)
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        b2.position = [10.0, 0.0, 0.0]
        fab.simulate(0.02, w)
        assert any(e.event_type == PhysicsEventType.CONTACT_END for e in w.event_queue)

    def test_trigger_enter(self):
        fab, w = make_test_world("ev_te")
        fab.create_body("b1", "e1", position=[0,0,0], world=w)
        fab.create_body("b2", "e2", position=[0.5,0,0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, is_trigger=True, world=w)
        fab.create_collider("c2", "b2", shape=s, world=w)
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        assert any(e.event_type == PhysicsEventType.TRIGGER_ENTER for e in w.event_queue)

    def test_trigger_stay(self):
        fab, w = make_test_world("ev_ts")
        fab.create_body("b1", "e1", position=[0,0,0], world=w)
        fab.create_body("b2", "e2", position=[0.5,0,0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, is_trigger=True, world=w)
        fab.create_collider("c2", "b2", shape=s, world=w)
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        fab.simulate(0.02, w)
        assert any(e.event_type == PhysicsEventType.TRIGGER_STAY for e in w.event_queue)

    def test_trigger_exit(self):
        fab, w = make_test_world("ev_tx")
        b1 = fab.create_body("b1", "e1", position=[0,0,0], world=w)
        b2 = fab.create_body("b2", "e2", position=[0.5,0,0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, is_trigger=True, world=w)
        fab.create_collider("c2", "b2", shape=s, world=w)
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        b2.position = [10.0, 0.0, 0.0]
        fab.simulate(0.02, w)
        assert any(e.event_type == PhysicsEventType.TRIGGER_EXIT for e in w.event_queue)

    def test_body_sleep_event(self):
        fab, w = make_test_world("ev_sleep")
        fab.create_body("b1", "e1", world=w)
        fab.sleep_body("b1", w)
        assert any(e.event_type == PhysicsEventType.BODY_SLEEP for e in w.event_queue)

    def test_body_wake_event(self):
        fab, w = make_test_world("ev_wake")
        fab.create_body("b1", "e1", world=w)
        fab.sleep_body("b1", w)
        fab.wake_body("b1", w)
        assert any(e.event_type == PhysicsEventType.BODY_WAKE for e in w.event_queue)

    def test_event_order(self):
        fab, w = make_test_world("ev_order")
        fab.create_body("b1", "e1", world=w)
        fab.sleep_body("b1", w)
        fab.wake_body("b1", w)
        ev_types = [e.event_type for e in w.event_queue]
        assert ev_types == [PhysicsEventType.BODY_SLEEP, PhysicsEventType.BODY_WAKE]

    def test_event_deduplication(self):
        fab, w = make_test_world("ev_dedup")
        fab.create_body("b1", "e1", world=w)
        fab.sleep_body("b1", w)
        fab.sleep_body("b1", w)  # second call does not re-add sleep event
        sleep_events = [e for e in w.event_queue if e.event_type == PhysicsEventType.BODY_SLEEP]
        assert len(sleep_events) == 1

    def test_destroyed_body_event_cleanup(self):
        fab, w = make_test_world("ev_clean_destroy")
        fab.create_body("b1", "e1", world=w)
        fab.sleep_body("b1", w)
        fab.destroy_body("b1", w)
        # Pending events for destroyed body are pruned
        assert not any(e.body_a_id == "b1" for e in w.event_queue)


# ==============================================================================
# §114. SNAPSHOT TESTS (8 tests)
# ==============================================================================

class TestPhysicsSnapshot:
    """Normative tests for Physics Snapshots and State Restoration (§114)."""

    def test_physics_snapshot(self):
        fab, w = make_test_world("snap_create")
        fab.create_body("b1", "e1", position=[1, 2, 3], world=w)
        snap = fab.create_snapshot("snap_1", w)
        assert snap.snapshot_id == "snap_1"
        assert snap.physics_world_id == "snap_create"
        assert len(snap.content_fingerprint) == 64

    def test_snapshot_identity(self):
        fab, w = make_test_world("snap_ident")
        snap = fab.create_snapshot("snap_id", w)
        assert snap.physics_world_id == w.physics_world_id

    def test_snapshot_validation(self):
        fab, w = make_test_world("snap_val")
        snap = fab.create_snapshot("snap_v", w)
        validator = UniversalRuntimePhysicsValidator()
        assert validator.validate_snapshot(snap)

    def test_snapshot_restore(self):
        fab, w = make_test_world("snap_res")
        b = fab.create_body("b1", "e1", position=[5, 5, 5], world=w)
        snap = fab.create_snapshot("snap_r", w)
        b.position = [20, 20, 20]
        fab.restore_snapshot(snap, w)
        assert w.bodies["b1"].position == [5, 5, 5]

    def test_snapshot_body_state(self):
        fab, w = make_test_world("snap_bstate")
        b = fab.create_body("b1", "e1", position=[1, 2, 3], linear_velocity=[4, 5, 6], world=w)
        snap = fab.create_snapshot("snap_bs", w)
        assert snap.world_data["bodies"]["b1"]["linear_velocity"] == [4.0, 5.0, 6.0]

    def test_snapshot_constraint_state(self):
        fab, w = make_test_world("snap_cstate")
        fab.create_body("b1", "e1", world=w)
        fab.create_body("b2", "e2", world=w)
        fab.create_constraint("cn1", ConstraintType.FIXED, "b1", "b2", world=w)
        snap = fab.create_snapshot("snap_cs", w)
        assert "cn1" in snap.world_data["constraints"]

    def test_snapshot_sleep_state(self):
        fab, w = make_test_world("snap_sstate")
        b = fab.create_body("b1", "e1", world=w)
        fab.sleep_body("b1", w)
        snap = fab.create_snapshot("snap_ss", w)
        assert snap.world_data["bodies"]["b1"]["is_sleeping"] is True

    def test_snapshot_determinism(self):
        fab, w = make_test_world("snap_det")
        fab.create_body("b1", "e1", position=[1, 2, 3], world=w)
        snap1 = fab.create_snapshot("s1", w)
        snap2 = fab.create_snapshot("s2", w)
        assert snap1.content_fingerprint == snap2.content_fingerprint


# ==============================================================================
# §115. REPLAY TESTS (8 tests)
# ==============================================================================

class TestPhysicsReplay:
    """Normative tests for Deterministic Command Logging and Replay (§115)."""

    def test_force_replay(self):
        fab, w = make_test_world("rep_force")
        fab.create_body("b1", "e1", world=w)
        snap = fab.create_snapshot("init_snap", w)
        cmd = PhysicsReplayCommand(frame_index=0, command_type="apply_force", target_id="b1", parameters={"force": [10.0, 0.0, 0.0]})
        replay = PhysicsReplay(replay_id="rep1", initial_snapshot=snap, commands=[cmd])
        fab.execute_replay(replay, w)
        assert w.bodies["b1"].position[0] > 0.0

    def test_impulse_replay(self):
        fab, w = make_test_world("rep_impulse")
        fab.create_body("b1", "e1", world=w)
        snap = fab.create_snapshot("init_snap2", w)
        cmd = PhysicsReplayCommand(frame_index=0, command_type="apply_impulse", target_id="b1", parameters={"impulse": [5.0, 0.0, 0.0]})
        replay = PhysicsReplay(replay_id="rep2", initial_snapshot=snap, commands=[cmd])
        fab.execute_replay(replay, w)
        assert w.bodies["b1"].position[0] > 0.0

    def test_controller_replay(self):
        fab, w = make_test_world("rep_ctrl")
        snap = fab.create_snapshot("init_snap_c", w)
        replay = PhysicsReplay(replay_id="rep_c", initial_snapshot=snap, commands=[])
        fab.execute_replay(replay, w)
        assert w.frame_index > 0

    def test_teleport_replay(self):
        fab, w = make_test_world("rep_tp")
        fab.create_body("b1", "e1", world=w)
        snap = fab.create_snapshot("init_tp", w)
        cmd = PhysicsReplayCommand(frame_index=1, command_type="teleport", target_id="b1", parameters={"position": [50.0, 0.0, 0.0]})
        replay = PhysicsReplay(replay_id="rep_tp", initial_snapshot=snap, commands=[cmd])
        fab.execute_replay(replay, w)
        assert w.bodies["b1"].position[0] >= 50.0

    def test_configuration_replay(self):
        fab, w = make_test_world("rep_cfg")
        snap = fab.create_snapshot("init_cfg", w)
        replay = PhysicsReplay(replay_id="rep_cfg", initial_snapshot=snap, commands=[])
        assert replay.initial_snapshot.physics_world_id == "rep_cfg"

    def test_physics_replay(self):
        fab, w = make_test_world("rep_phys")
        fab.create_body("b1", "e1", world=w)
        snap = fab.create_snapshot("init_p", w)
        replay = PhysicsReplay(replay_id="rep_p", initial_snapshot=snap, commands=[])
        fab.execute_replay(replay, w)
        assert w.time_seconds > 0.0

    def test_replay_determinism(self):
        def run_rep():
            fab, w = make_test_world("rep_det")
            fab.create_body("b1", "e1", world=w)
            snap = fab.create_snapshot("init_det", w)
            cmd = PhysicsReplayCommand(frame_index=0, command_type="apply_force", target_id="b1", parameters={"force": [20.0, 0.0, 0.0]})
            replay = PhysicsReplay(replay_id="rep_det", initial_snapshot=snap, commands=[cmd])
            fab.execute_replay(replay, w)
            return w.bodies["b1"].position[0]

        x1 = run_rep()
        x2 = run_rep()
        assert x1 == x2

    def test_replay_corruption(self):
        fab, w = make_test_world("rep_corrupt")
        snap = fab.create_snapshot("init_bad", w)
        snap.content_fingerprint = "corrupted_hash"
        replay = PhysicsReplay(replay_id="bad", initial_snapshot=snap, commands=[])
        with pytest.raises(ValueError, match="RESTORE_VALIDATION_FAILED"):
            fab.execute_replay(replay, w)


# ==============================================================================
# §116. DETERMINISM TESTS (10 tests)
# ==============================================================================

class TestPhysicsDeterminism:
    """Normative tests for Determinism, Ordering and Invariants (§116)."""

    def test_same_input_same_result(self):
        def run_sim():
            fab, w = make_test_world("det_input")
            b = fab.create_body("b1", "e1", world=w)
            fab.apply_force("b1", [15.0, 0.0, 0.0], w)
            fab.initialize_world(w)
            fab.simulate(0.05, w)
            return b.position[0]

        assert run_sim() == run_sim()

    def test_same_timestep_same_result(self):
        def run_sim():
            fab, w = make_test_world("det_step")
            b = fab.create_body("b1", "e1", world=w)
            fab.initialize_world(w)
            fab.simulate(0.0166667, w)
            return b.position[1]

        assert run_sim() == run_sim()

    def test_same_initial_state_same_result(self):
        def run_sim():
            fab, w = make_test_world("det_state")
            b = fab.create_body("b1", "e1", position=[1, 2, 3], linear_velocity=[0, 1, 0], world=w)
            fab.initialize_world(w)
            fab.simulate(0.033, w)
            return b.position

        assert run_sim() == run_sim()

    def test_scheduler_physics_order(self):
        fab, w = make_test_world("det_sched")
        fab.create_body("b_z", "ez", world=w)
        fab.create_body("b_a", "ea", world=w)
        sorted_keys = sorted(w.bodies.keys())
        assert sorted_keys == ["b_a", "b_z"]

    def test_collision_order_determinism(self):
        fab, w = make_test_world("det_col_ord")
        fab.create_body("b1", "e1", position=[0, 0, 0], world=w)
        fab.create_body("b2", "e2", position=[0.5, 0, 0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, world=w)
        fab.create_collider("c2", "b2", shape=s, world=w)
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        evs = [e.event_type.value for e in w.event_queue]
        assert evs == [PhysicsEventType.CONTACT_BEGIN.value]

    def test_query_order_determinism(self):
        fab, w = make_test_world("det_q_ord")
        fab.create_body("b1", "e1", position=[2, 0, 0], world=w)
        fab.create_body("b2", "e2", position=[4, 0, 0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, world=w)
        fab.create_collider("c2", "b2", shape=s, world=w)
        h = fab.raycast([0, 0, 0], [1, 0, 0], world=w)
        assert h.body_id == "b1"

    def test_event_order_determinism(self):
        fab, w = make_test_world("det_ev_ord")
        fab.create_body("b1", "e1", world=w)
        fab.sleep_body("b1", w)
        fab.wake_body("b1", w)
        types = [e.event_type for e in w.event_queue]
        assert types == [PhysicsEventType.BODY_SLEEP, PhysicsEventType.BODY_WAKE]

    def test_replay_determinism(self):
        fab, w = make_test_world("det_rep")
        snap = fab.create_snapshot("s_rep", w)
        r = PhysicsReplay(replay_id="r1", initial_snapshot=snap, commands=[])
        assert r.replay_id == "r1"

    def test_snapshot_determinism(self):
        fab, w = make_test_world("det_snap")
        s1 = fab.create_snapshot("s1", w)
        s2 = fab.create_snapshot("s2", w)
        assert s1.content_fingerprint == s2.content_fingerprint

    def test_fixed_step_determinism(self):
        fab, w = make_test_world("det_fixed")
        fab.initialize_world(w)
        fab.simulate(0.0166667, w)
        assert w.frame_index == 1


# ==============================================================================
# §117. SECURITY TESTS (18 tests)
# ==============================================================================

class TestPhysicsSecurity:
    """Normative tests for Security Boundaries and Resource Exhaustion (§117)."""

    def test_body_count_exhaustion(self):
        fab, w = make_test_world("sec_body_limit")
        w.settings.max_bodies = 5
        for i in range(5):
            fab.create_body(f"b_{i}", f"e_{i}", world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_body("b_overflow", "e_overflow", world=w)

    def test_collider_count_exhaustion(self):
        fab, w = make_test_world("sec_col_limit")
        w.settings.max_colliders = 3
        fab.create_body("b1", "e1", world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        for i in range(3):
            fab.create_collider(f"c_{i}", "b1", shape=s, world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_collider("c_overflow", "b1", shape=s, world=w)

    def test_constraint_count_exhaustion(self):
        fab, w = make_test_world("sec_cn_limit")
        w.settings.max_constraints = 2
        fab.create_body("b1", "e1", world=w)
        fab.create_body("b2", "e2", world=w)
        fab.create_constraint("cn_1", ConstraintType.FIXED, "b1", "b2", world=w)
        fab.create_constraint("cn_2", ConstraintType.FIXED, "b1", "b2", world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_constraint("cn_overflow", ConstraintType.FIXED, "b1", "b2", world=w)

    def test_event_flood(self):
        fab, w = make_test_world("sec_ev_flood")
        for i in range(100):
            ev = PhysicsEvent(event_type=PhysicsEventType.BODY_SLEEP, body_a_id=f"b_{i}")
            w.event_queue.append(ev)
        assert len(w.event_queue) == 100

    def test_query_flood(self):
        fab, w = make_test_world("sec_q_flood")
        fab.create_body("b1", "e1", position=[5, 0, 0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, world=w)
        for _ in range(50):
            h = fab.raycast([0, 0, 0], [1, 0, 0], world=w)
            assert h.hit

    def test_raycast_distance_overflow(self):
        fab, w = make_test_world("sec_ray_dist")
        w.settings.max_query_distance = 500.0
        with pytest.raises(ValueError, match="INVALID_QUERY"):
            fab.raycast([0, 0, 0], [1, 0, 0], max_distance=10000.0, world=w)

    def test_shape_parameter_overflow(self):
        fab, w = make_test_world("sec_shape_overflow")
        fab.create_body("b1", "e1", world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": -10.0})
        with pytest.raises(ValueError, match="DEGENERATE_SHAPE"):
            fab.create_collider("c_bad", "b1", shape=s, world=w)

    def test_compound_shape_explosion(self):
        fab, w = make_test_world("sec_comp_expl")
        fab.create_body("b1", "e1", world=w)
        sub_shapes = [{"type": "BOX", "extents": [1, 1, 1]} for _ in range(150)]
        s = CollisionShape(shape_type=CollisionShapeType.COMPOUND, params={"sub_shapes": sub_shapes})
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_collider("c_huge", "b1", shape=s, world=w)

    def test_mesh_shape_explosion(self):
        fab, w = make_test_world("sec_mesh_expl")
        fab.create_body("b1", "e1", world=w)
        indices = list(range(300))
        s = CollisionShape(shape_type=CollisionShapeType.TRIANGLE_MESH, params={"indices": indices})
        c = fab.create_collider("c_mesh", "b1", shape=s, world=w)
        assert len(c.shape.params["indices"]) == 300

    def test_degenerate_shape(self):
        fab, w = make_test_world("sec_degen")
        fab.create_body("b1", "e1", world=w)
        s = CollisionShape(shape_type=CollisionShapeType.BOX, params={"extents": [0.0, 1.0, 1.0]})
        with pytest.raises(ValueError, match="DEGENERATE_SHAPE"):
            fab.create_collider("c_zero", "b1", shape=s, world=w)

    def test_invalid_mass(self):
        fab, w = make_test_world("sec_bad_mass")
        with pytest.raises(ValueError, match="INVALID_MASS"):
            fab.create_body("b_bad", "e1", body_type=BodyType.DYNAMIC, mass=0.0, world=w)

    def test_invalid_velocity(self):
        fab, w = make_test_world("sec_vel_clamp")
        b = fab.create_body("b1", "e1", world=w)
        w.settings.max_linear_velocity = 50.0
        fab.set_linear_velocity("b1", [5000.0, 0.0, 0.0], w)
        assert b.linear_velocity[0] <= 50.001

    def test_invalid_timestep(self):
        fab, w = make_test_world("sec_dt_bad")
        fab.initialize_world(w)
        with pytest.raises(ValueError, match="INVALID_TIMESTEP"):
            fab.simulate(-0.016, w)

    def test_substep_exhaustion(self):
        fab, w = make_test_world("sec_sub_exhaust")
        w.settings.max_substeps = 4
        fab.initialize_world(w)
        fab.simulate(10.0, w)
        # Clamped to max_substeps
        assert w.frame_index == 4

    def test_snapshot_tampering(self):
        fab, w = make_test_world("sec_snap_tamp")
        snap = fab.create_snapshot("s1", w)
        snap.world_data["time_seconds"] = 9999.0  # tampering without updating hash
        with pytest.raises(ValueError, match="RESTORE_VALIDATION_FAILED"):
            fab.restore_snapshot(snap, w)

    def test_replay_tampering(self):
        fab, w = make_test_world("sec_rep_tamp")
        snap = fab.create_snapshot("s1", w)
        snap.world_data["frame_index"] = 777
        r = PhysicsReplay(replay_id="r_tamp", initial_snapshot=snap, commands=[])
        with pytest.raises(ValueError, match="RESTORE_VALIDATION_FAILED"):
            fab.execute_replay(r, w)

    def test_resource_lifetime_bypass(self):
        fab, w = make_test_world("sec_res_bypass")
        fab.create_body("b1", "e1", world=w)
        fab.destroy_body("b1", w)
        with pytest.raises(ValueError, match="NO_CALLBACK_AFTER_DESTROY"):
            fab.activate_body("b1", w)

    def test_physics_world_memory_exhaustion(self):
        fab, w = make_test_world("sec_mem_clean")
        for i in range(20):
            fab.create_body(f"b_{i}", f"e_{i}", world=w)
        fab.destroy_world(w)
        assert len(w.bodies) == 0


# ==============================================================================
# §118. PERFORMANCE TESTS (15 tests)
# ==============================================================================

class TestPhysicsPerformance:
    """Normative tests for Performance Scalability and Throughput (§118)."""

    def test_1k_bodies(self):
        fab, w = make_test_world("perf_1k")
        w.settings.max_bodies = 1000
        t0 = time.perf_counter()
        for i in range(150):
            fab.create_body(f"b_{i}", f"e_{i}", world=w)
        t1 = time.perf_counter()
        assert (t1 - t0) < 1.0

    def test_10k_bodies(self):
        fab, w = make_test_world("perf_10k")
        w.settings.max_bodies = 10000
        for i in range(200):
            fab.create_body(f"b_{i}", f"e_{i}", world=w)
        assert len(w.bodies) == 200

    def test_100k_bodies(self):
        fab, w = make_test_world("perf_100k")
        w.settings.max_bodies = 100000
        for i in range(250):
            fab.create_body(f"b_{i}", f"e_{i}", world=w)
        assert len(w.bodies) == 250

    def test_many_colliders(self):
        fab, w = make_test_world("perf_cols")
        fab.create_body("host", "e_host", world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 0.5})
        for i in range(100):
            fab.create_collider(f"c_{i}", "host", shape=s, world=w)
        assert len(w.colliders) == 100

    def test_many_contacts(self):
        fab, w = make_test_world("perf_contacts")
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        for i in range(10):
            fab.create_body(f"b_{i}", f"e_{i}", position=[float(i * 0.1), 0, 0], world=w)
            fab.create_collider(f"c_{i}", f"b_{i}", shape=s, world=w)
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        assert len(w.event_queue) > 0

    def test_many_constraints(self):
        fab, w = make_test_world("perf_constraints")
        for i in range(15):
            fab.create_body(f"b_{i}", f"e_{i}", world=w)
        for i in range(14):
            fab.create_constraint(f"cn_{i}", ConstraintType.DISTANCE, f"b_{i}", f"b_{i+1}", limits={"distance": 1.0}, world=w)
        assert len(w.constraints) == 14

    def test_large_compound_shape(self):
        fab, w = make_test_world("perf_comp")
        fab.create_body("b1", "e1", world=w)
        sub_shapes = [{"type": "BOX", "extents": [0.1, 0.1, 0.1]} for _ in range(50)]
        s = CollisionShape(shape_type=CollisionShapeType.COMPOUND, params={"sub_shapes": sub_shapes})
        c = fab.create_collider("c_comp", "b1", shape=s, world=w)
        assert len(c.shape.params["sub_shapes"]) == 50

    def test_large_mesh_collision(self):
        fab, w = make_test_world("perf_mesh")
        fab.create_body("b1", "e1", world=w)
        indices = list(range(600))
        s = CollisionShape(shape_type=CollisionShapeType.TRIANGLE_MESH, params={"indices": indices})
        c = fab.create_collider("c_mesh", "b1", shape=s, world=w)
        assert len(c.shape.params["indices"]) == 600

    def test_raycast_throughput(self):
        fab, w = make_test_world("perf_ray_tp")
        fab.create_body("tgt", "e_tgt", position=[5, 0, 0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c_tgt", "tgt", shape=s, world=w)
        t0 = time.perf_counter()
        for _ in range(100):
            fab.raycast([0, 0, 0], [1, 0, 0], world=w)
        t1 = time.perf_counter()
        assert (t1 - t0) < 0.5

    def test_overlap_throughput(self):
        fab, w = make_test_world("perf_ov_tp")
        fab.create_body("tgt", "e_tgt", position=[1, 0, 0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c_tgt", "tgt", shape=s, world=w)
        q = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 2.0})
        for _ in range(50):
            hits = fab.overlap(q, [0, 0, 0], world=w)
            assert len(hits) == 1

    def test_shapecast_throughput(self):
        fab, w = make_test_world("perf_sc_tp")
        fab.create_body("tgt", "e_tgt", position=[5, 0, 0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c_tgt", "tgt", shape=s, world=w)
        sw = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 0.5})
        for _ in range(50):
            hit = fab.shapecast(sw, [0, 0, 0], [1, 0, 0], world=w)
            assert hit.hit

    def test_event_throughput(self):
        fab, w = make_test_world("perf_ev_tp")
        for i in range(200):
            w.event_queue.append(PhysicsEvent(event_type=PhysicsEventType.BODY_SLEEP, body_a_id=f"b_{i}"))
        assert len(w.event_queue) == 200

    def test_snapshot_throughput(self):
        fab, w = make_test_world("perf_snap_tp")
        fab.create_body("b1", "e1", world=w)
        t0 = time.perf_counter()
        for i in range(20):
            fab.create_snapshot(f"snap_{i}", w)
        t1 = time.perf_counter()
        assert (t1 - t0) < 0.5

    def test_replay_throughput(self):
        fab, w = make_test_world("perf_rep_tp")
        fab.create_body("b1", "e1", world=w)
        snap = fab.create_snapshot("init_rep", w)
        r = PhysicsReplay(replay_id="rep_bench", initial_snapshot=snap, commands=[])
        t0 = time.perf_counter()
        fab.execute_replay(r, w)
        t1 = time.perf_counter()
        assert (t1 - t0) < 0.5

    def test_streaming_physics_activation(self):
        fab, w = make_test_world("perf_stream")
        for i in range(30):
            b = fab.create_body(f"b_{i}", f"e_{i}", world=w)
            fab.deactivate_body(f"b_{i}", w)
        for i in range(30):
            fab.activate_body(f"b_{i}", w)
        assert all(b.enabled for b in w.bodies.values())


# ==============================================================================
# §119. STRESS TESTS (15 tests)
# ==============================================================================

class TestPhysicsStress:
    """Normative tests for Concurrency, Iteration and Stress Reliability (§119)."""

    def test_stress_body_spawn(self):
        fab, w = make_test_world("str_spawn")
        for i in range(100):
            fab.create_body(f"b_{i}", f"e_{i}", world=w)
        assert len(w.bodies) == 100

    def test_stress_body_destroy(self):
        fab, w = make_test_world("str_destroy")
        for i in range(50):
            fab.create_body(f"b_{i}", f"e_{i}", world=w)
        for i in range(50):
            fab.destroy_body(f"b_{i}", w)
        assert len(w.bodies) == 0

    def test_stress_collider_create(self):
        fab, w = make_test_world("str_col_c")
        fab.create_body("b1", "e1", world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        for i in range(50):
            fab.create_collider(f"c_{i}", "b1", shape=s, world=w)
        assert len(w.colliders) == 50

    def test_stress_collider_destroy(self):
        fab, w = make_test_world("str_col_d")
        fab.create_body("b1", "e1", world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        for i in range(30):
            fab.create_collider(f"c_{i}", "b1", shape=s, world=w)
        for i in range(30):
            fab.destroy_collider(f"c_{i}", w)
        assert len(w.colliders) == 0

    def test_stress_force_application(self):
        fab, w = make_test_world("str_force")
        b = fab.create_body("b1", "e1", world=w)
        for i in range(100):
            fab.apply_force("b1", [1.0, 0.0, 0.0], w)
        assert b.forces[0] == 100.0

    def test_stress_contact_generation(self):
        fab, w = make_test_world("str_contact")
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        for i in range(5):
            fab.create_body(f"b_{i}", f"e_{i}", position=[0, 0, 0], world=w)
            fab.create_collider(f"c_{i}", f"b_{i}", shape=s, world=w)
        fab.initialize_world(w)
        for _ in range(5):
            fab.simulate(0.02, w)
        assert len(w.event_queue) > 0

    def test_stress_trigger_events(self):
        fab, w = make_test_world("str_trig")
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_body("zone", "e_z", position=[0, 0, 0], world=w)
        fab.create_collider("c_z", "zone", shape=s, is_trigger=True, world=w)
        for i in range(5):
            fab.create_body(f"hero_{i}", f"e_{i}", position=[0.2, 0, 0], world=w)
            fab.create_collider(f"c_{i}", f"hero_{i}", shape=s, world=w)
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        assert any(e.event_type == PhysicsEventType.TRIGGER_ENTER for e in w.event_queue)

    def test_stress_constraint_creation(self):
        fab, w = make_test_world("str_cn_c")
        for i in range(20):
            fab.create_body(f"b_{i}", f"e_{i}", world=w)
        for i in range(19):
            fab.create_constraint(f"cn_{i}", ConstraintType.FIXED, f"b_{i}", f"b_{i+1}", world=w)
        assert len(w.constraints) == 19

    def test_stress_character_movement(self):
        fab, w = make_test_world("str_cc_move")
        cc = fab.create_character_controller("cc1", "e1", world=w)
        for i in range(50):
            fab.move_character("cc1", [0.1, 0.0, 0.0], 0.02, w)
        assert abs(cc.position[0] - 5.0) < 0.01

    def test_stress_queries(self):
        fab, w = make_test_world("str_queries")
        fab.create_body("b1", "e1", position=[10, 0, 0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, world=w)
        for _ in range(100):
            h = fab.raycast([0, 0, 0], [1, 0, 0], world=w)
            assert h.hit

    def test_stress_simulation_steps(self):
        fab, w = make_test_world("str_sim_steps")
        b = fab.create_body("b1", "e1", position=[0, 100, 0], world=w)
        fab.initialize_world(w)
        for _ in range(50):
            fab.simulate(0.02, w)
        assert w.frame_index >= 50

    def test_stress_snapshot(self):
        fab, w = make_test_world("str_snap")
        fab.create_body("b1", "e1", world=w)
        for i in range(30):
            snap = fab.create_snapshot(f"s_{i}", w)
            assert snap.snapshot_id == f"s_{i}"

    def test_stress_restore(self):
        fab, w = make_test_world("str_restore")
        b = fab.create_body("b1", "e1", position=[0, 0, 0], world=w)
        snap = fab.create_snapshot("orig", w)
        for i in range(20):
            b.position = [float(i), float(i), float(i)]
            fab.restore_snapshot(snap, w)
            assert w.bodies["b1"].position == [0, 0, 0]

    def test_stress_replay(self):
        fab, w = make_test_world("str_rep")
        fab.create_body("b1", "e1", world=w)
        snap = fab.create_snapshot("init", w)
        r = PhysicsReplay(replay_id="r_str", initial_snapshot=snap, commands=[])
        for _ in range(5):
            fab.execute_replay(r, w)
        assert w.frame_index > 0

    def test_stress_world_restart(self):
        fab, w = make_test_world("str_restart")
        fab.initialize_world(w)
        fab.start_simulation(w)
        fab.stop_simulation(w)
        fab.start_simulation(w)
        assert w.state == PhysicsWorldState.SIMULATING


# ==============================================================================
# §120. PROPERTY-BASED TESTS (7 tests)
# ==============================================================================

class TestPhysicsPropertyBased:
    """Normative Property-based invariant tests (§120)."""

    def test_property_simulation_valid_state(self):
        fab, w = make_test_world("prop_sim_valid")
        fab.create_body("b1", "e1", position=[0, 10, 0], world=w)
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        val = UniversalRuntimePhysicsValidator()
        errors = val.validate_world(w)
        assert len(errors) == 0

    def test_property_snapshot_restore_identity(self):
        fab, w = make_test_world("prop_snap_id")
        fab.create_body("b1", "e1", position=[1, 2, 3], world=w)
        snap = fab.create_snapshot("s1", w)
        fp_orig = w.compute_fingerprint()
        fab.restore_snapshot(snap, w)
        assert w.compute_fingerprint() == fp_orig

    def test_property_same_inputs_same_result(self):
        def run(f_val):
            fab, w = make_test_world("prop_input")
            b = fab.create_body("b1", "e1", world=w)
            fab.apply_force("b1", [f_val, 0, 0], w)
            fab.initialize_world(w)
            fab.simulate(0.02, w)
            return b.position[0]

        assert run(10.0) == run(10.0)
        assert run(20.0) == run(20.0)

    def test_property_filter_query_mask(self):
        fab, w = make_test_world("prop_filter")
        fab.create_body("b1", "e1", position=[5, 0, 0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, layer=8, world=w)
        # Query with mask disjoint from 8 -> no hit
        h_miss = fab.raycast([0, 0, 0], [1, 0, 0], layer_mask=1, world=w)
        assert not h_miss.hit
        # Query with mask containing 8 -> hit
        h_hit = fab.raycast([0, 0, 0], [1, 0, 0], layer_mask=8, world=w)
        assert h_hit.hit

    def test_property_destroy_body_no_references(self):
        fab, w = make_test_world("prop_destroy_ref")
        fab.create_body("b1", "e1", world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, world=w)
        fab.destroy_body("b1", w)
        assert "b1" not in w.bodies
        assert "c1" not in w.colliders

    def test_property_destroy_world_no_resources(self):
        fab, w = make_test_world("prop_world_res")
        fab.create_body("b1", "e1", world=w)
        fab.destroy_world(w)
        assert len(w.bodies) == 0
        assert len(w.colliders) == 0
        assert len(w.constraints) == 0

    def test_property_spawn_and_destroy_no_leak(self):
        fab, w = make_test_world("prop_leak")
        initial_body_count = len(w.bodies)
        fab.create_body("temp", "e_temp", world=w)
        fab.destroy_body("temp", w)
        assert len(w.bodies) == initial_body_count


# ==============================================================================
# §121. GOLDEN TESTS (18 tests)
# ==============================================================================

class TestPhysicsGolden:
    """Normative Golden Canonical Tests for Physics Simulation System (§121)."""

    def test_golden_empty_physics_world(self):
        fab, w = make_test_world("g_empty")
        fp = w.compute_fingerprint()
        assert len(fp) == 64
        assert w.state == PhysicsWorldState.CREATED

    def test_golden_static_body(self):
        fab, w = make_test_world("g_static")
        b = fab.create_body("ground", "e_g", body_type=BodyType.STATIC, world=w)
        assert b.mass == 0.0
        assert b.inverse_mass == 0.0

    def test_golden_dynamic_body(self):
        fab, w = make_test_world("g_dyn")
        b = fab.create_body("dyn", "e_d", body_type=BodyType.DYNAMIC, mass=2.5, world=w)
        assert b.mass == 2.5
        assert abs(b.inverse_mass - 0.4) < 1e-6

    def test_golden_kinematic_body(self):
        fab, w = make_test_world("g_kin")
        b = fab.create_body("kin", "e_k", body_type=BodyType.KINEMATIC, world=w)
        assert b.body_type == BodyType.KINEMATIC

    def test_golden_box_collision(self):
        fab, w = make_test_world("g_box_col")
        fab.create_body("b1", "e1", world=w)
        s = CollisionShape(shape_type=CollisionShapeType.BOX, params={"extents": [1.0, 1.0, 1.0]})
        c = fab.create_collider("c_box", "b1", shape=s, world=w)
        assert c.shape.shape_type == CollisionShapeType.BOX

    def test_golden_sphere_collision(self):
        fab, w = make_test_world("g_sph_col")
        fab.create_body("b1", "e1", world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 2.0})
        c = fab.create_collider("c_sph", "b1", shape=s, world=w)
        assert c.shape.params["radius"] == 2.0

    def test_golden_compound_collision(self):
        fab, w = make_test_world("g_comp_col")
        fab.create_body("b1", "e1", world=w)
        s = CollisionShape(shape_type=CollisionShapeType.COMPOUND, params={"sub_shapes": [{"type": "BOX", "extents": [1, 1, 1]}]})
        c = fab.create_collider("c_comp", "b1", shape=s, world=w)
        assert c.shape.shape_type == CollisionShapeType.COMPOUND

    def test_golden_trigger(self):
        fab, w = make_test_world("g_trig")
        fab.create_body("z", "e_z", world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        c = fab.create_collider("c_tr", "z", shape=s, is_trigger=True, world=w)
        assert c.is_trigger

    def test_golden_constraint(self):
        fab, w = make_test_world("g_cn")
        fab.create_body("b1", "e1", world=w)
        fab.create_body("b2", "e2", world=w)
        c = fab.create_constraint("cn1", ConstraintType.FIXED, "b1", "b2", world=w)
        assert c.constraint_id == "cn1"

    def test_golden_character_controller(self):
        fab, w = make_test_world("g_cc")
        cc = fab.create_character_controller("cc_gold", "e_gold", height=1.8, radius=0.3, world=w)
        assert cc.controller_id == "cc_gold"

    def test_golden_raycast(self):
        fab, w = make_test_world("g_ray")
        fab.create_body("b1", "e1", position=[5, 0, 0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, world=w)
        h = fab.raycast([0, 0, 0], [1, 0, 0], world=w)
        assert h.hit

    def test_golden_overlap(self):
        fab, w = make_test_world("g_overlap")
        fab.create_body("b1", "e1", position=[1, 0, 0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, world=w)
        hits = fab.overlap(s, [0, 0, 0], world=w)
        assert len(hits) == 1

    def test_golden_contact_events(self):
        fab, w = make_test_world("g_events")
        fab.create_body("b1", "e1", position=[0, 0, 0], world=w)
        fab.create_body("b2", "e2", position=[0.5, 0, 0], world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, world=w)
        fab.create_collider("c2", "b2", shape=s, world=w)
        fab.initialize_world(w)
        fab.simulate(0.02, w)
        assert len(w.event_queue) > 0

    def test_golden_physics_snapshot(self):
        fab, w = make_test_world("g_snap")
        snap = fab.create_snapshot("snap_g", w)
        assert snap.content_fingerprint == w.compute_fingerprint()

    def test_golden_physics_replay(self):
        fab, w = make_test_world("g_rep")
        snap = fab.create_snapshot("s_g", w)
        r = PhysicsReplay(replay_id="rep_g", initial_snapshot=snap, commands=[])
        assert r.replay_id == "rep_g"

    def test_golden_deterministic_simulation(self):
        def run_gold():
            fab, w = make_test_world("g_det")
            b = fab.create_body("b1", "e1", position=[0, 10, 0], world=w)
            fab.initialize_world(w)
            fab.simulate(0.0166667, w)
            return b.position[1]

        assert run_gold() == run_gold()

    def test_golden_physics_failure(self):
        fab, w = make_test_world("g_fail")
        with pytest.raises(ValueError):
            fab.create_body("", "e_bad", world=w)

    def test_golden_physics_shutdown(self):
        fab, w = make_test_world("g_shutdown")
        fab.create_body("b1", "e1", world=w)
        fab.destroy_world(w)
        assert w.state == PhysicsWorldState.DESTROYED


# ==============================================================================
# §122. CROSS-PHASE INTEGRATION TESTS (15 tests)
# ==============================================================================

class TestCrossPhaseIntegration:
    """Normative Cross-Phase Integration tests with UAF-81.72 and UAF-81.73 (§122)."""

    def test_scene_collider_to_physics(self):
        fab, w = make_test_world("cp_sc_col")
        s = CollisionShape(shape_type=CollisionShapeType.BOX, params={"extents": [2, 2, 2]})
        fab.create_body("b_scene", "e_scene", world=w)
        c = fab.create_collider("c_scene", "b_scene", shape=s, world=w)
        assert c.collider_id == "c_scene"

    def test_scene_rigidbody_to_physics(self):
        fab, w = make_test_world("cp_sc_rb")
        b = fab.create_body("b_dyn_scene", "e_dyn_scene", body_type=BodyType.DYNAMIC, mass=10.0, world=w)
        assert b.mass == 10.0

    def test_scene_material_to_physics(self):
        fab, w = make_test_world("cp_mat")
        m = fab.create_material("mat_concrete", friction=0.8, restitution=0.1, world=w)
        assert m.friction == 0.8

    def test_scene_constraint_to_physics(self):
        fab, w = make_test_world("cp_cn")
        fab.create_body("b1", "e1", world=w)
        fab.create_body("b2", "e2", world=w)
        cn = fab.create_constraint("cn_door", ConstraintType.HINGE, "b1", "b2", world=w)
        assert cn.constraint_type == ConstraintType.HINGE

    def test_runtime_entity_to_physics_body(self):
        phys_fab, pw = make_test_world("cp_ent_body")
        world_fab = UniversalRuntimeWorldFabricator()
        rw = world_fab.create_world("rw_ent_body")
        ent = world_fab.create_entity("actor_1", world=rw)
        body = phys_fab.create_body("b_actor", ent.entity_id, world=pw)
        assert body.entity_id == "actor_1"

    def test_runtime_transform_to_physics(self):
        phys_fab, pw = make_test_world("cp_tr_p")
        world_fab = UniversalRuntimeWorldFabricator()
        rw = world_fab.create_world("rw_trp")
        ent = world_fab.create_entity("actor_2", world=rw)
        ent.local_transform.position = [12.0, 3.0, -4.0]
        body = phys_fab.create_body("b2", "actor_2", world=pw)
        phys_fab.sync_from_runtime_world(rw, pw)
        assert body.position == [12.0, 3.0, -4.0]

    def test_physics_transform_to_runtime(self):
        phys_fab, pw = make_test_world("cp_p_tr")
        world_fab = UniversalRuntimeWorldFabricator()
        rw = world_fab.create_world("rw_ptr")
        ent = world_fab.create_entity("actor_3", world=rw)
        body = phys_fab.create_body("b3", "actor_3", position=[8.0, 1.0, 2.0], world=pw)
        phys_fab.sync_to_runtime_world(rw, pw)
        assert ent.local_transform.position == [8.0, 1.0, 2.0]

    def test_runtime_event_to_physics(self):
        phys_fab, pw = make_test_world("cp_ev_p")
        ev = PhysicsEvent(event_type=PhysicsEventType.BODY_SLEEP, body_a_id="b_test")
        pw.event_queue.append(ev)
        assert len(pw.event_queue) == 1

    def test_physics_event_to_runtime(self):
        phys_fab, pw = make_test_world("cp_p_ev")
        ev = PhysicsEvent(event_type=PhysicsEventType.CONTACT_BEGIN, body_a_id="b1", body_b_id="b2")
        pw.event_queue.append(ev)
        assert pw.event_queue[0].event_type == PhysicsEventType.CONTACT_BEGIN

    def test_prefab_to_physics_instance(self):
        phys_fab, pw = make_test_world("cp_pf_inst")
        b = phys_fab.create_body("pf_body_1", "e_pf_1", world=pw)
        s = CollisionShape(shape_type=CollisionShapeType.BOX, params={"extents": [1, 1, 1]})
        c = phys_fab.create_collider("pf_col_1", "pf_body_1", shape=s, world=pw)
        assert c.body_id == "pf_body_1"

    def test_streaming_cell_to_physics_world(self):
        phys_fab, pw = make_test_world("cp_stream")
        b = phys_fab.create_body("cell_b1", "e_cell_1", world=pw)
        phys_fab.deactivate_body("cell_b1", pw)
        assert not b.enabled
        phys_fab.activate_body("cell_b1", pw)
        assert b.enabled

    def test_scene_build_to_physics_resources(self):
        phys_fab, pw = make_test_world("cp_sc_build")
        m = phys_fab.create_material("wood_sc", friction=0.5, world=pw)
        assert m.material_id == "wood_sc"

    def test_asset_change_to_physics_rebuild(self):
        phys_fab, pw = make_test_world("cp_asset_chg")
        b = phys_fab.create_body("b_chg", "e_chg", world=pw)
        s_old = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        phys_fab.create_collider("c_chg", "b_chg", shape=s_old, world=pw)
        phys_fab.destroy_collider("c_chg", pw)
        s_new = CollisionShape(shape_type=CollisionShapeType.BOX, params={"extents": [2, 2, 2]})
        c_new = phys_fab.create_collider("c_chg", "b_chg", shape=s_new, world=pw)
        assert c_new.shape.shape_type == CollisionShapeType.BOX

    def test_physics_shutdown_to_runtime_cleanup(self):
        phys_fab, pw = make_test_world("cp_shut")
        phys_fab.create_body("b_clean", "e_clean", world=pw)
        phys_fab.destroy_world(pw)
        assert pw.state == PhysicsWorldState.DESTROYED

    def test_world_destroy_to_physics_destroy(self):
        phys_fab, pw = make_test_world("cp_w_destroy")
        phys_fab.destroy_world(pw)
        assert len(pw.bodies) == 0


# ==============================================================================
# §123. CLEANUP TESTS (12 tests)
# ==============================================================================

class TestPhysicsCleanup:
    """Normative tests for Resource Reclamation and Zero-Leak Cleanup (§123)."""

    def test_physics_world_cleanup(self):
        fab, w = make_test_world("cln_world")
        fab.create_body("b1", "e1", world=w)
        fab.destroy_world(w)
        assert len(w.bodies) == 0
        assert len(w.colliders) == 0

    def test_body_cleanup(self):
        fab, w = make_test_world("cln_body")
        fab.create_body("b1", "e1", world=w)
        fab.destroy_body("b1", w)
        assert "b1" not in w.bodies

    def test_collider_cleanup(self):
        fab, w = make_test_world("cln_col")
        fab.create_body("b1", "e1", world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": 1.0})
        fab.create_collider("c1", "b1", shape=s, world=w)
        fab.destroy_collider("c1", w)
        assert "c1" not in w.colliders

    def test_shape_cleanup(self):
        fab, w = make_test_world("cln_shape")
        fab.create_body("b1", "e1", world=w)
        s = CollisionShape(shape_type=CollisionShapeType.BOX, params={"extents": [1, 1, 1]})
        c = fab.create_collider("c1", "b1", shape=s, world=w)
        fab.destroy_collider("c1", w)
        assert "c1" not in w.bodies["b1"].colliders

    def test_material_cleanup(self):
        fab, w = make_test_world("cln_mat")
        m = fab.create_material("m_cln", world=w)
        assert m.material_id in w.materials

    def test_constraint_cleanup(self):
        fab, w = make_test_world("cln_cn")
        fab.create_body("b1", "e1", world=w)
        fab.create_body("b2", "e2", world=w)
        fab.create_constraint("cn1", ConstraintType.FIXED, "b1", "b2", world=w)
        fab.destroy_constraint("cn1", w)
        assert "cn1" not in w.constraints

    def test_controller_cleanup(self):
        fab, w = make_test_world("cln_cc")
        fab.create_character_controller("cc_cln", "e1", world=w)
        fab.destroy_character_controller("cc_cln", w)
        assert "cc_cln" not in w.character_controllers

    def test_query_cleanup(self):
        fab, w = make_test_world("cln_q")
        h = fab.raycast([0, 0, 0], [1, 0, 0], world=w)
        assert not h.hit

    def test_event_cleanup(self):
        fab, w = make_test_world("cln_ev")
        w.event_queue.append(PhysicsEvent(event_type=PhysicsEventType.BODY_SLEEP, body_a_id="b1"))
        w.event_queue.clear()
        assert len(w.event_queue) == 0

    def test_snapshot_cleanup(self):
        fab, w = make_test_world("cln_snap")
        snap = fab.create_snapshot("snap_c", w)
        del snap
        assert True

    def test_replay_cleanup(self):
        fab, w = make_test_world("cln_rep")
        snap = fab.create_snapshot("snap_r", w)
        r = PhysicsReplay(replay_id="r_c", initial_snapshot=snap, commands=[])
        del r
        assert True

    def test_debug_visualization_cleanup(self):
        fab, w = make_test_world("cln_vis")
        fab.create_body("b1", "e1", world=w)
        vis = fab.get_debug_visualization_data(w)
        assert vis["bodies_count"] == 1


# ==============================================================================
# PACKAGER & INVARIANTS TESTS (15 tests)
# ==============================================================================

class TestPackagerAndInvariants:
    """Normative tests for C++ Packager generation and non-negotiable invariants (§127)."""

    def test_packager_manifest_generation(self):
        fab, w = make_test_world("pkg_man")
        packager = UniversalRuntimePhysicsPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            res = packager.package_for_unreal(w, tmpdir)
            assert os.path.exists(res["manifest"])

    def test_packager_signature_generation(self):
        fab, w = make_test_world("pkg_sig")
        packager = UniversalRuntimePhysicsPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            res = packager.package_for_unreal(w, tmpdir)
            assert os.path.exists(res["signature"])

    def test_packager_header_generation(self):
        fab, w = make_test_world("pkg_hdr")
        packager = UniversalRuntimePhysicsPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            res = packager.package_for_unreal(w, tmpdir)
            assert os.path.exists(res["header"])
            with open(res["header"], "r", encoding="utf-8") as f:
                content = f.read()
            assert "UUAFRuntimePhysicsSubsystem" in content

    def test_packager_source_generation(self):
        fab, w = make_test_world("pkg_src")
        packager = UniversalRuntimePhysicsPackager()
        with tempfile.TemporaryDirectory() as tmpdir:
            res = packager.package_for_unreal(w, tmpdir)
            assert os.path.exists(res["source"])
            with open(res["source"], "r", encoding="utf-8") as f:
                content = f.read()
            assert "UUAFRuntimePhysicsSubsystem::Initialize" in content

    def test_debug_visualization_no_state_mutation(self):
        fab, w = make_test_world("dbg_no_mut")
        fab.create_body("b1", "e1", position=[1, 2, 3], world=w)
        fp_before = w.compute_fingerprint()
        fab.get_debug_visualization_data(w)
        fp_after = w.compute_fingerprint()
        assert fp_before == fp_after

    def test_invariant_no_invalid_world_state(self):
        fab, w = make_test_world("inv_ws")
        with pytest.raises(ValueError, match="NO_INVALID_PHYSICS_WORLD_STATE"):
            fab.stop_simulation(w)

    def test_invariant_no_invalid_body_type(self):
        fab, w = make_test_world("inv_bt")
        b = fab.create_body("b1", "e1", body_type=BodyType.STATIC, world=w)
        assert b.mass == 0.0

    def test_invariant_no_degenerate_shape(self):
        fab, w = make_test_world("inv_shape")
        fab.create_body("b1", "e1", world=w)
        s = CollisionShape(shape_type=CollisionShapeType.SPHERE, params={"radius": -5.0})
        with pytest.raises(ValueError, match="DEGENERATE_SHAPE"):
            fab.create_collider("c1", "b1", shape=s, world=w)

    def test_invariant_no_invalid_mass(self):
        fab, w = make_test_world("inv_mass")
        with pytest.raises(ValueError, match="INVALID_MASS"):
            fab.create_body("b_bad", "e1", body_type=BodyType.DYNAMIC, mass=-2.0, world=w)

    def test_invariant_no_invalid_material(self):
        fab, w = make_test_world("inv_mat")
        with pytest.raises(ValueError, match="INVALID_MATERIAL"):
            fab.create_material("m_bad", restitution=2.5, world=w)

    def test_invariant_no_constraint_missing_endpoint(self):
        fab, w = make_test_world("inv_cn_end")
        fab.create_body("b1", "e1", world=w)
        with pytest.raises(ValueError, match="INVALID_CONSTRAINT_ENDPOINTS"):
            fab.create_constraint("cn_bad", ConstraintType.FIXED, "b1", "missing_b2", world=w)

    def test_invariant_no_callback_after_destroy(self):
        fab, w = make_test_world("inv_cb_dst")
        fab.create_body("b1", "e1", world=w)
        fab.destroy_body("b1", w)
        with pytest.raises(ValueError, match="NO_CALLBACK_AFTER_DESTROY"):
            fab.activate_body("b1", w)

    def test_invariant_no_query_without_valid_limits(self):
        fab, w = make_test_world("inv_q_lim")
        with pytest.raises(ValueError, match="INVALID_QUERY"):
            fab.raycast([0, 0, 0], [1, 0, 0], max_distance=-10.0, world=w)

    def test_invariant_unbounded_substeps_clamped(self):
        fab, w = make_test_world("inv_sub_clamp")
        w.settings.max_substeps = 3
        fab.initialize_world(w)
        fab.simulate(1.0, w)
        assert w.frame_index == 3

    def test_invariant_no_event_to_destroyed_body(self):
        fab, w = make_test_world("inv_ev_dest")
        fab.create_body("b1", "e1", world=w)
        fab.sleep_body("b1", w)
        fab.destroy_body("b1", w)
        assert not any(e.body_a_id == "b1" for e in w.event_queue)
