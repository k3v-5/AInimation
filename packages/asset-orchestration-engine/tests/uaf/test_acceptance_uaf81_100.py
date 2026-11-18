"""
Acceptance Test Suite for UAF-81.100: Volumetric Weather Cycles, Dynamic Day/Night & Atmosphere.
Validates Pydantic v2 atmospheric contracts, Whittaker biome profile presets,
celestial trajectory mechanics, physical airmass & Planckian color temperature,
photometric Lux & EV100 eye adaptation, dynamic surface weathering (wetness, puddles, snow),
and Unreal Engine 5 JSON manifest & Python automation script exports.
"""

import json
import math
import tempfile
from pathlib import Path
import pytest

from uaf.weather_atmosphere import (
    WeatherBiomeType,
    PrecipitationType,
    CloudCoveragePreset,
    Vector3D,
    ColorRGB,
    SkyAtmosphereSpec,
    ExponentialHeightFogSpec,
    VolumetricCloudSpec,
    BiomeAtmosphereProfile,
    WeatherState,
    SurfaceWeatherModifier,
    MaterialParameterCollectionSpec,
    DiurnalKeyframe,
    WeatherSystemManifest,
    BIOME_PROFILE_REGISTRY,
    get_default_biome_profile,
    create_arctic_profile,
    create_desert_profile,
    create_swamp_profile,
    create_temperate_forest_profile,
    create_cyberpunk_neon_profile,
    DayNightCycleController,
    EnvironmentalShaderBlender,
    UE5WeatherExporter,
)


