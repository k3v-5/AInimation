from typing import Dict, Any, Optional, List, Tuple
from ..core.unreal_engine import UnrealEngine
from ..scene.actor_registry import UnrealActor
from ..assets.asset_registry import UnrealAssetReference

class UnrealAPI:
    def __init__(self, unreal_engine: UnrealEngine):
        self.engine = unreal_engine

    def register_asset(self, logical_asset_id: str, unreal_package_path: str, asset_class: str = "StaticMesh") -> UnrealAssetReference:
        return self.engine.register_asset(logical_asset_id, unreal_package_path, asset_class)

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
        return self.engine.spawn_actor(
            asset_id=asset_id,
            name=name,
            location=location,
            rotation=rotation,
            scale=scale,
            tags=tags,
            parent_id=parent_id,
            attached_socket=attached_socket,
            dimensions_cm=dimensions_cm,
            actor_id=actor_id
        )

    def move_actor(self, target: str, delta: Optional[Tuple[float, float, float]] = None, new_location: Optional[Tuple[float, float, float]] = None, scope: Optional[List[str]] = None, dry_run: bool = False) -> Dict[str, Any]:
        return self.engine.move_actor(target, delta=delta, new_location=new_location, scope=scope, dry_run=dry_run)

    def attach_actor(self, child: str, parent: str, socket_name: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
        return self.engine.attach_actor(child, parent, socket_name=socket_name, dry_run=dry_run)

    def set_property(self, actor: str, prop_name: str, value: Any, is_exposed: bool = True, dry_run: bool = False) -> Dict[str, Any]:
        return self.engine.set_property(actor, prop_name, value, is_exposed=is_exposed, dry_run=dry_run)

    def override_material(self, actor: str, slot_index: int, material_path: str, dry_run: bool = False) -> Dict[str, Any]:
        return self.engine.override_material(actor, slot_index, material_path, dry_run=dry_run)

    def apply_spatial_relation(self, target: str, relation: str, reference: str, offset: Tuple[float, float, float] = (0.0, 0.0, 0.0), dry_run: bool = False) -> Dict[str, Any]:
        return self.engine.apply_spatial_relation(target, relation, reference, offset=offset, dry_run=dry_run)

    def delete_actor(self, actor: str, dry_run: bool = False) -> Dict[str, Any]:
        return self.engine.delete_actor(actor, dry_run=dry_run)

    def validate_scene(self) -> Dict[str, Any]:
        return self.engine.validate_scene()
