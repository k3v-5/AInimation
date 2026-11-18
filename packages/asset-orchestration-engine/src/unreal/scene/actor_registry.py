import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Set

@dataclass
class ActorTransform:
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0) # X, Y, Z in cm
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0) # Roll, Pitch, Yaw in degrees
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)    # Scale multipliers

@dataclass
class UnrealActor:
    actor_id: str
    name: str
    actor_class: str = "StaticMeshActor"
    asset_id: Optional[str] = None
    transform: ActorTransform = field(default_factory=ActorTransform)
    parent_id: Optional[str] = None
    attached_socket: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    components: Dict[str, Dict[str, Any]] = field(default_factory=dict) # comp_name -> props
    material_overrides: Dict[int, str] = field(default_factory=dict) # slot -> material_path
    blueprint_properties: Dict[str, Any] = field(default_factory=dict) # prop_name -> val
    dimensions_cm: Tuple[float, float, float] = (10.0, 10.0, 10.0)

class ActorRegistry:
    def __init__(self):
        self.actors: Dict[str, UnrealActor] = {} # actor_id -> UnrealActor

    def register_actor(self, actor: UnrealActor):
        self.actors[actor.actor_id] = actor

    def find_by_id(self, actor_id: str) -> Optional[UnrealActor]:
        return self.actors.get(actor_id)

    def find_by_name(self, name: str) -> List[UnrealActor]:
        return [a for a in self.actors.values() if a.name == name]

    def find_by_tag(self, tag: str) -> List[UnrealActor]:
        return [a for a in self.actors.values() if tag in a.tags]

    def find_by_class(self, actor_class: str) -> List[UnrealActor]:
        return [a for a in self.actors.values() if a.actor_class == actor_class]

    def find_by_asset(self, asset_id: str) -> List[UnrealActor]:
        return [a for a in self.actors.values() if a.asset_id == asset_id]

    def find_by_parent(self, parent_id: str) -> List[UnrealActor]:
        return [a for a in self.actors.values() if a.parent_id == parent_id]

    def remove_actor(self, actor_id: str):
        if actor_id in self.actors:
            del self.actors[actor_id]

    def list_actors(self) -> List[UnrealActor]:
        return list(self.actors.values())
