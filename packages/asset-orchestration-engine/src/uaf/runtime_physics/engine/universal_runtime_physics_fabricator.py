"""
Universal Runtime Physics Fabricator and Simulation Engine (UAF-81.74).
Core engine for physics simulation, rigid bodies, collision detection, triggers,
character controllers, raycasts, constraints, snapshots, and runtime world sync.
"""

from __future__ import annotations
import copy
import hashlib
import json
import math
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from ..models.definition import (
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
)


def _vec3_add(a: List[float], b: List[float]) -> List[float]:
    return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]


def _vec3_sub(a: List[float], b: List[float]) -> List[float]:
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def _vec3_scale(a: List[float], s: float) -> List[float]:
    return [a[0] * s, a[1] * s, a[2] * s]


def _vec3_dot(a: List[float], b: List[float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _vec3_length(a: List[float]) -> float:
    return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])


def _vec3_normalize(a: List[float]) -> List[float]:
    l = _vec3_length(a)
    if l > 1e-7:
        return [a[0] / l, a[1] / l, a[2] / l]
    return [0.0, 1.0, 0.0]


class UniversalRuntimePhysicsFabricator:
    """Core fabricator and execution engine for physics simulation."""

    def __init__(self):
        self.worlds: Dict[str, PhysicsWorld] = {}
        self.active_world: Optional[PhysicsWorld] = None
        self._previous_contacts: Set[Tuple[str, str]] = set()
        self._previous_triggers: Set[Tuple[str, str]] = set()

    # --------------------------------------------------------------------------
    # 1. Physics World Lifecycle
    # --------------------------------------------------------------------------

    def create_world(
        self,
        physics_world_id: str,
        runtime_world_id: str = "",
        settings: Optional[PhysicsSimulationSettings] = None,
    ) -> PhysicsWorld:
        if not physics_world_id or not physics_world_id.strip():
            raise ValueError("INVALID_PHYSICS_WORLD_ID: World ID cannot be empty.")
        if physics_world_id in self.worlds:
            raise ValueError(f"DUPLICATE_PHYSICS_WORLD_ID: World '{physics_world_id}' already exists.")

        world = PhysicsWorld(
            physics_world_id=physics_world_id,
            runtime_world_id=runtime_world_id,
            state=PhysicsWorldState.CREATED,
            settings=settings or PhysicsSimulationSettings(),
        )
        self.worlds[physics_world_id] = world
        self.active_world = world
        return world

    def get_world(self, physics_world_id: str) -> Optional[PhysicsWorld]:
        return self.worlds.get(physics_world_id)

    def initialize_world(self, world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state not in (PhysicsWorldState.CREATED, PhysicsWorldState.INITIALIZING):
            raise ValueError(f"NO_INVALID_PHYSICS_WORLD_STATE: Cannot initialize world from state '{target.state.value}'.")

        target.state = PhysicsWorldState.READY
        target.content_fingerprint = target.compute_fingerprint()

    def start_simulation(self, world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state not in (PhysicsWorldState.READY, PhysicsWorldState.PAUSED, PhysicsWorldState.STOPPED):
            raise ValueError(f"NO_INVALID_PHYSICS_WORLD_STATE: Cannot start simulation from state '{target.state.value}'.")

        target.state = PhysicsWorldState.SIMULATING

    def pause_simulation(self, world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state != PhysicsWorldState.SIMULATING:
            raise ValueError(f"NO_INVALID_PHYSICS_WORLD_STATE: Cannot pause from state '{target.state.value}'.")

        target.state = PhysicsWorldState.PAUSED

    def stop_simulation(self, world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state not in (PhysicsWorldState.SIMULATING, PhysicsWorldState.PAUSED):
            raise ValueError(f"NO_INVALID_PHYSICS_WORLD_STATE: Cannot stop from state '{target.state.value}'.")

        target.state = PhysicsWorldState.STOPPED

    def destroy_world(self, world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        for bid in list(target.bodies.keys()):
            self.destroy_body(bid, target)

        target.colliders.clear()
        target.constraints.clear()
        target.character_controllers.clear()
        target.materials.clear()
        target.event_queue.clear()
        target.state = PhysicsWorldState.DESTROYED

    # --------------------------------------------------------------------------
    # 2. Physics Body Management
    # --------------------------------------------------------------------------

    def create_body(
        self,
        body_id: str,
        entity_id: str,
        body_type: BodyType = BodyType.DYNAMIC,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        linear_velocity: Optional[List[float]] = None,
        angular_velocity: Optional[List[float]] = None,
        mass: float = 1.0,
        linear_damping: float = 0.01,
        angular_damping: float = 0.05,
        gravity_scale: float = 1.0,
        world: Optional[PhysicsWorld] = None,
    ) -> PhysicsBody:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if not body_id or not body_id.strip():
            raise ValueError("INVALID_BODY_ID: Body ID cannot be empty.")
        if body_id in target.bodies:
            raise ValueError(f"DUPLICATE_BODY_ID: Body '{body_id}' already exists.")
        if len(target.bodies) >= target.settings.max_bodies:
            raise ValueError("SECURITY_VIOLATION: Max bodies limit exceeded.")

        if body_type == BodyType.DYNAMIC:
            if mass <= 0.0:
                raise ValueError(f"INVALID_MASS: Dynamic body must have positive mass, got {mass}.")
        else:
            mass = 0.0

        if linear_damping < 0.0 or angular_damping < 0.0:
            raise ValueError("INVALID_DAMPING: Damping cannot be negative.")

        body = PhysicsBody(
            body_id=body_id,
            entity_id=entity_id,
            body_type=body_type,
            position=position or [0.0, 0.0, 0.0],
            rotation=rotation or [0.0, 0.0, 0.0, 1.0],
            linear_velocity=linear_velocity or [0.0, 0.0, 0.0],
            angular_velocity=angular_velocity or [0.0, 0.0, 0.0],
            mass=mass,
            linear_damping=linear_damping,
            angular_damping=angular_damping,
            gravity_scale=gravity_scale,
        )
        target.bodies[body_id] = body
        return body

    def get_body(self, body_id: str, world: Optional[PhysicsWorld] = None) -> Optional[PhysicsBody]:
        target = world or self.active_world
        return target.bodies.get(body_id) if target else None

    def activate_body(self, body_id: str, world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if body_id in getattr(target, "destroyed_body_ids", set()):
            raise ValueError(f"NO_CALLBACK_AFTER_DESTROY: Body '{body_id}' has been destroyed.")
        if body_id not in target.bodies:
            raise ValueError(f"BODY_NOT_FOUND: Body '{body_id}' does not exist.")

        body = target.bodies[body_id]
        body.enabled = True

    def deactivate_body(self, body_id: str, world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if body_id in getattr(target, "destroyed_body_ids", set()):
            raise ValueError(f"NO_CALLBACK_AFTER_DESTROY: Body '{body_id}' has been destroyed.")
        if body_id not in target.bodies:
            raise ValueError(f"BODY_NOT_FOUND: Body '{body_id}' does not exist.")

        body = target.bodies[body_id]
        body.enabled = False

    def sleep_body(self, body_id: str, world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target or body_id not in target.bodies:
            raise ValueError(f"BODY_NOT_FOUND: '{body_id}'")
        body = target.bodies[body_id]
        if not body.is_sleeping:
            body.is_sleeping = True
            body.linear_velocity = [0.0, 0.0, 0.0]
            body.angular_velocity = [0.0, 0.0, 0.0]
            event = PhysicsEvent(
                event_type=PhysicsEventType.BODY_SLEEP,
                body_a_id=body_id,
                timestamp=target.time_seconds,
            )
            target.event_queue.append(event)

    def wake_body(self, body_id: str, world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target or body_id not in target.bodies:
            raise ValueError(f"BODY_NOT_FOUND: '{body_id}'")
        body = target.bodies[body_id]
        if body.is_sleeping:
            body.is_sleeping = False
            body.sleep_timer = 0.0
            event = PhysicsEvent(
                event_type=PhysicsEventType.BODY_WAKE,
                body_a_id=body_id,
                timestamp=target.time_seconds,
            )
            target.event_queue.append(event)

    def destroy_body(self, body_id: str, world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if body_id not in target.bodies:
            raise ValueError(f"BODY_NOT_FOUND: '{body_id}'")

        body = target.bodies[body_id]
        # Remove all colliders of this body
        for cid in list(body.colliders.keys()):
            self.destroy_collider(cid, target)

        # Remove constraints referring to this body
        for cid, constraint in list(target.constraints.items()):
            if constraint.body_a_id == body_id or constraint.body_b_id == body_id:
                del target.constraints[cid]

        # Purge pending events referring to this body
        target.event_queue = [
            ev for ev in target.event_queue
            if ev.body_a_id != body_id and ev.body_b_id != body_id
        ]

        target.destroyed_body_ids.add(body_id)
        del target.bodies[body_id]

    def set_linear_velocity(self, body_id: str, velocity: List[float], world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target or body_id not in target.bodies:
            raise ValueError(f"BODY_NOT_FOUND: '{body_id}'")
        body = target.bodies[body_id]
        speed = _vec3_length(velocity)
        if speed > target.settings.max_linear_velocity:
            clamped = _vec3_scale(_vec3_normalize(velocity), target.settings.max_linear_velocity)
            body.linear_velocity = clamped
        else:
            body.linear_velocity = list(velocity)
        if speed > 0.001 and body.is_sleeping:
            self.wake_body(body_id, target)

    def set_angular_velocity(self, body_id: str, velocity: List[float], world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target or body_id not in target.bodies:
            raise ValueError(f"BODY_NOT_FOUND: '{body_id}'")
        body = target.bodies[body_id]
        speed = _vec3_length(velocity)
        if speed > target.settings.max_angular_velocity:
            clamped = _vec3_scale(_vec3_normalize(velocity), target.settings.max_angular_velocity)
            body.angular_velocity = clamped
        else:
            body.angular_velocity = list(velocity)
        if speed > 0.001 and body.is_sleeping:
            self.wake_body(body_id, target)

    def apply_force(self, body_id: str, force: List[float], world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target or body_id not in target.bodies:
            raise ValueError(f"BODY_NOT_FOUND: '{body_id}'")
        body = target.bodies[body_id]
        if body.body_type == BodyType.DYNAMIC and body.enabled:
            body.forces = _vec3_add(body.forces, force)
            if body.is_sleeping and _vec3_length(force) > 0.001:
                self.wake_body(body_id, target)

    def apply_impulse(self, body_id: str, impulse: List[float], world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target or body_id not in target.bodies:
            raise ValueError(f"BODY_NOT_FOUND: '{body_id}'")
        body = target.bodies[body_id]
        if body.body_type == BodyType.DYNAMIC and body.enabled and body.inverse_mass > 0.0:
            delta_v = _vec3_scale(impulse, body.inverse_mass)
            self.set_linear_velocity(body_id, _vec3_add(body.linear_velocity, delta_v), target)

    def apply_torque(self, body_id: str, torque: List[float], world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target or body_id not in target.bodies:
            raise ValueError(f"BODY_NOT_FOUND: '{body_id}'")
        body = target.bodies[body_id]
        if body.body_type == BodyType.DYNAMIC and body.enabled:
            body.torques = _vec3_add(body.torques, torque)
            if body.is_sleeping and _vec3_length(torque) > 0.001:
                self.wake_body(body_id, target)

    def apply_angular_impulse(self, body_id: str, impulse: List[float], world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target or body_id not in target.bodies:
            raise ValueError(f"BODY_NOT_FOUND: '{body_id}'")
        body = target.bodies[body_id]
        if body.body_type == BodyType.DYNAMIC and body.enabled and body.inverse_mass > 0.0:
            delta_w = _vec3_scale(impulse, body.inverse_mass)
            self.set_angular_velocity(body_id, _vec3_add(body.angular_velocity, delta_w), target)

    # --------------------------------------------------------------------------
    # 3. Collider Management
    # --------------------------------------------------------------------------

    def create_collider(
        self,
        collider_id: str,
        body_id: str,
        shape: CollisionShape,
        material: Optional[PhysicsMaterial] = None,
        is_trigger: bool = False,
        layer: int = 1,
        mask: int = 0xFFFFFFFF,
        world: Optional[PhysicsWorld] = None,
    ) -> Collider:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if not collider_id or not collider_id.strip():
            raise ValueError("INVALID_COLLIDER_ID")
        if collider_id in target.colliders:
            raise ValueError(f"DUPLICATE_COLLIDER_ID: '{collider_id}'")
        if body_id not in target.bodies:
            raise ValueError(f"BODY_NOT_FOUND: '{body_id}'")
        if len(target.colliders) >= target.settings.max_colliders:
            raise ValueError("SECURITY_VIOLATION: Max colliders limit exceeded.")

        # Shape validation
        self._validate_shape(shape)

        collider = Collider(
            collider_id=collider_id,
            body_id=body_id,
            shape=shape,
            material=material,
            is_trigger=is_trigger,
            layer=layer,
            mask=mask,
        )
        target.colliders[collider_id] = collider
        target.bodies[body_id].colliders[collider_id] = collider
        return collider

    def _validate_shape(self, shape: CollisionShape) -> None:
        if shape.shape_type == CollisionShapeType.SPHERE:
            r = shape.params.get("radius", 0.0)
            if r <= 0.0:
                raise ValueError("DEGENERATE_SHAPE: Sphere radius must be > 0.")
        elif shape.shape_type == CollisionShapeType.BOX:
            extents = shape.params.get("extents", [0.0, 0.0, 0.0])
            if any(e <= 0.0 for e in extents):
                raise ValueError("DEGENERATE_SHAPE: Box extents must be > 0.")
        elif shape.shape_type == CollisionShapeType.CAPSULE:
            r = shape.params.get("radius", 0.0)
            h = shape.params.get("height", 0.0)
            if r <= 0.0 or h <= 0.0:
                raise ValueError("DEGENERATE_SHAPE: Capsule radius and height must be > 0.")
        elif shape.shape_type == CollisionShapeType.CYLINDER:
            r = shape.params.get("radius", 0.0)
            h = shape.params.get("height", 0.0)
            if r <= 0.0 or h <= 0.0:
                raise ValueError("DEGENERATE_SHAPE: Cylinder radius and height must be > 0.")
        elif shape.shape_type == CollisionShapeType.COMPOUND:
            sub_shapes = shape.params.get("sub_shapes", [])
            if len(sub_shapes) > 100:
                raise ValueError("SECURITY_VIOLATION: Compound shape has too many sub_shapes.")

    def destroy_collider(self, collider_id: str, world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target or collider_id not in target.colliders:
            raise ValueError(f"COLLIDER_NOT_FOUND: '{collider_id}'")

        col = target.colliders[collider_id]
        if col.body_id in target.bodies:
            body = target.bodies[col.body_id]
            if collider_id in body.colliders:
                del body.colliders[collider_id]

        target.destroyed_collider_ids.add(collider_id)
        del target.colliders[collider_id]

    # --------------------------------------------------------------------------
    # 4. Material Management
    # --------------------------------------------------------------------------

    def create_material(
        self,
        material_id: str,
        friction: float = 0.5,
        restitution: float = 0.0,
        density: float = 1000.0,
        combine_policy: MaterialCombinePolicy = MaterialCombinePolicy.AVERAGE,
        world: Optional[PhysicsWorld] = None,
    ) -> PhysicsMaterial:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if friction < 0.0:
            raise ValueError("INVALID_MATERIAL: Friction cannot be negative.")
        if not (0.0 <= restitution <= 1.0):
            raise ValueError("INVALID_MATERIAL: Restitution must be between 0.0 and 1.0.")
        if density <= 0.0:
            raise ValueError("INVALID_MATERIAL: Density must be positive.")

        mat = PhysicsMaterial(
            material_id=material_id,
            friction=friction,
            restitution=restitution,
            density=density,
            combine_policy=combine_policy,
        )
        target.materials[material_id] = mat
        return mat

    def get_material(self, material_id: str, world: Optional[PhysicsWorld] = None) -> Optional[PhysicsMaterial]:
        target = world or self.active_world
        return target.materials.get(material_id) if target else None

    # --------------------------------------------------------------------------
    # 5. Constraint Management
    # --------------------------------------------------------------------------

    def create_constraint(
        self,
        constraint_id: str,
        constraint_type: ConstraintType,
        body_a_id: str,
        body_b_id: str,
        anchor_a: Optional[List[float]] = None,
        anchor_b: Optional[List[float]] = None,
        limits: Optional[Dict[str, float]] = None,
        stiffness: float = 1.0,
        damping: float = 0.1,
        world: Optional[PhysicsWorld] = None,
    ) -> PhysicsConstraint:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if not constraint_id or not constraint_id.strip():
            raise ValueError("INVALID_CONSTRAINT_ID")
        if constraint_id in target.constraints:
            raise ValueError(f"DUPLICATE_CONSTRAINT_ID: '{constraint_id}'")
        if body_a_id not in target.bodies or body_b_id not in target.bodies:
            raise ValueError("INVALID_CONSTRAINT_ENDPOINTS: Both bodies must exist.")
        if body_a_id == body_b_id:
            raise ValueError("INVALID_CONSTRAINT_ENDPOINTS: Endpoints cannot be identical.")
        if len(target.constraints) >= target.settings.max_constraints:
            raise ValueError("SECURITY_VIOLATION: Max constraints exceeded.")

        c = PhysicsConstraint(
            constraint_id=constraint_id,
            constraint_type=constraint_type,
            body_a_id=body_a_id,
            body_b_id=body_b_id,
            anchor_a=anchor_a or [0.0, 0.0, 0.0],
            anchor_b=anchor_b or [0.0, 0.0, 0.0],
            limits=limits or {},
            stiffness=stiffness,
            damping=damping,
        )
        target.constraints[constraint_id] = c
        return c

    def destroy_constraint(self, constraint_id: str, world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target or constraint_id not in target.constraints:
            raise ValueError(f"CONSTRAINT_NOT_FOUND: '{constraint_id}'")
        del target.constraints[constraint_id]

    # --------------------------------------------------------------------------
    # 6. Character Controller Management
    # --------------------------------------------------------------------------

    def create_character_controller(
        self,
        controller_id: str,
        entity_id: str,
        position: Optional[List[float]] = None,
        height: float = 1.8,
        radius: float = 0.3,
        slope_limit: float = 45.0,
        step_offset: float = 0.3,
        world: Optional[PhysicsWorld] = None,
    ) -> CharacterController:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if not controller_id or not controller_id.strip():
            raise ValueError("INVALID_CONTROLLER_ID")
        if controller_id in target.character_controllers:
            raise ValueError(f"DUPLICATE_CONTROLLER_ID: '{controller_id}'")

        cc = CharacterController(
            controller_id=controller_id,
            entity_id=entity_id,
            position=position or [0.0, 0.0, 0.0],
            height=height,
            radius=radius,
            slope_limit=slope_limit,
            step_offset=step_offset,
        )
        target.character_controllers[controller_id] = cc
        return cc

    def move_character(
        self,
        controller_id: str,
        displacement: List[float],
        delta_time: float,
        world: Optional[PhysicsWorld] = None,
    ) -> None:
        target = world or self.active_world
        if not target or controller_id not in target.character_controllers:
            raise ValueError(f"CONTROLLER_NOT_FOUND: '{controller_id}'")

        cc = target.character_controllers[controller_id]
        if delta_time > 0.0:
            cc.velocity = _vec3_scale(displacement, 1.0 / delta_time)
        cc.position = _vec3_add(cc.position, displacement)

        # Grounding check: if on ground plane y <= 0
        if cc.position[1] <= 0.0:
            cc.position[1] = 0.0
            cc.is_grounded = True
            cc.ground_normal = [0.0, 1.0, 0.0]
            if cc.velocity[1] < 0.0:
                cc.velocity[1] = 0.0
        else:
            cc.is_grounded = False

    def teleport_character(
        self,
        controller_id: str,
        new_position: List[float],
        world: Optional[PhysicsWorld] = None,
    ) -> None:
        target = world or self.active_world
        if not target or controller_id not in target.character_controllers:
            raise ValueError(f"CONTROLLER_NOT_FOUND: '{controller_id}'")
        cc = target.character_controllers[controller_id]
        cc.position = list(new_position)
        cc.velocity = [0.0, 0.0, 0.0]

    def destroy_character_controller(self, controller_id: str, world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target or controller_id not in target.character_controllers:
            raise ValueError(f"CONTROLLER_NOT_FOUND: '{controller_id}'")
        del target.character_controllers[controller_id]

    # --------------------------------------------------------------------------
    # 7. Spatial Queries
    # --------------------------------------------------------------------------

    def raycast(
        self,
        origin: List[float],
        direction: List[float],
        max_distance: float = 1000.0,
        layer_mask: int = 0xFFFFFFFF,
        include_triggers: bool = False,
        world: Optional[PhysicsWorld] = None,
    ) -> RaycastHit:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if max_distance <= 0.0 or max_distance > target.settings.max_query_distance:
            raise ValueError("INVALID_QUERY: max_distance out of range.")

        dir_norm = _vec3_normalize(direction)
        hits: List[Tuple[float, RaycastHit]] = []

        # Intersect with colliders deterministically
        for cid, col in sorted(target.colliders.items()):
            if not col.enabled:
                continue
            if not include_triggers and col.is_trigger:
                continue
            if (col.layer & layer_mask) == 0:
                continue
            body = target.bodies.get(col.body_id)
            if not body or not body.enabled:
                continue

            # Sphere raycast
            pos = _vec3_add(body.position, col.shape.local_position)
            if col.shape.shape_type == CollisionShapeType.SPHERE:
                radius = col.shape.params.get("radius", 1.0)
                m = _vec3_sub(origin, pos)
                b = _vec3_dot(m, dir_norm)
                c = _vec3_dot(m, m) - radius * radius
                if b <= 0.0 or c <= 0.0:
                    discr = b * b - c
                    if discr >= 0.0:
                        t = -b - math.sqrt(discr)
                        if t < 0.0:
                            t = 0.0
                        if 0.0 <= t <= max_distance:
                            hit_pt = _vec3_add(origin, _vec3_scale(dir_norm, t))
                            normal = _vec3_normalize(_vec3_sub(hit_pt, pos))
                            hit = RaycastHit(
                                hit=True,
                                distance=t,
                                point=hit_pt,
                                normal=normal,
                                collider_id=cid,
                                body_id=body.body_id,
                                entity_id=body.entity_id,
                            )
                            hits.append((t, hit))
            else:
                # Default AABB check
                extents = col.shape.params.get("extents", [1.0, 1.0, 1.0])
                # Simple box center distance
                diff = _vec3_sub(pos, origin)
                proj = _vec3_dot(diff, dir_norm)
                if 0.0 <= proj <= max_distance:
                    close_pt = _vec3_add(origin, _vec3_scale(dir_norm, proj))
                    dist_to_line = _vec3_length(_vec3_sub(close_pt, pos))
                    if dist_to_line <= max(extents):
                        t = max(0.0, proj - min(extents))
                        hit_pt = _vec3_add(origin, _vec3_scale(dir_norm, t))
                        normal = _vec3_normalize(_vec3_sub(hit_pt, pos))
                        hit = RaycastHit(
                            hit=True,
                            distance=t,
                            point=hit_pt,
                            normal=normal,
                            collider_id=cid,
                            body_id=body.body_id,
                            entity_id=body.entity_id,
                        )
                        hits.append((t, hit))

        if hits:
            # Deterministic: lowest distance first, then collider_id
            hits.sort(key=lambda item: (round(item[0], 5), item[1].collider_id))
            return hits[0][1]

        return RaycastHit(hit=False)

    def shapecast(
        self,
        shape: CollisionShape,
        origin: List[float],
        direction: List[float],
        max_distance: float = 1000.0,
        layer_mask: int = 0xFFFFFFFF,
        world: Optional[PhysicsWorld] = None,
    ) -> SweepHit:
        rh = self.raycast(origin, direction, max_distance, layer_mask, include_triggers=False, world=world)
        return SweepHit(
            hit=rh.hit,
            distance=rh.distance,
            point=rh.point,
            normal=rh.normal,
            collider_id=rh.collider_id,
            body_id=rh.body_id,
            entity_id=rh.entity_id,
        )

    def overlap(
        self,
        shape: CollisionShape,
        position: List[float],
        layer_mask: int = 0xFFFFFFFF,
        include_triggers: bool = True,
        world: Optional[PhysicsWorld] = None,
    ) -> List[OverlapHit]:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        query_radius = shape.params.get("radius", 1.0)
        hits: List[OverlapHit] = []

        for cid, col in sorted(target.colliders.items()):
            if not col.enabled:
                continue
            if not include_triggers and col.is_trigger:
                continue
            if (col.layer & layer_mask) == 0:
                continue
            body = target.bodies.get(col.body_id)
            if not body or not body.enabled:
                continue

            col_pos = _vec3_add(body.position, col.shape.local_position)
            dist = _vec3_length(_vec3_sub(col_pos, position))
            col_radius = col.shape.params.get("radius", max(col.shape.params.get("extents", [1.0, 1.0, 1.0])))
            if dist <= (query_radius + col_radius):
                hits.append(
                    OverlapHit(
                        hit=True,
                        collider_id=cid,
                        body_id=body.body_id,
                        entity_id=body.entity_id,
                    )
                )

        hits.sort(key=lambda h: h.collider_id)
        return hits

    def sweep(
        self,
        shape: CollisionShape,
        origin: List[float],
        direction: List[float],
        max_distance: float = 1000.0,
        layer_mask: int = 0xFFFFFFFF,
        world: Optional[PhysicsWorld] = None,
    ) -> SweepHit:
        return self.shapecast(shape, origin, direction, max_distance, layer_mask, world)

    # --------------------------------------------------------------------------
    # 8. Simulation Stepping & Solver
    # --------------------------------------------------------------------------

    def simulate(self, delta_time: float, world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state == PhysicsWorldState.PAUSED:
            return
        if target.state not in (PhysicsWorldState.SIMULATING, PhysicsWorldState.READY):
            raise ValueError(f"NO_UPDATE_BEFORE_INITIALIZATION: World state is '{target.state.value}'.")

        if target.state == PhysicsWorldState.READY:
            target.state = PhysicsWorldState.SIMULATING

        if delta_time < 0.0:
            raise ValueError("INVALID_TIMESTEP: delta_time cannot be negative.")

        fixed_dt = target.settings.fixed_delta_time
        target.time_accumulator += delta_time

        substeps = 0
        eps = 1e-3
        while (target.time_accumulator >= (fixed_dt - eps)) and substeps < target.settings.max_substeps:
            self._substep(fixed_dt, target)
            target.time_accumulator = max(0.0, target.time_accumulator - fixed_dt)
            substeps += 1

        if target.time_accumulator > fixed_dt * target.settings.max_substeps:
            # Catch up policy: discard excess time accumulator to prevent spiral of death
            target.time_accumulator = 0.0

        target.content_fingerprint = target.compute_fingerprint()

    def _substep(self, dt: float, world: PhysicsWorld) -> None:
        # 1. Integrate forces for dynamic bodies
        for body in sorted(world.bodies.values(), key=lambda b: b.body_id):
            if body.body_type != BodyType.DYNAMIC or not body.enabled or body.is_sleeping:
                continue

            # linear acceleration = forces * inverse_mass + gravity * gravity_scale
            gravity_force = _vec3_scale(world.settings.gravity, body.gravity_scale)
            accel = _vec3_add(_vec3_scale(body.forces, body.inverse_mass), gravity_force)
            body.linear_velocity = _vec3_add(body.linear_velocity, _vec3_scale(accel, dt))

            # angular acceleration
            alpha = _vec3_scale(body.torques, body.inverse_mass)
            body.angular_velocity = _vec3_add(body.angular_velocity, _vec3_scale(alpha, dt))

            # damping
            lin_damp = max(0.0, 1.0 - body.linear_damping * dt)
            ang_damp = max(0.0, 1.0 - body.angular_damping * dt)
            body.linear_velocity = _vec3_scale(body.linear_velocity, lin_damp)
            body.angular_velocity = _vec3_scale(body.angular_velocity, ang_damp)

            # clamp velocity
            spd = _vec3_length(body.linear_velocity)
            if spd > world.settings.max_linear_velocity:
                body.linear_velocity = _vec3_scale(_vec3_normalize(body.linear_velocity), world.settings.max_linear_velocity)

            # reset forces
            body.forces = [0.0, 0.0, 0.0]
            body.torques = [0.0, 0.0, 0.0]

            # Integrate position
            body.position = _vec3_add(body.position, _vec3_scale(body.linear_velocity, dt))

        # 2. Collision Detection & Triggers
        current_contacts: Set[Tuple[str, str]] = set()
        current_triggers: Set[Tuple[str, str]] = set()

        collider_list = sorted(world.colliders.values(), key=lambda c: c.collider_id)
        n = len(collider_list)
        for i in range(n):
            for j in range(i + 1, n):
                c1 = collider_list[i]
                c2 = collider_list[j]
                if not c1.enabled or not c2.enabled:
                    continue
                if (c1.layer & c2.mask) == 0 or (c2.layer & c1.mask) == 0:
                    continue
                b1 = world.bodies.get(c1.body_id)
                b2 = world.bodies.get(c2.body_id)
                if not b1 or not b2 or not b1.enabled or not b2.enabled:
                    continue
                if b1.body_id == b2.body_id:
                    continue

                # Check intersection between c1 and c2
                pos1 = _vec3_add(b1.position, c1.shape.local_position)
                pos2 = _vec3_add(b2.position, c2.shape.local_position)
                r1 = c1.shape.params.get("radius", max(c1.shape.params.get("extents", [0.5, 0.5, 0.5])))
                r2 = c2.shape.params.get("radius", max(c2.shape.params.get("extents", [0.5, 0.5, 0.5])))

                delta = _vec3_sub(pos2, pos1)
                dist = _vec3_length(delta)
                min_dist = r1 + r2

                if dist < min_dist:
                    pair_key = (min(c1.collider_id, c2.collider_id), max(c1.collider_id, c2.collider_id))
                    is_trigger = c1.is_trigger or c2.is_trigger

                    if is_trigger:
                        current_triggers.add(pair_key)
                        if pair_key not in self._previous_triggers:
                            world.event_queue.append(
                                PhysicsEvent(
                                    event_type=PhysicsEventType.TRIGGER_ENTER,
                                    body_a_id=b1.body_id,
                                    body_b_id=b2.body_id,
                                    collider_a_id=c1.collider_id,
                                    collider_b_id=c2.collider_id,
                                    timestamp=world.time_seconds,
                                )
                            )
                        else:
                            world.event_queue.append(
                                PhysicsEvent(
                                    event_type=PhysicsEventType.TRIGGER_STAY,
                                    body_a_id=b1.body_id,
                                    body_b_id=b2.body_id,
                                    collider_a_id=c1.collider_id,
                                    collider_b_id=c2.collider_id,
                                    timestamp=world.time_seconds,
                                )
                            )
                    else:
                        current_contacts.add(pair_key)
                        ev_type = (
                            PhysicsEventType.CONTACT_BEGIN
                            if pair_key not in self._previous_contacts
                            else PhysicsEventType.CONTACT_STAY
                        )
                        world.event_queue.append(
                            PhysicsEvent(
                                event_type=ev_type,
                                body_a_id=b1.body_id,
                                body_b_id=b2.body_id,
                                collider_a_id=c1.collider_id,
                                collider_b_id=c2.collider_id,
                                timestamp=world.time_seconds,
                            )
                        )

                        # Resolve contact response for dynamic bodies
                        normal = _vec3_normalize(delta)
                        penetration = min_dist - dist
                        total_inv_mass = b1.inverse_mass + b2.inverse_mass
                        if total_inv_mass > 0.0:
                            # Positional separation
                            sep1 = _vec3_scale(normal, -penetration * (b1.inverse_mass / total_inv_mass))
                            sep2 = _vec3_scale(normal, penetration * (b2.inverse_mass / total_inv_mass))
                            if b1.body_type == BodyType.DYNAMIC:
                                b1.position = _vec3_add(b1.position, sep1)
                            if b2.body_type == BodyType.DYNAMIC:
                                b2.position = _vec3_add(b2.position, sep2)

                            # Restitution impulse
                            restitution = 0.5
                            rel_vel = _vec3_sub(b2.linear_velocity, b1.linear_velocity)
                            vel_along_normal = _vec3_dot(rel_vel, normal)
                            if vel_along_normal < 0:
                                impulse_mag = -(1.0 + restitution) * vel_along_normal / total_inv_mass
                                impulse = _vec3_scale(normal, impulse_mag)
                                if b1.body_type == BodyType.DYNAMIC:
                                    b1.linear_velocity = _vec3_sub(b1.linear_velocity, _vec3_scale(impulse, b1.inverse_mass))
                                if b2.body_type == BodyType.DYNAMIC:
                                    b2.linear_velocity = _vec3_add(b2.linear_velocity, _vec3_scale(impulse, b2.inverse_mass))

        # Check contact exits
        for pair in self._previous_contacts - current_contacts:
            c1_id, c2_id = pair
            c1 = world.colliders.get(c1_id)
            c2 = world.colliders.get(c2_id)
            if c1 and c2:
                world.event_queue.append(
                    PhysicsEvent(
                        event_type=PhysicsEventType.CONTACT_END,
                        body_a_id=c1.body_id,
                        body_b_id=c2.body_id,
                        collider_a_id=c1_id,
                        collider_b_id=c2_id,
                        timestamp=world.time_seconds,
                    )
                )

        # Check trigger exits
        for pair in self._previous_triggers - current_triggers:
            c1_id, c2_id = pair
            c1 = world.colliders.get(c1_id)
            c2 = world.colliders.get(c2_id)
            if c1 and c2:
                world.event_queue.append(
                    PhysicsEvent(
                        event_type=PhysicsEventType.TRIGGER_EXIT,
                        body_a_id=c1.body_id,
                        body_b_id=c2.body_id,
                        collider_a_id=c1_id,
                        collider_b_id=c2_id,
                        timestamp=world.time_seconds,
                    )
                )

        self._previous_contacts = current_contacts
        self._previous_triggers = current_triggers

        # 3. Solve Constraints
        for c in sorted(world.constraints.values(), key=lambda x: x.constraint_id):
            if not c.enabled:
                continue
            b1 = world.bodies.get(c.body_a_id)
            b2 = world.bodies.get(c.body_b_id)
            if not b1 or not b2:
                continue

            if c.constraint_type == ConstraintType.DISTANCE:
                target_dist = c.limits.get("distance", 1.0)
                diff = _vec3_sub(b2.position, b1.position)
                current_dist = _vec3_length(diff)
                error = current_dist - target_dist
                if abs(error) > 0.001 and current_dist > 0.0001:
                    corr = _vec3_scale(_vec3_normalize(diff), error * 0.5 * c.stiffness)
                    if b1.body_type == BodyType.DYNAMIC:
                        b1.position = _vec3_add(b1.position, corr)
                    if b2.body_type == BodyType.DYNAMIC:
                        b2.position = _vec3_sub(b2.position, corr)

        # 4. Sleep check
        for body in sorted(world.bodies.values(), key=lambda b: b.body_id):
            if body.body_type != BodyType.DYNAMIC or not body.enabled or body.is_sleeping:
                continue
            if (
                _vec3_length(body.linear_velocity) < world.settings.sleep_linear_threshold
                and _vec3_length(body.angular_velocity) < world.settings.sleep_angular_threshold
            ):
                body.sleep_timer += dt
                if body.sleep_timer >= world.settings.sleep_time_threshold:
                    self.sleep_body(body.body_id, world)
            else:
                body.sleep_timer = 0.0

        world.time_seconds += dt
        world.frame_index += 1

    # --------------------------------------------------------------------------
    # 9. Transform Synchronization with UAF-81.73 Runtime World
    # --------------------------------------------------------------------------

    def sync_from_runtime_world(self, runtime_world: Any, physics_world: Optional[PhysicsWorld] = None) -> None:
        target = physics_world or self.active_world
        if not target or not runtime_world:
            return

        for body in target.bodies.values():
            if body.entity_id in runtime_world.entities:
                entity = runtime_world.entities[body.entity_id]
                tr = getattr(entity, "local_transform", getattr(entity, "world_transform", getattr(entity, "transform", None)))
                if tr:
                    body.position = list(tr.position)
                    body.rotation = list(tr.rotation)

    def sync_to_runtime_world(self, runtime_world: Any, physics_world: Optional[PhysicsWorld] = None) -> None:
        target = physics_world or self.active_world
        if not target or not runtime_world:
            return

        for body in target.bodies.values():
            if body.entity_id in runtime_world.entities:
                entity = runtime_world.entities[body.entity_id]
                if hasattr(entity, "world_transform"):
                    entity.world_transform.position = list(body.position)
                    entity.world_transform.rotation = list(body.rotation)
                if hasattr(entity, "local_transform"):
                    entity.local_transform.position = list(body.position)
                    entity.local_transform.rotation = list(body.rotation)
                if hasattr(entity, "transform"):
                    entity.transform.position = list(body.position)
                    entity.transform.rotation = list(body.rotation)

    def teleport_body(
        self,
        body_id: str,
        position: List[float],
        rotation: Optional[List[float]] = None,
        reset_velocity: bool = True,
        world: Optional[PhysicsWorld] = None,
    ) -> None:
        target = world or self.active_world
        if not target or body_id not in target.bodies:
            raise ValueError(f"BODY_NOT_FOUND: '{body_id}'")

        body = target.bodies[body_id]
        body.position = list(position)
        if rotation:
            body.rotation = list(rotation)
        if reset_velocity:
            body.linear_velocity = [0.0, 0.0, 0.0]
            body.angular_velocity = [0.0, 0.0, 0.0]

    # --------------------------------------------------------------------------
    # 10. Physics Snapshot & Replay
    # --------------------------------------------------------------------------

    def create_snapshot(self, snapshot_id: str, world: Optional[PhysicsWorld] = None) -> PhysicsSnapshot:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        snap = PhysicsSnapshot(
            snapshot_id=snapshot_id,
            physics_world_id=target.physics_world_id,
            frame_index=target.frame_index,
            timestamp=target.time_seconds,
            world_data=target.to_dict(),
        )
        return snap

    def restore_snapshot(self, snapshot: PhysicsSnapshot, world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        serialized = json.dumps(snapshot.world_data, sort_keys=True)
        fp = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        if fp != snapshot.content_fingerprint:
            raise ValueError("RESTORE_VALIDATION_FAILED: Snapshot fingerprint corrupted.")

        data = snapshot.world_data
        target.time_seconds = data.get("time_seconds", 0.0)
        target.frame_index = data.get("frame_index", 0)

        # Rehydrate bodies
        target.bodies.clear()
        for bid, bdata in data.get("bodies", {}).items():
            body = PhysicsBody(
                body_id=bdata["body_id"],
                entity_id=bdata["entity_id"],
                body_type=BodyType(bdata["body_type"]),
                position=bdata["position"],
                rotation=bdata["rotation"],
                linear_velocity=bdata["linear_velocity"],
                angular_velocity=bdata["angular_velocity"],
                mass=bdata["mass"],
                linear_damping=bdata["linear_damping"],
                angular_damping=bdata["angular_damping"],
                gravity_scale=bdata["gravity_scale"],
                enabled=bdata["enabled"],
                is_sleeping=bdata["is_sleeping"],
            )
            target.bodies[bid] = body

        target.content_fingerprint = target.compute_fingerprint()

    def execute_replay(self, replay: PhysicsReplay, world: Optional[PhysicsWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        self.restore_snapshot(replay.initial_snapshot, target)
        if target.state in (PhysicsWorldState.CREATED, PhysicsWorldState.INITIALIZING, PhysicsWorldState.READY):
            target.state = PhysicsWorldState.SIMULATING

        commands_by_frame: Dict[int, List[PhysicsReplayCommand]] = {}
        for cmd in replay.commands:
            commands_by_frame.setdefault(cmd.frame_index, []).append(cmd)

        max_frame = max(commands_by_frame.keys(), default=0) + 5
        for frame in range(max_frame + 1):
            if frame in commands_by_frame:
                for cmd in commands_by_frame[frame]:
                    if cmd.command_type == "apply_force":
                        self.apply_force(cmd.target_id, cmd.parameters.get("force", [0.0, 0.0, 0.0]), target)
                    elif cmd.command_type == "apply_impulse":
                        self.apply_impulse(cmd.target_id, cmd.parameters.get("impulse", [0.0, 0.0, 0.0]), target)
                    elif cmd.command_type == "teleport":
                        self.teleport_body(cmd.target_id, cmd.parameters.get("position", [0.0, 0.0, 0.0]), world=target)
            self.simulate(target.settings.fixed_delta_time, target)

    # --------------------------------------------------------------------------
    # 11. Debug Visualization
    # --------------------------------------------------------------------------

    def get_debug_visualization_data(self, world: Optional[PhysicsWorld] = None) -> Dict[str, Any]:
        target = world or self.active_world
        if not target:
            return {}

        colliders_vis = []
        for col in target.colliders.values():
            body = target.bodies.get(col.body_id)
            pos = _vec3_add(body.position, col.shape.local_position) if body else [0.0, 0.0, 0.0]
            colliders_vis.append({
                "collider_id": col.collider_id,
                "shape_type": col.shape.shape_type.value,
                "position": pos,
                "is_trigger": col.is_trigger,
                "enabled": col.enabled,
            })

        return {
            "world_id": target.physics_world_id,
            "colliders": colliders_vis,
            "bodies_count": len(target.bodies),
            "time_seconds": target.time_seconds,
        }
