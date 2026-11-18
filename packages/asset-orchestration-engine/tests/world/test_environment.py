"""
Tests for Environment, Lighting, Weather & Audio Hooks (UAF-81.56 Section 200).
"""

import pytest
from uaf.universal_world import (
    EnvironmentProfile,
    LightingProfile,
    TimeOfDayProfile,
    WeatherProfile,
    WeatherType,
    WorldAudioProfile,
    WorldVFXProfile,
    UniversalWorldFabricator,
)


def test_environment_profile():
    env = EnvironmentProfile()
    assert env.lighting is not None
    assert env.time_of_day is not None
    assert env.weather is not None


def test_lighting_hook():
    light = LightingProfile(sun_intensity=120000.0, volumetric_fog=True)
    assert light.sun_intensity == 120000.0
    assert light.volumetric_fog is True


def test_time_of_day():
    tod = TimeOfDayProfile(time=18.5, ambient_intensity=0.3)
    assert tod.time == 18.5
    assert tod.ambient_intensity == 0.3


def test_weather_hook():
    w = WeatherProfile(weather_type=WeatherType.RAIN, precipitation=0.8, wind_speed=15.0)
    assert w.weather_type == WeatherType.RAIN
    assert w.precipitation == 0.8
    assert w.wind_speed == 15.0


def test_audio_zone():
    audio = WorldAudioProfile(reverb_preset="MOUNTAIN_ECHO")
    assert audio.reverb_preset == "MOUNTAIN_ECHO"
    assert audio.sound_occlusion is True


def test_vfx_hook():
    vfx = WorldVFXProfile(effects=["dust", "rain", "sparks"])
    assert len(vfx.effects) == 3
    assert "sparks" in vfx.effects
