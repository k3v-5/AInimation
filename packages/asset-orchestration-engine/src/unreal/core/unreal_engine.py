import uuid
import copy
from typing import Dict, Any, Optional, List, Tuple
from ..assets.asset_registry import UnrealAssetRegistry, UnrealAssetReference
from ..scene.actor_registry import UnrealActor, ActorRegistry, ActorTransform
from ..scene.scene_graph import SceneGraph, SceneSnapshot
from ..spatial.spatial_solver import SpatialSolver, SpatialRelation
from ..planning.scene_diff import SceneDiff, PropertyChange
from ..planning.dependency_graph import UnrealDependencyGraph

class UnrealEngine:
    """
    Unreal Asset Integration & Scene Assembly Engine (AOE v7)
    
    Principio Fundamental:
    NO REBUILD THE WORLD WHEN ONE PROPERTY CHANGES.
    """
    def __init__(self, scene_id: str = "Level_001"):
        self.scene = SceneGraph(scene_id)
        self.assets = UnrealAssetRegistry()

    def register_asset(self, logical_asset_id: str, unreal_package_path: str, asset_class: str = "StaticMesh") -> UnrealAssetReference:
        ref = UnrealAssetReference(
            logical_asset_id=logical_asset_id,
            unreal_package_path=unreal_package_path,
            asset_class=asset_class
        )
        self.assets.register_asset(ref)
        return ref

    def spawn_actor(
        self,
        asset_id: str,
        name: str,
        location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        scale: Tuple[float, float, float] = (1.0, 1.0, 1.0),
        tags: Optional[List[str]] = None,
        parent_id: Optional[str] = None,
        attached_socket: Optional[str] = None,
        dimensions_cm: Tuple[float, float, float] = (15.0, 5.0, 95.0),
        actor_id: Optional[str] = None
    ) -> UnrealActor:
        a_id = actor_id or f"actor_{uuid.uuid4().hex[:6]}"
        actor = UnrealActor(
            actor_id=a_id,
            name=name,
            asset_id=asset_id,
            transform=ActorTransform(location=location, rotation=rotation, scale=scale),
            parent_id=parent_id,
            attached_socket=attached_socket,
            tags=tags or [],
            dimensions_cm=dimensions_cm
        )
        self.scene.registry.register_actor(actor)
        return actor

    def move_actor(
        self,
        target_id_or_name: str,
        delta: Optional[Tuple[float, float, float]] = None,
        new_location: Optional[Tuple[float, float, float]] = None,
        scope: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        # 1. Target Resolution
        actor = self._resolve_actor(target_id_or_name)
        if isinstance(actor, dict): return actor # Error (AMBIGUOUS_TARGET or ACTOR_NOT_FOUND)

        # 2. Scope check
        if scope and actor.actor_id not in scope:
            return {"success": False, "error_code": "UNREAL_SCOPE_VIOLATION", "message": f"Actor '{actor.actor_id}' is outside allowed scope {scope}."}

        cur_loc = actor.transform.location
        if new_location is not None:
            target_loc = new_location
        elif delta is not None:
            target_loc = (cur_loc[0] + delta[0], cur_loc[1] + delta[1], cur_loc[2] + delta[2])
        else:
            target_loc = cur_loc

        # 3. NO_OP detection
        if target_loc == cur_loc:
            return {"success": True, "status": "NO_OP", "actor_id": actor.actor_id, "modified_actors": 0}

        diff = SceneDiff()
        diff.modified_actors.append(actor.actor_id)
        diff.property_changes.append(PropertyChange(
            actor_id=actor.actor_id,
            property_name="location",
            before=cur_loc,
            after=target_loc
        ))

        if dry_run:
            return {"success": True, "status": "dry_run", "diff": diff.to_dict()}

        actor.transform.location = target_loc
        self.scene.scene_version += 1

        return {
            "success": True,
            "status": "completed",
            "actor_id": actor.actor_id,
            "new_location": target_loc,
            "diff": diff.to_dict()
        }

    def attach_actor(
        self,
        child_id_or_name: str,
        parent_id_or_name: str,
        socket_name: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        child = self._resolve_actor(child_id_or_name)
        if isinstance(child, dict): return child
        parent = self._resolve_actor(parent_id_or_name)
        if isinstance(parent, dict): return parent

        diff = SceneDiff()
        diff.modified_actors.append(child.actor_id)
        diff.property_changes.append(PropertyChange(
            actor_id=child.actor_id,
            property_name="attachment",
            before={"parent": child.parent_id, "socket": child.attached_socket},
            after={"parent": parent.actor_id, "socket": socket_name}
        ))

        if dry_run:
            return {"success": True, "status": "dry_run", "diff": diff.to_dict()}

        child.parent_id = parent.actor_id
        child.attached_socket = socket_name
        self.scene.scene_version += 1

        return {
            "success": True,
            "status": "completed",
            "child_actor_id": child.actor_id,
            "parent_actor_id": parent.actor_id,
            "attached_socket": socket_name,
            "diff": diff.to_dict()
        }

    def set_property(
        self,
        actor_id_or_name: str,
        prop_name: str,
        value: Any,
        is_exposed: bool = True,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        actor = self._resolve_actor(actor_id_or_name)
        if isinstance(actor, dict): return actor

        if not is_exposed:
            return {"success": False, "error_code": "PROPERTY_NOT_EDITABLE", "message": f"Property '{prop_name}' on actor '{actor.name}' is internal and hidden."}

        prev_val = actor.blueprint_properties.get(prop_name)
        if prev_val == value:
            return {"success": True, "status": "NO_OP", "actor_id": actor.actor_id}

        diff = SceneDiff()
        diff.modified_actors.append(actor.actor_id)
        diff.property_changes.append(PropertyChange(
            actor_id=actor.actor_id,
            property_name=prop_name,
            before=prev_val,
            after=value
        ))

        if dry_run:
            return {"success": True, "status": "dry_run", "diff": diff.to_dict()}

        actor.blueprint_properties[prop_name] = value
        self.scene.scene_version += 1

        return {"success": True, "status": "completed", "actor_id": actor.actor_id, "diff": diff.to_dict()}

    def override_material(
        self,
        actor_id_or_name: str,
        slot_index: int,
        material_path: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        actor = self._resolve_actor(actor_id_or_name)
        if isinstance(actor, dict): return actor

        prev_mat = actor.material_overrides.get(slot_index)
        diff = SceneDiff()
        diff.modified_actors.append(actor.actor_id)
        diff.property_changes.append(PropertyChange(
            actor_id=actor.actor_id,
            property_name=f"material_slot_{slot_index}",
            before=prev_mat,
            after=material_path
        ))

        if dry_run:
            return {"success": True, "status": "dry_run", "diff": diff.to_dict()}

        actor.material_overrides[slot_index] = material_path
        self.scene.scene_version += 1
        return {"success": True, "status": "completed", "actor_id": actor.actor_id, "diff": diff.to_dict()}

    def apply_spatial_relation(
        self,
        target_id_or_name: str,
        relation: str,
        reference_id_or_name: str,
        offset: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        dry_run: bool = False
    ) -> Dict[str, Any]:
        target = self._resolve_actor(target_id_or_name)
        if isinstance(target, dict): return target
        reference = self._resolve_actor(reference_id_or_name)
        if isinstance(reference, dict): return reference

        rel_enum = SpatialRelation(relation.upper())
        new_loc = SpatialSolver.solve_position(target, rel_enum, reference, offset)

        return self.move_actor(target.actor_id, new_location=new_loc, dry_run=dry_run)

    def delete_actor(self, actor_id_or_name: str, dry_run: bool = False) -> Dict[str, Any]:
        actor = self._resolve_actor(actor_id_or_name)
        if isinstance(actor, dict): return actor

        safe, err_msg, dependents = UnrealDependencyGraph.check_safe_delete(actor.actor_id, self.scene.registry)
        if not safe:
            return {"success": False, "error_code": "DEPENDENCY_CONFLICT", "message": err_msg, "dependents": dependents}

        diff = SceneDiff()
        diff.removed_actors.append(actor.actor_id)

        if dry_run:
            return {"success": True, "status": "dry_run", "diff": diff.to_dict()}

        self.scene.registry.remove_actor(actor.actor_id)
        self.scene.scene_version += 1
        return {"success": True, "status": "completed", "actor_id": actor.actor_id, "diff": diff.to_dict()}

    def _resolve_actor(self, identifier: str) -> Any:
        # 1. Exact ID match
        by_id = self.scene.registry.find_by_id(identifier)
        if by_id: return by_id

        # 2. Exact Name match
        by_name = self.scene.registry.find_by_name(identifier)
        if len(by_name) == 1: return by_name[0]
        if len(by_name) > 1:
            return {"success": False, "error_code": "AMBIGUOUS_TARGET", "message": f"Multiple actors found with name '{identifier}'."}

        # 3. By Asset match
        by_asset = self.scene.registry.find_by_asset(identifier)
        if len(by_asset) == 1: return by_asset[0]
        if len(by_asset) > 1:
            return {"success": False, "error_code": "AMBIGUOUS_TARGET", "message": f"Multiple actors found using asset '{identifier}'."}

        return {"success": False, "error_code": "ACTOR_NOT_FOUND", "message": f"Actor '{identifier}' not found in scene."}

    def validate_scene(self) -> Dict[str, Any]:
        actors = self.scene.registry.list_actors()
        invalid_refs = 0
        missing_assets = 0

        for a in actors:
            if a.parent_id and not self.scene.registry.find_by_id(a.parent_id):
                invalid_refs += 1
            if a.asset_id and not self.assets.get_asset(a.asset_id):
                missing_assets += 1

        is_valid = (invalid_refs == 0 and missing_assets == 0)
        return {
            "status": "PASS" if is_valid else "FAIL",
            "scene_id": self.scene.scene_id,
            "scene_version": self.scene.scene_version,
            "actor_count": len(actors),
            "invalid_references": invalid_refs,
            "missing_assets": missing_assets
        }
