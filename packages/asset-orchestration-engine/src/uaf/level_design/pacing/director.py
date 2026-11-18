"""
UAF-81.90: Dynamic AI Pacing Director.
Models player stress curves and dynamically controls encounter rhythm across 5 phases:
CALM -> BUILDUP -> PEAK -> SUSTAINED_PEAK -> COOLDOWN.
Provides out-of-sight spatial spawn queries and dynamic difficulty adjustment (DDA).
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from uaf.level_design.core.contracts import (
    PacingPhase,
    PlayerStressMetric,
    PacingDecision,
)


class SpatialSpawnPoint(BaseModel):
    """Candidate spawn point in world coordinates."""
    spawn_id: str
    world_pos: Tuple[float, float, float]
    room_id: Optional[str] = None
    is_active: bool = True


class DynamicPacingDirector:
    """
    Real-time AI Pacing Director.
    Regulates combat intensity, enemy spawn cadence, and audio-visual tension
    to prevent player exhaustion while maintaining engagement.
    """

    def __init__(
        self,
        calm_duration_sec: float = 12.0,
        buildup_duration_sec: float = 20.0,
        peak_duration_sec: float = 15.0,
        sustained_duration_sec: float = 8.0,
        cooldown_duration_sec: float = 12.0,
    ):
        self.calm_duration = calm_duration_sec
        self.buildup_duration = buildup_duration_sec
        self.peak_duration = peak_duration_sec
        self.sustained_duration = sustained_duration_sec
        self.cooldown_duration = cooldown_duration_sec

        self.current_phase: PacingPhase = PacingPhase.CALM
        self.phase_elapsed_time: float = 0.0
        self.total_elapsed_time: float = 0.0
        self.historical_stress: List[float] = []

    def update(self, delta_time_sec: float, stress_metric: PlayerStressMetric) -> PacingDecision:
        """
        Advances pacing state machine according to elapsed time and composite player stress.
        """
        self.phase_elapsed_time += delta_time_sec
        self.total_elapsed_time += delta_time_sec

        stress_score = stress_metric.compute_stress_score()
        self.historical_stress.append(stress_score)
        if len(self.historical_stress) > 100:
            self.historical_stress.pop(0)

        # State transitions
        if self.current_phase == PacingPhase.CALM:
            # Transition to BUILDUP if calm timer finishes or stress starts creeping up
            if self.phase_elapsed_time >= self.calm_duration or stress_score > 0.35:
                self._transition_to(PacingPhase.BUILDUP)

        elif self.current_phase == PacingPhase.BUILDUP:
            # Transition to PEAK if stress reaches high threshold or buildup completes
            if stress_score >= 0.65 or self.phase_elapsed_time >= self.buildup_duration:
                self._transition_to(PacingPhase.PEAK)

        elif self.current_phase == PacingPhase.PEAK:
            # Transition to SUSTAINED_PEAK or COOLDOWN
            if self.phase_elapsed_time >= self.peak_duration:
                if stress_score < 0.85:
                    self._transition_to(PacingPhase.SUSTAINED_PEAK)
                else:
                    self._transition_to(PacingPhase.COOLDOWN)
            elif stress_score >= 0.90:
                # Emergency pressure relief
                self._transition_to(PacingPhase.COOLDOWN)

        elif self.current_phase == PacingPhase.SUSTAINED_PEAK:
            if self.phase_elapsed_time >= self.sustained_duration or stress_score >= 0.85:
                self._transition_to(PacingPhase.COOLDOWN)

        elif self.current_phase == PacingPhase.COOLDOWN:
            # Force recovery period: don't leave cooldown until min duration has passed
            if self.phase_elapsed_time >= self.cooldown_duration and stress_score <= 0.40:
                self._transition_to(PacingPhase.CALM)

        # Compute outputs based on current phase
        return self._generate_decision(stress_score)

    def _transition_to(self, new_phase: PacingPhase) -> None:
        self.current_phase = new_phase
        self.phase_elapsed_time = 0.0

    def _generate_decision(self, stress_score: float) -> PacingDecision:
        """Generates spawn multipliers, music intensity, and archetype recommendations."""
        if self.current_phase == PacingPhase.CALM:
            spawn_multiplier = 0.25
            recommended_archetype = "SCOUT_ROAMER"
            music_intensity = 0.15

        elif self.current_phase == PacingPhase.BUILDUP:
            progress = min(1.0, self.phase_elapsed_time / max(1.0, self.buildup_duration))
            spawn_multiplier = 1.0 + (0.5 * progress)
            recommended_archetype = "GRUNT_SQUAD"
            music_intensity = 0.4 + (0.3 * progress)

        elif self.current_phase == PacingPhase.PEAK:
            spawn_multiplier = 2.2
            recommended_archetype = "HEAVY_ENFORCER"
            music_intensity = 0.95

        elif self.current_phase == PacingPhase.SUSTAINED_PEAK:
            spawn_multiplier = 1.8
            recommended_archetype = "FLANKER_SWARM"
            music_intensity = 0.90

        else:  # COOLDOWN
            spawn_multiplier = 0.0  # Complete suppression of aggressive spawns
            recommended_archetype = "NONE"
            music_intensity = 0.10

        return PacingDecision(
            current_phase=self.current_phase,
            stress_score=round(stress_score, 4),
            spawn_multiplier=round(spawn_multiplier, 3),
            recommended_archetype=recommended_archetype,
            music_intensity=round(music_intensity, 3),
        )

    def select_out_of_sight_spawn_points(
        self,
        player_pos: Tuple[float, float, float],
        player_forward_vector: Tuple[float, float, float],
        candidate_spawns: List[SpatialSpawnPoint],
        min_distance: float = 800.0,   # 8 meters in Unreal centimeters
        max_distance: float = 3500.0,  # 35 meters in Unreal centimeters
        fov_angle_deg: float = 90.0,
    ) -> List[SpatialSpawnPoint]:
        """
        Filters spawn candidates so enemies never spawn directly inside the player's line of sight
        or unrealistically close/far.
        Uses 2D dot product against player forward vector to check field of view.
        """
        valid_points: List[SpatialSpawnPoint] = []
        cos_half_fov = math.cos(math.radians(fov_angle_deg / 2.0))

        px, py, pz = player_pos
        fx, fy, _ = player_forward_vector
        forward_len = math.hypot(fx, fy)
        if forward_len > 1e-5:
            fx /= forward_len
            fy /= forward_len
        else:
            fx, fy = 1.0, 0.0

        for sp in candidate_spawns:
            if not sp.is_active:
                continue

            sx, sy, sz = sp.world_pos
            dx, dy, dz = sx - px, sy - py, sz - pz
            dist_2d = math.hypot(dx, dy)
            dist_3d = math.sqrt(dx * dx + dy * dy + dz * dz)

            # Check distance bounds
            if dist_3d < min_distance or dist_3d > max_distance:
                continue

            # Check if in front of player
            if dist_2d > 1e-4:
                to_spawn_x = dx / dist_2d
                to_spawn_y = dy / dist_2d
                dot = (to_spawn_x * fx) + (to_spawn_y * fy)

                # If dot > cos_half_fov, it is inside the player's direct field of view
                if dot > cos_half_fov:
                    continue

            valid_points.append(sp)

        return valid_points
