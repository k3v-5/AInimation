"""
Comprehensive Acceptance Test Suite for UAF-81.85:
Universal Runtime Dynamic Lighting, Shadowing, Atmosphere & Post-Process System.

Validates all 14 normative sub-phases:
- 81.85.0 — Core Contracts, Photometric Models, Enums & Numeric Security
- 81.85.1 — Dynamic Light Types & Light Management
- 81.85.2 — Shadow System (CSM, Shadow Atlas, Contact Shadows)
- 81.85.3 — Global / Ambient Illumination & Probes
- 81.85.4 — Sky, Sun, Moon & Astronomical Day/Night Cycle
- 81.85.5 — Atmosphere, Fog & Volumetric Lighting
- 81.85.6 — Clouds & Weather Lighting Integration
- 81.85.7 — Exposure, HDR, Tone Mapping & Color Management
- 81.85.8 — Post-Process Stack & Priority Volume Blending
- 81.85.9 — Lighting LOD, Culling & 7-Step Budget Degradation
- 81.85.10 — Materials, VFX, World Streaming & Fail-Safe Isolation
- 81.85.11 — Unreal Engine 5 Bridge & Compatibility Audit
- 81.85.12 — Checkpoints, Replay Engine & Canonical SHA-256 State Hashing
- 81.85.13 — Golden Lighting Certification & 10,000 Light Stress Test
"""

import math
import json
import pytest
from typing import List, Tuple

from uaf.runtime_lighting import (
    LightId,
    ShadowCasterId,
    PostProcessVolumeId,
    ProbeId,
    LightType,
    LightMobility,
    LightPriority,
    ShadowBackend,
    FogType,
    VolumetricQuality,
    ToneMapperType,
    ExposureMode,
    AOBackend,
    UpdateFrequency,
    FallbackLevel,
    WeatherCondition,
    ensure_finite_scalar,
    ensure_finite_vec3,
    ensure_finite_vec4,
    normalize_vec3,
    kelvin_to_rgb,
    ev100_to_luminance,
    luminance_to_ev100,
    lumens_to_candelas,
    candelas_to_lumens,
    Light,
    PointLight,
    SpotLight,
    DirectionalLight,
    RectAreaLight,
    DiskAreaLight,
    LineAreaLight,
    CSMCalculator,
    CascadeSlice,
    ShadowAtlas,
    AtlasTile,
    ShadowRequest,
    ShadowResult,
    CSMShadowProvider,
    AtlasShadowProvider,
    ReferenceShadowProvider,
    ContactShadowEvaluator,
    IrradianceProbe,
    ReflectionProbe,
    LightProbeGrid,
    AmbientLighting,
    StaticBakePipeline,
    Sun,
    Moon,
    DayPeriod,
    EphemerisData,
    DayNightController,
    SkySystem,
    AtmosphereScattering,
    FogSystem,
    VolumetricSystem,
    CloudSystem,
    WeatherSystem,
    WeatherPreset,
    WEATHER_PRESETS,
    ExposureSettings,
    ToneMapper,
    ColorGradingSettings,
    LUT3D,
    BloomSettings,
    AOSettings,
    DOFSettings,
    MotionBlurSettings,
    LensSettings,
    PostProcessSettings,
    PostProcessVolume,
    PostProcessStack,
    SimpleFrustum,
    LightCuller,
    LightingLODManager,
    BudgetManager,
    LightingBudgets,
    DegradationStep,
    LightingProfiler,
    LightingProfileFrame,
    LightingValidator,
    LightingValidationReport,
    LightingCrashRecovery,
    LightingSnapshot,
    LightingEvent,
    LightingReplayEngine,
    LightingWorld,
    GoldenLightingPresets,
)

from uaf.adapters.ue5.lighting import (
    UE5LightExporter,
    UE5AtmosphereExporter,
    UE5FogExporter,
    UE5PostProcessExporter,
    UE5LightingValidator,
    UE5LightingCompatibilityReport,
    UE5LightingLiveReloader,
    UE5LiveUpdatePacket,
)


