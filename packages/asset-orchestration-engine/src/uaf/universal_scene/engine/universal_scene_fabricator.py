"""
Universal Scene Assembly Fabricator & Engine.
Complies with UAF-81.72 specification.
"""

import copy
import hashlib
import json
from pathlib import Path
import re
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from uaf.universal_scene.models.definition import (
    ComponentType,
    OverrideType,
    MergeConflictResolution,
    SceneBuildMode,
    SceneState,
    normalize_scene_path,
    Transform,
    Component,
    Entity,
    PrefabOverride,
    Prefab,
    PrefabInstance,
    Scene,
    SceneDiff,
    SceneMergeResult,
    SceneBuildArtifact,
    SceneStateSnapshot,
    SceneDiagnosticBundle,
)


class UniversalSceneFabricator:
    """Core fabricator coordinating entity hierarchies, prefabs, serialization, diff/merge and scene build."""

    def __init__(self):
        self.scenes: Dict[str, Scene] = {}
        self.active_scene: Optional[Scene] = None
        self.prefabs: Dict[str, Prefab] = {}
        self.undo_stack: List[Tuple[Callable[[], None], Callable[[], None]]] = []
        self.redo_stack: List[Tuple[Callable[[], None], Callable[[], None]]] = []
        self.snapshots: List[SceneStateSnapshot] = []

    # --------------------------------------------------------------------------
    # 1. Scene Management
    # --------------------------------------------------------------------------

    def create_scene(self, scene_id: str, scene_path: str, name: str = "NewScene") -> Scene:
        norm_path = normalize_scene_path(scene_path)
        root_entity = Entity(entity_id="root", name="SceneRoot")
        scene = Scene(
            scene_id=scene_id,
            scene_path=norm_path,
            name=name,
            root_entity_id="root",
            entities={"root": root_entity}
        )
        self.scenes[scene_id] = scene
        self.active_scene = scene
        return scene

    def get_scene(self, scene_id: str) -> Optional[Scene]:
        return self.scenes.get(scene_id)

    def mark_dirty(self, scene: Optional[Scene] = None) -> None:
        target = scene or self.active_scene
        if target:
            target.is_dirty = True
            target.scene_version += 1
            target.content_fingerprint = target.compute_fingerprint()

    # --------------------------------------------------------------------------
    # 2. Entity Management & Hierarchy
    # --------------------------------------------------------------------------

    def create_entity(
        self,
        entity_id: str,
        name: str = "Entity",
        parent_id: Optional[str] = None,
        scene: Optional[Scene] = None
    ) -> Entity:
        target_scene = scene or self.active_scene
        if not target_scene:
            raise ValueError("NO_ACTIVE_SCENE: Cannot create entity without an active scene.")
        if entity_id in target_scene.entities:
            raise ValueError(f"NO_DUPLICATE_ENTITY_ID: Entity '{entity_id}' already exists in scene.")

        effective_parent = parent_id or target_scene.root_entity_id
        if effective_parent and effective_parent not in target_scene.entities:
            raise ValueError(f"PARENT_NOT_FOUND: Parent entity '{effective_parent}' does not exist.")

        entity = Entity(entity_id=entity_id, name=name, parent_id=effective_parent)
        target_scene.entities[entity_id] = entity

        if effective_parent:
            parent = target_scene.entities[effective_parent]
            if entity_id not in parent.children_ids:
                parent.children_ids.append(entity_id)

        self.mark_dirty(target_scene)
        return entity

    def set_parent(
        self,
        entity_id: str,
        new_parent_id: Optional[str],
        scene: Optional[Scene] = None
    ) -> None:
        target_scene = scene or self.active_scene
        if not target_scene:
            raise ValueError("NO_ACTIVE_SCENE")
        if entity_id not in target_scene.entities:
            raise ValueError(f"ENTITY_NOT_FOUND: Entity '{entity_id}' not found.")
        if entity_id == target_scene.root_entity_id:
            raise ValueError("ROOT_CANNOT_BE_REPARENTED: Cannot reparent the root entity.")
        if entity_id == new_parent_id:
            raise ValueError("SELF_PARENTING_PROHIBITED: Entity cannot be its own parent.")

        if new_parent_id is not None:
            if new_parent_id not in target_scene.entities:
                raise ValueError(f"PARENT_NOT_FOUND: Parent '{new_parent_id}' not found.")
            # Cycle check: traverse new_parent ancestors to ensure entity_id is not among them
            curr: Optional[str] = new_parent_id
            while curr:
                if curr == entity_id:
                    raise ValueError(f"NO_HIERARCHY_CYCLES: Reparenting creates a cycle with '{entity_id}'.")
                curr = target_scene.entities[curr].parent_id

        entity = target_scene.entities[entity_id]
        old_parent_id = entity.parent_id
        if old_parent_id and old_parent_id in target_scene.entities:
            target_scene.entities[old_parent_id].children_ids = [
                c for c in target_scene.entities[old_parent_id].children_ids if c != entity_id
            ]

        entity.parent_id = new_parent_id
        if new_parent_id and new_parent_id in target_scene.entities:
            target_scene.entities[new_parent_id].children_ids.append(entity_id)

        self.mark_dirty(target_scene)

    def delete_entity(self, entity_id: str, scene: Optional[Scene] = None) -> None:
        target_scene = scene or self.active_scene
        if not target_scene:
            raise ValueError("NO_ACTIVE_SCENE")
        if entity_id not in target_scene.entities:
            return
        if entity_id == target_scene.root_entity_id:
            raise ValueError("CANNOT_DELETE_ROOT: Root entity cannot be deleted.")

        entity = target_scene.entities[entity_id]
        # Recursively delete children
        for child_id in list(entity.children_ids):
            self.delete_entity(child_id, target_scene)

        # Unparent
        if entity.parent_id and entity.parent_id in target_scene.entities:
            target_scene.entities[entity.parent_id].children_ids = [
                c for c in target_scene.entities[entity.parent_id].children_ids if c != entity_id
            ]

        del target_scene.entities[entity_id]
        self.mark_dirty(target_scene)

    def compute_world_transform(self, entity_id: str, scene: Optional[Scene] = None) -> Transform:
        target_scene = scene or self.active_scene
        if not target_scene or entity_id not in target_scene.entities:
            return Transform()

        # Traverse upwards to root
        chain: List[Entity] = []
        curr: Optional[str] = entity_id
        visited: Set[str] = set()
        while curr and curr in target_scene.entities:
            if curr in visited:
                break
            visited.add(curr)
            chain.append(target_scene.entities[curr])
            curr = target_scene.entities[curr].parent_id

        # Accumulate top-down
        combined = Transform()
        for ent in reversed(chain):
            combined = ent.transform.combine(combined)
        return combined

    # --------------------------------------------------------------------------
    # 3. Component Management
    # --------------------------------------------------------------------------

    def add_component(
        self,
        entity_id: str,
        component: Component,
        scene: Optional[Scene] = None
    ) -> None:
        target_scene = scene or self.active_scene
        if not target_scene or entity_id not in target_scene.entities:
            raise ValueError("ENTITY_NOT_FOUND")
        target_scene.entities[entity_id].components[component.component_id] = component
        self.mark_dirty(target_scene)

    def get_component(
        self,
        entity_id: str,
        component_type: ComponentType,
        scene: Optional[Scene] = None
    ) -> Optional[Component]:
        target_scene = scene or self.active_scene
        if not target_scene or entity_id not in target_scene.entities:
            return None
        for comp in target_scene.entities[entity_id].components.values():
            if comp.component_type == component_type:
                return comp
        return None

    # --------------------------------------------------------------------------
    # 4. Prefab System
    # --------------------------------------------------------------------------

    def register_prefab(self, prefab: Prefab) -> None:
        self.prefabs[prefab.prefab_id] = prefab

    def create_prefab_from_entity(
        self,
        prefab_id: str,
        name: str,
        root_entity_id: str,
        scene: Optional[Scene] = None
    ) -> Prefab:
        target_scene = scene or self.active_scene
        if not target_scene or root_entity_id not in target_scene.entities:
            raise ValueError("ROOT_ENTITY_NOT_FOUND")

        # Extract subtree
        subtree: Dict[str, Entity] = {}
        def collect(eid: str):
            e = target_scene.entities[eid]
            subtree[eid] = copy.deepcopy(e)
            for c in e.children_ids:
                if c in target_scene.entities:
                    collect(c)

        collect(root_entity_id)
        prefab = Prefab(prefab_id=prefab_id, name=name, root_entity_id=root_entity_id, entities=subtree)
        self.register_prefab(prefab)
        if target_scene:
            target_scene.prefabs[prefab_id] = prefab
        return prefab

    def instantiate_prefab(
        self,
        prefab_id: str,
        instance_id: str,
        parent_id: Optional[str] = None,
        scene: Optional[Scene] = None
    ) -> List[Entity]:
        target_scene = scene or self.active_scene
        if not target_scene:
            raise ValueError("NO_ACTIVE_SCENE")
        if prefab_id not in self.prefabs:
            raise ValueError(f"PREFAB_NOT_FOUND: Prefab '{prefab_id}' does not exist.")

        prefab = self.prefabs[prefab_id]
        inst = PrefabInstance(instance_id=instance_id, prefab_id=prefab_id, root_entity_id="")
        target_scene.prefab_instances[instance_id] = inst

        id_map: Dict[str, str] = {}
        cloned_entities: List[Entity] = []

        # Generate unique IDs for all entities in prefab
        for orig_id in prefab.entities:
            new_id = f"{instance_id}_{orig_id}"
            id_map[orig_id] = new_id

        inst.root_entity_id = id_map[prefab.root_entity_id]

        for orig_id, orig_ent in prefab.entities.items():
            new_id = id_map[orig_id]
            new_parent = id_map[orig_ent.parent_id] if orig_ent.parent_id and orig_ent.parent_id in id_map else (parent_id or target_scene.root_entity_id)
            new_children = [id_map[c] for c in orig_ent.children_ids if c in id_map]
            cloned = Entity(
                entity_id=new_id,
                name=f"{orig_ent.name} (Instance)",
                parent_id=new_parent,
                children_ids=new_children,
                components=copy.deepcopy(orig_ent.components),
                transform=copy.deepcopy(orig_ent.transform),
                prefab_instance_id=instance_id,
                is_active=orig_ent.is_active,
                flags=copy.deepcopy(orig_ent.flags)
            )
            target_scene.entities[new_id] = cloned
            cloned_entities.append(cloned)

        # Attach root of prefab to parent
        effective_parent = parent_id or target_scene.root_entity_id
        if effective_parent in target_scene.entities:
            target_scene.entities[effective_parent].children_ids.append(inst.root_entity_id)

        self.mark_dirty(target_scene)
        return cloned_entities

    def apply_override(
        self,
        instance_id: str,
        override: PrefabOverride,
        scene: Optional[Scene] = None
    ) -> None:
        target_scene = scene or self.active_scene
        if not target_scene or instance_id not in target_scene.prefab_instances:
            raise ValueError("INSTANCE_NOT_FOUND")

        inst = target_scene.prefab_instances[instance_id]
        inst.overrides.append(override)

        # Apply property override directly
        if override.target_entity_id in target_scene.entities:
            ent = target_scene.entities[override.target_entity_id]
            if override.override_type == OverrideType.PROPERTY:
                parts = override.property_path.split(".")
                if parts[0] == "name":
                    ent.name = str(override.value)
                elif parts[0] == "transform" and len(parts) >= 2:
                    setattr(ent.transform, parts[1], override.value)
                elif parts[0] in ent.components:
                    comp = ent.components[parts[0]]
                    if len(parts) >= 2:
                        comp.properties[parts[1]] = override.value

        self.mark_dirty(target_scene)

    def revert_override(
        self,
        instance_id: str,
        property_path: str,
        scene: Optional[Scene] = None
    ) -> None:
        target_scene = scene or self.active_scene
        if not target_scene or instance_id not in target_scene.prefab_instances:
            return
        inst = target_scene.prefab_instances[instance_id]
        inst.overrides = [ov for ov in inst.overrides if ov.property_path != property_path]
        self.mark_dirty(target_scene)

    # --------------------------------------------------------------------------
    # 5. Serialization
    # --------------------------------------------------------------------------

    def serialize_scene(self, scene: Optional[Scene] = None) -> str:
        target_scene = scene or self.active_scene
        if not target_scene:
            raise ValueError("NO_ACTIVE_SCENE")
        return target_scene.to_json()

    def deserialize_scene(self, json_str: str) -> Scene:
        data = json.loads(json_str)
        scene = Scene(
            scene_id=data["scene_id"],
            scene_path=data["scene_path"],
            name=data.get("name", "Scene"),
            scene_version=data.get("scene_version", 1),
            root_entity_id=data.get("root_entity_id", "root"),
            schema_version=data.get("schema_version", "1.0.0"),
            metadata=data.get("metadata", {})
        )
        for eid, ed in data.get("entities", {}).items():
            components = {
                cid: Component(
                    component_id=cd["component_id"],
                    component_type=ComponentType(cd["component_type"]),
                    schema_version=cd.get("schema_version", "1.0.0"),
                    properties=cd.get("properties", {})
                )
                for cid, cd in ed.get("components", {}).items()
            }
            tf = ed.get("transform", {})
            transform = Transform(
                position=tf.get("position", [0.0, 0.0, 0.0]),
                rotation=tf.get("rotation", [0.0, 0.0, 0.0]),
                scale=tf.get("scale", [1.0, 1.0, 1.0]),
            )
            ent = Entity(
                entity_id=ed["entity_id"],
                name=ed.get("name", "Entity"),
                parent_id=ed.get("parent_id"),
                children_ids=ed.get("children_ids", []),
                components=components,
                transform=transform,
                prefab_instance_id=ed.get("prefab_instance_id"),
                is_active=ed.get("is_active", True),
                flags=ed.get("flags", {})
            )
            scene.entities[eid] = ent

        for pid, pd in data.get("prefabs", {}).items():
            pf_entities = {}
            for peid, ped in pd.get("entities", {}).items():
                comps = {
                    cid: Component(
                        component_id=cd["component_id"],
                        component_type=ComponentType(cd["component_type"]),
                        schema_version=cd.get("schema_version", "1.0.0"),
                        properties=cd.get("properties", {})
                    )
                    for cid, cd in ped.get("components", {}).items()
                }
                tf = ped.get("transform", {})
                transform = Transform(
                    position=tf.get("position", [0.0, 0.0, 0.0]),
                    rotation=tf.get("rotation", [0.0, 0.0, 0.0]),
                    scale=tf.get("scale", [1.0, 1.0, 1.0]),
                )
                pf_entities[peid] = Entity(
                    entity_id=ped["entity_id"],
                    name=ped.get("name", "Entity"),
                    parent_id=ped.get("parent_id"),
                    children_ids=ped.get("children_ids", []),
                    components=comps,
                    transform=transform,
                    prefab_instance_id=ped.get("prefab_instance_id"),
                    is_active=ped.get("is_active", True),
                    flags=ped.get("flags", {})
                )
            scene.prefabs[pid] = Prefab(
                prefab_id=pd["prefab_id"],
                name=pd.get("name", "Prefab"),
                root_entity_id=pd.get("root_entity_id", "root"),
                entities=pf_entities,
                nested_prefab_ids=pd.get("nested_prefab_ids", [])
            )

        for iid, idat in data.get("prefab_instances", {}).items():
            overrides = [
                PrefabOverride(
                    override_type=OverrideType(od["override_type"]),
                    target_entity_id=od["target_entity_id"],
                    property_path=od["property_path"],
                    value=od["value"]
                )
                for od in idat.get("overrides", [])
            ]
            scene.prefab_instances[iid] = PrefabInstance(
                instance_id=idat["instance_id"],
                prefab_id=idat["prefab_id"],
                root_entity_id=idat.get("root_entity_id", "root"),
                overrides=overrides
            )

        scene.content_fingerprint = scene.compute_fingerprint()
        self.scenes[scene.scene_id] = scene
        return scene

    # --------------------------------------------------------------------------
    # 6. Diff & Merge
    # --------------------------------------------------------------------------

    def diff_scenes(self, base: Scene, modified: Scene) -> SceneDiff:
        base_eids = set(base.entities.keys())
        mod_eids = set(modified.entities.keys())

        added = list(mod_eids - base_eids)
        removed = list(base_eids - mod_eids)
        common = base_eids & mod_eids

        modified_ents = []
        prop_changes: Dict[str, Dict[str, Any]] = {}
        for eid in common:
            e_base = base.entities[eid]
            e_mod = modified.entities[eid]
            if e_base.to_dict() != e_mod.to_dict():
                modified_ents.append(eid)
                prop_changes[eid] = {
                    "base": e_base.to_dict(),
                    "modified": e_mod.to_dict()
                }

        return SceneDiff(
            added_entities=sorted(added),
            removed_entities=sorted(removed),
            modified_entities=sorted(modified_ents),
            property_changes=prop_changes
        )

    def merge_scenes(
        self,
        base: Scene,
        mine: Scene,
        theirs: Scene,
        strategy: MergeConflictResolution = MergeConflictResolution.TAKE_MINE
    ) -> SceneMergeResult:
        diff_mine = self.diff_scenes(base, mine)
        diff_theirs = self.diff_scenes(base, theirs)

        # Detect conflicts: entity modified in both with different values, or deleted in one and modified in other
        conflicts = []
        common_mods = set(diff_mine.modified_entities) & set(diff_theirs.modified_entities)
        for eid in common_mods:
            if mine.entities[eid].to_dict() != theirs.entities[eid].to_dict():
                conflicts.append({
                    "entity_id": eid,
                    "type": "MODIFY_MODIFY_CONFLICT",
                    "mine": mine.entities[eid].to_dict(),
                    "theirs": theirs.entities[eid].to_dict()
                })

        # Base clone for merged result
        merged = copy.deepcopy(mine if strategy == MergeConflictResolution.TAKE_MINE else theirs)
        # Apply additions from theirs if not in mine
        for eid in diff_theirs.added_entities:
            if eid not in merged.entities:
                merged.entities[eid] = copy.deepcopy(theirs.entities[eid])

        return SceneMergeResult(
            success=len(conflicts) == 0 or strategy != MergeConflictResolution.MANUAL,
            merged_scene=merged,
            conflicts=conflicts
        )

    # --------------------------------------------------------------------------
    # 7. Scene Build
    # --------------------------------------------------------------------------

    def build_scene(
        self,
        scene: Optional[Scene] = None,
        mode: SceneBuildMode = SceneBuildMode.DEVELOPMENT,
        output_path: str = "/Game/BuiltScenes/Scene.uasset"
    ) -> SceneBuildArtifact:
        target_scene = scene or self.active_scene
        if not target_scene:
            raise ValueError("NO_ACTIVE_SCENE")

        norm_out = normalize_scene_path(output_path)
        content_json = target_scene.to_json()
        c_hash = hashlib.sha256(content_json.encode("utf-8")).hexdigest()
        art_id = f"scene_artifact_{target_scene.scene_id}_{mode.value}"

        return SceneBuildArtifact(
            artifact_id=art_id,
            scene_id=target_scene.scene_id,
            build_mode=mode,
            output_path=norm_out,
            entity_count=len(target_scene.entities),
            content_hash=c_hash
        )

    # --------------------------------------------------------------------------
    # 8. Command History & Snapshots
    # --------------------------------------------------------------------------

    def execute_command(self, do_fn: Callable[[], None], undo_fn: Callable[[], None]) -> None:
        do_fn()
        self.undo_stack.append((do_fn, undo_fn))
        self.redo_stack.clear()

    def undo(self) -> bool:
        if not self.undo_stack:
            return False
        do_fn, undo_fn = self.undo_stack.pop()
        undo_fn()
        self.redo_stack.append((do_fn, undo_fn))
        return True

    def redo(self) -> bool:
        if not self.redo_stack:
            return False
        do_fn, undo_fn = self.redo_stack.pop()
        do_fn()
        self.undo_stack.append((do_fn, undo_fn))
        return True

    def take_snapshot(self) -> SceneStateSnapshot:
        snap_id = f"snap_scene_{int(time.time() * 1000)}"
        scene_data = self.active_scene.to_dict() if self.active_scene else {}
        snap = SceneStateSnapshot(snapshot_id=snap_id, timestamp=time.time(), scene_data=scene_data)
        self.snapshots.append(snap)
        return snap

    def generate_diagnostic_bundle(self) -> SceneDiagnosticBundle:
        b_id = f"bundle_scene_{int(time.time() * 1000)}"
        snap = self.take_snapshot()
        return SceneDiagnosticBundle(bundle_id=b_id, timestamp=time.time(), snapshot=snap)
