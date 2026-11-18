import copy
from typing import Dict, Any, List, Set, Optional
from ..core.world_types import (
    NodeType, EdgeType, DependencyStrength, DirtyState
)
from ..core.world_schema import WorldNode, WorldEdge

class WorldDependencyGraph:
    def __init__(self):
        self.nodes: Dict[str, WorldNode] = {}
        self.edges: Dict[str, WorldEdge] = {}
        self.outgoing: Dict[str, List[str]] = {} # node_id -> [edge_id]
        self.incoming: Dict[str, List[str]] = {} # node_id -> [edge_id]

    def add_node(self, node: WorldNode):
        self.nodes[node.node_id] = copy.deepcopy(node)
        if node.node_id not in self.outgoing:
            self.outgoing[node.node_id] = []
        if node.node_id not in self.incoming:
            self.incoming[node.node_id] = []

    def add_edge(self, edge: WorldEdge):
        if edge.source_id not in self.nodes:
            raise KeyError(f"Source node '{edge.source_id}' does not exist.")
        if edge.target_id not in self.nodes:
            raise KeyError(f"Target node '{edge.target_id}' does not exist.")

        self.edges[edge.edge_id] = copy.deepcopy(edge)
        self.outgoing[edge.source_id].append(edge.edge_id)
        self.incoming[edge.target_id].append(edge.edge_id)

    def get_dependencies(self, node_id: str) -> List[str]:
        # Nodos de los que depende este nodo (outgoing targets)
        if node_id not in self.outgoing:
            return []
        return [self.edges[eid].target_id for eid in self.outgoing[node_id]]

    def get_consumers(self, node_id: str) -> List[str]:
        # Nodos que consumen o dependen de este nodo (incoming sources)
        if node_id not in self.incoming:
            return []
        return [self.edges[eid].source_id for eid in self.incoming[node_id]]

    def detect_cycles(self) -> Optional[List[str]]:
        # Algoritmo de detección de ciclos con DFS (3 colores: WHITE=0, GRAY=1, BLACK=2)
        color = {nid: 0 for nid in self.nodes}
        parent_map = {}
        cycle_path = []

        def dfs(u):
            color[u] = 1
            for target in self.get_dependencies(u):
                if color[target] == 1:
                    cycle_path.append(u)
                    cycle_path.append(target)
                    return True
                elif color[target] == 0:
                    parent_map[target] = u
                    if dfs(target):
                        return True
            color[u] = 2
            return False

        for nid in self.nodes:
            if color[nid] == 0:
                if dfs(nid):
                    return cycle_path
        return None

    def calculate_health_score(self) -> float:
        if not self.nodes:
            return 1.0
        cycles = self.detect_cycles()
        if cycles:
            return 0.0 # Ciclo bloquea producción
        
        # Comprobar nodos rotos o inválidos
        invalid_count = sum(1 for n in self.nodes.values() if n.dirty_state == DirtyState.INVALID)
        return max(0.0, round(1.0 - (invalid_count / len(self.nodes)), 3))