# ===========================================================================
# 81.85.0 — Core Contracts, Photometry & Numeric Security
# ===========================================================================

def test_identifiers_immutability():
    lid1 = LightId("light_001")
    lid2 = LightId("light_001")
    lid3 = LightId("light_002")
    assert lid1 == lid2
    assert lid1 != lid3
    assert str(lid1) == "light_001"
    with pytest.raises(AttributeError):
        lid1.value = "mutated"  # type: ignore


def test_numeric_security_sanitization():
    # NaN and Inf handling
    assert ensure_finite_scalar(float("nan"), "test", 10.0) == 10.0
    assert ensure_finite_scalar(float("inf"), "test", 5.0) == 5.0
    assert ensure_finite_scalar(42.5, "test", 0.0) == 42.5

    # Vec3 sanitization
    v = ensure_finite_vec3((float("nan"), 1.0, float("-inf")), "vec", (0.0, 0.0, 0.0))
    assert v == (0.0, 1.0, 0.0)

    # Normalize zero-vector safety
    norm_zero = normalize_vec3((0.0, 0.0, 0.0))
    assert norm_zero == (0.0, 1.0, 0.0)


def test_kelvin_to_linear_rgb_conversion():
    # Warm candle/fire (1800K) -> strong red, low blue
    warm_rgb = kelvin_to_rgb(1800.0)
    assert warm_rgb[0] > warm_rgb[1] > warm_rgb[2]

    # Daylight standard (6500K) -> balanced neutral white
    noon_rgb = kelvin_to_rgb(6500.0)
    assert abs(noon_rgb[0] - noon_rgb[1]) < 0.2
    assert abs(noon_rgb[1] - noon_rgb[2]) < 0.2

    # High Kelvin sky light (12000K) -> prominent blue
    cool_rgb = kelvin_to_rgb(12000.0)
    assert cool_rgb[2] > cool_rgb[0]


def test_photometric_unit_conversions():
    # Lumens <-> Candela for isotropic sphere (4*pi sr)
    candelas = 100.0
    lumens = candelas_to_lumens(candelas)
    assert round(lumens, 2) == round(100.0 * 4.0 * math.pi, 2)
    assert round(lumens_to_candelas(lumens), 2) == candelas

    # EV100 <-> Luminance
    ev = 10.0
    lum = ev100_to_luminance(ev)
    assert lum > 0.0
    assert round(luminance_to_ev100(lum), 2) == ev


# ===========================================================================
# 81.85.1 — Dynamic Light Types & Light Management
# ===========================================================================

def test_dynamic_light_types_and_properties():
    # Directional Light
    dir_light = DirectionalLight(
        light_id=LightId("sun"),
        direction=(0.0, -1.0, 0.0),
        intensity=100000.0,
        sun_angular_diameter=0.53,
        cascade_count=4,
    )
    assert dir_light.light_type == LightType.DIRECTIONAL
    assert dir_light.cascade_count == 4

    # Point Light
    pt_light = PointLight(
        light_id=LightId("lamp"),
        position=(1.0, 2.0, 3.0),
        intensity=1500.0,
        range=10.0,
        source_radius=0.1,
    )
    assert pt_light.light_type == LightType.POINT
    assert pt_light.source_radius == 0.1

    # Spot Light with cone attenuation
    spot = SpotLight(
        light_id=LightId("torch"),
        position=(0.0, 5.0, 0.0),
        inner_cone_angle=15.0,
        outer_cone_angle=45.0,
    )
    assert spot.light_type == LightType.SPOT
    # Check cone falloff evaluation
    # Center axis (cos=1.0) -> full intensity
    assert spot.evaluate_spot_factor(1.0) == 1.0
    # Outside outer cone (cos < cos(45 deg)) -> 0.0
    assert spot.evaluate_spot_factor(math.cos(math.radians(60.0))) == 0.0
    # Between inner and outer -> smooth blend
    mid_cos = math.cos(math.radians(30.0))
    factor = spot.evaluate_spot_factor(mid_cos)
    assert 0.0 < factor < 1.0

    # Area Lights
    rect = RectAreaLight(light_id=LightId("panel"), source_width=2.0, source_height=1.0)
    assert rect.light_type == LightType.RECT_AREA
    assert rect.source_width == 2.0


