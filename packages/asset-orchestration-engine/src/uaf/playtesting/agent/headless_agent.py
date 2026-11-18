"""
UAF-81.96: Autonomous Headless Playtesting Agent Simulator.
Implements multi-archetype discrete-event simulation of player behavior,
combat exchanges, puzzle solving, key-door reachability and telemetry event streaming.
"""

import math
import random
import uuid
from typing import Dict, List, Optional, Set, Tuple
from ..core.contracts import (
    PlaytestArchetype,
    SimulationOutcome,
    TelemetryEventType,
    Vector3D,
    AgentStats,
    ArchetypeProfile,
    TelemetryEvent,
    EnemySpawn,
    DoorConnection,
    RoomSpec,
    PlaytestLevelSpec,
    PlaytestRunResult,
)


class HeadlessPlaytestAgent:
    """
    Autonomous discrete-event bot that navigates levels, resolves combat encounters,
    solves puzzles, manages inventory/resources and streams telemetry events.
    """

    def __init__(
        self,
        archetype: PlaytestArchetype = PlaytestArchetype.EXPLORER,
        seed: int = 42,
        custom_stats: Optional[AgentStats] = None,
    ):
        self.archetype = archetype
        self.rng = random.Random(seed)
        self.seed = seed
        self.stats = custom_stats or self._build_default_stats(archetype)
        self.profile = self._build_archetype_profile(archetype)

    def _build_default_stats(self, archetype: PlaytestArchetype) -> AgentStats:
        if archetype == PlaytestArchetype.SPEEDRUNNER:
            return AgentStats(
                max_health=100.0,
                current_health=100.0,
                max_shield=50.0,
                current_shield=50.0,
                ammo=120,
                max_ammo=240,
                weapon_damage=30.0,
                fire_rate=3.5,
                accuracy=0.90,
                evasion=0.30,
                movement_speed_mps=6.5,
            )
        elif archetype == PlaytestArchetype.COMBATANT:
            return AgentStats(
                max_health=120.0,
                current_health=120.0,
                max_shield=60.0,
                current_shield=60.0,
                ammo=180,
                max_ammo=300,
                weapon_damage=35.0,
                fire_rate=4.0,
                accuracy=0.92,
                evasion=0.15,
                movement_speed_mps=5.0,
            )
        elif archetype == PlaytestArchetype.NOVICE:
            return AgentStats(
                max_health=80.0,
                current_health=80.0,
                max_shield=30.0,
                current_shield=30.0,
                ammo=70,
                max_ammo=150,
                weapon_damage=20.0,
                fire_rate=2.5,
                accuracy=0.55,
                evasion=0.08,
                movement_speed_mps=4.0,
            )
        elif archetype == PlaytestArchetype.COMPLETIONIST:
            return AgentStats(
                max_health=100.0,
                current_health=100.0,
                max_shield=50.0,
                current_shield=50.0,
                ammo=140,
                max_ammo=250,
                weapon_damage=25.0,
                fire_rate=3.0,
                accuracy=0.85,
                evasion=0.20,
                movement_speed_mps=5.0,
            )
        else:  # EXPLORER
            return AgentStats(
                max_health=100.0,
                current_health=100.0,
                max_shield=50.0,
                current_shield=50.0,
                ammo=120,
                max_ammo=240,
                weapon_damage=25.0,
                fire_rate=3.0,
                accuracy=0.80,
                evasion=0.22,
                movement_speed_mps=5.0,
            )

    def _build_archetype_profile(self, archetype: PlaytestArchetype) -> ArchetypeProfile:
        if archetype == PlaytestArchetype.SPEEDRUNNER:
            return ArchetypeProfile(
                archetype=archetype,
                accuracy_mult=1.1,
                damage_taken_mult=0.9,
                exploration_desire=0.05,
                caution_factor=0.3,
                speedrun_factor=1.0,
            )
        elif archetype == PlaytestArchetype.COMBATANT:
            return ArchetypeProfile(
                archetype=archetype,
                accuracy_mult=1.15,
                damage_taken_mult=1.0,
                exploration_desire=0.4,
                caution_factor=0.2,
                speedrun_factor=0.2,
            )
        elif archetype == PlaytestArchetype.NOVICE:
            return ArchetypeProfile(
                archetype=archetype,
                accuracy_mult=0.65,
                damage_taken_mult=1.35,
                exploration_desire=0.6,
                caution_factor=0.1,
                speedrun_factor=0.0,
            )
        elif archetype == PlaytestArchetype.COMPLETIONIST:
            return ArchetypeProfile(
                archetype=archetype,
                accuracy_mult=1.0,
                damage_taken_mult=1.0,
                exploration_desire=1.0,
                caution_factor=0.7,
                speedrun_factor=0.0,
            )
        else:  # EXPLORER
            return ArchetypeProfile(
                archetype=archetype,
                accuracy_mult=1.0,
                damage_taken_mult=1.0,
                exploration_desire=0.9,
                caution_factor=0.5,
                speedrun_factor=0.1,
            )

    def simulate_run(
        self,
        level: PlaytestLevelSpec,
        max_ticks: int = 1000,
        tick_delta_s: float = 0.5,
    ) -> PlaytestRunResult:
        """
        Executes a complete simulated session through the level.
        Returns detailed telemetry events and performance metrics.
        """
        session_id = f"sim_{self.archetype.value.lower()}_{uuid.uuid4().hex[:8]}"
        stats = self.stats.model_copy(deep=True)
        telemetry: List[TelemetryEvent] = []

        # Identify Start and Goal rooms
        start_room_id: Optional[str] = None
        goal_room_id: Optional[str] = None
        for r_id, r in level.rooms.items():
            if r.is_start:
                start_room_id = r_id
            if r.is_goal:
                goal_room_id = r_id

        if not start_room_id and level.rooms:
            start_room_id = next(iter(level.rooms.keys()))

        if not start_room_id:
            return PlaytestRunResult(
                session_id=session_id,
                archetype=self.archetype,
                outcome=SimulationOutcome.SOFTLOCK,
                total_time_s=0.0,
                rooms_visited=[],
                keys_collected=[],
                enemies_defeated=0,
                damage_dealt=0.0,
                damage_taken=0.0,
                ammo_spent=0,
                shots_fired=0,
                accuracy_achieved=0.0,
                telemetry_events=[],
            )

        current_room_id = start_room_id
        current_time_s = 0.0

        def emit(event_type: TelemetryEventType, pos: Vector3D, data: Optional[Dict] = None):
            nonlocal current_time_s
            telemetry.append(
                TelemetryEvent(
                    event_id=f"evt_{len(telemetry)}_{uuid.uuid4().hex[:6]}",
                    timestamp_s=round(current_time_s, 2),
                    event_type=event_type,
                    room_id=current_room_id,
                    position=pos,
                    data=data or {},
                )
            )

        # Emit initial spawn event
        start_pos = level.rooms[start_room_id].center_position
        emit(TelemetryEventType.SPAWN, start_pos)
        emit(TelemetryEventType.ROOM_ENTER, start_pos, {"room_id": start_room_id})

        rooms_visited: List[str] = [start_room_id]
        visited_set: Set[str] = {start_room_id}
        keys_collected: Set[str] = set()
        unlocked_doors: Set[Tuple[str, str]] = set()
        defeated_enemies_by_room: Dict[str, Set[str]] = {r_id: set() for r_id in level.rooms}
        looted_health_by_room: Dict[str, int] = {r_id: 0 for r_id in level.rooms}
        looted_ammo_by_room: Dict[str, int] = {r_id: 0 for r_id in level.rooms}
        solved_puzzles: Set[str] = set()

        total_enemies_defeated = 0
        total_damage_dealt = 0.0
        total_damage_taken = 0.0
        total_ammo_spent = 0
        total_shots_fired = 0
        total_hits = 0

        outcome = SimulationOutcome.TIMEOUT
        ticks = 0

        while ticks < max_ticks:
            ticks += 1
            current_time_s += tick_delta_s
            room = level.rooms[current_room_id]
            room_pos = room.center_position

            # 1. Combat resolution for active room
            alive_enemies = [
                e for e in room.enemies if e.enemy_id not in defeated_enemies_by_room[current_room_id]
            ]

            if alive_enemies:
                # Combat exchange
                for enemy in list(alive_enemies):
                    # Player attacks enemy
                    if stats.ammo > 0:
                        stats.ammo -= 1
                        total_ammo_spent += 1
                        total_shots_fired += 1
                        emit(TelemetryEventType.FIRE_WEAPON, room_pos, {"ammo_left": stats.ammo})

                        hit_roll = self.rng.random()
                        effective_accuracy = min(1.0, stats.accuracy * self.profile.accuracy_mult)
                        if hit_roll <= effective_accuracy:
                            total_hits += 1
                            dmg = stats.weapon_damage
                            total_damage_dealt += dmg
                            enemy.health -= dmg
                            emit(
                                TelemetryEventType.HIT_ENEMY,
                                room_pos,
                                {"enemy_id": enemy.enemy_id, "damage": dmg},
                            )

                            if enemy.health <= 0.0:
                                defeated_enemies_by_room[current_room_id].add(enemy.enemy_id)
                                total_enemies_defeated += 1
                                emit(
                                    TelemetryEventType.ENEMY_DEFEATED,
                                    room_pos,
                                    {"enemy_id": enemy.enemy_id},
                                )
                                continue
                    else:
                        # Out of ammo in combat!
                        if enemy.is_mandatory:
                            # Softlock due to resource exhaustion
                            emit(
                                TelemetryEventType.STUCK_TIMEOUT,
                                room_pos,
                                {"reason": "NO_AMMO_MANDATORY_COMBAT"},
                            )
                            outcome = SimulationOutcome.SOFTLOCK
                            break

                    # Enemy attacks player (if still alive)
                    evasion_roll = self.rng.random()
                    if evasion_roll > stats.evasion:
                        incoming_dmg = enemy.damage * self.profile.damage_taken_mult
                        total_damage_taken += incoming_dmg

                        # Shield absorption first
                        if stats.current_shield > 0:
                            if stats.current_shield >= incoming_dmg:
                                stats.current_shield -= incoming_dmg
                                incoming_dmg = 0.0
                            else:
                                incoming_dmg -= stats.current_shield
                                stats.current_shield = 0.0

                        stats.current_health -= incoming_dmg
                        emit(
                            TelemetryEventType.TAKE_DAMAGE,
                            room_pos,
                            {
                                "enemy_id": enemy.enemy_id,
                                "health_left": stats.current_health,
                                "shield_left": stats.current_shield,
                            },
                        )

                        if stats.current_health <= 0.0:
                            emit(TelemetryEventType.DEATH, room_pos, {"killer": enemy.enemy_id})
                            outcome = SimulationOutcome.DEATH
                            break

                if outcome in (SimulationOutcome.DEATH, SimulationOutcome.SOFTLOCK):
                    break

            # 2. Key pickups
            for key_id in room.contained_keys:
                if key_id not in keys_collected:
                    keys_collected.add(key_id)
                    emit(TelemetryEventType.PICKUP_KEY, room_pos, {"key_id": key_id})

            # 3. Health & Ammo pickups
            if room.health_pickups > looted_health_by_room[current_room_id]:
                needed_health = stats.max_health - stats.current_health
                if needed_health > 15.0 or self.profile.caution_factor > 0.4:
                    looted_health_by_room[current_room_id] += 1
                    healed = min(50.0, needed_health)
                    stats.current_health = min(stats.max_health, stats.current_health + 50.0)
                    emit(TelemetryEventType.PICKUP_HEALTH, room_pos, {"healed": healed})

            if room.ammo_pickups > looted_ammo_by_room[current_room_id]:
                if stats.ammo < (stats.max_ammo * 0.75):
                    looted_ammo_by_room[current_room_id] += 1
                    gained = min(60, stats.max_ammo - stats.ammo)
                    stats.ammo += gained
                    emit(TelemetryEventType.PICKUP_AMMO, room_pos, {"ammo_gained": gained})

            # 4. Terminal / Puzzle solving
            if room.has_terminal_puzzle and room.room_id not in solved_puzzles:
                solved_puzzles.add(room.room_id)
                current_time_s += 2.0  # Puzzle time
                emit(
                    TelemetryEventType.SOLVE_PUZZLE,
                    room_pos,
                    {"puzzle_id": room.puzzle_id or room.room_id},
                )

            # 5. Check victory
            if room.is_goal or (goal_room_id and current_room_id == goal_room_id):
                # If completionist, check if other accessible secrets remain
                if self.archetype == PlaytestArchetype.COMPLETIONIST:
                    unvisited_available = [
                        r_id for r_id in level.rooms if r_id not in visited_set
                    ]
                    # If still unvisited rooms exist and ticks permit, allow searching
                    if unvisited_available and ticks < (max_ticks * 0.7):
                        pass
                    else:
                        emit(TelemetryEventType.GOAL_REACHED, room_pos)
                        outcome = SimulationOutcome.VICTORY
                        break
                else:
                    emit(TelemetryEventType.GOAL_REACHED, room_pos)
                    outcome = SimulationOutcome.VICTORY
                    break

            # 6. Navigation and path decision
            # Identify accessible exits from current_room_id
            accessible_neighbors: List[str] = []
            for conn in level.connections:
                target: Optional[str] = None
                edge_tuple: Optional[Tuple[str, str]] = None
                if conn.source_room_id == current_room_id:
                    target = conn.target_room_id
                    edge_tuple = (conn.source_room_id, conn.target_room_id)
                elif conn.is_two_way and conn.target_room_id == current_room_id:
                    target = conn.source_room_id
                    edge_tuple = (conn.target_room_id, conn.source_room_id)

                if target and target in level.rooms:
                    # Door lock check
                    if conn.required_key_id:
                        if conn.required_key_id in keys_collected:
                            if edge_tuple and edge_tuple not in unlocked_doors:
                                unlocked_doors.add(edge_tuple)
                                emit(
                                    TelemetryEventType.UNLOCK_DOOR,
                                    room_pos,
                                    {"door": f"{edge_tuple[0]}->{edge_tuple[1]}", "key": conn.required_key_id},
                                )
                            accessible_neighbors.append(target)
                    else:
                        accessible_neighbors.append(target)

            if not accessible_neighbors:
                # Dead end with no exit!
                emit(TelemetryEventType.STUCK_TIMEOUT, room_pos, {"reason": "NO_ACCESSIBLE_NEIGHBORS"})
                outcome = SimulationOutcome.SOFTLOCK
                break

            # Choose next room according to archetype policy
            next_room_id = self._select_next_room(
                current_room_id=current_room_id,
                accessible_neighbors=accessible_neighbors,
                level=level,
                visited_set=visited_set,
                goal_room_id=goal_room_id,
                defeated_enemies_by_room=defeated_enemies_by_room,
            )

            # Move to next room
            emit(TelemetryEventType.ROOM_EXIT, room_pos, {"room_id": current_room_id})
            target_pos = level.rooms[next_room_id].center_position
            dist = room_pos.distance_to(target_pos)
            travel_time = max(0.2, dist / stats.movement_speed_mps)
            current_time_s += travel_time

            current_room_id = next_room_id
            rooms_visited.append(current_room_id)
            visited_set.add(current_room_id)
            emit(TelemetryEventType.ROOM_ENTER, target_pos, {"room_id": current_room_id})

        acc_val = (total_hits / total_shots_fired) if total_shots_fired > 0 else 1.0

        return PlaytestRunResult(
            session_id=session_id,
            archetype=self.archetype,
            outcome=outcome,
            total_time_s=round(current_time_s, 2),
            rooms_visited=rooms_visited,
            keys_collected=list(keys_collected),
            enemies_defeated=total_enemies_defeated,
            damage_dealt=round(total_damage_dealt, 2),
            damage_taken=round(total_damage_taken, 2),
            ammo_spent=total_ammo_spent,
            shots_fired=total_shots_fired,
            accuracy_achieved=round(acc_val, 4),
            telemetry_events=telemetry,
        )

    def _select_next_room(
        self,
        current_room_id: str,
        accessible_neighbors: List[str],
        level: PlaytestLevelSpec,
        visited_set: Set[str],
        goal_room_id: Optional[str],
        defeated_enemies_by_room: Dict[str, Set[str]],
    ) -> str:
        """
        Archetype-driven utility choice among accessible adjacent rooms.
        """
        unvisited = [n for n in accessible_neighbors if n not in visited_set]

        # SPEEDRUNNER: choose neighbor with shortest Euclidean/Manhattan distance to goal
        if self.archetype == PlaytestArchetype.SPEEDRUNNER and goal_room_id and goal_room_id in level.rooms:
            goal_pos = level.rooms[goal_room_id].center_position
            # Sort neighbors by distance to goal
            sorted_by_dist = sorted(
                accessible_neighbors,
                key=lambda n: level.rooms[n].center_position.distance_to(goal_pos),
            )
            return sorted_by_dist[0]

        # COMBATANT: prioritize unvisited rooms with alive enemies
        if self.archetype == PlaytestArchetype.COMBATANT:
            combat_neighbors = [
                n
                for n in accessible_neighbors
                if any(
                    e.enemy_id not in defeated_enemies_by_room.get(n, set())
                    for e in level.rooms[n].enemies
                )
            ]
            if combat_neighbors:
                return self.rng.choice(combat_neighbors)

        # EXPLORER / COMPLETIONIST: prioritize unvisited rooms
        if unvisited and (
            self.archetype in (PlaytestArchetype.EXPLORER, PlaytestArchetype.COMPLETIONIST)
            or self.rng.random() < self.profile.exploration_desire
        ):
            return self.rng.choice(unvisited)

        # Default / Fallback: random neighbor (allows backtracking)
        return self.rng.choice(accessible_neighbors)
