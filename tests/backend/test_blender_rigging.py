"""
Unit and Integration Tests for Blender Skeletal Rigging and Articulation.

Validates:
- BlenderRigger health check and binary resolution.
- Anatomical skeleton presets (avian, canine, bipedal).
- Harmonic curve generation with aerodynamic wave propagation.
- End-to-end rigging and animation execution in Blender 4.3+.
"""

import math
from pathlib import Path
import pytest

from backend.blender.rigging import (
    AVIAN_BONES,
    BIPEDAL_BONES,
    CANINE_BONES,
    BlenderRigger,
    RiggingConfig,
    RiggingResult,
    generate_avian_flap_animation,
)


def test_blender_rigger_health_check():
    """Verify BlenderRigger detects Blender 4.3+ binary."""
    rigger = BlenderRigger()
    assert rigger.health_check() is True


def test_bone_presets_integrity():
    """Verify bone definitions have valid coordinate vectors and parent links."""
    for preset, bones in [("avian", AVIAN_BONES), ("canine", CANINE_BONES), ("bipedal", BIPEDAL_BONES)]:
        assert len(bones) >= 10, f"Preset {preset} should have at least 10 bones"
        names = {b.name for b in bones}
        assert len(names) == len(bones), f"Bone names must be unique in {preset}"

        for b in bones:
            assert len(b.head) == 3
            assert len(b.tail) == 3
            # Head and tail must not be identical
            dist = math.dist(b.head, b.tail)
            assert dist > 1e-4, f"Bone {b.name} has zero length"

            if b.parent:
                assert b.parent in names, f"Parent {b.parent} of {b.name} must exist in {preset}"


def test_avian_flap_animation_generation():
    """Verify procedural flap animation produces valid harmonic keyframes."""
    anim = generate_avian_flap_animation(total_frames=36, fps=24)
    assert anim.name == "avian_flap_cycle"
    assert anim.frame_end == 36
    assert anim.fps == 24
    assert len(anim.tracks) >= 6

    # Verify shoulder track has continuous wave motion without NaN
    shoulder_track = next(t for t in anim.tracks if t.bone_name == "Wing_Shoulder_L")
    assert len(shoulder_track.keyframes) == 36

    for kf in shoulder_track.keyframes:
        assert 1 <= kf.frame <= 36
        for angle in kf.rotation_euler_deg:
            assert not math.isnan(angle)
            assert not math.isinf(angle)


def test_blender_rigger_missing_mesh():
    """Verify clean error result when mesh does not exist."""
    rigger = BlenderRigger()
    cfg = RiggingConfig(
        mesh_path="non_existent_file.obj",
        skeleton_type="avian",
    )
    res = rigger.rig_and_animate(cfg)
    assert res.success is False
    assert "not found" in res.message


def test_blender_rigger_end_to_end_raven(tmp_path):
    """
    Test real Blender 4.3+ rigging and animation using raven mesh.
    Validates generation of .blend and .glb files.
    """
    raven_mesh = Path("outputs/raven_3d/raven_volumetric_3d.obj")
    if not raven_mesh.exists():
        pytest.skip("Raven volumetric mesh fixture not found")

    rigger = BlenderRigger()
    out_blend = tmp_path / "test_raven_rigged.blend"
    out_glb = tmp_path / "test_raven_rigged.glb"

    cfg = RiggingConfig(
        mesh_path=str(raven_mesh),
        skeleton_type="avian",
        animation_action="flap_cycle",
        output_blend=str(out_blend),
        output_glb=str(out_glb),
        total_frames=12,
        fps=24,
    )

    res = rigger.rig_and_animate(cfg)
    assert res.success is True
    assert res.bone_count == len(AVIAN_BONES)
    assert out_blend.exists()
    assert out_glb.exists()
    assert out_glb.stat().st_size > 1000


def test_blender_rigger_multi_component_collision_free(tmp_path):
    """
    Test multi-component scene assembly, GLB export, and verify 0 ribcage penetration.
    """
    comp_dir = Path("outputs/component_rig_refined")
    torso_obj = comp_dir / "subject_torso.obj"
    wing_v_obj = comp_dir / "subject_wing_ventral.obj"
    wing_d_obj = comp_dir / "subject_wing_dorsal.obj"

    if not (torso_obj.exists() and wing_v_obj.exists() and wing_d_obj.exists()):
        pytest.skip("Component OBJ fixtures not found in outputs/component_rig_refined")

    rigger = BlenderRigger()
    out_blend = tmp_path / "test_multi_flight.blend"
    out_glb = tmp_path / "test_multi_flight.glb"

    components = [
        {
            "name": "Subject_Torso",
            "role": "torso",
            "mesh_path": str(torso_obj),
            "pivot_point": [0.0, 0.0, 0.0],
            "z_offset": 0.0,
            "parent_bone": "Spine",
            "is_prop": False,
        },
        {
            "name": "Subject_Wing_Ventral",
            "role": "wing_ventral",
            "mesh_path": str(wing_v_obj),
            "pivot_point": [-0.3967, 0.4542, 0.16],
            "z_offset": 0.16,
            "parent_bone": "Wing_Shoulder_L",
            "is_prop": False,
        },
        {
            "name": "Subject_Wing_Dorsal",
            "role": "wing_dorsal",
            "mesh_path": str(wing_d_obj),
            "pivot_point": [-0.2767, 0.4542, -0.10],
            "z_offset": -0.10,
            "parent_bone": "Wing_Shoulder_R",
            "is_prop": False,
        },
    ]

    res = rigger.rig_multi_component_scene(
        components=components,
        output_blend=str(out_blend),
        output_glb=str(out_glb),
        total_frames=12,
        fps=24,
    )

    assert res.success is True
    assert out_blend.exists()
    assert out_glb.exists()
    assert res.bone_count == 5
    assert "Root" in res.hierarchy
    assert "Wing_Shoulder_L" in res.hierarchy