def test_light_attachment_hierarchy():
    world = LightingWorld()
    pt = PointLight(light_id=LightId("gun_flash"), position=(0.0, 1.0, 0.0))
    world.create_light(pt)

    assert world.attach_light(LightId("gun_flash"), "HeroCharacter", "MuzzleSocket")
    light = world.get_light(LightId("gun_flash"))
    assert light is not None
    assert light.attached_to == "HeroCharacter"
    assert light.socket_name == "MuzzleSocket"

    assert world.detach_light(LightId("gun_flash"))
    assert light.attached_to is None


# ===========================================================================
# 81.85.2 — Shadow System (CSM, Shadow Atlas, Contact Shadows)
# ===========================================================================

def test_cascaded_shadow_maps_splits_and_slices():
    # 4 cascades between 0.1m and 200m
    splits = CSMCalculator.compute_splits(near_z=0.1, far_z=200.0, cascade_count=4, lambda_factor=0.8)
    assert len(splits) == 5  # 4 cascades + far
    assert splits[0] == 0.1
    assert splits[-1] == 200.0
    # Increasing cascade distance
    for i in range(len(splits) - 1):
        assert splits[i] < splits[i + 1]

    slices = CSMCalculator.calculate_slices(
        camera_fov_rad=math.radians(60.0),
        aspect_ratio=1.777,
        camera_pos=(0.0, 1.7, 0.0),
        camera_forward=(0.0, 0.0, -1.0),
        splits=splits,
        shadow_map_resolution=1024,
    )
    assert len(slices) == 4
    # Bounding radius expands with each cascade
    for i in range(3):
        assert slices[i].bounding_radius < slices[i + 1].bounding_radius


def test_shadow_atlas_allocation_and_eviction():
    atlas = ShadowAtlas(size=1024, bytes_per_pixel=4)
    # Total memory = 1024 * 1024 * 4 = 4 MB
    assert atlas.total_memory_bytes == 4 * 1024 * 1024

    # Allocate 3 critical lights of size 512
    t1 = atlas.allocate(LightId("boss_light_1"), 512, LightPriority.CRITICAL, frame=1)
    t2 = atlas.allocate(LightId("boss_light_2"), 512, LightPriority.CRITICAL, frame=1)
    t3 = atlas.allocate(LightId("boss_light_3"), 512, LightPriority.CRITICAL, frame=1)
    assert t1 is not None and t2 is not None and t3 is not None

    # Allocate 1 cosmetic light of size 512 filling the 4th quadrant
    t4 = atlas.allocate(LightId("particle_spark"), 512, LightPriority.COSMETIC, frame=1)
    assert t4 is not None

    # Atlas is now completely filled (4 * 512x512 = 1024x1024)
    assert atlas.allocated_memory_bytes == atlas.total_memory_bytes

    # Requesting another 512 block for a GAMEPLAY light must evict the COSMETIC light
    t5 = atlas.allocate(LightId("player_flashlight"), 512, LightPriority.GAMEPLAY, frame=2)
    assert t5 is not None
    # Verify cosmetic light was evicted
    assert "particle_spark" not in atlas.allocated_tiles
    assert "player_flashlight" in atlas.allocated_tiles
    assert "boss_light_1" in atlas.allocated_tiles


def test_contact_shadows_evaluator():
    # Inside contact distance (< 0.05m) -> occluded
    assert ContactShadowEvaluator.evaluate_contact(0.01, max_length=0.05) == 0.0
    # Beyond max contact length -> unoccluded (1.0)
    assert ContactShadowEvaluator.evaluate_contact(0.10, max_length=0.05) == 1.0


