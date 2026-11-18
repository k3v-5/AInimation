from typing import Dict, Optional

class ObjectMapper:
    def __init__(self):
        self.node_to_blender: Dict[str, str] = {}
        self.blender_to_node: Dict[str, str] = {}

    def register(self, node_id: str, blender_name: str):
        self.node_to_blender[node_id] = blender_name
        self.blender_to_node[blender_name] = node_id

    def get_blender_name(self, node_id: str) -> str:
        return self.node_to_blender.get(node_id, node_id.replace(".", "_"))

    def get_node_id(self, blender_name: str) -> Optional[str]:
        return self.blender_to_node.get(blender_name)
