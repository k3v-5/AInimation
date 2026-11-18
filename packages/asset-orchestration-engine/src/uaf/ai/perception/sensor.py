"""
UAF-81.92: Sensory Perception & Threat Memory Decay.
Models vision cones with FOV frustum angles, sound propagation with attenuation,
and exponential confidence decay for threat Last Known Positions (LKP).
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from uaf.ai.core.contracts import StimulusType, PerceptionStimulus


class TrackedThreat(BaseModel):
    """Internal mental record of a detected threat."""
    threat_id: str
    last_known_pos: Tuple[float, float, float]
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    last_perceived_time: float = 0.0
    is_currently_visible: bool = True


class PerceptionSensor:
    """
    Multi-modal perception sensor evaluating vision cones, acoustic hearing,
    and threat memory decay.
    """

    def __init__(
        self,
        sight_range_cm: float = 2500.0,  # 25 meters in Unreal cm
        fov_angle_deg: float = 110.0,
        hearing_range_cm: float = 3500.0,
        memory_decay_rate: float = 0.12,  # lambda in exponential decay
        lost_threshold: float = 0.15,
    ):
        self.sight_range = sight_range_cm
        self.fov_deg = fov_angle_deg
        self.cos_half_fov = math.cos(math.radians(fov_angle_deg / 2.0))
        self.hearing_range = hearing_range_cm
        self.decay_rate = memory_decay_rate
        self.lost_threshold = lost_threshold

        self.memory: Dict[str, TrackedThreat] = {}

    def can_see(
        self,
        agent_pos: Tuple[float, float, float],
        agent_forward: Tuple[float, float, float],
        target_pos: Tuple[float, float, float],
        is_occluded: bool = False,
    ) -> bool:
        """
        Evaluates visual line of sight:
        Within sight range, inside horizontal FOV cone, and non-occluded by walls/terrain.
        """
        if is_occluded:
            return False

        ax, ay, az = agent_pos
        tx, ty, tz = target_pos

        dx, dy, dz = tx - ax, ty - ay, tz - az
        dist_3d = math.sqrt(dx * dx + dy * dy + dz * dz)

        if dist_3d > self.sight_range:
            return False

        # 2D horizontal angle
        dist_2d = math.hypot(dx, dy)
        if dist_2d < 1e-4:
            return True  # Directly on top of agent

        fx, fy, _ = agent_forward
        f_len = math.hypot(fx, fy)
        if f_len > 1e-5:
            fx /= f_len
            fy /= f_len
        else:
            fx, fy = 1.0, 0.0

        dot = ((dx / dist_2d) * fx) + ((dy / dist_2d) * fy)
        return dot >= self.cos_half_fov

    def can_hear(
        self,
        agent_pos: Tuple[float, float, float],
        sound_pos: Tuple[float, float, float],
        sound_intensity: float = 1.0,
        occlusion_factor: float = 1.0,
    ) -> bool:
        """Evaluates whether an acoustic event reaches the sensor above hearing threshold."""
        ax, ay, az = agent_pos
        sx, sy, sz = sound_pos

        dist = math.sqrt((sx - ax) ** 2 + (sy - ay) ** 2 + (sz - az) ** 2)
        effective_range = self.hearing_range * sound_intensity * occlusion_factor
        return dist <= effective_range

    def process_stimulus(
        self,
        threat_id: str,
        stimulus: PerceptionStimulus,
        current_time: float,
    ) -> TrackedThreat:
        """Registers a fresh sensory perception and resets confidence to 1.0."""
        record = TrackedThreat(
            threat_id=threat_id,
            last_known_pos=stimulus.source_pos,
            confidence=1.0,
            last_perceived_time=current_time,
            is_currently_visible=(stimulus.stimulus_type == StimulusType.VISION),
        )
        self.memory[threat_id] = record
        return record

    def update_memory(self, delta_time_sec: float) -> List[TrackedThreat]:
        """
        Decays confidence of unobserved threats exponentially:
        C(t + dt) = C(t) * exp(-lambda * dt)
        Removes threats whose confidence drops below lost_threshold.
        """
        decay_factor = math.exp(-self.decay_rate * delta_time_sec)
        active_threats: List[TrackedThreat] = []
        to_remove: List[str] = []

        for threat_id, record in self.memory.items():
            if not record.is_currently_visible:
                record.confidence = max(0.0, record.confidence * decay_factor)

            if record.confidence < self.lost_threshold:
                to_remove.append(threat_id)
            else:
                active_threats.append(record)

        for tid in to_remove:
            del self.memory[tid]

        return active_threats
