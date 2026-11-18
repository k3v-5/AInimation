"""
GameplayNodeType, GameplayNode, GameplayEdge, and GameplayGraph models.
UAF-81.20 Sections 6, 7, 8, 9, 10, 153.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from collections import deque


class GameplayNodeType(str, Enum):
    START = "START"
    END = "END"
    OBJECTIVE = "OBJECTIVE"
    ENCOUNTER = "ENCOUNTER"
    CHECKPOINT = "CHECKPOINT"
    TRIGGER = "TRIGGER"
    BRANCH = "BRANCH"
    SPAWN = "SPAWN"
    BOSS = "BOSS"
    REWARD = "REWARD"
    FAILURE = "FAILURE"


@dataclass
class GameplayNode:
    node_id: str
    node_type: GameplayNodeType
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "description": self.description,
        }


@dataclass
class GameplayEdge:
    from_node: str
    to_node: str
    transition_condition: str = "COMPLETED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_node": self.from_node,
            "to_node": self.to_node,
            "transition_condition": self.transition_condition,
        }


@dataclass
class GameplayGraph:
    nodes: Dict[str, GameplayNode] = field(default_factory=dict)
    edges: List[GameplayEdge] = field(default_factory=list)

    def add_node(self, node: GameplayNode) -> None:
        self.nodes[node.node_id] = node

    def add_edge(self, from_id: str, to_id: str, condition: str = "COMPLETED") -> None:
        self.edges.append(GameplayEdge(from_id, to_id, condition))

    def has_start_and_end(self) -> bool:
        has_start = any(n.node_type == GameplayNodeType.START for n in self.nodes.values())
        has_end = any(n.node_type == GameplayNodeType.END for n in self.nodes.values())
        return has_start and has_end

    def is_solvable_path_exists(self) -> bool:
        """Verifies using BFS that a path exists from START node to END node."""
        start_nodes = [nid for nid, n in self.nodes.items() if n.node_type == GameplayNodeType.START]
        end_nodes = [nid for nid, n in self.nodes.items() if n.node_type == GameplayNodeType.END]
        if not start_nodes or not end_nodes:
            return False

        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        for edge in self.edges:
            if edge.from_node in adj and edge.to_node in self.nodes:
                adj[edge.from_node].append(edge.to_node)

        for start_id in start_nodes:
            visited = set([start_id])
            queue = deque([start_id])
            while queue:
                curr = queue.popleft()
                if curr in end_nodes:
                    return True
                for neighbor in adj.get(curr, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": {k: v.to_dict() for k, v in sorted(self.nodes.items())},
            "edges": [e.to_dict() for e in self.edges],
            "has_start_and_end": self.has_start_and_end(),
            "is_solvable": self.is_solvable_path_exists(),
        }