class TestAcceptanceUAF81_100:

    def test_uaf81_100_contracts_and_models(self):
        """Validates Pydantic v2 contracts and vector mathematics."""
        vec = Vector3D(x=3.0, y=4.0, z=0.0)
        assert pytest.approx(vec.length(), 1e-5) == 5.0
        assert pytest.approx(vec.normalize().length(), 1e-5) == 1.0
        assert vec.dot(Vector3D(x=1.0, y=0.0, z=0.0)) == 3.0
        assert vec.to_ue5_cm().x == 300.0

        col = ColorRGB(r=0.2, g=0.5, b=0.8)
        assert col.to_tuple() == (0.2, 0.5, 0.8)
        linear = col.to_ue5_linear()
        assert linear["r"] == 0.2 and linear["a"] == 1.0

        sky = SkyAtmosphereSpec()
        assert sky.rayleigh_scale_height_km == 8.0
        assert sky.mie_anisotropy_g == 0.8

        fog = ExponentialHeightFogSpec()
        assert fog.volumetric_fog_enabled is True

        clouds = VolumetricCloudSpec()
        assert clouds.layer_bottom_altitude_km == 1.5

        weather = WeatherState(
            time_of_day_hours=14.0,
            precipitation_type=PrecipitationType.LIGHT_RAIN,
            precipitation_intensity=0.4,
            temperature_celsius=18.0,
        )
        assert weather.is_precipitating is True
        assert weather.is_freezing is False

    def test_uaf81_100_biome_atmosphere_profiles_registry(self):
        """Verifies atmospheric profiles for all 8 supported biomes."""
        assert len(BIOME_PROFILE_REGISTRY) == 8
        for biome_type in WeatherBiomeType:
            profile = get_default_biome_profile(biome_type)
            assert profile.biome == biome_type
            assert profile.sky_atmosphere.rayleigh_scale_height_km > 0.0
            assert profile.height_fog.fog_density > 0.0
            assert profile.volumetric_clouds.layer_height_km > 0.0

        arctic = create_arctic_profile()
        assert arctic.default_temperature_celsius < 0.0
        assert PrecipitationType.BLIZZARD in arctic.typical_precipitations

        desert = create_desert_profile()
        assert desert.default_temperature_celsius > 30.0
        assert desert.base_humidity < 0.25
        assert desert.sky_atmosphere.mie_scattering > 0.01  # High dust aerosol

        swamp = create_swamp_profile()
        assert swamp.base_humidity > 0.90
        assert swamp.height_fog.fog_density >= 0.05  # Dense low-lying mist

    def test_uaf81_100_celestial_trajectory_solar(self):
        """Tests solar elevation and azimuth at solar noon, sunrise, sunset, and midnight."""
        ctrl = DayNightCycleController(latitude_deg=35.0)

        # Solar noon (12:00)
        elev_noon, az_noon = ctrl.compute_sun_position(12.0)
        assert elev_noon > 55.0  # High in the sky
        assert az_noon == 180.0  # Due South in northern hemisphere

        # Midnight (0:00 / 24:00)
        elev_midnight, _ = ctrl.compute_sun_position(0.0)
        assert elev_midnight < -40.0  # Deep nadir below horizon

        # Dawn (~6:00) and Dusk (~18:00)
        elev_dawn, az_dawn = ctrl.compute_sun_position(6.0)
        assert elev_dawn > 0.0 and elev_dawn < 15.0  # Low morning sun
        assert az_dawn < 95.0  # Eastward

        elev_dusk, az_dusk = ctrl.compute_sun_position(18.0)
        assert elev_dusk > 0.0 and elev_dusk < 15.0
        assert az_dusk > 260.0  # Westward

    def test_uaf81_100_celestial_trajectory_lunar(self):
        """Tests lunar position and synodic phase progression."""
        ctrl = DayNightCycleController(latitude_deg=35.0)

        # Midnight: Sun is below horizon, moon should be high in the sky
        sun_elev, _ = ctrl.compute_sun_position(0.0)
        moon_elev, _ = ctrl.compute_moon_position(0.0)
        assert sun_elev < 0.0
        assert moon_elev > 35.0

        # Lunar phases across 29.53-day cycle
        phase_new = ctrl.compute_moon_phase(day=0.0)
        assert pytest.approx(phase_new, abs=0.01) == 0.0

        phase_full = ctrl.compute_moon_phase(day=14.765)
        assert pytest.approx(phase_full, abs=0.01) == 1.0

        phase_quarter = ctrl.compute_moon_phase(day=7.38)
        assert pytest.approx(phase_quarter, abs=0.05) == 0.5

    def test_uaf81_100_solar_and_lunar_irradiance_lux(self):
        """Validates physical photometric illuminance in Lux."""
        ctrl = DayNightCycleController()

        # Solar noon clear sky
        noon_elev, _ = ctrl.compute_sun_position(12.0)
        noon_lux = ctrl.compute_solar_lux(noon_elev)
        assert noon_lux > 70000.0 and noon_lux <= 120000.0

        # Civil twilight
        twilight_lux = ctrl.compute_solar_lux(-3.0)
        assert twilight_lux > 0.0 and twilight_lux < 500.0

        # Complete night
        night_lux = ctrl.compute_solar_lux(-10.0)
        assert night_lux == 0.0

        # Full moon illumination at zenith
        full_moon_lux = ctrl.compute_lunar_lux(elevation_deg=90.0, moon_phase=1.0)
        assert pytest.approx(full_moon_lux, abs=0.01) == 0.25

        # New moon illumination
        new_moon_lux = ctrl.compute_lunar_lux(elevation_deg=90.0, moon_phase=0.0)
        assert new_moon_lux == 0.0

    def test_uaf81_100_kelvin_to_rgb_color_temperature(self):
        """Tests Planckian locus correlated color temperature conversions."""
        ctrl = DayNightCycleController()

        # Dawn / Dusk golden hour (2200K) -> warm amber (Red heavy, minimal Blue)
        rgb_amber = ctrl.kelvin_to_rgb(2200.0)
        assert rgb_amber.r > 0.95
        assert rgb_amber.g > 0.50 and rgb_amber.g < 0.75
        assert rgb_amber.b < 0.40

        # Midday sunlight (6000K) -> balanced neutral white
        rgb_noon = ctrl.kelvin_to_rgb(6000.0)
        assert rgb_noon.r > 0.90
        assert rgb_noon.g > 0.90
        assert rgb_noon.b > 0.90

        # High sky overcast / blue hour (10000K) -> cool bluish
        rgb_blue = ctrl.kelvin_to_rgb(10000.0)
        assert rgb_blue.b == 1.0
        assert rgb_blue.r < rgb_blue.b

        # Elevation to temperature mapping
        assert ctrl.compute_sun_color_temperature(-5.0) == 2000.0
        assert ctrl.compute_sun_color_temperature(5.0) < 3500.0
        assert ctrl.compute_sun_color_temperature(70.0) > 5500.0

    def test_uaf81_100_eye_adaptation_and_ev100(self):
        """Verifies EV100 exposure math and asymmetric pupil adaptation."""
        ctrl = DayNightCycleController()

        # Sunny day (100,000 Lux) -> EV100 ~ 15.5
        ev_bright = ctrl.compute_ev100(100000.0)
        assert pytest.approx(ev_bright, abs=0.2) == 15.5

        # Overcast day (1,000 Lux) -> EV100 ~ 8.8
        ev_overcast = ctrl.compute_ev100(1000.0)
        assert pytest.approx(ev_overcast, abs=0.2) == 8.8

        # Full moon (0.1 Lux) -> EV100 ~ -4.5
        ev_night = ctrl.compute_ev100(0.1)
        assert pytest.approx(ev_night, abs=0.2) == -4.5

        # Asymmetric pupil adaptation: faster adjusting to bright than dark
        start_ev = 5.0
        bright_target = 15.0
        dark_target = 0.0
        delta_t = 0.5

        ev_adapted_up = ctrl.adapt_exposure(bright_target, start_ev, delta_t, speed_up=4.0, speed_down=1.0)
        ev_adapted_down = ctrl.adapt_exposure(dark_target, start_ev, delta_t, speed_up=4.0, speed_down=1.0)

        # Delta up should be proportionally larger than delta down due to speed_up > speed_down
        fraction_up = (ev_adapted_up - start_ev) / (bright_target - start_ev)
        fraction_down = (start_ev - ev_adapted_down) / (start_ev - dark_target)
        assert fraction_up > fraction_down

    def test_uaf81_100_weather_state_progression(self):
        """Tests day/night controller time advancement, pausing, and scaling."""
        ctrl = DayNightCycleController(initial_hour=10.0, time_scale=3600.0)  # 1 sec = 1 hour
        assert ctrl.time_of_day_hours == 10.0

        new_time = ctrl.advance_time(delta_seconds=2.0)
        assert pytest.approx(new_time, 1e-4) == 12.0

        ctrl.pause()
        paused_time = ctrl.advance_time(delta_seconds=5.0)
        assert paused_time == 12.0

        ctrl.resume()
        resumed_time = ctrl.advance_time(delta_seconds=1.0)
        assert pytest.approx(resumed_time, 1e-4) == 13.0

        # Wrapping 24h
        ctrl.set_time(23.5)
        wrapped = ctrl.advance_time(delta_seconds=1.5)
        assert pytest.approx(wrapped, 1e-4) == 1.0

    def test_uaf81_100_surface_wetness_accumulation_and_drying(self):
        """Verifies rainfall water accumulation and thermodynamic drying rates."""
        blender = EnvironmentalShaderBlender()

        # 1. Influx: Rain increases wetness
        w1 = blender.accumulate_wetness(
            current_wetness=0.0,
            precip_type=PrecipitationType.HEAVY_STORM,
            intensity=0.8,
            temperature_c=22.0,
            humidity=0.85,
            slope_deg=0.0,
            delta_s=5.0,
        )
        assert w1 > 0.40

        # 2. Drying: Hot dry desert air dries fast
        w_dry_fast = blender.accumulate_wetness(
            current_wetness=w1,
            precip_type=PrecipitationType.NONE,
            intensity=0.0,
            temperature_c=38.0,
            humidity=0.15,
            slope_deg=0.0,
            delta_s=5.0,
        )

        # 3. Drying: Cold humid swamp air dries slow
        w_dry_slow = blender.accumulate_wetness(
            current_wetness=w1,
            precip_type=PrecipitationType.NONE,
            intensity=0.0,
            temperature_c=10.0,
            humidity=0.90,
            slope_deg=0.0,
            delta_s=5.0,
        )

        assert w_dry_fast < w_dry_slow

        # 4. Slope runoff: steep surfaces drain faster
        w_steep = blender.accumulate_wetness(
            current_wetness=w1,
            precip_type=PrecipitationType.NONE,
            intensity=0.0,
            temperature_c=25.0,
            humidity=0.5,
            slope_deg=60.0,
            delta_s=5.0,
        )
        w_flat = blender.accumulate_wetness(
            current_wetness=w1,
            precip_type=PrecipitationType.NONE,
            intensity=0.0,
            temperature_c=25.0,
            humidity=0.5,
            slope_deg=0.0,
            delta_s=5.0,
        )
        assert w_steep < w_flat

    def test_uaf81_100_puddle_formation_and_normal_flattening(self):
        """Verifies thresholded puddle pooling and specular normal flattening."""
        blender = EnvironmentalShaderBlender()

        # Upward flat surface with high wetness
        cov, depth, flatten = blender.compute_puddles(wetness=0.9, normal_z=1.0, slope_deg=0.0)
        assert cov > 0.70
        assert depth > 1.0  # cm
        assert flatten > 0.65

        # Low wetness -> no puddles
        cov_dry, _, _ = blender.compute_puddles(wetness=0.2, normal_z=1.0, slope_deg=0.0)
        assert cov_dry == 0.0

        # Steep slope (40 deg) -> puddles cannot form
        cov_steep, _, _ = blender.compute_puddles(wetness=0.9, normal_z=0.76, slope_deg=40.0)
        assert cov_steep == 0.0

    def test_uaf81_100_snow_accumulation_zenith_slope_cutoff(self):
        """Verifies snow accumulation at subzero temps and cliff runoff cutoff."""
        blender = EnvironmentalShaderBlender()

        # Flat terrain under blizzard at -10°C
        snow_flat, thick_flat = blender.accumulate_snow(
            current_snow=0.0,
            precip_type=PrecipitationType.BLIZZARD,
            intensity=1.0,
            temperature_c=-10.0,
            normal_z=1.0,
            slope_deg=0.0,
            delta_s=5.0,
        )
        assert snow_flat > 0.30
        assert thick_flat > 4.0  # cm

        # Vertical cliff (slope 85°) -> snow cannot settle
        snow_cliff, thick_cliff = blender.accumulate_snow(
            current_snow=0.0,
            precip_type=PrecipitationType.BLIZZARD,
            intensity=1.0,
            temperature_c=-10.0,
            normal_z=0.08,
            slope_deg=85.0,
            delta_s=5.0,
        )
        assert snow_cliff == 0.0
        assert thick_cliff == 0.0

        # Melting above freezing (+15°C)
        melted_snow, _ = blender.accumulate_snow(
            current_snow=snow_flat,
            precip_type=PrecipitationType.NONE,
            intensity=0.0,
            temperature_c=15.0,
            normal_z=1.0,
            slope_deg=0.0,
            delta_s=5.0,
        )
        assert melted_snow < snow_flat

    def test_uaf81_100_wind_vector_and_surface_evaluation(self):
        """Verifies full surface evaluation with wind displacement and roughness changes."""
        blender = EnvironmentalShaderBlender()

        weather = WeatherState(
            precipitation_type=PrecipitationType.HEAVY_STORM,
            precipitation_intensity=0.85,
            temperature_celsius=16.0,
            relative_humidity=0.90,
            wind_vector=Vector3D(x=10.0, y=0.0, z=0.0),
        )

        flat_norm = Vector3D(x=0.0, y=0.0, z=1.0)
        pos = Vector3D(x=10.0, y=20.0, z=0.0)

        mod = blender.evaluate_surface(pos, flat_norm, weather, delta_s=6.0)

        assert mod.wetness_amount > 0.5
        assert mod.puddle_coverage > 0.4
        # Wet surface should have lowered roughness
        assert mod.roughness_multiplier < 0.6
        # Wet surface should have darkened albedo
        assert mod.albedo_darkening_factor < 0.85
        # Wind displacement vector should be directed along wind X axis
        assert mod.wind_ripple_displacement.x > 0.0

    def test_uaf81_100_material_parameter_collection_compilation(self):
        """Verifies MaterialParameterCollectionSpec generation for UE5 MPC_Weather."""
        blender = EnvironmentalShaderBlender()
        ctrl = DayNightCycleController(initial_hour=12.0)
        profile = create_temperate_forest_profile()
        weather = WeatherState(
            time_of_day_hours=12.0,
            precipitation_type=PrecipitationType.LIGHT_RAIN,
            precipitation_intensity=0.3,
            wind_vector=Vector3D(x=6.0, y=2.0, z=0.0),
        )

        mpc = blender.compile_mpc_parameters(weather, ctrl, profile)
        assert mpc.collection_name == "MPC_Weather"

        # Check required scalar keys
        required_scalars = [
            "Weather_Wetness",
            "Weather_PuddleAmount",
            "Weather_SnowAmount",
            "Weather_WindSpeed",
            "Weather_RainIntensity",
            "Weather_TemperatureC",
            "Weather_SunLux",
            "Weather_MoonLux",
            "Weather_EV100",
            "Weather_FogDensity",
        ]
        for key in required_scalars:
            assert key in mpc.scalar_parameters

        # Check required vector keys
        required_vectors = [
            "Weather_WindDirection",
            "Weather_SunDirection",
            "Weather_SunColor",
            "Weather_MoonDirection",
            "Weather_MoonColor",
            "Weather_FogColor",
        ]
        for key in required_vectors:
            assert key in mpc.vector_parameters
            assert len(mpc.vector_parameters[key]) == 4

    def test_uaf81_100_diurnal_curve_track_export(self):
        """Verifies generation and serialization of 24-hour float curve channels."""
        ctrl = DayNightCycleController()
        track = ctrl.generate_diurnal_track(steps_per_hour=2)
        assert len(track) == 48  # 48 keyframes

        exporter = UE5WeatherExporter()
        with tempfile.TemporaryDirectory() as tmpdir:
            out_p = Path(tmpdir)
            curve_file = exporter.export_diurnal_curve_tracks(track, out_p)
            assert curve_file.exists()

            with open(curve_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert data["total_keyframes"] == 48
            assert "sun_elevation_deg" in data["channels"]
            assert "sun_lux" in data["channels"]
            assert "ev100" in data["channels"]

    def test_uaf81_100_ue5_exporter_manifest_and_script(self):
        """Verifies complete manifest export and UE5 Editor automation python script."""
        profile = create_cyberpunk_neon_profile()
        ctrl = DayNightCycleController(initial_hour=21.0)
        track = ctrl.generate_diurnal_track(steps_per_hour=1)
        blender = EnvironmentalShaderBlender()
        weather = WeatherState(
            time_of_day_hours=21.0,
            precipitation_type=PrecipitationType.LIGHT_RAIN,
            precipitation_intensity=0.5,
            temperature_celsius=17.0,
        )
        mpc = blender.compile_mpc_parameters(weather, ctrl, profile)

        manifest = WeatherSystemManifest(
            manifest_id="weather_neon_01",
            active_biome=profile.biome,
            atmosphere_profile=profile,
            initial_weather=weather,
            diurnal_track=track,
            mpc_spec=mpc,
            ue5_version="5.4",
        )

        exporter = UE5WeatherExporter()
        with tempfile.TemporaryDirectory() as tmpdir:
            out_p = Path(tmpdir)
            exported = exporter.export_all(manifest, out_p)

            assert exported["manifest"].exists()
            assert exported["curves"].exists()
            assert exported["script"].exists()

            # Inspect python script syntax
            script_text = exported["script"].read_text(encoding="utf-8")
            assert "import unreal" in script_text
            assert "SkyAtmosphere" in script_text
            assert "DirectionalLight_Sun" in script_text
            assert "ExponentialHeightFog" in script_text
            assert "VolumetricCloud" in script_text

    def test_uaf81_100_end_to_end_biome_weather_cycle(self):
        """Full end-to-end integration across entire diurnal weather cycle."""
        biome = WeatherBiomeType.ARCTIC
        profile = get_default_biome_profile(biome)
        ctrl = DayNightCycleController(initial_hour=6.0, time_scale=60.0, latitude_deg=70.0)
        blender = EnvironmentalShaderBlender()

        # Step through 24 hours in discrete 1-hour simulation increments
        total_hours = 24
        weather_states = []
        surface = None
        flat_normal = Vector3D(x=0.0, y=0.0, z=1.0)

        for step in range(total_hours):
            ctrl.advance_time(delta_seconds=60.0)  # 60s at 60x = 3600s = 1h
            h = ctrl.time_of_day_hours

            # Arctic blizzard during night, clear cold during midday
            is_night = h < 6.0 or h > 18.0
            precip = PrecipitationType.BLIZZARD if is_night else PrecipitationType.NONE
            intensity = 0.9 if is_night else 0.0

            state = WeatherState(
                time_of_day_hours=round(h, 2),
                precipitation_type=precip,
                precipitation_intensity=intensity,
                temperature_celsius=-15.0 if is_night else -5.0,
                relative_humidity=0.85,
                wind_vector=Vector3D(x=12.0, y=4.0, z=0.0),
            )
            weather_states.append(state)

            surface = blender.evaluate_surface(
                world_pos=Vector3D(x=0, y=0, z=0),
                normal=flat_normal,
                weather=state,
                current_surface=surface,
                delta_s=10.0,
            )

        # In arctic subzero conditions, snow coverage must be high
        assert surface.snow_coverage > 0.5
        assert surface.snow_thickness_cm > 5.0
        assert surface.wetness_amount == 0.0  # Completely frozen