# ===========================================================================
# 81.85.3 — Global / Ambient Illumination & Probes
# ===========================================================================

def test_spherical_harmonics_irradiance_probe():
    # Probe with uniform ambient L0
    probe = IrradianceProbe(
        probe_id=ProbeId("probe_0"),
        position=(0.0, 0.0, 0.0),
        sh_coefficients=[(0.5, 0.5, 0.5)] + [(0.0, 0.0, 0.0)] * 8,
    )
    up_irr = probe.evaluate_direction((0.0, 1.0, 0.0))
    assert up_irr[0] > 0.0
    down_irr = probe.evaluate_direction((0.0, -1.0, 0.0))
    # Since L1 is zero, L0 gives isotropic spherical response
    assert abs(up_irr[0] - down_irr[0]) < 1e-4


def test_light_probe_grid_sampling():
    grid = LightProbeGrid(origin=(-10.0, 0.0, -10.0), spacing=5.0, grid_dims=(5, 3, 5))
    sample = grid.sample_irradiance((0.0, 2.0, 0.0), (0.0, 1.0, 0.0))
    assert len(sample) == 3
    assert sample[0] > 0.0


def test_static_bake_pipeline_validation():
    bake = StaticBakePipeline(target_texel_density=32.0)
    # Failed bake due to overlapping UVs
    res_fail = bake.bake_scene("test_room", 10, 5, uv_overlap=True)
    assert not res_fail.is_valid
    assert len(res_fail.errors) > 0

    # Successful bake
    res_ok = bake.bake_scene("test_room", 10, 5, uv_overlap=False)
    assert res_ok.is_valid
    assert len(res_ok.cache_hash) == 64


# ===========================================================================
# 81.85.4 — Sky, Sun, Moon & Astronomical Ephemeris
# ===========================================================================

def test_day_night_controller_ephemeris():
    controller = DayNightController(latitude_deg=34.0, longitude_deg=-118.0)

    # Noon (12:00) -> sun high above horizon
    noon_eph = controller.set_time_of_day(12.0)
    assert noon_eph.sun_elevation_deg > 60.0
    assert noon_eph.period == DayPeriod.NOON
    assert noon_eph.sun_direction[1] < 0.0  # Light travels downwards

    # Midnight (00:00) -> sun below horizon, moon above
    night_eph = controller.set_time_of_day(0.0)
    assert night_eph.sun_elevation_deg < -30.0
    assert night_eph.period == DayPeriod.NIGHT
    assert night_eph.moon_elevation_deg > 0.0


def test_lunar_phase_and_irradiance():
    moon = Moon(phase=0.5, intensity=0.25)  # Full moon
    assert moon.phase_illumination_fraction == 1.0
    assert moon.get_lunar_irradiance(90.0) == 0.25

    moon_new = Moon(phase=0.0, intensity=0.25)  # New moon
    assert moon_new.phase_illumination_fraction == 0.0
    assert moon_new.get_lunar_irradiance(90.0) == 0.0


def test_sky_system_radiance_evaluation():
    sky = SkySystem()
    sky.controller.set_time_of_day(12.0)
    eph = sky.update(0.0)
    assert sky.sun.intensity > 50000.0

    # Zenith sky radiance is bright blue
    zenith_color = sky.evaluate_sky_radiance((0.0, 1.0, 0.0))
    assert zenith_color[2] > zenith_color[0]  # Blue > Red


# ===========================================================================
# 81.85.5 — Atmosphere, Fog & Volumetric Lighting
# ===========================================================================

