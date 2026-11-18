from typing import List, Tuple, Dict
from ..core.scene_schema import SceneNode, ProxyBounds

class ProxyScene:
    @staticmethod
    def validate_spatial_integrity(nodes: Dict[str, SceneNode]) -> Tuple[bool, List[str]]:
        errors = []
        node_list = list(nodes.values())

        for i in range(len(node_list)):
            for j in range(i + 1, len(node_list)):
                n1 = node_list[i]
                n2 = node_list[j]
                if n1.bounds.intersects(n2.bounds):
                    errors.append(f"SPATIAL_OVERLAP_ERROR: '{n1.node_id}' intersects with '{n2.node_id}'.")

        return len(errors) == 0, errors
