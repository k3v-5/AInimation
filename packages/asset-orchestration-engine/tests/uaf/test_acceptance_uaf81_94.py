"""
UAF-81.94: Procedural Interactive Audio, Spatial Acoustics & MetaSounds
Acceptance Test Suite.
Verifies Quartz musical quantization clock, equal-power stem crossfading,
analytical Sabine/Eyring acoustic RT60, axial resonance modes, topological diffraction,
closed-door transmission loss, 3D spatial attenuation conforming to Rule 10,
and Unreal Engine 5 MetaSounds / USoundAttenuation export.
"""

import json
import math
import pytest
from typing import Dict

from uaf.interactive_audio import (
    AcousticMaterial,
    StemRole,
    QuantizationSubdivision,
    OcclusionState,
    AttenuationCurveType,
    MATERIAL_ABSORPTION_TABLE,
    MaterialAbsorption,
    RoomAcousticProfile,
    AudioStem,
    SpatialAttenuationProfile,
    AcousticRaycastResult,
    QuartzQuantizationClock,
    AdaptiveMusicOrchestrator,
    SabineEyringAcousticCalculator,
    TopologicalAcousticDiffraction,
    SpatialAttenuationCalculator,
    MetaSoundNodeSchema,
    UE5MetaSoundsGraphManifest,
    UE5MetaSoundsExporter,
)
from uaf.level_design.core.contracts import PacingPhase


class TestQuartzQuantizationClock:
    """Verifies rhythmic clock accuracy and quantization grid boundary calculation."""

    def test_clock_intervals(self):
        clock = QuartzQuantizationClock(bpm=120.0, beats_per_bar=4)
        assert math.isclose(clock.seconds_per_beat, 0.5, abs_tol=1e-3)
        assert math.isclose(clock.seconds_per_bar, 2.0, abs_tol=1e-3)

        clock.advance_time(1.25)
        assert math.isclose(clock.current_time_seconds, 1.25, abs_tol=1e-3)
        assert math.isclose(clock.current_beat, 2.5, abs_tol=1e-3)
        assert clock.current_bar == 0

    def test_quantized_next_timestamps(self):
        clock = QuartzQuantizationClock(bpm=120.0, beats_per_bar=4)
        clock.advance_time(1.25)  # halfway through bar 0 (which ends at 2.0s)

        next_quarter = clock.get_next_quantized_timestamp(QuantizationSubdivision.QUARTER_NOTE)
        assert math.isclose(next_quarter, 1.5, abs_tol=1e-3)

        next_bar = clock.get_next_quantized_timestamp(QuantizationSubdivision.BAR_1)
        assert math.isclose(next_bar, 2.0, abs_tol=1e-3)

        next_bar2 = clock.get_next_quantized_timestamp(QuantizationSubdivision.BAR_2)
        assert math.isclose(next_bar2, 4.0, abs_tol=1e-3)


class TestAdaptiveMusicOrchestrator:
    """Verifies multi-stem mixing, equal-power crossfade curves, and pacing coupling."""

    def test_equal_power_crossfade_conservation(self):
        # Energy conservation test: g_in^2 + g_out^2 must be strictly 1.0 for all t
        for step in range(101):
            t = step / 100.0
            g_out, g_in = AdaptiveMusicOrchestrator.calculate_equal_power_crossfade(t)
            energy = g_in * g_in + g_out * g_out
            assert math.isclose(energy, 1.0, abs_tol=1e-4), f"Failed energy conservation at t={t}: {energy}"

    def test_stem_gains_per_pacing_phase(self):
        orchestrator = AdaptiveMusicOrchestrator()
        pad = AudioStem(stem_id="pad", role=StemRole.ATMOSPHERE_PAD, file_path="/Audio/Pad")
        bass = AudioStem(stem_id="bass", role=StemRole.BASS_SYNTH, file_path="/Audio/Bass")
        drums = AudioStem(stem_id="drums", role=StemRole.DRUMS_PERCUSSION, file_path="/Audio/Drums")
        lead = AudioStem(stem_id="lead", role=StemRole.MELODIC_LEAD, file_path="/Audio/Lead")
        tension = AudioStem(stem_id="tension", role=StemRole.TENSION_NOISE, file_path="/Audio/Tension")

        for s in (pad, bass, drums, lead, tension):
            orchestrator.register_stem(s)

        # In CALM: only PAD is active
        orchestrator.current_phase = PacingPhase.CALM
        gains_calm = orchestrator.compute_stem_gains()
        assert gains_calm["pad"] == 1.0
        assert gains_calm["bass"] == 0.0
        assert gains_calm["drums"] == 0.0
        assert gains_calm["lead"] == 0.0

        # In PEAK: PAD, BASS, DRUMS, LEAD active
        orchestrator.current_phase = PacingPhase.PEAK
        gains_peak = orchestrator.compute_stem_gains()
        assert gains_peak["pad"] == 1.0
        assert gains_peak["bass"] == 1.0
        assert gains_peak["drums"] == 1.0
        assert gains_peak["lead"] == 1.0
        assert gains_peak["tension"] == 0.0

        # In SUSTAINED_PEAK: TENSION also active
        orchestrator.current_phase = PacingPhase.SUSTAINED_PEAK
        gains_sustained = orchestrator.compute_stem_gains()
        assert gains_sustained["tension"] == 1.0


