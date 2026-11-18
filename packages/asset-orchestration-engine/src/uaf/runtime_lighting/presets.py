"""
14 Golden Lighting Scenarios & Presets for UAF-81.85.
"""

from __future__ import annotations
from typing import Dict, Tuple

from .core import LightId, LightPriority, WeatherCondition, PostProcessVolumeId
from .lights import Light
from .point import PointLight
from .spot import SpotLight
from .directional import DirectionalLight
from .area import RectAreaLight
from .postprocess import PostProcessVolume, PostProcessSettings
from .world import LightingWorld


class GoldenLightingPresets:
    """
    Factory for the 14 normative Golden Lighting scenarios.
    """

    @staticmethod
    def apply_preset(world: LightingWorld, scenario_name: str) -> None:
        """Configures the lighting world for a specific golden scenario."""
        scenario = scenario_name.lower().strip()

        # Clear existing dynamic lights
        for l_id in list(world.lights.keys()):
            world.destroy_light(LightId(l_id))

        if scenario == "day":
            world.sky.controller.set_time_of_day(12.0)
            world.weather.set_weather(WeatherCondition.CLEAR, 0.0)
            sun = DirectionalLight(
                light_id=LightId("sun_noon"),
                intensity=120000.0,
                color=(1.0, 0.98, 0.95),
                cast_shadows=True,
                cascade_count=4,
                priority=LightPriority.CRITICAL,
            )
            world.create_light(sun)

        elif scenario == "night":
            world.sky.controller.set_time_of_day(0.0)
            world.weather.set_weather(WeatherCondition.CLEAR, 0.0)
            moon = DirectionalLight(
                light_id=LightId("moon_light"),
                intensity=0.25,
                color=(0.75, 0.85, 1.0),
                cast_shadows=True,
                priority=LightPriority.CRITICAL,
            )
            world.create_light(moon)

        elif scenario == "dawn":
            world.sky.controller.set_time_of_day(5.8)
            world.weather.set_weather(WeatherCondition.CLEAR, 0.0)
            sun = DirectionalLight(
                light_id=LightId("sun_dawn"),
                intensity=25000.0,
                color=(1.0, 0.7, 0.4),
                temperature=3200.0,
                use_temperature=True,
                cast_shadows=True,
                priority=LightPriority.CRITICAL,
            )
            world.create_light(sun)

        elif scenario == "sunset":
            world.sky.controller.set_time_of_day(18.5)
            world.weather.set_weather(WeatherCondition.CLEAR, 0.0)
            sun = DirectionalLight(
                light_id=LightId("sun_sunset"),
                intensity=30000.0,
                color=(1.0, 0.5, 0.2),
                temperature=2800.0,
                use_temperature=True,
                cast_shadows=True,
                priority=LightPriority.CRITICAL,
            )
            world.create_light(sun)

        elif scenario == "interior":
            world.sky.controller.set_time_of_day(12.0)
            # Enclosed interior with artificial lights
            for i in range(4):
                p = PointLight(
                    light_id=LightId(f"ceiling_light_{i}"),
                    position=(-10.0 + i * 6.0, 3.5, 0.0),
                    intensity=1500.0,
                    color=(1.0, 0.95, 0.85),
                    range=12.0,
                    cast_shadows=True,
                    priority=LightPriority.ENVIRONMENT,
                )
                world.create_light(p)

        elif scenario == "exterior":
            world.sky.controller.set_time_of_day(14.0)
            sun = DirectionalLight(
                light_id=LightId("sun_exterior"),
                intensity=100000.0,
                color=(1.0, 1.0, 0.97),
                cast_shadows=True,
                cascade_count=4,
                cascade_max_distance=300.0,
                priority=LightPriority.CRITICAL,
            )
            world.create_light(sun)

        elif scenario == "cave":
            world.sky.controller.set_time_of_day(0.0)
            world.fog.density = 0.08
            torch = PointLight(
                light_id=LightId("cave_torch"),
                position=(0.0, 1.5, 0.0),
                intensity=2500.0,
                temperature=2200.0,
                use_temperature=True,
                range=15.0,
                cast_shadows=True,
                priority=LightPriority.GAMEPLAY,
            )
            world.create_light(torch)

        elif scenario == "storm":
            world.weather.set_weather(WeatherCondition.STORM, 0.0)

        elif scenario == "fog":
            world.weather.set_weather(WeatherCondition.FOG, 0.0)

        elif scenario == "high_density_lights":
            # 128 dynamic point lights packed in grid
            for i in range(128):
                gx = (i % 16) * 5.0 - 40.0
                gz = (i // 16) * 5.0 - 20.0
                p = PointLight(
                    light_id=LightId(f"density_light_{i}"),
                    position=(gx, 2.0, gz),
                    intensity=800.0,
                    color=(0.8 + (i % 3) * 0.1, 0.7, 0.9),
                    range=8.0,
                    cast_shadows=(i % 4 == 0),
                    priority=LightPriority.COSMETIC if i > 32 else LightPriority.ENVIRONMENT,
                )
                world.create_light(p)

        elif scenario == "high_shadow_load":
            # 32 shadow-casting spot lights
            for i in range(32):
                s = SpotLight(
                    light_id=LightId(f"shadow_spot_{i}"),
                    position=(-30.0 + (i % 8) * 8.0, 10.0, -15.0 + (i // 8) * 10.0),
                    direction=(0.0, -1.0, 0.0),
                    intensity=5000.0,
                    range=25.0,
                    cast_shadows=True,
                    priority=LightPriority.GAMEPLAY,
                )
                world.create_light(s)

        elif scenario == "vfx_heavy_scene":
            # Lights attached to dynamic entities
            for i in range(10):
                p = PointLight(
                    light_id=LightId(f"vfx_spell_light_{i}"),
                    position=(i * 2.0, 1.0, 0.0),
                    intensity=3000.0,
                    color=(0.2, 0.6, 1.0),
                    range=6.0,
                    attached_to=f"particle_emitter_{i}",
                    priority=LightPriority.VFX,
                )
                world.create_light(p)

        elif scenario == "streaming_transition":
            # Streaming cell with lights
            cell_lights = [
                PointLight(
                    light_id=LightId(f"streamed_light_{i}"),
                    position=(100.0 + i * 2.0, 2.0, 100.0),
                    intensity=1000.0,
                    range=10.0,
                )
                for i in range(5)
            ]
            world.register_streaming_cell("Cell_X1_Y1", cell_lights)

        elif scenario == "desert_sandstorm":
            world.weather.set_weather(WeatherCondition.SANDSTORM, 0.0)
            sun = DirectionalLight(
                light_id=LightId("sandstorm_sun"),
                intensity=15000.0,
                color=(1.0, 0.75, 0.4),
                cast_shadows=False,
            )
            world.create_light(sun)
