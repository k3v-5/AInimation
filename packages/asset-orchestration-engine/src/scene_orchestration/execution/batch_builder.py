from typing import Dict, List, Tuple
from ..core.scene_schema import SceneNode
from ...correction_execution.providers.blender_provider import IBlenderProvider

class BatchSceneBuilder:
    @staticmethod
    def build_node_batch(
        scene_id: str,
        nodes_to_build: List[SceneNode],
        provider: IBlenderProvider
    ) -> Tuple[int, List[str]]:
        built_count = 0
        built_ids = []

        for node in nodes_to_build:
            # Registrar asset en Blender Provider
            comps = {
                "root": {
                    "dimensions": (node.bounds.max_point[0] - node.bounds.min_point[0],
                                   node.bounds.max_point[1] - node.bounds.min_point[1],
                                   node.bounds.max_point[2] - node.bounds.min_point[2]),
                    "location": node.location,
                    "rotation": node.rotation
                }
            }
            provider.init_asset(f"{scene_id}_{node.node_id}", comps)
            built_count += 1
            built_ids.append(node.node_id)

        return built_count, built_ids