def test_atmosphere_rayleigh_and_mie():
    atmo = AtmosphereScattering()
    # Rayleigh phase is symmetric forward/backward (cos^2)
    assert atmo.evaluate_rayleigh_phase(1.0) == atmo.evaluate_rayleigh_phase(-1.0)

    # Mie forward scattering is much stronger forward than backward
    forward_mie = atmo.evaluate_mie_phase(1.0)
    backward_mie = atmo.evaluate_mie_phase(-1.0)
    assert forward_mie > backward_mie * 5.0

    # Optical transmittance over 10 km
    trans = atmo.evaluate_transmittance(10000.0, 0.0)
    assert 0.0 < trans[0] < 1.0
    # Red light transmits better than blue light (blue is scattered more)
    assert trans[0] > trans[2]


def test_exponential_height_fog_integration():
    fog = FogSystem(density=0.02, height_falloff=0.05, height=0.0)
    # Horizontal ray at sea level
    transmission, inscatter = fog.evaluate_fog_factor(
        ray_origin=(0.0, 0.0, 0.0),
        ray_dir=(0.0, 0.0, 1.0),
        ray_length=100.0,
    )
    assert 0.0 < transmission < 1.0
    assert inscatter[0] > 0.0


def test_volumetric_lighting_raymarching():
    vol = VolumetricSystem(quality=VolumetricQuality.MEDIUM)
    pt = PointLight(
        light_id=LightId("v_light"),
        position=(0.0, 0.0, 5.0),
        intensity=5000.0,
        range=10.0,
        affect_volumetrics=True,
    )
    # Ray passing directly through light position
    inscatter = vol.evaluate_volumetric_inscattering(
        ray_origin=(0.0, 0.0, 0.0),
        ray_dir=(0.0, 0.0, 1.0),
        ray_length=10.0,
        lights=[pt],
    )
    assert inscatter[0] > 0.0
    assert inscatter[1] > 0.0


# ===========================================================================
# 81.85.6 — Clouds & Weather Lighting Integration
# ===========================================================================

def test_clouds_wind_advection_and_occlusion():
    clouds = CloudSystem(coverage=0.8, density=1.0, wind_velocity=(10.0, 0.0, 0.0))
    clouds.update(1.0)
    assert clouds.wind_offset[0] == 10.0

    # Sun occlusion under dense clouds
    occlusion = clouds.evaluate_sun_occlusion((0.0, -1.0, 0.0))
    assert occlusion < 0.2


def test_weather_system_transition():
    weather = WeatherSystem(initial_condition=WeatherCondition.CLEAR)
    clouds = CloudSystem()
    fog = FogSystem()

    # Start transition to STORM
    weather.set_weather(WeatherCondition.STORM, transition_time=2.0)
    weather.tick(1.0, clouds, fog)  # Halfway
    assert 0.1 < clouds.coverage < 1.0

    weather.tick(1.0, clouds, fog)  # Completed
    assert weather.current_condition == WeatherCondition.STORM
    assert clouds.coverage == 1.0
    assert fog.density == WEATHER_PRESETS[WeatherCondition.STORM].fog_density


# ===========================================================================
# 81.85.7 — Exposure, HDR, Tone Mapping & Color Management
# ===========================================================================

def test_exposure_adaptation():
    exp = ExposureSettings(mode=ExposureMode.AUTOMATIC, adaptation_speed_up=4.0)
    exp.current_ev100 = 5.0
    # Scene gets very bright (high luminance)
    scale = exp.evaluate_exposure(scene_average_luminance=10000.0, dt=0.5)
    # Adaptation increases EV100
    assert exp.current_ev100 > 5.0
    assert scale > 0.0


def test_tone_mappers():
    hdr_color = (5.0, 10.0, 20.0)  # Super-bright HDR values

    # ACES filmic maps gracefully to [0, 1]
    aces = ToneMapper.map_color(hdr_color, ToneMapperType.ACES)
    assert 0.0 <= aces[0] <= 1.0
    assert 0.0 <= aces[1] <= 1.0
    assert 0.0 <= aces[2] <= 1.0

    # Reinhard maps gracefully
    reinhard = ToneMapper.map_color(hdr_color, ToneMapperType.NEUTRAL)
    assert 0.0 <= reinhard[0] < 1.0


