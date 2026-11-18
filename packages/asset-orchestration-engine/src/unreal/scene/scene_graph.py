import copy
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .actor_registry import UnrealActor, ActorRegistry

@dataclass
class SceneSnapshot:
    scene_id: str
    scene_version: int
    actors: Dict[str, UnrealActor]

class SceneGraph:
    def __init__(self, scene_id: str = "Level_001"):
        self.scene_id = scene_id
        self.scene_version: int = 1
        self.registry = ActorRegistry()

    def create_snapshot(self) -> SceneSnapshot:
        return SceneSnapshot(
            scene_id=self.scene_id,
            scene_version=self.scene_version,
            actors=copy.deepcopy(self.registry.actors)
        )

    def restore_snapshot(self, snapshot: SceneSnapshot):
        self.scene_id = snapshot.scene_id
        self.scene_version = snapshot.scene_version
        self.registry.actors = copy.deepcopy(snapshot.actors)

    def get_children(self, parent_actor_id: str) -> List[UnrealActor]:
        return self.registry.find_by_parent(parent_actor_id)
