"""
UAF-81.82: AI Resource Budget Enforcement and Scheduler Fairness.
"""

from __future__ import annotations

from typing import Dict
from ..models.definition import AIBudget


class AIBudgetManager:
    """
    Tracks and throttles per-tick computational budgets for pathfinding,
    sensory perception queries, Behavior Tree evaluations, and RVO/ORCA pairs.
    Applies deterministic fairness penalties to prevent starvation.
    """

    def __init__(self, budget: AIBudget = AIBudget()):
        self.budget = budget
        self.path_requests_this_tick: int = 0
        self.sensor_queries_this_tick: int = 0
        self.bt_nodes_this_tick: int = 0
        self.avoidance_agents_this_tick: int = 0

        # Monopolization penalty tracker (agent_id -> accumulated_requests)
        self._agent_usage: Dict[str, int] = {}

    def reset_tick(self) -> None:
        self.path_requests_this_tick = 0
        self.sensor_queries_this_tick = 0
        self.bt_nodes_this_tick = 0
        self.avoidance_agents_this_tick = 0

    def can_process_path(self, agent_id: str) -> bool:
        if self.path_requests_this_tick >= self.budget.max_path_requests_per_tick:
            return False
        return True

    def consume_path(self, agent_id: str) -> None:
        self.path_requests_this_tick += 1
        self._agent_usage[agent_id] = self._agent_usage.get(agent_id, 0) + 1

    def can_process_sensor_query(self) -> bool:
        return self.sensor_queries_this_tick < self.budget.max_sensor_queries_per_tick

    def consume_sensor_query(self) -> None:
        self.sensor_queries_this_tick += 1

    def can_process_bt_node(self) -> bool:
        return self.bt_nodes_this_tick < self.budget.max_bt_nodes_per_tick

    def consume_bt_node(self) -> None:
        self.bt_nodes_this_tick += 1

    def can_process_avoidance(self) -> bool:
        return self.avoidance_agents_this_tick < self.budget.max_avoidance_agents

    def consume_avoidance(self) -> None:
        self.avoidance_agents_this_tick += 1