def test_color_grading_and_lut3d():
    cg = ColorGradingSettings(saturation=1.5, contrast=1.2)
    graded = cg.apply((0.2, 0.4, 0.8))
    assert len(graded) == 3

    # 3D LUT identity test
    lut = LUT3D(size=16)
    sampled = lut.sample(0.5, 0.5, 0.5)
    assert abs(sampled[0] - 0.5) < 0.05
    assert abs(sampled[1] - 0.5) < 0.05
    assert abs(sampled[2] - 0.5) < 0.05


# ===========================================================================
# 81.85.8 — Post-Process Stack & Priority Volumes
# ===========================================================================

def test_bloom_prefilter():
    bloom = BloomSettings(threshold=2.0, intensity=1.0)
    # Sub-threshold light yields 0 bloom
    assert bloom.evaluate_prefilter((0.5, 0.5, 0.5)) == (0.0, 0.0, 0.0)
    # Super-threshold yields positive bloom
    assert bloom.evaluate_prefilter((5.0, 5.0, 5.0))[0] > 0.0


def test_circle_of_confusion_dof():
    dof = DOFSettings(enabled=True, focus_distance=5.0, focal_length=50.0, aperture_f_stop=2.8)
    # On focal plane -> 0 blur
    assert dof.calculate_coc(5.0) == 0.0
    # Far away -> non-zero circle of confusion
    assert dof.calculate_coc(50.0) > 0.0


def test_post_process_volume_priority_blending():
    stack = PostProcessStack()

    # Base volume (low priority, saturation = 1.0)
    base_vol = PostProcessVolume(
        volume_id=PostProcessVolumeId("base"),
        is_unbound=True,
        priority=0.0,
        settings=PostProcessSettings(),
    )
    base_vol.settings.color_grading.saturation = 1.0
    stack.add_volume(base_vol)

    # Local volume (high priority, saturation = 2.0, located at (10, 0, 0))
    local_vol = PostProcessVolume(
        volume_id=PostProcessVolumeId("cave_override"),
        is_unbound=False,
        priority=10.0,
        position=(10.0, 0.0, 0.0),
        extents=(5.0, 5.0, 5.0),
        blend_radius=2.0,
        settings=PostProcessSettings(),
    )
    local_vol.settings.color_grading.saturation = 2.0
    stack.add_volume(local_vol)

    # Camera at (0, 0, 0) -> outside local volume, gets saturation ~1.0
    s_outside = stack.resolve_effective_settings((0.0, 0.0, 0.0))
    assert abs(s_outside.color_grading.saturation - 1.0) < 0.05

    # Camera at (10, 0, 0) -> inside local volume, gets saturation ~2.0
    s_inside = stack.resolve_effective_settings((10.0, 0.0, 0.0))
    assert abs(s_inside.color_grading.saturation - 2.0) < 0.05


# ===========================================================================
# 81.85.9 — Lighting LOD, Culling & 7-Step Budget Degradation
# ===========================================================================

def test_frustum_light_culler():
    frustum = SimpleFrustum(
        position=(0.0, 1.7, 0.0),
        forward=(0.0, 0.0, -1.0),
        fov_rad=math.radians(60.0),
        aspect_ratio=1.777,
    )
    # Light in front
    front_light = PointLight(light_id=LightId("front"), position=(0.0, 1.7, -10.0), range=5.0)
    # Light behind camera
    back_light = PointLight(light_id=LightId("back"), position=(0.0, 1.7, 10.0), range=5.0)

    visible = LightCuller.cull_lights([front_light, back_light], frustum)
    assert front_light in visible
    assert back_light not in visible


