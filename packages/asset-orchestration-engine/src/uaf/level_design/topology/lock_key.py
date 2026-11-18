"""
UAF-81.90: Lock-and-Key Generation and Softlock Verification.
Generates key and locked door placements along critical paths with mathematical zero-softlock guarantees.
"""

from __future__ import annotations

import random
from collections import deque
from typing import Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

from uaf.level_design.topology.graph import LevelTopologyGraph


class KeyItem(BaseModel):
    key_id: str
    name: str
    coord: Tuple[int, ...]
    color: str = "RED"


class LockedDoor(BaseModel):
    door_id: str
    name: str
    coord: Tuple[int, ...]
    required_key_id: str
    color: str = "RED"


class LockKeyProgressionResult(BaseModel):
    is_solvable: bool
    collected_keys: List[str] = Field(default_factory=list)
    unlocked_doors: List[str] = Field(default_factory=list)
    critical_path_length: int = 0
    softlock_details: Optional[str] = None


class LockAndKeyGenerator:
    """
    Places keys and locked doors on a level topology graph and mathematically
    verifies zero-softlock solvability.
    """

    def __init__(self, graph: LevelTopologyGraph, seed: Optional[int] = 42):
        self.graph = graph
        self.rng = random.Random(seed)

    def generate_lock_and_key_loop(
        self,
        start_coord: Tuple[int, ...],
        goal_coord: Tuple[int, ...],
        key_id: str = "KEY_ALPHA",
        door_id: str = "DOOR_ALPHA",
        color: str = "RED",
    ) -> Optional[Tuple[KeyItem, LockedDoor]]:
        """
        Generates a verified key-and-door pair between start and goal.
        Guarantees that:
        1. The door is on the critical path to the goal.
        2. The key is placed in a branch/side-room reachable from start WITHOUT passing through the door.
        """
        # Find baseline critical path from start to goal
        critical_path = self.graph.shortest_path_astar(start_coord, goal_coord)
        if not critical_path or len(critical_path) < 4:
            # Path too short to insert non-trivial lock and key
            return None

        # Choose a door location on the critical path (middle portion)
        door_candidates = critical_path[2:-1]  # Exclude start and goal immediate neighbors
        if not door_candidates:
            return None

        door_coord = self.rng.choice(door_candidates)
        door_index = critical_path.index(door_coord)

        # Compute all nodes reachable from start without crossing door_coord
        reachable_before_door = self._get_reachable_nodes(start_coord, blocked_nodes={door_coord})

        # Exclude nodes that are on the critical path after the door
        forbidden_for_key = set(critical_path[door_index:])
        forbidden_for_key.add(start_coord)
        forbidden_for_key.add(door_coord)

        valid_key_coords = [c for c in reachable_before_door if c not in forbidden_for_key]

        if not valid_key_coords:
            # Fallback: any node in reachable_before_door that isn't start or door
            valid_key_coords = [c for c in reachable_before_door if c != start_coord and c != door_coord]

        if not valid_key_coords:
            return None

        # Prefer side rooms / dead ends or nodes furthest from start
        key_coord = self.rng.choice(valid_key_coords)

        key_item = KeyItem(
            key_id=key_id,
            name=f"{color.capitalize()} Access Card",
            coord=key_coord,
            color=color,
        )

        locked_door = LockedDoor(
            door_id=door_id,
            name=f"{color.capitalize()} Security Gate",
            coord=door_coord,
            required_key_id=key_id,
            color=color,
        )

        # Mathematical verification
        verification = self.verify_progression(
            start_coord=start_coord,
            goal_coord=goal_coord,
            doors=[locked_door],
            keys=[key_item],
        )

        if not verification.is_solvable:
            return None

        return key_item, locked_door

    def _get_reachable_nodes(
        self,
        start: Tuple[int, ...],
        blocked_nodes: Set[Tuple[int, ...]],
    ) -> Set[Tuple[int, ...]]:
        """Finds all nodes reachable from start without passing through blocked_nodes."""
        if start not in self.graph.nodes or start in blocked_nodes:
            return set()

        reachable: Set[Tuple[int, ...]] = {start}
        queue = deque([start])

        while queue:
            curr = queue.popleft()
            for neighbor in self.graph.nodes[curr].neighbors:
                if neighbor not in reachable and neighbor not in blocked_nodes:
                    reachable.add(neighbor)
                    queue.append(neighbor)

        return reachable

    def verify_progression(
        self,
        start_coord: Tuple[int, ...],
        goal_coord: Tuple[int, ...],
        doors: List[LockedDoor],
        keys: List[KeyItem],
    ) -> LockKeyProgressionResult:
        """
        Simulates player progression to guarantee zero softlocks:
        1. Starts at start_coord with empty key inventory.
        2. Expands reachable frontier through unlocked doors.
        3. Collects keys found in reachable nodes.
        4. Unlocks matching doors and continues.
        5. Verifies whether goal_coord is reached.
        """
        key_locations = {k.coord: k for k in keys}
        door_by_coord = {d.coord: d for d in doors}
        door_by_key = {d.required_key_id: d for d in doors}

        inventory: Set[str] = set()
        unlocked_door_coords: Set[Tuple[int, ...]] = set()

        changed = True
        while changed:
            changed = False

            # Blocked coordinates are currently locked doors
            blocked = {d.coord for d in doors if d.coord not in unlocked_door_coords}
            reachable = self._get_reachable_nodes(start_coord, blocked_nodes=blocked)

            # Check if goal reached
            if goal_coord in reachable:
                # Goal reached! Compute critical path length with unlocked doors
                final_path = self.graph.shortest_path_astar(start_coord, goal_coord, blocked_nodes=blocked)
                path_len = len(final_path) if final_path else 0

                return LockKeyProgressionResult(
                    is_solvable=True,
                    collected_keys=list(inventory),
                    unlocked_doors=[d.door_id for d in doors if d.coord in unlocked_door_coords],
                    critical_path_length=path_len,
                )

            # Check for keys in reachable territory that haven't been picked up yet
            for coord in reachable:
                if coord in key_locations:
                    key = key_locations[coord]
                    if key.key_id not in inventory:
                        inventory.add(key.key_id)
                        changed = True

                        # Unlock corresponding door if exists
                        if key.key_id in door_by_key:
                            matching_door = door_by_key[key.key_id]
                            unlocked_door_coords.add(matching_door.coord)

        # If loop terminates without reaching goal, softlock detected!
        return LockKeyProgressionResult(
            is_solvable=False,
            collected_keys=list(inventory),
            unlocked_doors=[d.door_id for d in doors if d.coord in unlocked_door_coords],
            critical_path_length=0,
            softlock_details=f"Player trapped! Goal {goal_coord} unreachable. Collected keys: {list(inventory)}",
        )
