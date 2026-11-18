"""
UAF-81.89.6: Audio-Reactive Spectral Coupler and ADSR Envelopes.
Performs 6-band psychoacoustic spectrum analysis and drives VFX particle parameters using ADSR dynamic envelopes.
"""

from __future__ import annotations

import math
from typing import Dict, Tuple, List, Optional
from pydantic import BaseModel, Field
from ..core.contracts import SpectralBand, AudioBandEnvelope, clamp_scalar


class ADSREnvelope(BaseModel):
    """Attack-Decay-Sustain-Release envelope generator for audio parameter smoothing."""
    attack_time: float = Field(default=0.02, gt=0.0, description="Attack time in seconds")
    decay_time: float = Field(default=0.08, gt=0.0, description="Decay time in seconds")
    sustain_level: float = Field(default=0.4, ge=0.0, le=1.0, description="Sustain amplitude [0, 1]")
    release_time: float = Field(default=0.15, gt=0.0, description="Release time in seconds")

    _current_val: float = 0.0
    _gate_active: bool = False

    def trigger(self) -> None:
        self._gate_active = True

    def release(self) -> None:
        self._gate_active = False

    def update(self, dt: float, target_energy: float) -> float:
        """Step envelope towards target energy with ADSR curves."""
        if target_energy > self._current_val:
            # Attack phase: quick rise
            attack_rate = 1.0 / max(0.001, self.attack_time)
            self._current_val = min(target_energy, self._current_val + attack_rate * dt)
        elif self._gate_active:
            # Decay towards sustain
            sustain_target = target_energy * self.sustain_level
            decay_rate = 1.0 / max(0.001, self.decay_time)
            self._current_val = max(sustain_target, self._current_val - decay_rate * dt)
        else:
            # Release phase: smooth fade to zero
            release_rate = 1.0 / max(0.001, self.release_time)
            self._current_val = max(0.0, self._current_val - release_rate * dt)

        return self._current_val


BAND_FREQUENCIES: Dict[SpectralBand, Tuple[float, float]] = {
    SpectralBand.SUB_BASS: (20.0, 60.0),
    SpectralBand.BASS: (60.0, 250.0),
    SpectralBand.LOW_MID: (250.0, 500.0),
    SpectralBand.MID: (500.0, 2000.0),
    SpectralBand.HIGH: (2000.0, 8000.0),
    SpectralBand.AIR: (8000.0, 22000.0),
}


class AudioSpectralCoupler:
    """
    Couples live or captured audio spectral energy to particle emission, turbulences, and luminescence.
    """

    def __init__(self) -> None:
        self.bands: Dict[SpectralBand, AudioBandEnvelope] = {}
        self.envelopes: Dict[SpectralBand, ADSREnvelope] = {}

        for band, freq_range in BAND_FREQUENCIES.items():
            self.bands[band] = AudioBandEnvelope(
                band=band,
                frequency_range_hz=freq_range,
                current_energy=0.0,
                peak_energy=0.0,
                adsr_value=0.0,
            )
            # Custom ADSR timings per band (e.g. Bass has punchy attack, Air has smooth release)
            if band in (SpectralBand.SUB_BASS, SpectralBand.BASS):
                self.envelopes[band] = ADSREnvelope(attack_time=0.015, decay_time=0.06, sustain_level=0.3, release_time=0.12)
            else:
                self.envelopes[band] = ADSREnvelope(attack_time=0.02, decay_time=0.08, sustain_level=0.4, release_time=0.15)

    def process_spectrum(self, energy_per_band: Dict[SpectralBand, float], dt: float) -> None:
        """Feeds raw band spectral energies and steps envelope smoothing."""
        for band in SpectralBand:
            energy = clamp_scalar(energy_per_band.get(band, 0.0), 0.0, 10.0)
            b_info = self.bands[band]
            b_info.current_energy = energy
            b_info.peak_energy = max(b_info.peak_energy * 0.98, energy)

            # Trigger envelope if energy spikes
            env = self.envelopes[band]
            if energy > b_info.peak_energy * 0.5:
                env.trigger()
            else:
                env.release()

            b_info.adsr_value = env.update(dt, energy)

    def get_band_envelope(self, band: SpectralBand) -> float:
        return self.bands[band].adsr_value

    def get_spawn_rate_multiplier(self, band: SpectralBand, sensitivity: float = 1.0) -> float:
        """Returns emission multiplier scaled by smoothed band energy."""
        env = self.bands[band].adsr_value
        return 1.0 + env * sensitivity

    def get_emissive_boost(self, band: SpectralBand, sensitivity: float = 2.0) -> float:
        """Returns light emission boost factor."""
        env = self.bands[band].adsr_value
        return 1.0 + env * sensitivity

    def get_turbulence_boost(self, band: SpectralBand, sensitivity: float = 1.5) -> float:
        """Returns curl noise / wind turbulence multiplier."""
        env = self.bands[band].adsr_value
        return 1.0 + env * sensitivity
