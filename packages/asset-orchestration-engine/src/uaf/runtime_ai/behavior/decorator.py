"""
UAF-81.82: Behavior Tree Decorator Nodes.
"""

from __future__ import annotations

from typing import Callable, Optional
from ..models.definition import NodeStatus
from .node import BTContext, BTNode


class InverterDecorator(BTNode):
    """Inverts SUCCESS to FAILURE and FAILURE to SUCCESS. Preserves RUNNING."""

    def __init__(self, node_id: str, child: BTNode, name: str = ""):
        super().__init__(node_id, name)
        self.child = child

    def tick(self, context: BTContext) -> NodeStatus:
        res = self.child.tick(context)
        if res == NodeStatus.SUCCESS:
            self.status = NodeStatus.FAILURE
        elif res == NodeStatus.FAILURE:
            self.status = NodeStatus.SUCCESS
        else:
            self.status = res
        return self.status

    def abort(self, context: BTContext) -> None:
        self.child.abort(context)
        self.status = NodeStatus.ABORTED

    def reset(self) -> None:
        self.child.reset()
        self.status = NodeStatus.FAILURE


class RepeaterDecorator(BTNode):
    """Repeats child execution up to max_repeats times (or infinite if max_repeats <= 0)."""

    def __init__(self, node_id: str, child: BTNode, max_repeats: int = 1, name: str = ""):
        super().__init__(node_id, name)
        self.child = child
        self.max_repeats = max_repeats
        self._iteration: int = 0

    def enter(self, context: BTContext) -> None:
        self._iteration = 0
        self.status = NodeStatus.RUNNING

    def tick(self, context: BTContext) -> NodeStatus:
        res = self.child.tick(context)
        if res == NodeStatus.RUNNING:
            self.status = NodeStatus.RUNNING
            return self.status

        self._iteration += 1
        self.child.reset()

        if 0 < self.max_repeats <= self._iteration:
            self.status = NodeStatus.SUCCESS
            return self.status

        self.status = NodeStatus.RUNNING
        return self.status

    def abort(self, context: BTContext) -> None:
        self.child.abort(context)
        self._iteration = 0
        self.status = NodeStatus.ABORTED

    def reset(self) -> None:
        self._iteration = 0
        self.child.reset()
        self.status = NodeStatus.FAILURE


class CooldownDecorator(BTNode):
    """Prevents child execution until cooldown_ticks have elapsed since last completion."""

    def __init__(self, node_id: str, child: BTNode, cooldown_ticks: int = 10, name: str = ""):
        super().__init__(node_id, name)
        self.child = child
        self.cooldown_ticks = cooldown_ticks
        self._last_completed_tick: int = -999999

    def tick(self, context: BTContext) -> NodeStatus:
        if context.tick - self._last_completed_tick < self.cooldown_ticks:
            self.status = NodeStatus.FAILURE
            return self.status

        res = self.child.tick(context)
        if res in (NodeStatus.SUCCESS, NodeStatus.FAILURE):
            self._last_completed_tick = context.tick
            self.status = res
        else:
            self.status = res
        return self.status

    def abort(self, context: BTContext) -> None:
        self.child.abort(context)
        self.status = NodeStatus.ABORTED

    def reset(self) -> None:
        self.child.reset()
        self.status = NodeStatus.FAILURE


class TimeoutDecorator(BTNode):
    """Aborts child and returns FAILURE if child remains RUNNING for longer than timeout_ticks."""

    def __init__(self, node_id: str, child: BTNode, timeout_ticks: int = 30, name: str = ""):
        super().__init__(node_id, name)
        self.child = child
        self.timeout_ticks = timeout_ticks
        self._running_ticks: int = 0

    def tick(self, context: BTContext) -> NodeStatus:
        res = self.child.tick(context)
        if res == NodeStatus.RUNNING:
            self._running_ticks += 1
            if self._running_ticks >= self.timeout_ticks:
                self.child.abort(context)
                self._running_ticks = 0
                self.status = NodeStatus.FAILURE
                return self.status
            self.status = NodeStatus.RUNNING
            return self.status

        self._running_ticks = 0
        self.status = res
        return self.status

    def abort(self, context: BTContext) -> None:
        self.child.abort(context)
        self._running_ticks = 0
        self.status = NodeStatus.ABORTED

    def reset(self) -> None:
        self._running_ticks = 0
        self.child.reset()
        self.status = NodeStatus.FAILURE


class ConditionGateDecorator(BTNode):
    """Permits child execution only if predicate(blackboard) evaluates to True."""

    def __init__(self, node_id: str, child: BTNode, predicate: Callable[[Any], bool], name: str = ""):
        super().__init__(node_id, name)
        self.child = child
        self.predicate = predicate

    def tick(self, context: BTContext) -> NodeStatus:
        if not self.predicate(context.blackboard):
            self.status = NodeStatus.FAILURE
            return self.status
        self.status = self.child.tick(context)
        return self.status

    def abort(self, context: BTContext) -> None:
        self.child.abort(context)
        self.status = NodeStatus.ABORTED

    def reset(self) -> None:
        self.child.reset()
        self.status = NodeStatus.FAILURE
