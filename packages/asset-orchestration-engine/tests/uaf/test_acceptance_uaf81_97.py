"""
Acceptance Test Suite for UAF-81.97: Procedural Cinematics, CineCamera Director & UE5 Sequencer.
Validates framing rules (Rule of Thirds, Golden Ratio, OTS, 180-degree axis preservation),
Catmull-Rom spline trajectory evaluation with obstacle collision clearance,
physical depth of field & autofocus optics, and UE5 LevelSequence manifest generation.
"""

import pytest
import math
import json
import tempfile
from pathlib import Path

from uaf.cinematics import (
    CinematicShotType,
    FramingRule,
    CameraDampingMode,
    Vector3D,
    Rotator3D,
    Transform3D,
    CinematicSubject,
    LensSettings,
    FocusSettings,
    CameraKeyframe,
    CinematicShot,
    CinematicSequenceSpec,
    UE5LevelSequenceManifest,
    CinematicFramingEngine,
    CameraTrajectorySolver,
    BoundingBox3D,
    AutoFocusDepthOfField,
    UE5SequencerExporter,
)


class TestAcceptanceUAF81_97:

    def test_uaf81_97_contracts_and_models(self):
        """Tests domain model instantiation with keyword arguments."""
        vec = Vector3D(x=1.0, y=2.0, z=3.0)
        assert vec.to_ue5_cm().x == 100.0

        rot = Rotator3D(pitch=15.0, yaw=45.0, roll=0.0)
        transform = Transform3D(position=vec, rotation=rot)
        assert transform.rotation.pitch == 15.0

        lens = LensSettings(focal_length_mm=50.0, current_aperture_fstop=1.8)
        assert lens.focal_length_mm == 50.0

        kf = CameraKeyframe(
            time_seconds=1.0,
            transform=transform,
            focal_length_mm=50.0,
            aperture_fstop=1.8,
            focus_distance_m=4.5,
        )
        assert kf.focus_distance_m == 4.5

    def test_uaf81_97_vector3d_and_lens_fov(self):
        """Verifies vector geometry and optical field of view calculations."""
        v1 = Vector3D(x=1.0, y=0.0, z=0.0)
        v2 = Vector3D(x=0.0, y=1.0, z=0.0)
        v3 = v1.cross(v2)
        assert v3.x == 0.0 and v3.y == 0.0 and v3.z == 1.0

        lens_35mm = LensSettings(focal_length_mm=35.0, sensor_width_mm=36.0)
        fov_deg = lens_35mm.compute_horizontal_fov_deg()
        # 35mm lens on full frame sensor has FOV approx 54.4 degrees
        assert 50.0 < fov_deg < 60.0

    def test_uaf81_97_look_at_rotation_computation(self):
        """Tests pitch and yaw calculation from camera to aim point."""
        cam = Vector3D(x=0.0, y=0.0, z=0.0)
        target_front = Vector3D(x=10.0, y=0.0, z=0.0)
        rot_front = CinematicFramingEngine.compute_look_at_rotation(cam, target_front)
        assert rot_front.yaw == 0.0
        assert rot_front.pitch == 0.0

        target_up = Vector3D(x=10.0, y=0.0, z=10.0)
        rot_up = CinematicFramingEngine.compute_look_at_rotation(cam, target_up)
        assert rot_up.yaw == 0.0
        assert round(rot_up.pitch, 1) == 45.0

        target_right = Vector3D(x=0.0, y=10.0, z=0.0)
        rot_right = CinematicFramingEngine.compute_look_at_rotation(cam, target_right)
        assert rot_right.yaw == 90.0

    def test_uaf81_97_framing_rule_of_thirds(self):
        """Tests that rule of thirds offsets look-at aim point horizontally."""
        cam = Vector3D(x=0.0, y=0.0, z=1.7)
        hero = CinematicSubject(
            actor_id="Hero",
            world_pos=Vector3D(x=5.0, y=0.0, z=0.0),
            eye_level_pos=Vector3D(x=5.0, y=0.0, z=1.7),
        )

        transform_center = CinematicFramingEngine.frame_subject(
            cam_pos=cam,
            subject=hero,
            rule=FramingRule.CENTER_SYMMETRY,
        )
        assert transform_center.rotation.yaw == 0.0

        transform_right = CinematicFramingEngine.frame_subject(
            cam_pos=cam,
            subject=hero,
            rule=FramingRule.RULE_OF_THIRDS,
            use_right_side=True,
        )
        # Offset aim creates non-zero yaw
        assert transform_right.rotation.yaw != 0.0

    def test_uaf81_97_framing_golden_ratio(self):
        """Verifies golden ratio composition calculation."""
        cam = Vector3D(x=0.0, y=0.0, z=1.7)
        subject = CinematicSubject(
            actor_id="Target",
            world_pos=Vector3D(x=6.0, y=0.0, z=0.0),
            eye_level_pos=Vector3D(x=6.0, y=0.0, z=1.7),
        )
        transform_gold = CinematicFramingEngine.frame_subject(
            cam_pos=cam,
            subject=subject,
            rule=FramingRule.GOLDEN_RATIO,
            use_right_side=False,
        )
        assert transform_gold.rotation.yaw != 0.0

    def test_uaf81_97_over_the_shoulder_shot_generation(self):
        """Verifies over-the-shoulder camera placement and focus targeting."""
        speaker_a = CinematicSubject(
            actor_id="Char_A",
            world_pos=Vector3D(x=0.0, y=0.0, z=0.0),
            eye_level_pos=Vector3D(x=0.0, y=0.0, z=1.7),
        )
        speaker_b = CinematicSubject(
            actor_id="Char_B",
            world_pos=Vector3D(x=3.0, y=0.0, z=0.0),
            eye_level_pos=Vector3D(x=3.0, y=0.0, z=1.7),
        )

        shot = CinematicFramingEngine.create_over_the_shoulder_shot(
            observer=speaker_a,
            target=speaker_b,
            shot_id="shot_ots_A_to_B",
            over_right_shoulder=True,
            camera_distance_m=1.8,
            shoulder_offset_m=0.45,
        )

        assert shot.shot_type == CinematicShotType.OVER_THE_SHOULDER
        assert shot.primary_subject_id == "Char_B"
        assert shot.secondary_subject_id == "Char_A"
        assert len(shot.keyframes) == 1

        cam_pos = shot.keyframes[0].transform.position
        # Camera should be positioned behind speaker_a (negative X)
        assert cam_pos.x < speaker_a.world_pos.x
        assert shot.keyframes[0].focus_distance_m > 1.8

    def test_uaf81_97_180_degree_rule_compliance(self):
        """Verifies detection of 180-degree action line crossing."""
        pos_a = Vector3D(x=0.0, y=0.0, z=0.0)
        pos_b = Vector3D(x=4.0, y=0.0, z=0.0)

        # Both cameras on the positive Y side (same side)
        cam1_valid = Vector3D(x=-1.0, y=1.5, z=1.7)
        cam2_valid = Vector3D(x=5.0, y=1.5, z=1.7)
        assert CinematicFramingEngine.verify_180_degree_rule(cam1_valid, cam2_valid, pos_a, pos_b) is True

        # Cam2 crosses to negative Y side (axis violation)
        cam2_invalid = Vector3D(x=5.0, y=-1.5, z=1.7)
        assert CinematicFramingEngine.verify_180_degree_rule(cam1_valid, cam2_invalid, pos_a, pos_b) is False

    def test_uaf81_97_shot_reverse_shot_pair_generation(self):
        """Tests that generated shot-reverse-shot pairs satisfy 180-degree line rule."""
        char_a = CinematicSubject(
            actor_id="A",
            world_pos=Vector3D(x=10.0, y=20.0, z=0.0),
            eye_level_pos=Vector3D(x=10.0, y=20.0, z=1.7),
        )
        char_b = CinematicSubject(
            actor_id="B",
            world_pos=Vector3D(x=13.0, y=22.0, z=0.0),
            eye_level_pos=Vector3D(x=13.0, y=22.0, z=1.7),
        )

        shot_a, shot_b = CinematicFramingEngine.create_shot_reverse_shot_pair(char_a, char_b)
        cam_a = shot_a.keyframes[0].transform.position
        cam_b = shot_b.keyframes[0].transform.position

        is_compliant = CinematicFramingEngine.verify_180_degree_rule(cam_a, cam_b, char_a.world_pos, char_b.world_pos)
        assert is_compliant is True

    def test_uaf81_97_orbit_boss_reveal_generation(self):
        """Verifies ascending orbital boss reveal generation."""
        boss = CinematicSubject(
            actor_id="Boss_Titan",
            world_pos=Vector3D(x=50.0, y=50.0, z=0.0),
            eye_level_pos=Vector3D(x=50.0, y=50.0, z=4.0),
        )

        shot = CinematicFramingEngine.create_orbit_boss_reveal(
            boss=boss,
            radius_m=8.0,
            start_height_m=0.5,
            end_height_m=5.0,
            total_rotation_deg=180.0,
            duration_s=6.0,
            sample_count=12,
        )

        assert shot.shot_type == CinematicShotType.ORBIT_BOSS_REVEAL
        assert len(shot.keyframes) == 12
        assert shot.keyframes[0].time_seconds == 0.0
        assert shot.keyframes[-1].time_seconds == 6.0
        # Height should ascend
        assert shot.keyframes[-1].transform.position.z > shot.keyframes[0].transform.position.z

    def test_uaf81_97_catmull_rom_spline_evaluation(self):
        """Tests cubic Catmull-Rom point evaluation."""
        p0 = Vector3D(x=0.0, y=0.0, z=0.0)
        p1 = Vector3D(x=10.0, y=0.0, z=0.0)
        p2 = Vector3D(x=20.0, y=10.0, z=0.0)
        p3 = Vector3D(x=30.0, y=10.0, z=0.0)

        # At t=0, must exactly equal p1
        pt_start = CameraTrajectorySolver.evaluate_catmull_rom_point(p0, p1, p2, p3, 0.0)
        assert round(pt_start.x, 2) == 10.0
        assert round(pt_start.y, 2) == 0.0

        # At t=1, must exactly equal p2
        pt_end = CameraTrajectorySolver.evaluate_catmull_rom_point(p0, p1, p2, p3, 1.0)
        assert round(pt_end.x, 2) == 20.0
        assert round(pt_end.y, 2) == 10.0

        # Intermediate point should be smooth
        pt_mid = CameraTrajectorySolver.evaluate_catmull_rom_point(p0, p1, p2, p3, 0.5)
        assert 10.0 < pt_mid.x < 20.0

    def test_uaf81_97_spline_path_generation_and_continuity(self):
        """Tests multi-point spline path evaluation."""
        controls = [
            Vector3D(x=0.0, y=0.0, z=1.0),
            Vector3D(x=10.0, y=5.0, z=2.0),
            Vector3D(x=20.0, y=0.0, z=3.0),
            Vector3D(x=30.0, y=-5.0, z=2.0),
        ]

        path = CameraTrajectorySolver.evaluate_spline_path(controls, samples_per_segment=8)
        assert len(path) == (len(controls) - 1) * 8 + 1
        assert round(path[0].x, 2) == controls[0].x
        assert round(path[-1].x, 2) == controls[-1].x

    def test_uaf81_97_collision_avoidance_against_obstacles(self):
        """Verifies that camera paths push clear of obstacle bounding boxes and ground."""
        obstacle = BoundingBox3D(min_x=8.0, max_x=12.0, min_y=-2.0, max_y=2.0, min_z=0.0, max_z=3.0)

        raw_path = [
            Vector3D(x=5.0, y=0.0, z=1.5),
            Vector3D(x=10.0, y=0.0, z=1.5),  # Directly inside obstacle
            Vector3D(x=15.0, y=0.0, z=-0.5), # Below ground
        ]

        safe_path = CameraTrajectorySolver.apply_collision_avoidance(
            path=raw_path,
            obstacles=[obstacle],
            min_clearance_m=0.5,
            min_ground_height_m=0.5,
        )

        assert len(safe_path) == 3
        # First point outside obstacle remains unchanged
        assert safe_path[0].x == 5.0

        # Second point should be pushed out of obstacle
        assert not obstacle.contains(safe_path[1], margin=0.0)

        # Third point should be elevated above ground
        assert safe_path[2].z >= 0.5

    def test_uaf81_97_autofocus_hyperfocal_and_depth_of_field(self):
        """Tests hyperfocal and depth of field calculations."""
        # 50mm lens at f/2.8, circle of confusion 0.03mm
        # H = (50^2 / (2.8 * 0.03)) + 50 mm = 29761 mm + 50 mm approx 29.8 m
        h_dist = AutoFocusDepthOfField.compute_hyperfocal_distance_m(50.0, 2.8, 0.03)
        assert 25.0 < h_dist < 35.0

        dof = AutoFocusDepthOfField.compute_depth_of_field(
            subject_distance_m=3.0,
            focal_length_mm=50.0,
            aperture_fstop=2.8,
        )
        assert dof["near_limit_m"] < 3.0
        assert dof["far_limit_m"] > 3.0
        assert dof["dof_total_m"] > 0.0

    def test_uaf81_97_shot_aperture_recommendations(self):
        """Verifies narrative f-stop recommendations by shot type."""
        f_close = AutoFocusDepthOfField.recommend_aperture_for_shot(CinematicShotType.CLOSE_UP)
        f_wide = AutoFocusDepthOfField.recommend_aperture_for_shot(CinematicShotType.WIDE_ACTION)
        # Close up should have shallower aperture (lower f-stop) than wide action
        assert f_close < f_wide

    def test_uaf81_97_ue5_sequencer_exporter_manifest_and_json(self):
        """Verifies full sequence export to native UE5 LevelSequence JSON manifest and script."""
        hero = CinematicSubject(
            actor_id="Hero_Player",
            world_pos=Vector3D(x=0.0, y=0.0, z=0.0),
            eye_level_pos=Vector3D(x=0.0, y=0.0, z=1.7),
        )
        boss = CinematicSubject(
            actor_id="Boss_Gargoyle",
            world_pos=Vector3D(x=20.0, y=0.0, z=0.0),
            eye_level_pos=Vector3D(x=20.0, y=0.0, z=4.0),
        )

        shot1 = CinematicFramingEngine.create_over_the_shoulder_shot(hero, boss, "Shot1", duration_s=4.0)
        shot2 = CinematicFramingEngine.create_orbit_boss_reveal(boss, duration_s=6.0)

        sequence = CinematicSequenceSpec(
            sequence_id="Boss_Intro_Cutscene",
            sequence_name="Gargoyle Encounter Intro",
            frame_rate=30.0,
            total_duration_s=10.0,
            shots=[shot1, shot2],
            audio_cue_track="/Game/Audio/Boss_Intro_Music",
        )

        manifest = UE5SequencerExporter.build_level_sequence_manifest(sequence)
        assert manifest.total_frames == 300
        assert manifest.frame_rate == 30.0
        assert len(manifest.tracks) >= 5

        # Check tracks contain transform and camera cuts
        track_types = [t["track_type"] for t in manifest.tracks]
        assert "MovieScene3DTransformTrack" in track_types
        assert "MovieSceneFloatTrack" in track_types
        assert "MovieSceneCameraCutTrack" in track_types
        assert "MovieSceneAudioTrack" in track_types

        # Test export to JSON file
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "Boss_Intro_LevelSequence.json"
            json_str = UE5SequencerExporter.export_to_json(sequence, out_file)

            assert out_file.exists()
            data = json.loads(json_str)
            assert data["asset_name"] == "LS_Boss_Intro_Cutscene"
            assert len(data["tracks"]) >= 5
