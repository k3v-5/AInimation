from typing import Dict, List, Optional, Set
from .scene_schema import SceneNode
from .scene_status import NodeDirtyState

class SceneGraph:
    def __init__(self):
        self.nodes: Dict[str, SceneNode] = {}
        self.edges: Dict[str, List[str]] = {} # parent -> [children]

    def add_node(self, node: SceneNode):
        self.nodes[node.node_id] = node
        if node.node_id not in self.edges:
            self.edges[node.node_id] = []

    def add_dependency(self, parent_id: str, child_id: str):
        if parent_id in self.edges:
            self.edges[parent_id].append(child_id)

    def mark_dirty(self, node_id: str, propagate: bool = True) -> Set[str]:
        affected = set()
        if node_id in self.nodes:
            self.nodes[node_id].dirty_state = NodeDirtyState.DIRTY
            affected.add(node_id)

            if propagate:
                for child_id in self.edges.get(node_id, []):
                    affected.update(self.mark_dirty(child_id, propagate=True))

        return affected

    def get_dirty_nodes(self) -> List[SceneNode]:
        return [n for n in self.nodes.values() if n.dirty_state == NodeDirtyState.DIRTY]
