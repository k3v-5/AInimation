"""
UAF-81.82: Parallel Composite Node with Explicit Termination Policies.
"""

from __future__ import annotations

from typing import List
from ..models.definition import NodeStatus, ParallelPolicy
from .node import BTContext, BTNode


class ParallelNode(BTNode):
    """
    Executes multiple child nodes concurrently during each tick.
    Requires an explicit ParallelPolicy; implicit policies are forbidden.
    """

    def __init__(
        self,
        node_id: str,
        children: List[BTNode],
        policy: ParallelPolicy = ParallelPolicy.SUCCESS_ON_ALL,
        name: str = "",
    ):
        super().__init__(node_id, name)
        self.children = children
        self.policy = policy

    def tick(self, context: BTContext) -> NodeStatus:
        if not self.children:
            self.status = NodeStatus.SUCCESS
            return self.status

        success_count = 0
        failure_count = 0
        running_count = 0

        for child in self.children:
            child_status = child.tick(context)
            if child_status == NodeStatus.SUCCESS:
                success_count += 1
            elif child_status == NodeStatus.FAILURE:
                failure_count += 1
            elif child_status == NodeStatus.RUNNING:
                running_count += 1

        total = len(self.children)

        # Policy Resolution
        if self.policy == ParallelPolicy.SUCCESS_ON_ALL:
            if failure_count > 0:
                self.abort_children(context)
                self.status = NodeStatus.FAILURE
            elif success_count == total:
                self.status = NodeStatus.SUCCESS
            else:
                self.status = NodeStatus.RUNNING

        elif self.policy == ParallelPolicy.SUCCESS_ON_ONE:
            if success_count > 0:
                self.abort_children(context)
                self.status = NodeStatus.SUCCESS
            elif failure_count == total:
                self.status = NodeStatus.FAILURE
            else:
                self.status = NodeStatus.RUNNING

        elif self.policy == ParallelPolicy.FAIL_ON_ONE:
            if failure_count > 0:
                self.abort_children(context)
                self.status = NodeStatus.FAILURE
            elif success_count == total:
                self.status = NodeStatus.SUCCESS
            else:
                self.status = NodeStatus.RUNNING

        elif self.policy == ParallelPolicy.FAIL_ON_ALL:
            if failure_count == total:
                self.status = NodeStatus.FAILURE
            elif success_count > 0 and running_count == 0:
                self.status = NodeStatus.SUCCESS
            else:
                self.status = NodeStatus.RUNNING

        return self.status

    def abort_children(self, context: BTContext) -> None:
        for child in self.children:
            child.abort(context)

    def abort(self, context: BTContext) -> None:
        self.abort_children(context)
        self.status = NodeStatus.ABORTED

    def reset(self) -> None:
        for child in self.children:
            child.reset()
        self.status = NodeStatus.FAILURE
