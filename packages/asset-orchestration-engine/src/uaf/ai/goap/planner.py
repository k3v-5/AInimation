"""
UAF-81.92: Goal-Oriented Action Planning (GOAP) State-Space A* Search Engine.
Discovers the optimal minimum-cost sequence of actions bridging the gap between
the agent's current belief state and target goal conditions.
"""

from __future__ import annotations

import heapq
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

from uaf.ai.core.contracts import WorldState, GOAPAction, GOAPGoal


class GOAPPlan(BaseModel):
    """Execution container for a generated sequence of GOAP actions."""
    goal_id: str
    actions: List[GOAPAction] = Field(default_factory=list)
    total_cost: float = 0.0
    current_index: int = 0

    @property
    def is_complete(self) -> bool:
        return self.current_index >= len(self.actions)

    def get_current_action(self) -> Optional[GOAPAction]:
        if self.is_complete:
            return None
        return self.actions[self.current_index]

    def advance(self) -> Optional[GOAPAction]:
        """Advances execution pointer to the next action in the plan."""
        self.current_index += 1
        return self.get_current_action()

    def validate_step(self, current_state: WorldState) -> bool:
        """Verifies that the next scheduled action's preconditions are currently satisfied."""
        curr = self.get_current_action()
        if not curr:
            return True
        return curr.can_execute(current_state)


class GOAPPlanner:
    """
    A* State-space search planner for GOAP agents.
    """

    def __init__(self, actions: Optional[List[GOAPAction]] = None):
        self.actions: List[GOAPAction] = actions or []

    def add_action(self, action: GOAPAction) -> None:
        self.actions.append(action)

    @staticmethod
    def _state_to_key(state: WorldState) -> Tuple[Tuple[str, Any], ...]:
        """Converts WorldState values to an immutable hashable tuple for visited tracking."""
        return tuple(sorted(state.values.items()))

    def plan(
        self,
        current_state: WorldState,
        goal: GOAPGoal,
        max_iterations: int = 1000,
    ) -> Optional[GOAPPlan]:
        """
        Executes A* search in belief state space to find the lowest-cost action sequence.
        Returns GOAPPlan if a valid path exists, or None if the goal is unreachable.
        """
        if goal.is_satisfied(current_state):
            # Already satisfied, no actions required
            return GOAPPlan(goal_id=goal.goal_id, actions=[], total_cost=0.0)

        # Priority queue stores: (f_score, g_score, counter, state, action_history)
        counter = 0
        h_start = current_state.heuristic_distance(goal.target_state)
        frontier: List[Tuple[float, float, int, WorldState, List[GOAPAction]]] = []
        heapq.heappush(frontier, (float(h_start), 0.0, counter, current_state.clone(), []))

        visited_costs: Dict[Tuple[Tuple[str, Any], ...], float] = {
            self._state_to_key(current_state): 0.0
        }

        iterations = 0

        while frontier and iterations < max_iterations:
            iterations += 1
            f, g, _, curr_state, path = heapq.heappop(frontier)

            # Goal test
            if goal.is_satisfied(curr_state):
                return GOAPPlan(
                    goal_id=goal.goal_id,
                    actions=path,
                    total_cost=round(g, 3),
                )

            # Explore outgoing transitions
            for action in self.actions:
                if not action.can_execute(curr_state):
                    continue

                # Apply action effects to generate neighbor state
                next_state = curr_state.apply_effects(action.effects)
                tentative_g = g + action.cost
                state_key = self._state_to_key(next_state)

                if tentative_g < visited_costs.get(state_key, float("inf")):
                    visited_costs[state_key] = tentative_g
                    h = float(next_state.heuristic_distance(goal.target_state))
                    f_score = tentative_g + h
                    counter += 1
                    heapq.heappush(
                        frontier,
                        (f_score, tentative_g, counter, next_state, path + [action]),
                    )

        # No valid plan found within iteration budget
        return None

    def replan(
        self,
        current_state: WorldState,
        goal: GOAPGoal,
    ) -> Optional[GOAPPlan]:
        """Re-evaluates and generates a fresh plan when an in-progress plan becomes invalid."""
        return self.plan(current_state, goal)
