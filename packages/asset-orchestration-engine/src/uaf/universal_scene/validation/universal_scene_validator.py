"""
Universal Scene Assembly Validation Pipeline.
Complies with UAF-81.72 specification.
"""

from typing import List, Set, Tuple

from uaf.universal_scene.models.definition import (
    Scene,
    SceneBuildArtifact,
    SceneStateSnapshot,
    SceneDiagnosticBundle,
)


class UniversalSceneValidator:
    """Normative validation suite for scene graphs, entity hierarchies, prefabs, and build artifacts."""

    @staticmethod
    def validate_hierarchy(scene: Scene) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if scene.root_entity_id not in scene.entities:
            errors.append(f"ROOT_NOT_FOUND: Root entity '{scene.root_entity_id}' does not exist in scene.")
            return False, errors

        # Check acyclicity and reachable entities
        visited: Set[str] = set()
        stack: Set[str] = set()

        def dfs(eid: str) -> bool:
            visited.add(eid)
            stack.add(eid)
            ent = scene.entities[eid]
            for child_id in ent.children_ids:
                if child_id not in scene.entities:
                    errors.append(f"CHILD_NOT_FOUND: Child entity '{child_id}' referenced by '{eid}' not found.")
                    continue
                if child_id in stack:
                    errors.append(f"NO_HIERARCHY_CYCLES: Hierarchy cycle detected at '{child_id}'.")
                    return False
                if child_id not in visited:
                    if not dfs(child_id):
                        return False
            stack.remove(eid)
            return True

        has_no_cycles = dfs(scene.root_entity_id)

        # Check for disconnected/orphan entities
        for eid in scene.entities:
            if eid not in visited and eid != scene.root_entity_id:
                errors.append(f"ORPHAN_ENTITY: Entity '{eid}' is not connected to root.")

        return len(errors) == 0, errors

    @staticmethod
    def validate_scene(scene: Scene) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not scene.scene_id or not scene.scene_id.strip():
            errors.append("EMPTY_SCENE_ID: Scene ID cannot be empty.")
        if not scene.scene_path or not scene.scene_path.startswith("/"):
            errors.append(f"INVALID_SCENE_PATH: Scene path '{scene.scene_path}' must be a canonical forward-slash path.")

        ok_hier, hier_errs = UniversalSceneValidator.validate_hierarchy(scene)
        if not ok_hier:
            errors.extend(hier_errs)

        # Validate components
        for eid, ent in scene.entities.items():
            for cid, comp in ent.components.items():
                if not comp.component_id:
                    errors.append(f"EMPTY_COMPONENT_ID: Component on entity '{eid}' has empty ID.")

        return len(errors) == 0, errors

    @staticmethod
    def validate_build_artifact(artifact: SceneBuildArtifact) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not artifact.artifact_id or not artifact.artifact_id.strip():
            errors.append("EMPTY_ARTIFACT_ID: Artifact ID cannot be empty.")
        expected_sig = artifact.compute_signature()
        if artifact.signature != expected_sig:
            errors.append(f"ARTIFACT_SIGNATURE_MISMATCH: Expected '{expected_sig}', got '{artifact.signature}'.")
        return len(errors) == 0, errors

    @staticmethod
    def validate_snapshot(snapshot: SceneStateSnapshot) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not snapshot.snapshot_id or not snapshot.snapshot_id.strip():
            errors.append("EMPTY_SNAPSHOT_ID: Snapshot ID cannot be empty.")
        expected_h = snapshot.compute_state_hash()
        if snapshot.state_hash != expected_h:
            errors.append(f"SNAPSHOT_HASH_MISMATCH: Expected '{expected_h}', got '{snapshot.state_hash}'.")
        return len(errors) == 0, errors

    @staticmethod
    def validate_diagnostic_bundle(bundle: SceneDiagnosticBundle) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not bundle.bundle_id or not bundle.bundle_id.strip():
            errors.append("EMPTY_BUNDLE_ID: Bundle ID cannot be empty.")
        expected_sig = bundle.compute_signature()
        if bundle.signature != expected_sig:
            errors.append(f"BUNDLE_SIGNATURE_MISMATCH: Expected '{expected_sig}', got '{bundle.signature}'.")
        ok_snap, snap_errs = UniversalSceneValidator.validate_snapshot(bundle.snapshot)
        if not ok_snap:
            errors.extend(snap_errs)
        return len(errors) == 0, errors
