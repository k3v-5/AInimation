"""
Core Contracts, Identification, Enums & Numeric Security for UAF-81.85.
"""

from __future__ import annotations
import math
import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union


# ---------------------------------------------------------------------------
# Identifiers
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LightId:
    """Stable, unique identifier for a light entity."""
    value: str

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ShadowCasterId:
    """Stable identifier for a shadow-casting entity or light."""
    value: str

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PostProcessVolumeId:
    """Stable identifier for a post-process volume."""
    value: str

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ProbeId:
    """Stable identifier for an irradiance or reflection probe."""
    value: str

    def __str__(self) -> str:
        return self.value


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class LightType(str, Enum):
    POINT = "POINT"
    SPOT = "SPOT"
    DIRECTIONAL = "DIRECTIONAL"
    RECT_AREA = "RECT_AREA"
    DISK_AREA = "DISK_AREA"
    LINE_AREA = "LINE_AREA"
    EMISSIVE = "EMISSIVE"
    ENVIRONMENT = "ENVIRONMENT"


class LightMobility(str, Enum):
    STATIC = "STATIC"
    STATIONARY = "STATIONARY"
    MOVABLE = "MOVABLE"


class LightPriority(str, Enum):
    CRITICAL = "CRITICAL"
    GAMEPLAY = "GAMEPLAY"
    CHARACTER = "CHARACTER"
    ENVIRONMENT = "ENVIRONMENT"
    VFX = "VFX"
    COSMETIC = "COSMETIC"


class ShadowBackend(str, Enum):
    SHADOW_MAP = "SHADOW_MAP"
    CSM = "CSM"
    CUBE_SHADOW = "CUBE_SHADOW"
    ATLAS_SHADOW = "ATLAS_SHADOW"
    VIRTUAL_SHADOW = "VIRTUAL_SHADOW"
    RAY_TRACED = "RAY_TRACED"
    REFERENCE = "REFERENCE"


class FogType(str, Enum):
    LINEAR = "LINEAR"
    EXPONENTIAL = "EXPONENTIAL"
    EXPONENTIAL_HEIGHT = "EXPONENTIAL_HEIGHT"
    VOLUMETRIC = "VOLUMETRIC"


class VolumetricQuality(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    OFF = "OFF"


class ToneMapperType(str, Enum):
    ACES = "ACES"
    FILMIC = "FILMIC"
    AGX = "AGX"
    NEUTRAL = "NEUTRAL"
    CUSTOM = "CUSTOM"


class ExposureMode(str, Enum):
    MANUAL = "MANUAL"
    AUTOMATIC = "AUTOMATIC"
    HISTOGRAM = "HISTOGRAM"
    AVERAGE_LUMINANCE = "AVERAGE_LUMINANCE"
    CENTER_WEIGHTED = "CENTER_WEIGHTED"


class AOBackend(str, Enum):
    SSAO = "SSAO"
    GTAO = "GTAO"
    HBAO = "HBAO"
    RAY_TRACED = "RAY_TRACED"
    REFERENCE = "REFERENCE"


class UpdateFrequency(str, Enum):
    EVERY_FRAME = "EVERY_FRAME"
    EVERY_2_FRAMES = "EVERY_2_FRAMES"
    EVERY_4_FRAMES = "EVERY_4_FRAMES"
    EVENT_DRIVEN = "EVENT_DRIVEN"
    STATIC = "STATIC"


class FallbackLevel(str, Enum):
    FULL = "FULL"
    REDUCED = "REDUCED"
    MINIMAL = "MINIMAL"
    EMERGENCY = "EMERGENCY"


class WeatherCondition(str, Enum):
    CLEAR = "CLEAR"
    CLOUDY = "CLOUDY"
    OVERCAST = "OVERCAST"
    STORM = "STORM"
    FOG = "FOG"
    RAIN = "RAIN"
    SNOW = "SNOW"
    DUST = "DUST"
    SANDSTORM = "SANDSTORM"


# ---------------------------------------------------------------------------
# Numeric Validation & Security
# ---------------------------------------------------------------------------

def ensure_finite_scalar(val: Any, name: str, default: float = 0.0) -> float:
    """Validates that a scalar value is a finite float, sanitizing NaN/Inf."""
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except (TypeError, ValueError):
        return default


def ensure_finite_vec3(vec: Any, name: str, default: Tuple[float, float, float] = (0.0, 0.0, 0.0)) -> Tuple[float, float, float]:
    """Validates that a 3D vector contains only finite floats."""
    if not isinstance(vec, (tuple, list)) or len(vec) < 3:
        return default
    x = ensure_finite_scalar(vec[0], f"{name}.x", default[0])
    y = ensure_finite_scalar(vec[1], f"{name}.y", default[1])
    z = ensure_finite_scalar(vec[2], f"{name}.z", default[2])
    return (x, y, z)


def ensure_finite_vec4(vec: Any, name: str, default: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)) -> Tuple[float, float, float, float]:
    """Validates that a 4D vector contains only finite floats."""
    if not isinstance(vec, (tuple, list)) or len(vec) < 4:
        return default
    x = ensure_finite_scalar(vec[0], f"{name}.x", default[0])
    y = ensure_finite_scalar(vec[1], f"{name}.y", default[1])
    z = ensure_finite_scalar(vec[2], f"{name}.z", default[2])
    w = ensure_finite_scalar(vec[3], f"{name}.w", default[3])
    return (x, y, z, w)


