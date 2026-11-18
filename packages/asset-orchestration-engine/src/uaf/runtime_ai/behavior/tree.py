"""
UAF-81.82: Behavior Tree Manager, Integrity Validation, and Execution Orchestrator.
"""

from __future__ import annotations

from typing import List, Optional, Set
from ..models.definition import BehaviorTreeInvalid, NodeStatus
from .node import BTContext, BTNode
from .service import BTService


class BehaviorTree:
    """
    Authoritative Behavior Tree orchestrator.
    Manages tick evaluation, periodic services, cascade aborts, and cycle validation.
    """

    def __init__(self, root: BTNode, services: Optional[List[BTService]] = None):
        self.root = root
        self.services = services or []
        self.validate_integrity()

    def tick(self, context: BTContext) -> NodeStatus:
        """Evaluate attached services and tick root node."""
        for service in self.services:
            service.tick_service(context)

        return self.root.tick(context)

    def abort(self, context: BTContext) -> None:
        """Abort active tree execution."""
        self.root.abort(context)

    def reset(self) -> None:
        """Reset tree to initial state."""
        self.root.reset()

    def validate_integrity(self, max_depth: int = 64) -> None:
        """Verify that the tree is strictly acyclic and within max_depth."""
        visited: Set[str] = set()

        def check_node(node: BTNode, depth: int) -> None:
            if depth > max_depth:
                raise BehaviorTreeInvalid(f"BehaviorTree exceeded maximum recursion depth {max_depth}.")
            if node.node_id in visited:
                raise BehaviorTreeInvalid(f"Cycle detected in BehaviorTree at node '{node.node_id}'.")

            visited.add(node.node_id)

            # Recurse children if composite or decorator
            children = getattr(node, "children", None)
            if children is not None:
                for child in children:
                    check_node(child, depth + 1)
            elif hasattr(node, "child"):
                check_node(node.child, depth + 1)

            visited.remove(node.node_id)

        check_node(self.root, 1)
