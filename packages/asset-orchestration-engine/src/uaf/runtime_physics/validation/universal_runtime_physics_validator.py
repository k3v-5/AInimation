"""
Universal Runtime Physics Validator (UAF-81.74).
Normative validation of physics worlds, rigid bodies, shapes, materials,
constraints, queries, and simulation invariants.
"""

from __future__ import annotations
import hashlib
import json
from typing import List, Optional

from ..models.definition import (
    PhysicsWorldState,
    BodyType,
    CollisionShapeType,
    PhysicsMaterial,
    CollisionShape,
    Collider,
    PhysicsBody,
    PhysicsConstraint,
    CharacterController,
    PhysicsSimulationSettings,
    PhysicsWorld,
    PhysicsSnapshot,
)


class UniversalRuntimePhysicsValidator:
    """Normative validator for physics simulation integrity and invariants."""

    def validate_material(self, material: PhysicsMaterial) -> List[str]:
        errors: List[str] = []
        if material.friction < 0.0:
            errors.append(f"INVALID_MATERIAL: Friction cannot be negative ({material.friction}).")
        if not (0.0 <= material.restitution <= 1.0):
            errors.append(f"INVALID_MATERIAL: Restitution must be in [0, 1] ({material.restitution}).")
        if material.density <= 0.0:
            errors.append(f"INVALID_MATERIAL: Density must be positive ({material.density}).")
        return errors

    def validate_shape(self, shape: CollisionShape) -> List[str]:
        errors: List[str] = []
        if shape.shape_type == CollisionShapeType.SPHERE:
            r = shape.params.get("radius", 0.0)
            if r <= 0.0:
                errors.append(f"DEGENERATE_SHAPE: Sphere radius must be > 0 ({r}).")
        elif shape.shape_type == CollisionShapeType.BOX:
            extents = shape.params.get("extents", [0.0, 0.0, 0.0])
            if any(e <= 0.0 for e in extents):
                errors.append(f"DEGENERATE_SHAPE: Box extents must be positive ({extents}).")
        elif shape.shape_type == CollisionShapeType.CAPSULE:
            r = shape.params.get("radius", 0.0)
            h = shape.params.get("height", 0.0)
            if r <= 0.0 or h <= 0.0:
                errors.append(f"DEGENERATE_SHAPE: Capsule radius and height must be > 0.")
        elif shape.shape_type == CollisionShapeType.CYLINDER:
            r = shape.params.get("radius", 0.0)
            h = shape.params.get("height", 0.0)
            if r <= 0.0 or h <= 0.0:
                errors.append(f"DEGENERATE_SHAPE: Cylinder radius and height must be > 0.")
        elif shape.shape_type == CollisionShapeType.COMPOUND:
            sub_shapes = shape.params.get("sub_shapes", [])
            if len(sub_shapes) > 100:
                errors.append("SECURITY_VIOLATION: Compound shape has too many sub_shapes.")
        return errors

    def validate_body(self, body: PhysicsBody) -> List[str]:
        errors: List[str] = []
        if body.body_type == BodyType.DYNAMIC:
            if body.mass <= 0.0:
                errors.append(f"INVALID_MASS: Dynamic body must have positive mass ({body.mass}).")
        elif body.body_type in (BodyType.STATIC, BodyType.KINEMATIC):
            if body.mass != 0.0:
                errors.append(f"INVALID_MASS: Static/Kinematic body must have mass 0 ({body.mass}).")

        if body.linear_damping < 0.0 or body.angular_damping < 0.0:
            errors.append("INVALID_DAMPING: Damping values cannot be negative.")
        return errors

    def validate_collider(self, collider: Collider) -> List[str]:
        errors = self.validate_shape(collider.shape)
        if collider.material:
            errors.extend(self.validate_material(collider.material))
        return errors

    def validate_constraint(self, constraint: PhysicsConstraint, world: PhysicsWorld) -> List[str]:
        errors: List[str] = []
        if constraint.body_a_id not in world.bodies:
            errors.append(f"MISSING_CONSTRAINT_ENDPOINT: body_a '{constraint.body_a_id}' does not exist.")
        if constraint.body_b_id not in world.bodies:
            errors.append(f"MISSING_CONSTRAINT_ENDPOINT: body_b '{constraint.body_b_id}' does not exist.")
        if constraint.body_a_id == constraint.body_b_id:
            errors.append("IDENTICAL_CONSTRAINT_ENDPOINTS: A body cannot be constrained to itself.")
        return errors

    def validate_snapshot(self, snapshot: PhysicsSnapshot) -> bool:
        serialized = json.dumps(snapshot.world_data, sort_keys=True)
        computed = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return computed == snapshot.content_fingerprint

    def validate_world(self, world: PhysicsWorld) -> List[str]:
        errors: List[str] = []
        # Check settings
        if world.settings.fixed_delta_time <= 0.0:
            errors.append("INVALID_TIMESTEP: fixed_delta_time must be positive.")
        if world.settings.max_substeps <= 0 or world.settings.max_substeps > 64:
            errors.append("UNBOUNDED_SUBSTEPS: max_substeps out of allowed range [1, 64].")

        # Check bodies
        for body in world.bodies.values():
            errors.extend(self.validate_body(body))

        # Check colliders
        for col in world.colliders.values():
            errors.extend(self.validate_collider(col))

        # Check constraints
        for c in world.constraints.values():
            errors.extend(self.validate_constraint(c, world))

        # Check controllers
        for cc in world.character_controllers.values():
            if cc.height <= 0.0 or cc.radius <= 0.0:
                errors.append(f"DEGENERATE_CHARACTER: Controller '{cc.controller_id}' dimensions must be > 0.")

        return errors
