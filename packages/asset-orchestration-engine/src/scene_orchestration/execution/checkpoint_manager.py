from typing import Dict, List, Set, Any, Optional

class CheckpointManager:
    def __init__(self):
        self.checkpoints: Dict[str, Dict[str, Any]] = {} # scene_id -> {stage, built_nodes: set}

    def save_checkpoint(self, scene_id: str, stage: int, built_nodes: Set[str]):
        self.checkpoints[scene_id] = {
            "stage": stage,
            "built_nodes": set(built_nodes)
        }

    def get_checkpoint(self, scene_id: str) -> Optional[Dict[str, Any]]:
        return self.checkpoints.get(scene_id)
