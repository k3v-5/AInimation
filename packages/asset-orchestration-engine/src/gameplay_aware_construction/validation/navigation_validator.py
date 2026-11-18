from typing import List, Tuple, Dict, Set
from ..core.gameplay_types import GameplaySeverity
from ..core.gameplay_schema import ActorProfile, StairDefinition

class GameplayNavigationValidator:
    @staticmethod
    def validate_connectivity(
        start_node: str,
        goal_node: str,
        navigation_graph: Dict[str, List[str]],
        blocked_nodes: Set[str] = None
    ) -> Tuple[bool, List[str]]:
        blocked = blocked_nodes or set()
        if start_node in blocked or goal_node in blocked:
            return False, [f"PATH_UNREACHABLE: Start '{start_node}' or Goal '{goal_node}' is blocked by geometry."]

        # Búsqueda BFS de camino
        queue = [[start_node]]
        visited = set([start_node])

        while queue:
            path = queue.pop(0)
            node = path[-1]
            if node == goal_node:
                return True, [f"PATH_CONNECTED: Reachable path found ({' -> '.join(path)})."]

            for neighbor in navigation_graph.get(node, []):
                if neighbor not in visited and neighbor not in blocked:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])

        return False, [f"PATH_UNREACHABLE: No connected navigable path between '{start_node}' and '{goal_node}'."]

class GameplayTraversalValidator:
    @staticmethod
    def validate_stairs(
        stair: StairDefinition,
        actor: ActorProfile
    ) -> List[Tuple[GameplaySeverity, str]]:
        issues = []
        if stair.slope > actor.max_slope:
            issues.append((
                GameplaySeverity.CRITICAL,
                f"STAIR_TOO_STEEP: Stair slope ({stair.slope:.1f}°) exceeds actor maximum traversable slope ({actor.max_slope:.1f}°)."
            ))

        if stair.step_height > actor.step_height:
            issues.append((
                GameplaySeverity.CRITICAL,
                f"STEP_TOO_HIGH: Step height ({stair.step_height:.2f}m) exceeds actor maximum step height ({actor.step_height:.2f}m)."
            ))

        return issues
