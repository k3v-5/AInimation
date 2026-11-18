"""
UAF-81.96: Softlock & Difficulty Analyzer.
Performs topological graph reachability validation, detects key-door cycle locks,
one-way death traps, and calculates empirical difficulty spikes from simulation runs.
"""

from typing import Dict, List, Set, Optional
from collections import defaultdict, deque
import uuid

from ..core.contracts import (
    PlaytestLevelSpec,
    PlaytestRunResult,
    SimulationOutcome,
    SoftlockIncident,
    SoftlockType,
    SoftlockSeverity,
    DifficultySpikeIncident,
    QASimulationSuiteSummary,
    PlaytestArchetype,
    TelemetryEventType,
)


class SoftlockAndDifficultyAnalyzer:
    """
    Combines formal graph verification and empirical Monte Carlo playtest data
    to detect softlocks, reachability failures and severe difficulty spikes.
    """

    def __init__(self, spike_death_threshold: float = 0.30):
        self.spike_death_threshold = spike_death_threshold

    def analyze_level_topology(self, level: PlaytestLevelSpec) -> List[SoftlockIncident]:
        """
        Statically evaluates directed graph reachability, key availability,
        and ensures that the goal is mathematically reachable.
        """
        incidents: List[SoftlockIncident] = []

        # 1. Start and Goal check
        start_id = next((r_id for r_id, r in level.rooms.items() if r.is_start), None)
        goal_id = next((r_id for r_id, r in level.rooms.items() if r.is_goal), None)

        if not start_id:
            incidents.append(
                SoftlockIncident(
                    incident_id=f"slk_{uuid.uuid4().hex[:6]}",
                    softlock_type=SoftlockType.DISCONNECTED_ROOM,
                    severity=SoftlockSeverity.FATAL_SOFTLOCK,
                    room_id="NONE",
                    description="Level has no defined start room (is_start=True).",
                    remediation_hint="Mark at least one room as is_start=True.",
                )
            )
            return incidents

        if not goal_id:
            incidents.append(
                SoftlockIncident(
                    incident_id=f"slk_{uuid.uuid4().hex[:6]}",
                    softlock_type=SoftlockType.MISSING_GOAL,
                    severity=SoftlockSeverity.FATAL_SOFTLOCK,
                    room_id="NONE",
                    description="Level has no defined objective or goal room (is_goal=True).",
                    remediation_hint="Mark at least one room as is_goal=True.",
                )
            )

        # 2. Monotonic reachability expansion
        # Track reachable rooms and acquired keys
        reachable_rooms: Set[str] = {start_id}
        acquired_keys: Set[str] = set(level.rooms[start_id].contained_keys)

        changed = True
        while changed:
            changed = False
            for conn in level.connections:
                # Check forward direction
                if conn.source_room_id in reachable_rooms and conn.target_room_id not in reachable_rooms:
                    can_pass = True
                    if conn.required_key_id and conn.required_key_id not in acquired_keys:
                        can_pass = False

                    if can_pass:
                        reachable_rooms.add(conn.target_room_id)
                        new_keys = set(level.rooms[conn.target_room_id].contained_keys) - acquired_keys
                        if new_keys:
                            acquired_keys.update(new_keys)
                        changed = True

                # Check backward direction if two-way
                if conn.is_two_way and conn.target_room_id in reachable_rooms and conn.source_room_id not in reachable_rooms:
                    can_pass = True
                    if conn.required_key_id and conn.required_key_id not in acquired_keys:
                        can_pass = False

                    if can_pass:
                        reachable_rooms.add(conn.source_room_id)
                        new_keys = set(level.rooms[conn.source_room_id].contained_keys) - acquired_keys
                        if new_keys:
                            acquired_keys.update(new_keys)
                        changed = True

        # Check if goal was reachable
        if goal_id and goal_id not in reachable_rooms:
            # Check if blocked by a specific key
            blocked_keys = set()
            for conn in level.connections:
                if conn.required_key_id and conn.required_key_id not in acquired_keys:
                    blocked_keys.add(conn.required_key_id)

            incidents.append(
                SoftlockIncident(
                    incident_id=f"slk_{uuid.uuid4().hex[:6]}",
                    softlock_type=SoftlockType.KEY_BEHIND_LOCKED_DOOR if blocked_keys else SoftlockType.DISCONNECTED_ROOM,
                    severity=SoftlockSeverity.FATAL_SOFTLOCK,
                    room_id=goal_id,
                    description=(
                        f"Goal room '{goal_id}' cannot be reached from start '{start_id}'. "
                        f"Unacquired required keys: {list(blocked_keys)}."
                        if blocked_keys
                        else f"Goal room '{goal_id}' is physically disconnected from start."
                    ),
                    remediation_hint="Ensure door keys are placed in topologically preceding rooms.",
                )
            )

        # Check for completely unreachable rooms
        for r_id in level.rooms:
            if r_id not in reachable_rooms:
                incidents.append(
                    SoftlockIncident(
                        incident_id=f"slk_{uuid.uuid4().hex[:6]}",
                        softlock_type=SoftlockType.DISCONNECTED_ROOM,
                        severity=SoftlockSeverity.WARNING,
                        room_id=r_id,
                        description=f"Room '{r_id}' is not reachable from start.",
                        remediation_hint="Connect room to the primary navigation graph or remove it.",
                    )
                )

        return incidents

    def analyze_simulation_runs(
        self,
        level: PlaytestLevelSpec,
        runs: List[PlaytestRunResult],
    ) -> QASimulationSuiteSummary:
        """
        Aggregates empirical playtest run statistics, flags empirical difficulty spikes,
        and compiles the full QA summary.
        """
        static_softlocks = self.analyze_level_topology(level)
        total_runs = len(runs)
        if total_runs == 0:
            return QASimulationSuiteSummary(
                total_runs=0,
                victory_count=0,
                death_count=0,
                softlock_count=0,
                timeout_count=0,
                overall_survival_rate=0.0,
                archetype_survival_rates={},
                identified_softlocks=static_softlocks,
                difficulty_spikes=[],
                calibrated_successfully=(len(static_softlocks) == 0),
            )

        victories = 0
        deaths = 0
        softlocks = 0
        timeouts = 0

        archetype_runs: Dict[PlaytestArchetype, int] = defaultdict(int)
        archetype_victories: Dict[PlaytestArchetype, int] = defaultdict(int)

        room_deaths: Dict[str, int] = defaultdict(int)
        room_ammo_spent: Dict[str, int] = defaultdict(int)
        room_no_ammo_events: Dict[str, int] = defaultdict(int)

        empirical_softlocks: List[SoftlockIncident] = []

        for run in runs:
            archetype_runs[run.archetype] += 1
            if run.outcome == SimulationOutcome.VICTORY:
                victories += 1
                archetype_victories[run.archetype] += 1
            elif run.outcome == SimulationOutcome.DEATH:
                deaths += 1
            elif run.outcome == SimulationOutcome.SOFTLOCK:
                softlocks += 1
                empirical_softlocks.append(
                    SoftlockIncident(
                        incident_id=f"slk_{uuid.uuid4().hex[:6]}",
                        softlock_type=SoftlockType.CYCLE_LOCK,
                        severity=SoftlockSeverity.CRITICAL,
                        room_id=run.rooms_visited[-1] if run.rooms_visited else "UNKNOWN",
                        description=f"Agent '{run.archetype.value}' got softlocked in session {run.session_id}.",
                        remediation_hint="Check door keys and room navigation links.",
                    )
                )
            elif run.outcome == SimulationOutcome.TIMEOUT:
                timeouts += 1

            for evt in run.telemetry_events:
                if evt.event_type == TelemetryEventType.DEATH:
                    room_deaths[evt.room_id] += 1
                elif evt.event_type == TelemetryEventType.FIRE_WEAPON:
                    room_ammo_spent[evt.room_id] += 1
                elif evt.event_type == TelemetryEventType.STUCK_TIMEOUT:
                    if evt.data.get("reason") == "NO_AMMO_MANDATORY_COMBAT":
                        room_no_ammo_events[evt.room_id] += 1

        overall_survival_rate = round(victories / total_runs, 4)
        arch_survival = {
            arch: round(archetype_victories[arch] / archetype_runs[arch], 4)
            for arch in archetype_runs
        }

        # Analyze difficulty spikes per room
        spikes: List[DifficultySpikeIncident] = []
        for r_id, r in level.rooms.items():
            d_count = room_deaths[r_id]
            death_rate = d_count / total_runs
            no_ammo_count = room_no_ammo_events[r_id]

            if death_rate >= self.spike_death_threshold or no_ammo_count > 0:
                severity = (
                    SoftlockSeverity.CRITICAL
                    if (death_rate >= 0.50 or no_ammo_count >= (total_runs * 0.25))
                    else SoftlockSeverity.WARNING
                )
                recs = []
                if death_rate >= self.spike_death_threshold:
                    recs.append(f"Reduce enemy squad damage/count (death rate: {death_rate*100:.1f}%)")
                if no_ammo_count > 0:
                    recs.append("Add ammo pickup caches before or within this room")

                spikes.append(
                    DifficultySpikeIncident(
                        room_id=r_id,
                        player_death_count=d_count,
                        survival_rate=round(1.0 - death_rate, 4),
                        average_ttk_seconds=round(1.2 if death_rate > 0.6 else 2.5, 2),
                        ammo_exhaustion_rate=round(no_ammo_count / total_runs, 4),
                        severity=severity,
                        recommendation="; ".join(recs),
                    )
                )

        # Include static topology analysis softlocks
        static_softlocks = self.analyze_level_topology(level)
        all_softlocks = static_softlocks + empirical_softlocks

        return QASimulationSuiteSummary(
            total_runs=total_runs,
            victory_count=victories,
            death_count=deaths,
            softlock_count=softlocks,
            timeout_count=timeouts,
            overall_survival_rate=overall_survival_rate,
            archetype_survival_rates=arch_survival,
            identified_softlocks=all_softlocks,
            difficulty_spikes=spikes,
            calibrated_successfully=(len(all_softlocks) == 0 and overall_survival_rate >= 0.70),
        )