class TestSabineEyringAcousticCalculator:
    """Verifies analytical RT60 equations and axial resonance calculations."""

    def test_sabine_rt60_exact_formula(self):
        # Room: 10m x 10m x 3m (V = 300 m3, S = 2*(100 + 30 + 30) = 320 m2)
        # 100% Concrete: alpha_mid = 0.02
        # A = 320 * 0.02 = 6.4
        # RT60 = 0.161 * 300 / 6.4 = 7.5468...
        profile = SabineEyringAcousticCalculator.calculate_room_profile(
            room_id="room_concrete",
            dimensions_m=(10.0, 10.0, 3.0),
            materials={AcousticMaterial.CONCRETE: 1.0},
        )
        assert profile.volume_m3 == 300.0
        assert profile.surface_area_m2 == 320.0
        assert math.isclose(profile.rt60_sabine_seconds, 7.547, abs_tol=1e-2)

    def test_eyring_rt60_damped_space(self):
        # Damped room with foam/carpet (alpha_mid = 0.35)
        # Eyring must yield lower and more physical RT60 than Sabine for absorptive spaces
        profile = SabineEyringAcousticCalculator.calculate_room_profile(
            room_id="room_foam",
            dimensions_m=(6.0, 4.0, 2.5),
            materials={AcousticMaterial.CARPET_FOAM: 1.0},
        )
        assert profile.rt60_eyring_seconds < profile.rt60_sabine_seconds
        assert profile.rt60_eyring_seconds < 0.5  # Heavy acoustic absorption

    def test_axial_room_resonance_modes(self):
        # Length=10m, Width=5m, Height=2.5m, c=343 m/s
        # f_x1 = 343 / 20 = 17.15 Hz
        # f_y1 = 343 / 10 = 34.3 Hz
        # f_z1 = 343 / 5 = 68.6 Hz
        profile = SabineEyringAcousticCalculator.calculate_room_profile(
            room_id="room_modes",
            dimensions_m=(10.0, 5.0, 2.5),
            materials={AcousticMaterial.WOOD_PANEL: 1.0},
        )
        assert any(math.isclose(m, 17.15, abs_tol=0.2) for m in profile.axial_resonance_modes_hz)
        assert any(math.isclose(m, 34.3, abs_tol=0.2) for m in profile.axial_resonance_modes_hz)
        assert any(math.isclose(m, 68.6, abs_tol=0.2) for m in profile.axial_resonance_modes_hz)


class TestTopologicalAcousticDiffraction:
    """Verifies sound propagation across topological graph corridors and doors."""

    def test_same_room_clear_los(self):
        result = TopologicalAcousticDiffraction.evaluate_path_occlusion(
            source_pos=(0.0, 0.0, 1.0),
            listener_pos=(5.0, 5.0, 1.0),
            source_room_id="R1",
            listener_room_id="R1",
        )
        assert result.direct_path_clear is True
        assert result.occlusion_state == OcclusionState.CLEAR_LOS
        assert result.transmission_loss_db == 0.0
        assert result.low_pass_cutoff_hz == 20000.0

    def test_closed_door_acoustic_isolation(self):
        result = TopologicalAcousticDiffraction.evaluate_path_occlusion(
            source_pos=(0.0, 0.0, 1.0),
            listener_pos=(10.0, 0.0, 1.0),
            source_room_id="R1",
            listener_room_id="R2",
            path_distance_rooms=1,
            doors_closed_along_path=1,
        )
        assert result.direct_path_clear is False
        assert result.occlusion_state == OcclusionState.FULL_OCCLUDED
        assert result.transmission_loss_db >= 24.0
        assert result.low_pass_cutoff_hz <= 800.0  # Muffled


