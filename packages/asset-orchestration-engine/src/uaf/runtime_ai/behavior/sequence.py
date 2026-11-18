"""
UAF-81.82: Sequence Composite Node.
"""

from __future__ import annotations

from typing import List
from ..models.definition import NodeStatus
from .node import BTContext, BTNode


class SequenceNode(BTNode):
    """
    Executes children sequentially in ordered array:
    - If a child returns RUNNING -> Sequence returns RUNNING.
    - If a child returns FAILURE -> Sequence aborts remaining and returns FAILURE.
    - If a child returns SUCCESS -> Sequence proceeds to next child.
    - When all children return SUCCESS -> Sequence returns SUCCESS.
    """

    def __init__(self, node_id: str, children: List[BTNode], name: str = ""):
        super().__init__(node_id, name)
        self.children = children
        self._current_idx: int = 0

    def enter(self, context: BTContext) -> None:
        self._current_idx = 0
        self.status = NodeStatus.RUNNING

    def tick(self, context: BTContext) -> NodeStatus:
        if not self.children:
            self.status = NodeStatus.SUCCESS
            return self.status

        while self._current_idx < len(self.children):
            child = self.children[self._current_idx]
            child_status = child.tick(context)

            if child_status == NodeStatus.RUNNING:
                self.status = NodeStatus.RUNNING
                return self.status

            if child_status == NodeStatus.FAILURE:
                self.reset()
                self.status = NodeStatus.FAILURE
                return self.status

            if child_status == NodeStatus.SUCCESS:
                self._current_idx += 1

        self.reset()
        self.status = NodeStatus.SUCCESS
        return self.status

    def abort(self, context: BTContext) -> None:
        if 0 <= self._current_idx < len(self.children):
            self.children[self._current_idx].abort(context)
        self.reset()
        self.status = NodeStatus.ABORTED

    def reset(self) -> None:
        self._current_idx = 0
        for child in self.children:
            child.reset()
