"""
Weather System & Lighting Integration for UAF-81.85.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from .core import WeatherCondition, ensure_finite_scalar, ensure_finite_vec3
from .fog import FogSystem
from .clouds import CloudSystem


@dataclass
class WeatherPreset:
    """Lighting and atmospheric modifiers for a specific weather condition."""
    name: WeatherCondition
    cloud_coverage: float
    cloud_density: float
    fog_density: float
    sun_intensity_multiplier: float
    ambient_multiplier: float
    wind_speed: float
    precipitation_vfx: bool = False
    lightning_events: bool = False


WEATHER_PRESETS: Dict[WeatherCondition, WeatherPreset] = {
    WeatherCondition.CLEAR: WeatherPreset(
        name=WeatherCondition.CLEAR,
        cloud_coverage=0.1,
        cloud_density=0.3,
        fog_density=0.005,
        sun_intensity_multiplier=1.0,
        ambient_multiplier=1.0,
        wind_speed=2.0,
    ),
    WeatherCondition.CLOUDY: WeatherPreset(
        name=WeatherCondition.CLOUDY,
        cloud_coverage=0.5,
        cloud_density=0.6,
        fog_density=0.01,
        sun_intensity_multiplier=0.75,
        ambient_multiplier=0.9,
        wind_speed=5.0,
    ),
    WeatherCondition.OVERCAST: WeatherPreset(
        name=WeatherCondition.OVERCAST,
        cloud_coverage=0.95,
        cloud_density=0.9,
        fog_density=0.02,
        sun_intensity_multiplier=0.25,
        ambient_multiplier=0.6,
        wind_speed=8.0,
    ),
    WeatherCondition.STORM: WeatherPreset(
        name=WeatherCondition.STORM,
        cloud_coverage=1.0,
        cloud_density=1.0,
        fog_density=0.05,
        sun_intensity_multiplier=0.05,
        ambient_multiplier=0.3,
        wind_speed=20.0,
        precipitation_vfx=True,
        lightning_events=True,
    ),
    WeatherCondition.FOG: WeatherPreset(
        name=WeatherCondition.FOG,
        cloud_coverage=0.7,
        cloud_density=0.5,
        fog_density=0.15,
        sun_intensity_multiplier=0.2,
        ambient_multiplier=0.5,
        wind_speed=1.0,
    ),
    WeatherCondition.RAIN: WeatherPreset(
        name=WeatherCondition.RAIN,
        cloud_coverage=0.9,
        cloud_density=0.8,
        fog_density=0.03,
        sun_intensity_multiplier=0.3,
        ambient_multiplier=0.6,
        wind_speed=10.0,
        precipitation_vfx=True,
    ),
    WeatherCondition.SNOW: WeatherPreset(
        name=WeatherCondition.SNOW,
        cloud_coverage=0.85,
        cloud_density=0.7,
        fog_density=0.025,
        sun_intensity_multiplier=0.4,
        ambient_multiplier=0.8,
        wind_speed=6.0,
        precipitation_vfx=True,
    ),
    WeatherCondition.DUST: WeatherPreset(
        name=WeatherCondition.DUST,
        cloud_coverage=0.4,
        cloud_density=0.5,
        fog_density=0.08,
        sun_intensity_multiplier=0.4,
        ambient_multiplier=0.7,
        wind_speed=12.0,
    ),
    WeatherCondition.SANDSTORM: WeatherPreset(
        name=WeatherCondition.SANDSTORM,
        cloud_coverage=0.8,
        cloud_density=0.9,
        fog_density=0.2,
        sun_intensity_multiplier=0.1,
        ambient_multiplier=0.4,
        wind_speed=25.0,
        precipitation_vfx=True,
    ),
}


class WeatherSystem:
    """
    Coordinates weather conditions, interpolating atmospheric and lighting parameters,
    and dispatching weather triggers to the VFX event bus.
    """

    def __init__(self, initial_condition: WeatherCondition = WeatherCondition.CLEAR) -> None:
        self.current_condition = initial_condition
        self.target_condition = initial_condition
        self.transition_progress: float = 1.0
        self.transition_duration: float = 10.0  # Seconds
        self.vfx_event_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None

    def set_weather(self, condition: WeatherCondition, transition_time: float = 5.0) -> None:
        """Transitions smoothly to a new weather condition."""
        if condition != self.target_condition:
            self.target_condition = condition
            self.transition_duration = max(0.1, transition_time)
            self.transition_progress = 0.0

    def tick(self, dt: float, clouds: CloudSystem, fog: FogSystem) -> None:
        """Updates weather transition and applies values to clouds and fog."""
        if self.transition_progress < 1.0:
            self.transition_progress = min(1.0, self.transition_progress + (dt / self.transition_duration))
            if self.transition_progress >= 1.0:
                self.current_condition = self.target_condition

        curr_preset = WEATHER_PRESETS.get(self.current_condition, WEATHER_PRESETS[WeatherCondition.CLEAR])
        target_preset = WEATHER_PRESETS.get(self.target_condition, WEATHER_PRESETS[WeatherCondition.CLEAR])
        t = self.transition_progress

        # Interpolate
        clouds.coverage = curr_preset.cloud_coverage * (1.0 - t) + target_preset.cloud_coverage * t
        clouds.density = curr_preset.cloud_density * (1.0 - t) + target_preset.cloud_density * t
        fog.density = curr_preset.fog_density * (1.0 - t) + target_preset.fog_density * t

        # Check lightning triggers
        if target_preset.lightning_events and self.vfx_event_callback:
            # Can invoke VFX event if callback registered
            pass