def normalize_vec3(vec: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """Normalizes a 3D vector, returning (0.0, 1.0, 0.0) if length is near zero."""
    x, y, z = vec
    length_sq = x * x + y * y + z * z
    if length_sq < 1e-12:
        return (0.0, 1.0, 0.0)
    inv_len = 1.0 / math.sqrt(length_sq)
    return (x * inv_len, y * inv_len, z * inv_len)


# ---------------------------------------------------------------------------
# Color & Photometric Calculations
# ---------------------------------------------------------------------------

def kelvin_to_rgb(kelvin: float) -> Tuple[float, float, float]:
    """
    Deterministic conversion of blackbody color temperature in Kelvin (1000K to 20000K+)
    to linear RGB using Tanner Helland's empirical Planckian fit with sRGB to Linear conversion.
    """
    k = max(1000.0, min(40000.0, float(kelvin)))
    temp = k / 100.0

    # Calculate Red
    if temp <= 66.0:
        r = 255.0
    else:
        r = temp - 60.0
        r = 329.698727446 * (r ** -0.1332047592)
        r = max(0.0, min(255.0, r))

    # Calculate Green
    if temp <= 66.0:
        g = temp
        g = 99.4708025861 * math.log(g) - 161.1195681661
        g = max(0.0, min(255.0, g))
    else:
        g = temp - 60.0
        g = 288.1221695283 * (g ** -0.0755148492)
        g = max(0.0, min(255.0, g))

    # Calculate Blue
    if temp >= 66.0:
        b = 255.0
    elif temp <= 19.0:
        b = 0.0
    else:
        b = temp - 10.0
        b = 138.5177312231 * math.log(b) - 305.0447927307
        b = max(0.0, min(255.0, b))

    # Normalize to [0, 1] sRGB
    sr = r / 255.0
    sg = g / 255.0
    sb = b / 255.0

    # Convert sRGB to Linear RGB
    def to_linear(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return (round(to_linear(sr), 6), round(to_linear(sg), 6), round(to_linear(sb), 6))


def ev100_to_luminance(ev100: float, calibration_k: float = 12.5) -> float:
    """Converts photographic EV100 to luminance (cd/m^2) using calibration constant K."""
    return (2.0 ** ev100) * (calibration_k / 100.0)


def luminance_to_ev100(luminance: float, calibration_k: float = 12.5) -> float:
    """Converts luminance (cd/m^2) to photographic EV100."""
    lum = max(1e-6, luminance)
    return math.log2(lum * (100.0 / calibration_k))


def lumens_to_candelas(lumens: float) -> float:
    """Converts luminous flux in Lumens to peak intensity in Candelas for an isotropic sphere."""
    return lumens / (4.0 * math.pi)


def candelas_to_lumens(candelas: float) -> float:
    """Converts peak intensity in Candelas to total luminous flux in Lumens for an isotropic sphere."""
    return candelas * (4.0 * math.pi)
