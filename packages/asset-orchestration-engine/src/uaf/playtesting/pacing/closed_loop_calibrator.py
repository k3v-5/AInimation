"""
UAF-81.96: Closed-Loop Dynamic Pacing Calibrator.
Analyzes QA simulation summaries and automatically generates mathematical corrections
for difficulty spikes, enemy squad dampening, resource caches, and softlock resolution.
"""

from typing import Dict, List, Tuple, Any
import copy

from ..core.contracts import (
    PlaytestLevelSpec,
    QASimulationSuiteSummary,
    SoftlockType,
    SoftlockSeverity,
    DoorConnection,
    EnemySpawn,
)


class ClosedLoopPacingCalibrator:
    """
    Applies closed-loop corrective mutations to level geometry, resource placement,
    and enemy squad balances based on autonomous playtest telemetry.
    """

    def __init__(
        self,
        target_survival_rate: float = 0.75,
        max_acceptable_death_rate_per_room: float = 0.30,
    ):
        self.target_survival_rate = target_survival_rate
        self.max_acceptable_death_rate_per_room = max_acceptable_death_rate_per_room

    def calibrate_level(
        self,
        level: PlaytestLevelSpec,
        summary: QASimulationSuiteSummary,
    ) -> Tuple[PlaytestLevelSpec, Dict[str, Any]]:
        """
        Produces a calibrated clone of the level specification, eliminating softlocks
        and smoothing out unfair difficulty spikes.
        """
        calibrated = level.model_copy(deep=True)
        corrections_applied: List[Dict[str, Any]] = []

        # 1. Softlock resolution
        for slk in summary.identified_softlocks:
            if slk.softlock_type == SoftlockType.KEY_BEHIND_LOCKED_DOOR or "Unacquired required keys" in slk.description:
                # Find the locked connections
                for conn in calibrated.connections:
                    if conn.required_key_id:
                        key = conn.required_key_id
                        # Ensure the key is present in an accessible earlier room (e.g. source_room or start_room)
                        source_r = calibrated.rooms.get(conn.source_room_id)
                        if source_r and key not in source_r.contained_keys:
                            source_r.contained_keys.append(key)
                            corrections_applied.append(
                                {
                                    "type": "SOFTLOCK_KEY_RELOCATION",
                                    "key_id": key,
                                    "target_room": conn.source_room_id,
                                    "reason": f"Resolved softlock: placed required key in predecessor room {conn.source_room_id}",
                                }
                            )

            elif slk.softlock_type == SoftlockType.MISSING_GOAL:
                # Designate the last room as goal
                last_room_id = list(calibrated.rooms.keys())[-1]
                calibrated.rooms[last_room_id].is_goal = True
                corrections_applied.append(
                    {
                        "type": "SOFTLOCK_GOAL_DESIGNATION",
                        "room_id": last_room_id,
                        "reason": f"Designated room '{last_room_id}' as level goal",
                    }
                )

            elif slk.softlock_type == SoftlockType.DISCONNECTED_ROOM and slk.room_id != "NONE":
                # Connect disconnected room to the first room
                first_room_id = list(calibrated.rooms.keys())[0]
                if slk.room_id in calibrated.rooms and slk.room_id != first_room_id:
                    new_conn = DoorConnection(
                        source_room_id=first_room_id,
                        target_room_id=slk.room_id,
                        is_two_way=True,
                        required_key_id=None,
                        is_locked_initially=False,
                    )
                    calibrated.connections.append(new_conn)
                    corrections_applied.append(
                        {
                            "type": "SOFTLOCK_CONNECTION_RESTORED",
                            "source": first_room_id,
                            "target": slk.room_id,
                            "reason": f"Connected isolated room '{slk.room_id}' to '{first_room_id}'",
                        }
                    )

        # 2. Difficulty Spike smoothing
        for spike in summary.difficulty_spikes:
            r_id = spike.room_id
            if r_id not in calibrated.rooms:
                continue

            room = calibrated.rooms[r_id]

            # Calculate dampening factor delta
            death_rate = 1.0 - spike.survival_rate
            if death_rate >= self.max_acceptable_death_rate_per_room:
                delta = max(0.40, 1.0 - (death_rate - 0.20))
                # Dampen enemy damage and health
                for enemy in room.enemies:
                    enemy.damage = round(enemy.damage * delta, 2)
                    enemy.health = round(enemy.health * delta, 2)

                corrections_applied.append(
                    {
                        "type": "DIFFICULTY_ENEMY_DAMPENING",
                        "room_id": r_id,
                        "dampening_factor": round(delta, 3),
                        "enemies_adjusted": len(room.enemies),
                    }
                )

            # Check ammo exhaustion
            if spike.ammo_exhaustion_rate > 0.05 or death_rate >= 0.25:
                room.ammo_pickups += 2
                room.health_pickups += 1
                corrections_applied.append(
                    {
                        "type": "RESOURCE_CACHE_INJECTION",
                        "room_id": r_id,
                        "added_ammo_pickups": 2,
                        "added_health_pickups": 1,
                    }
                )

        return calibrated, {
            "total_corrections": len(corrections_applied),
            "corrections": corrections_applied,
            "calibrated_successfully": True,
        }