def test_budget_manager_7_step_degradation():
    bm = BudgetManager(budgets=LightingBudgets(max_dynamic_lights=10, max_shadow_maps=4))

    # Overload scene with 30 lights
    lights = [
        PointLight(
            light_id=LightId(f"l_{i}"),
            cast_shadows=True,
            priority=LightPriority.COSMETIC if i >= 10 else LightPriority.GAMEPLAY,
        )
        for i in range(30)
    ]

    step = bm.evaluate_pressure(
        active_light_count=len(lights),
        active_shadow_count=len(lights),
        shadow_memory_bytes=200 * 1024 * 1024,
        estimated_frame_ms=25.0,
    )
    assert step > DegradationStep.NONE

    # Apply degradation -> cosmetic lights should be culled
    filtered = bm.apply_degradation(lights)
    assert len(filtered) < len(lights)
    assert not any(l.priority == LightPriority.COSMETIC for l in filtered)


# ===========================================================================
# 81.85.10 — World Integration, Streaming & Fail-Safe Isolation
# ===========================================================================

def test_streaming_cell_registration_and_symmetric_unload():
    world = LightingWorld()
    cell_lights = [
        PointLight(light_id=LightId("cell_l1"), position=(10.0, 0.0, 10.0)),
        PointLight(light_id=LightId("cell_l2"), position=(12.0, 0.0, 10.0)),
    ]
    world.register_streaming_cell("Cell_1_1", cell_lights)
    assert world.get_light(LightId("cell_l1")) is not None
    assert world.get_light(LightId("cell_l2")) is not None

    # Unload cell
    world.unload_streaming_cell("Cell_1_1")
    assert world.get_light(LightId("cell_l1")) is None
    assert world.get_light(LightId("cell_l2")) is None
    assert "Cell_1_1" not in world.streaming_cell_resources


def test_fail_safe_crash_recovery_isolation():
    world = LightingWorld()
    # Simulate corrupted state or exception handling in world.tick
    rec = world.recovery
    assert rec.current_level == FallbackLevel.FULL

    rec.trigger_fallback(FallbackLevel.EMERGENCY)
    assert rec.current_level == FallbackLevel.EMERGENCY
    assert rec.fault_count == 1

    emergency_lights = rec.get_emergency_lights()
    assert len(emergency_lights) == 1
    assert emergency_lights[0].priority == LightPriority.CRITICAL


# ===========================================================================
# 81.85.11 — Unreal Engine 5 Bridge & Compatibility Audit
# ===========================================================================

def test_ue5_manifest_export_and_compatibility():
    sun = DirectionalLight(
        light_id=LightId("ue_sun"),
        direction=(0.0, -0.7071, -0.7071),
        intensity=100000.0,
        cascade_count=4,
    )
    manifest = UE5LightExporter.export_light(sun)
    assert manifest["component_class"] == "UDirectionalLightComponent"
    assert manifest["num_dynamic_shadow_cascades"] == 4
    assert manifest["intensity"] == 100000.0

    # PostProcess export
    pps = PostProcessSettings()
    pp_manifest = UE5PostProcessExporter.export_settings(pps)
    assert pp_manifest["dynamic_global_illumination_method"] == "EDynamicGlobalIlluminationMethod::Lumen"
    assert pp_manifest["reflection_method"] == "EReflectionMethod::Lumen"

    # Compatibility Audit
    world = LightingWorld()
    world.create_light(sun)
    report = UE5LightingValidator.audit_world(world)
    assert report.is_compatible
    assert "DirectionalLight" in report.supported_features


def test_ue5_live_reloader():
    world = LightingWorld()
    reloader = UE5LightingLiveReloader()

    l1 = PointLight(light_id=LightId("p1"), position=(0.0, 0.0, 0.0), intensity=1000.0)
    world.create_light(l1)

    # Initial frame delta
    d1 = reloader.compute_delta(world)
    assert len(d1.added_lights) == 1
    assert d1.added_lights[0]["actor_name"] == "LightActor_p1"

    # Modify light
    l1.intensity = 2000.0
    d2 = reloader.compute_delta(world)
    assert len(d2.updated_lights) == 1

    # Remove light
    world.destroy_light(LightId("p1"))
    d3 = reloader.compute_delta(world)
    assert "p1" in d3.removed_light_ids


