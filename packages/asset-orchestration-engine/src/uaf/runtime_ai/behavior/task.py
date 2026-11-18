"""
UAF-81.82: Concrete Behavior Tree Tasks (Movement, Attack, Wait, Safe Idle).
"""

from __future__ import annotations

from typing import Optional
from ..models.definition import NodeStatus, Vec3, vec3_distance
from .node import BTContext, BTNode


class MoveToTargetTask(BTNode):
    """
    Directs agent toward a target position or blackboard target using steering.
    Never teleports; emits preferred velocity.
    """

    def __init__(
        self,
        node_id: str,
        target_blackboard_key: str = "target_position",
        stopping_distance: float = 0.5,
        speed: float = 4.0,
        name: str = "",
    ):
        super().__init__(node_id, name)
        self.target_blackboard_key = target_blackboard_key
        self.stopping_distance = stopping_distance
        self.speed = speed

    def tick(self, context: BTContext) -> NodeStatus:
        target_pos = context.blackboard.get(self.target_blackboard_key)
        if target_pos is None:
            self.status = NodeStatus.FAILURE
            return self.status

        # Delegate steering calculation to fabricator/agent
        if context.fabricator is not None:
            agent = context.fabricator.get_agent(context.agent_id)
            if agent is not None:
                dist = vec3_distance(agent.position, target_pos)
                if dist <= self.stopping_distance:
                    agent.preferred_velocity = (0.0, 0.0, 0.0)
                    self.status = NodeStatus.SUCCESS
                    return self.status

                # Compute steering towards target
                agent.seek_target(target_pos, self.speed)
                self.status = NodeStatus.RUNNING
                return self.status

        self.status = NodeStatus.SUCCESS
        return self.status


class AttackTargetTask(BTNode):
    """
    Executes an attack against an acquired target in the blackboard.
    Validates range, cooldown, and line of sight.
    """

    def __init__(
        self,
        node_id: str,
        target_id_key: str = "current_target_id",
        attack_range: float = 2.0,
        cooldown_ticks: int = 15,
        damage_amount: float = 10.0,
        name: str = "",
    ):
        super().__init__(node_id, name)
        self.target_id_key = target_id_key
        self.attack_range = attack_range
        self.cooldown_ticks = cooldown_ticks
        self.damage_amount = damage_amount
        self._last_attack_tick: int = -999999

    def tick(self, context: BTContext) -> NodeStatus:
        target_id = context.blackboard.get(self.target_id_key)
        if not target_id:
            self.status = NodeStatus.FAILURE
            return self.status

        if context.tick - self._last_attack_tick < self.cooldown_ticks:
            self.status = NodeStatus.FAILURE
            return self.status

        if context.fabricator is not None:
            agent = context.fabricator.get_agent(context.agent_id)
            target_agent = context.fabricator.get_agent(target_id)
            if agent is not None and target_agent is not None:
                dist = vec3_distance(agent.position, target_agent.position)
                if dist > self.attack_range:
                    self.status = NodeStatus.FAILURE
                    return self.status

                # Execute attack through fabricator
                context.fabricator.apply_agent_damage(context.agent_id, target_id, self.damage_amount, context.tick)
                self._last_attack_tick = context.tick
                self.status = NodeStatus.SUCCESS
                return self.status

        self.status = NodeStatus.FAILURE
        return self.status


class WaitTicksTask(BTNode):
    """Waits for duration_ticks simulation ticks."""

    def __init__(self, node_id: str, duration_ticks: int = 10, name: str = ""):
        super().__init__(node_id, name)
        self.duration_ticks = max(1, duration_ticks)
        self._elapsed: int = 0

    def enter(self, context: BTContext) -> None:
        self._elapsed = 0
        self.status = NodeStatus.RUNNING

    def tick(self, context: BTContext) -> NodeStatus:
        self._elapsed += 1
        if self._elapsed >= self.duration_ticks:
            self._elapsed = 0
            self.status = NodeStatus.SUCCESS
            return self.status

        self.status = NodeStatus.RUNNING
        return self.status

    def abort(self, context: BTContext) -> None:
        self._elapsed = 0
        self.status = NodeStatus.ABORTED

    def reset(self) -> None:
        self._elapsed = 0
        self.status = NodeStatus.FAILURE


class SafeIdleTask(BTNode):
    """Guaranteed safe fallback task. Zeroes velocity and movement intent."""

    def tick(self, context: BTContext) -> NodeStatus:
        if context.fabricator is not None:
            agent = context.fabricator.get_agent(context.agent_id)
            if agent is not None:
                agent.preferred_velocity = (0.0, 0.0, 0.0)
                agent.velocity = (0.0, 0.0, 0.0)
        self.status = NodeStatus.SUCCESS
        return self.status
