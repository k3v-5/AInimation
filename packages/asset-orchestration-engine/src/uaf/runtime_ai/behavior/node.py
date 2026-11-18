"""
UAF-81.82: Behavior Tree Base Node and Execution Context.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from ..models.definition import NodeStatus


class BTContext:
    """Carries execution state passed to Behavior Tree nodes on each tick."""

    def __init__(
        self,
        agent_id: str,
        blackboard: Any,  # Blackboard
        tick: int,
        delta_time: float,
        fabricator: Any = None,
    ):
        self.agent_id = agent_id
        self.blackboard = blackboard
        self.tick = tick
        self.delta_time = delta_time
        self.fabricator = fabricator


class BTNode:
    """Base class for all Behavior Tree composite, decorator, and leaf task nodes."""

    def __init__(self, node_id: str, name: str = ""):
        self.node_id = node_id
        self.name = name or node_id
        self.status = NodeStatus.FAILURE

    def enter(self, context: BTContext) -> None:
        """Invoked when node starts execution."""
        pass

    def tick(self, context: BTContext) -> NodeStatus:
        """Execute node logic for this simulation tick."""
        return NodeStatus.SUCCESS

    def exit(self, context: BTContext, status: NodeStatus) -> None:
        """Invoked when node completes with SUCCESS or FAILURE."""
        pass

    def abort(self, context: BTContext) -> None:
        """Invoked when execution is abruptly interrupted."""
        self.status = NodeStatus.ABORTED

    def reset(self) -> None:
        """Reset internal execution state."""
        self.status = NodeStatus.FAILURE
