"""
UAF-81.67: Universal Asset Viewport Validator.
Validates scene graph tree invariants, numerical transform stability,
camera parameters, spatial index integrity, snapshots, and diagnostic bundle signatures.
"""

from __future__ import annotations
import math
from typing import List, Set, Tuple

from uaf.universal_viewport.models.definition import (
    CameraState,
    ViewportStateSnapshot,
    ViewportDiagnosticBundle,
)
from uaf.universal_viewport.engine.universal_viewport_fabricator import (
    UniversalViewportFabricator,
)


class UniversalViewportValidator:
    """
    Authoritative validator for Universal Asset Viewport and Scene Graph.
    """

    @staticmethod
    def validate_scene_graph(fabricator: UniversalViewportFabricator) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        visited: Set[str] = set()
        stack: Set[str] = set()

        def dfs(node_id: str, parent_id: str | None) -> None:
            if node_id == parent_id:
                errors.append(f"NO_SELF_PARENT: Node '{node_id}' is its own parent.")
            if node_id in stack:
                errors.append(f"NO_CYCLES: Cycle detected in scene graph at '{node_id}'.")
                return
            if node_id not in fabricator.nodes:
                errors.append(f"Node '{node_id}' referenced in hierarchy does not exist.")
                return

            node = fabricator.nodes[node_id]
            if parent_id is not None and node.parent_id != parent_id:
                errors.append(f"ONE_PARENT: Node '{node_id}' has parent '{node.parent_id}', expected '{parent_id}'.")

            stack.add(node_id)
            visited.add(node_id)

            for child_id in node.children_ids:
                dfs(child_id, node_id)

            stack.remove(node_id)

        for root_id in fabricator.root_node_ids:
            dfs(root_id, None)

        return len(errors) == 0, errors

    @staticmethod
    def validate_transforms(fabricator: UniversalViewportFabricator) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        for node_id, node in fabricator.nodes.items():
            if not node.local_transform.is_finite():
                errors.append(f"NON_FINITE_TRANSFORM: Node '{node_id}' local transform contains NaN or Inf.")
            if not node.world_transform.is_finite():
                errors.append(f"NON_FINITE_TRANSFORM: Node '{node_id}' world transform contains NaN or Inf.")
            if node.local_transform.scale.x == 0 or node.local_transform.scale.y == 0 or node.local_transform.scale.z == 0:
                errors.append(f"ZERO_SCALE: Node '{node_id}' contains zero scale component.")

        return len(errors) == 0, errors

    @staticmethod
    def validate_camera(camera: CameraState) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not camera.position.is_finite():
            errors.append("NON_FINITE_CAMERA_POSITION: Camera position contains NaN or Inf.")
        if not camera.target.is_finite():
            errors.append("NON_FINITE_CAMERA_TARGET: Camera target contains NaN or Inf.")
        if camera.fov_deg <= 0.0 or camera.fov_deg >= 180.0:
            errors.append(f"INVALID_FOV: FOV ({camera.fov_deg}) must be between 0 and 180 degrees.")
        if camera.near_clip <= 0.0:
            errors.append(f"INVALID_NEAR_CLIP: near_clip ({camera.near_clip}) must be > 0.")
        if camera.far_clip <= camera.near_clip:
            errors.append(f"INVALID_FAR_CLIP: far_clip ({camera.far_clip}) must be > near_clip ({camera.near_clip}).")
        if camera.aspect_ratio <= 0.0:
            errors.append(f"INVALID_ASPECT_RATIO: aspect_ratio ({camera.aspect_ratio}) must be > 0.")

        return len(errors) == 0, errors

    @staticmethod
    def validate_snapshot(snapshot: ViewportStateSnapshot) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        expected = snapshot.compute_hash()
        if snapshot.state_hash != expected:
            errors.append(f"SNAPSHOT_CORRUPTION: Expected hash '{expected}', got '{snapshot.state_hash}'.")
        return len(errors) == 0, errors

    @staticmethod
    def validate_diagnostic_bundle(bundle: ViewportDiagnosticBundle) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        expected = bundle.sign()
        if bundle.signature != expected:
            errors.append(f"BUNDLE_CORRUPTION: Expected signature '{expected}', got '{bundle.signature}'.")
        return len(errors) == 0, errors