class TestSpatialAttenuationAndRule10:
    """Verifies distance attenuation, binaural stereo panning, and strict Rule 10 compliance."""

    def test_rule_10_compliance_validation(self):
        # Looping sound with falloff <= 20m is compliant
        prof_valid = SpatialAttenuationProfile(profile_id="valid_loop", falloff_distance_m=18.0, is_looping_spatial=True)
        assert SpatialAttenuationCalculator.validate_profile_compliance(prof_valid) is True

        # Looping sound with falloff > 20m violates Rule 10
        prof_invalid = SpatialAttenuationProfile(profile_id="invalid_loop", falloff_distance_m=25.0, is_looping_spatial=True)
        assert SpatialAttenuationCalculator.validate_profile_compliance(prof_invalid) is False

    def test_distance_gain_zero_outside_falloff(self):
        prof = SpatialAttenuationProfile(
            profile_id="enemy_hum",
            inner_radius_m=2.0,
            falloff_distance_m=18.0,
            curve_type=AttenuationCurveType.NATURAL_SOUND_EXPONENTIAL,
        )
        # Inside inner radius: full gain 1.0
        assert SpatialAttenuationCalculator.calculate_distance_gain(1.0, prof) == 1.0
        assert SpatialAttenuationCalculator.calculate_distance_gain(2.0, prof) == 1.0

        # Beyond falloff: strictly 0.0 (Rule 10 zero leakage)
        assert SpatialAttenuationCalculator.calculate_distance_gain(18.0, prof) == 0.0
        assert SpatialAttenuationCalculator.calculate_distance_gain(25.0, prof) == 0.0

        # Intermediate distance has non-zero decreasing gain
        g_mid = SpatialAttenuationCalculator.calculate_distance_gain(10.0, prof)
        assert 0.0 < g_mid < 1.0

    def test_air_absorption_low_pass(self):
        prof = SpatialAttenuationProfile(profile_id="test", falloff_distance_m=50.0, air_absorption_hf_loss_db_per_m=0.5)
        cutoff_close = SpatialAttenuationCalculator.calculate_air_absorption_cutoff(2.0, prof)
        cutoff_far = SpatialAttenuationCalculator.calculate_air_absorption_cutoff(30.0, prof)
        assert cutoff_close > cutoff_far

    def test_stereo_panning_equal_power(self):
        # Listener at origin facing +Y (0, 1, 0)
        # Source directly to the right (+X: 10, 0, 0)
        left_gain, right_gain = SpatialAttenuationCalculator.calculate_stereo_panning(
            source_pos=(10.0, 0.0, 0.0),
            listener_pos=(0.0, 0.0, 0.0),
            listener_forward=(0.0, 1.0, 0.0),
        )
        assert right_gain > left_gain
        energy = left_gain * left_gain + right_gain * right_gain
        assert math.isclose(energy, 1.0, abs_tol=1e-2)


class TestUE5MetaSoundsExporter:
    """Verifies MetaSounds graph schemas, attenuation assets, and ingestion scripts."""

    def test_build_metasound_graph_manifest(self):
        exporter = UE5MetaSoundsExporter(asset_name="MS_BossFightAudio")
        graph = exporter.build_metasound_graph()

        assert graph.graph_name == "MS_BossFightAudio"
        assert "Trigger.Play" in graph.inputs
        assert "Audio.Out_Left" in graph.outputs
        assert any(n.node_class == "MetaSounds.PlateReverb" for n in graph.nodes)
        assert any(n.node_class == "MetaSounds.MultiChannelCrossfader" for n in graph.nodes)
        assert graph.parameters["Rule10Compliant"] is True

    def test_sound_attenuation_asset_export(self):
        exporter = UE5MetaSoundsExporter()
        prof = SpatialAttenuationProfile(profile_id="SA_RobotPatrol", inner_radius_m=2.0, falloff_distance_m=18.0)
        asset = exporter.generate_sound_attenuation_asset(prof)

        assert asset["AssetClass"] == "USoundAttenuation"
        # Radius in centimeters (18m = 1800cm)
        assert asset["AttenuationSettings"]["FalloffDistance"] == 1800.0
        assert asset["AttenuationSettings"]["bSpatialization"] is True
        assert asset["Rule10Compliance"]["IsCompliant"] is True

    def test_editor_ingest_script(self):
        exporter = UE5MetaSoundsExporter()
        script = exporter.generate_editor_ingest_script()
        assert "run_import" in script
        assert "MetaSounds" in script