# ===========================================================================
# 81.85.12 — Checkpoints, Replay Engine & Canonical SHA-256 State Hashing
# ===========================================================================

def test_deterministic_snapshots_and_checkpoints():
    world = LightingWorld()
    world.sky.controller.set_time_of_day(14.0)
    world.create_light(PointLight(light_id=LightId("pt_a"), position=(5.0, 2.0, 5.0), intensity=2000.0))
    world.create_light(DirectionalLight(light_id=LightId("sun_a"), intensity=80000.0))

    snap1 = world.capture_snapshot()
    hash1 = snap1.canonical_hash
    assert len(hash1) == 64

    # Duplicate world with exact same state must produce identical hash
    world2 = LightingWorld()
    world2.restore_snapshot(snap1)
    snap2 = world2.capture_snapshot()
    assert snap2.canonical_hash == hash1


def test_lighting_replay_engine():
    engine = LightingReplayEngine()
    engine.record(frame=1, timestamp=0.016, event_type="LightCreated", payload={"light_id": "torch"})
    engine.record(frame=2, timestamp=0.033, event_type="WeatherChanged", payload={"condition": "STORM"})

    log_json = engine.export_replay_log()
    assert "torch" in log_json
    assert "STORM" in log_json

    # Restore in new engine
    engine2 = LightingReplayEngine()
    engine2.load_replay_log(log_json)
    assert len(engine2.recorded_events) == 2
    assert engine2.recorded_events[1].event_type == "WeatherChanged"


# ===========================================================================
# 81.85.13 — Golden Lighting Certification & Stress Test
# ===========================================================================

def test_14_golden_lighting_scenarios():
    world = LightingWorld()
    golden_names = [
        "day",
        "night",
        "dawn",
        "sunset",
        "interior",
        "exterior",
        "cave",
        "storm",
        "fog",
        "high_density_lights",
        "high_shadow_load",
        "vfx_heavy_scene",
        "streaming_transition",
        "desert_sandstorm",
    ]

    for name in golden_names:
        GoldenLightingPresets.apply_preset(world, name)
        # Advance simulation tick
        snap = world.tick(0.016)
        assert snap is not None
        assert len(snap.canonical_hash) == 64
        # Validate profile frame recorded
        latest = world.profiler.latest_frame
        assert latest is not None
        assert latest.total_cpu_ms > 0.0


def test_stress_test_10000_dynamic_lights():
    world = LightingWorld()
    # Configure relaxed budget for stress test verification
    world.budget_manager.budgets = LightingBudgets(max_dynamic_lights=10000, max_shadow_maps=1000)

    # Instantiate 10,000 lights across a 1000x1000m terrain
    for i in range(10000):
        gx = (i % 100) * 10.0 - 500.0
        gz = (i // 100) * 10.0 - 500.0
        l = PointLight(
            light_id=LightId(f"stress_light_{i}"),
            position=(gx, 1.5, gz),
            range=15.0,
            intensity=500.0,
            cast_shadows=(i < 1000),  # 1,000 shadow casters
            priority=LightPriority.COSMETIC if i >= 100 else LightPriority.GAMEPLAY,
        )
        world.lights[l.light_id.value] = l

    assert len(world.lights) == 10000

    # Frustum cull and simulate frame
    cam_pos = (0.0, 10.0, 0.0)
    snap = world.tick(0.016, camera_pos=cam_pos)
    assert snap is not None
    assert len(snap.canonical_hash) == 64

    # Verify profiler recorded frame with culled subset
    latest = world.profiler.latest_frame
    assert latest is not None
    assert latest.active_light_count < 10000  # Verified culling works at scale

    # Clean teardown
    world.lights.clear()
    assert len(world.lights) == 0
