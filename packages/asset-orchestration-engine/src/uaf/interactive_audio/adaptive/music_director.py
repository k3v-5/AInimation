"""
UAF-81.94: Adaptive Music Director, Quartz Quantization Clock & Equal-Power Crossfading.
Orchestrates synchronous audio stems across DynamicPacingDirector phases
with deterministic musical grid timing and constant-power energy preservation.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from uaf.level_design.core.contracts import PacingPhase
from uaf.interactive_audio.core.contracts import (
    AudioStem,
    QuantizationSubdivision,
    StemRole,
)


class QuartzQuantizationClock:
    """
    Simulates Unreal Engine Quartz quantization subsystem for musically
    accurate sample-rate-independent event scheduling.
    """

    def __init__(self, bpm: float = 120.0, beats_per_bar: int = 4):
        self.bpm = bpm
        self.beats_per_bar = beats_per_bar
        self.current_time_seconds: float = 0.0

    @property
    def seconds_per_beat(self) -> float:
        """Duration of a quarter note beat in seconds."""
        return 60.0 / max(1.0, self.bpm)

    @property
    def seconds_per_bar(self) -> float:
        """Duration of a full measure in seconds."""
        return self.seconds_per_beat * float(self.beats_per_bar)

    def advance_time(self, delta_time_seconds: float) -> float:
        """Advances clock and returns new elapsed time."""
        self.current_time_seconds += delta_time_seconds
        return self.current_time_seconds

    @property
    def current_beat(self) -> float:
        """Total elapsed beats since start."""
        return self.current_time_seconds / self.seconds_per_beat

    @property
    def current_bar(self) -> int:
        """Zero-indexed current measure number."""
        return int(self.current_beat // self.beats_per_bar)

    def get_subdivision_duration_seconds(self, subdivision: QuantizationSubdivision) -> float:
        """Returns interval duration for the specified quantization grid."""
        spb = self.seconds_per_beat
        bar = self.seconds_per_bar
        return {
            QuantizationSubdivision.EIGHTH_NOTE: spb * 0.5,
            QuantizationSubdivision.QUARTER_NOTE: spb,
            QuantizationSubdivision.BAR_1: bar,
            QuantizationSubdivision.BAR_2: bar * 2.0,
            QuantizationSubdivision.BAR_4: bar * 4.0,
        }[subdivision]

    def get_next_quantized_timestamp(self, subdivision: QuantizationSubdivision) -> float:
        """
        Calculates the exact timestamp (in seconds) of the next quantization boundary.
        Guarantees that musical cues do not fire midway through a bar or beat.
        """
        grid_duration = self.get_subdivision_duration_seconds(subdivision)
        current = self.current_time_seconds
        # Next boundary is the smallest multiple of grid_duration strictly greater than current
        index = math.floor(current / grid_duration) + 1
        return round(index * grid_duration, 6)


class AdaptiveMusicOrchestrator:
    """
    Manages multi-track audio stem layers and executes seamless equal-power
    crossfades tied to PacingPhase combat states.
    """

    MUTED_GAIN_DB: float = -60.0  # Inaudible noise floor

    def __init__(self, clock: Optional[QuartzQuantizationClock] = None):
        self.clock = clock or QuartzQuantizationClock(bpm=120.0)
        self.stems: Dict[str, AudioStem] = {}
        self.current_phase: PacingPhase = PacingPhase.CALM
        self.target_phase: PacingPhase = PacingPhase.CALM

        self.transition_start_time: float = 0.0
        self.transition_duration: float = 2.0  # seconds
        self.is_transitioning: bool = False

    def register_stem(self, stem: AudioStem) -> None:
        """Registers a musical stem in the active arrangement."""
        self.stems[stem.stem_id] = stem

    @classmethod
    def calculate_equal_power_crossfade(cls, progress: float) -> Tuple[float, float]:
        """
        Computes constant-power crossfade gain multipliers:
        g_in = sin(pi/2 * t), g_out = cos(pi/2 * t)
        Preserves RMS energy: g_in^2 + g_out^2 = 1.0.
        Progress t must be in [0.0, 1.0].
        """
        clamped_t = max(0.0, min(1.0, float(progress)))
        theta = (math.pi / 2.0) * clamped_t
        gain_in = math.sin(theta)
        gain_out = math.cos(theta)
        return gain_out, gain_in

    def request_phase_transition(
        self,
        new_phase: PacingPhase,
        subdivision: QuantizationSubdivision = QuantizationSubdivision.BAR_1,
    ) -> float:
        """
        Schedules a transition to a new pacing phase on the next musical bar boundary.
        Returns the scheduled execution timestamp in seconds.
        """
        if new_phase == self.current_phase and not self.is_transitioning:
            return self.clock.current_time_seconds

        scheduled_time = self.clock.get_next_quantized_timestamp(subdivision)
        self.target_phase = new_phase
        self.transition_start_time = scheduled_time
        self.is_transitioning = True
        return scheduled_time

    def is_stem_active_in_phase(self, stem: AudioStem, phase: PacingPhase) -> bool:
        """Evaluates whether a stem role is assigned to the given pacing phase."""
        if stem.active_phases:
            return phase in stem.active_phases

        # Default standard assignment if not explicitly configured
        role_map: Dict[StemRole, List[PacingPhase]] = {
            StemRole.ATMOSPHERE_PAD: [
                PacingPhase.CALM,
                PacingPhase.BUILDUP,
                PacingPhase.PEAK,
                PacingPhase.SUSTAINED_PEAK,
                PacingPhase.COOLDOWN,
            ],
            StemRole.BASS_SYNTH: [
                PacingPhase.BUILDUP,
                PacingPhase.PEAK,
                PacingPhase.SUSTAINED_PEAK,
            ],
            StemRole.DRUMS_PERCUSSION: [
                PacingPhase.BUILDUP,
                PacingPhase.PEAK,
                PacingPhase.SUSTAINED_PEAK,
            ],
            StemRole.MELODIC_LEAD: [
                PacingPhase.PEAK,
                PacingPhase.SUSTAINED_PEAK,
            ],
            StemRole.TENSION_NOISE: [
                PacingPhase.SUSTAINED_PEAK,
            ],
            StemRole.COMBAT_RISER: [
                PacingPhase.BUILDUP,
                PacingPhase.PEAK,
            ],
        }
        return phase in role_map.get(stem.role, [])

    def compute_stem_gains(self) -> Dict[str, float]:
        """
        Computes the linear gain (0.0 to 1.0) for every registered stem at current clock time,
        incorporating equal-power crossfading across phase boundaries.
        """
        current_time = self.clock.current_time_seconds
        gains: Dict[str, float] = {}

        if not self.is_transitioning or current_time < self.transition_start_time:
            # Steady state in current phase
            for stem_id, stem in self.stems.items():
                is_active = self.is_stem_active_in_phase(stem, self.current_phase)
                gains[stem_id] = 1.0 if is_active else 0.0
            return gains

        # Transition active
        elapsed_in_trans = current_time - self.transition_start_time
        progress = min(1.0, elapsed_in_trans / max(0.001, self.transition_duration))
        gain_out, gain_in = self.calculate_equal_power_crossfade(progress)

        if progress >= 1.0:
            # Transition finished
            self.current_phase = self.target_phase
            self.is_transitioning = False
            for stem_id, stem in self.stems.items():
                is_active = self.is_stem_active_in_phase(stem, self.current_phase)
                gains[stem_id] = 1.0 if is_active else 0.0
            return gains

        # In-between crossfade
        for stem_id, stem in self.stems.items():
            active_old = self.is_stem_active_in_phase(stem, self.current_phase)
            active_new = self.is_stem_active_in_phase(stem, self.target_phase)

            if active_old and active_new:
                gains[stem_id] = 1.0
            elif active_old and not active_new:
                gains[stem_id] = round(gain_out, 4)
            elif not active_old and active_new:
                gains[stem_id] = round(gain_in, 4)
            else:
                gains[stem_id] = 0.0

        return gains
