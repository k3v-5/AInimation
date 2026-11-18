from typing import Dict, List, Tuple, Optional, Set
from ..core.gameplay_schema import ActorProfile, DoorGameplayDefinition, StairDefinition, InteractionPoint, SpawnPoint

class GameplayTestAgent:
    """
    Automated Player Proxy: ejecuta pruebas de extremo a extremo simulando al jugador.
    Secuencia: SPAWN -> NAVIGATE -> INTERACT_DOOR -> ENTER -> TRAVERSE_STAIR -> REACH_OBJECTIVE.
    """
    def __init__(self, actor_profile: Optional[ActorProfile] = None):
        self.actor = actor_profile or ActorProfile()

    def run_end_to_end_test(
        self,
        spawn: SpawnPoint,
        door: DoorGameplayDefinition,
        stair: Optional[StairDefinition],
        interaction: Optional[InteractionPoint],
        nav_graph: Dict[str, List[str]],
        goal_node: str,
        blocked_nodes: Set[str] = None
    ) -> Tuple[bool, List[str], Optional[str]]:
        log = []

        # 1. Spawn Check
        if spawn.is_inside_geometry or not spawn.is_valid_ground:
            return False, log, f"FAILED_AT_SPAWN: Spawn point '{spawn.spawn_id}' invalid."
        log.append(f"1. SPAWN: Player spawned successfully at ({spawn.position[0]}, {spawn.position[1]}).")

        # 2. Door Clearance Check
        if door.width < self.actor.clearance:
            return False, log, f"FAILED_AT_DOOR: Door '{door.door_id}' width ({door.width:.2f}m) < required ({self.actor.clearance:.2f}m)."
        log.append(f"2. DOOR_PASS: Player passed through door '{door.door_id}' (width {door.width:.2f}m >= {self.actor.clearance:.2f}m).")

        # 3. Interaction Check
        if interaction:
            if interaction.is_blocked:
                return False, log, f"FAILED_AT_INTERACTION: Interaction point '{interaction.point_id}' is blocked."
            log.append(f"3. INTERACTION: Executed interaction '{interaction.interaction_type.value}' at '{interaction.point_id}'.")

        # 4. Stair Traversal Check
        if stair:
            if stair.slope > self.actor.max_slope or stair.step_height > self.actor.step_height:
                return False, log, f"FAILED_AT_STAIR: Stair slope ({stair.slope:.1f}°) or step ({stair.step_height:.2f}m) too steep."
            log.append(f"4. TRAVERSAL: Climbed stair (slope {stair.slope:.1f}° <= {self.actor.max_slope:.1f}°).")

        # 5. Goal Reachability Check
        start_node = "SPAWN"
        blocked = blocked_nodes or set()
        queue = [[start_node]]
        visited = set([start_node])
        reached = False

        while queue:
            path = queue.pop(0)
            node = path[-1]
            if node == goal_node:
                reached = True
                break
            for neighbor in nav_graph.get(node, []):
                if neighbor not in visited and neighbor not in blocked:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])

        if not reached:
            return False, log, f"FAILED_AT_OBJECTIVE: Could not reach goal node '{goal_node}'."
        log.append(f"5. OBJECTIVE: Successfully reached objective '{goal_node}'.")

        return True, log, None
