"""
UAF-81.94: Core Contracts, Enums & Models for Interactive Audio, Spatial Acoustics & MetaSounds.
Strict data models, absorption coefficients, acoustic rooms, stems, and spatialization presets.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from uaf.level_design.core.contracts import PacingPhase


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AcousticMaterial(str, Enum):
    """Surface material type determining frequency-dependent acoustic absorption."""
    CONCRETE = "CONCRETE"
    STEEL_PLATE = "STEEL_PLATE"
    GLASS_COMPOSITE = "GLASS_COMPOSITE"
    CARPET_FOAM = "CARPET_FOAM"
    WOOD_PANEL = "WOOD_PANEL"
    ROCK_SURFACE = "ROCK_SURFACE"
    WATER_SURFACE = "WATER_SURFACE"


class StemRole(str, Enum):
    """Musical stem functional role in adaptive composition."""
    ATMOSPHERE_PAD = "ATMOSPHERE_PAD"
    BASS_SYNTH = "BASS_SYNTH"
    DRUMS_PERCUSSION = "DRUMS_PERCUSSION"
    MELODIC_LEAD = "MELODIC_LEAD"
    TENSION_NOISE = "TENSION_NOISE"
    COMBAT_RISER = "COMBAT_RISER"


class QuantizationSubdivision(str, Enum):
    """Rhythmic quantization grid for musical transitions."""
    QUARTER_NOTE = "QUARTER_NOTE"      # 1 beat
    EIGHTH_NOTE = "EIGHTH_NOTE"        # 0.5 beat
    BAR_1 = "BAR_1"                    # 4 beats
    BAR_2 = "BAR_2"                    # 8 beats
    BAR_4 = "BAR_4"                    # 16 beats


class OcclusionState(str, Enum):
    """Topological sound occlusion state."""
    CLEAR_LOS = "CLEAR_LOS"
    PORTAL_DIFFRACTION = "PORTAL_DIFFRACTION"
    PARTIALLY_OCCLUDED = "PARTIALLY_OCCLUDED"
    FULL_OCCLUDED = "FULL_OCCLUDED"


class AttenuationCurveType(str, Enum):
    """Distance attenuation curve."""
    LOGARITHMIC = "LOGARITHMIC"
    NATURAL_SOUND_EXPONENTIAL = "NATURAL_SOUND_EXPONENTIAL"
    LINEAR = "LINEAR"
    SPHERICAL_INVERSE = "SPHERICAL_INVERSE"


# ---------------------------------------------------------------------------
# Acoustic Material Absorption Specs (Low: 125-250Hz, Mid: 500-1000Hz, High: 2000-4000Hz)
# ---------------------------------------------------------------------------

MATERIAL_ABSORPTION_TABLE: Dict[AcousticMaterial, Dict[str, float]] = {
    AcousticMaterial.CONCRETE: {
        "alpha_low": 0.01,
        "alpha_mid": 0.02,
        "alpha_high": 0.03,
    },
    AcousticMaterial.STEEL_PLATE: {
        "alpha_low": 0.03,
        "alpha_mid": 0.04,
        "alpha_high": 0.05,
    },
    AcousticMaterial.GLASS_COMPOSITE: {
        "alpha_low": 0.18,
        "alpha_mid": 0.06,
        "alpha_high": 0.04,
    },
    AcousticMaterial.CARPET_FOAM: {
        "alpha_low": 0.10,
        "alpha_mid": 0.35,
        "alpha_high": 0.65,
    },
    AcousticMaterial.WOOD_PANEL: {
        "alpha_low": 0.28,
        "alpha_mid": 0.15,
        "alpha_high": 0.10,
    },
    AcousticMaterial.ROCK_SURFACE: {
        "alpha_low": 0.05,
        "alpha_mid": 0.07,
        "alpha_high": 0.09,
    },
    AcousticMaterial.WATER_SURFACE: {
        "alpha_low": 0.01,
        "alpha_mid": 0.01,
        "alpha_high": 0.02,
    },
}


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class MaterialAbsorption(BaseModel):
    """Frequency-dependent sound absorption coefficients (0.0 to 1.0)."""
    alpha_low: float = Field(ge=0.0, le=1.0)
    alpha_mid: float = Field(ge=0.0, le=1.0)
    alpha_high: float = Field(ge=0.0, le=1.0)

    @property
    def average_alpha(self) -> float:
        """Arithmetic mean absorption coefficient."""
        return (self.alpha_low + self.alpha_mid + self.alpha_high) / 3.0


class RoomAcousticProfile(BaseModel):
    """Physical dimensions, materials, and computed acoustic properties of a space."""
    room_id: str
    dimensions_m: Tuple[float, float, float]  # (Length, Width, Height)
    volume_m3: float = Field(gt=0)
    surface_area_m2: float = Field(gt=0)
    material_distribution: Dict[AcousticMaterial, float] = Field(default_factory=dict)  # Area fraction (sums to 1.0)

    rt60_sabine_seconds: float = Field(ge=0)
    rt60_eyring_seconds: float = Field(ge=0)
    axial_resonance_modes_hz: List[float] = Field(default_factory=list)


class AudioStem(BaseModel):
    """A synchronous musical layer that can be dynamically faded and muted."""
    stem_id: str
    role: StemRole
    file_path: str
    bpm: float = Field(gt=0, default=120.0)
    duration_bars: int = Field(gt=0, default=4)
    nominal_gain_db: float = 0.0
    active_phases: List[PacingPhase] = Field(default_factory=list)
    priority: int = 1


class SpatialAttenuationProfile(BaseModel):
    """Distance attenuation and air absorption configuration conforming to Rule 10."""
    profile_id: str
    inner_radius_m: float = Field(ge=0.0, default=2.0)
    falloff_distance_m: float = Field(gt=0.0, default=18.0)  # Max <= 20.0m for loops per Rule 10
    curve_type: AttenuationCurveType = AttenuationCurveType.NATURAL_SOUND_EXPONENTIAL
    air_absorption_hf_loss_db_per_m: float = 0.5
    is_looping_spatial: bool = True


class AcousticRaycastResult(BaseModel):
    """Result of topological acoustic tracing between sound source and listener."""
    distance_m: float
    direct_path_clear: bool
    occlusion_state: OcclusionState
    occlusion_alpha: float = Field(ge=0.0, le=1.0)  # 0.0 = clear, 1.0 = fully blocked
    transmission_loss_db: float = Field(ge=0.0)
    low_pass_cutoff_hz: float = Field(ge=20.0, le=22000.0)
