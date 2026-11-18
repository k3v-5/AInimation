"""
Tests for Determinism, 15 Golden Animations, and End-to-End Pipeline (UAF-81.55 Sections 159-162).
"""

import pytest
from uaf.universal_animation import (
    UniversalAnimationFabricator,
    AnimationDefinition,
    AnimationType55,
    RetargetProfile55,
    AnimationCompressionProfile55,
    AnimationLODProfile55,
    FacialAnimationTrack55,
    ProductionReadyAnimatedCharacter,
)
from uaf.universal_character import UniversalCharacterFabricator


# --- 18 DETERMINISM TESTS (Section 159) ---

def test_det_animation_import():
    t1 = UniversalAnimationFabricator.generate_breathing(1.0)
    t2 = UniversalAnimationFabricator.generate_breathing(1.0)
    assert t1.to_dict() == t2.to_dict()


def test_det_coordinate_conversion():
    p1 = (10.0, -30.0, 20.0)
    p2 = (10.0, -30.0, 20.0)
    assert p1 == p2


def test_det_resampling():
    anim = UniversalAnimationFabricator.generate_breathing(1.0, 30)
    r1 = UniversalAnimationFabricator.resample_animation(anim, 60)
    r2 = UniversalAnimationFabricator.resample_animation(anim, 60)
    assert r1.to_dict() == r2.to_dict()


def test_det_retargeting():
    rp1 = RetargetProfile55("RP1", "S1", "S2", {"HEAD": "HEAD"})
    rp2 = RetargetProfile55("RP1", "S1", "S2", {"HEAD": "HEAD"})
    assert rp1.to_dict() == rp2.to_dict()


def test_det_ik_retargeting():
    rp1 = RetargetProfile55("RP_IK", "S1", "S2", ik_goals=["IK_Foot_L"])
    rp2 = RetargetProfile55("RP_IK", "S1", "S2", ik_goals=["IK_Foot_L"])
    assert rp1.to_dict() == rp2.to_dict()


def test_det_procedural_walk():
    w1 = UniversalAnimationFabricator.generate_procedural_walk(["ROOT", "PELVIS"])
    w2 = UniversalAnimationFabricator.generate_procedural_walk(["ROOT", "PELVIS"])
    assert w1.to_dict() == w2.to_dict()


def test_det_procedural_run():
    r1 = UniversalAnimationFabricator.generate_procedural_run(["ROOT", "PELVIS"])
    r2 = UniversalAnimationFabricator.generate_procedural_run(["ROOT", "PELVIS"])
    assert r1.to_dict() == r2.to_dict()


def test_det_look_at():
    l1 = UniversalAnimationFabricator.generate_look_at((0.0, 50.0, 150.0))
    l2 = UniversalAnimationFabricator.generate_look_at((0.0, 50.0, 150.0))
    assert l1.to_dict() == l2.to_dict()


def test_det_foot_placement():
    fp1 = UniversalAnimationFabricator.generate_foot_placement(5.0)
    fp2 = UniversalAnimationFabricator.generate_foot_placement(5.0)
    assert fp1 == fp2


def test_det_pose_generation():
    p1 = {"PELVIS": (0.0, 0.0, 95.0)}
    p2 = {"PELVIS": (0.0, 0.0, 95.0)}
    assert p1 == p2


def test_det_blending():
    bs1 = UniversalAnimationFabricator.build_blend_space_1d("BS1")
    bs2 = UniversalAnimationFabricator.build_blend_space_1d("BS1")
    assert bs1.to_dict() == bs2.to_dict()


def test_det_root_motion_extraction():
    rm1 = UniversalAnimationFabricator.build_golden_root_motion()
    rm2 = UniversalAnimationFabricator.build_golden_root_motion()
    assert rm1.canonical_hash == rm2.canonical_hash


def test_det_motion_warping():
    w1 = UniversalAnimationFabricator.build_golden_root_motion().warping
    w2 = UniversalAnimationFabricator.build_golden_root_motion().warping
    assert w1.to_dict() == w2.to_dict()


def test_det_facial_animation():
    f1 = UniversalAnimationFabricator.build_golden_facial()
    f2 = UniversalAnimationFabricator.build_golden_facial()
    assert f1.canonical_hash == f2.canonical_hash


def test_det_compression():
    c1 = AnimationCompressionProfile55()
    c2 = AnimationCompressionProfile55()
    assert c1.to_dict() == c2.to_dict()


def test_det_lod_generation():
    l1 = AnimationLODProfile55()
    l2 = AnimationLODProfile55()
    assert l1.to_dict() == l2.to_dict()


def test_det_event_generation():
    w1 = UniversalAnimationFabricator.generate_procedural_walk(["ROOT", "PELVIS"])
    w2 = UniversalAnimationFabricator.generate_procedural_walk(["ROOT", "PELVIS"])
    assert [e.to_dict() for e in w1.events] == [e.to_dict() for e in w2.events]


def test_det_package_hash():
    idle1 = UniversalAnimationFabricator.build_golden_idle()
    idle2 = UniversalAnimationFabricator.build_golden_idle()
    assert idle1.canonical_hash == idle2.canonical_hash


# --- 15 GOLDEN ANIMATION TESTS (Section 160) ---

def test_golden_idle():
    anim = UniversalAnimationFabricator.build_golden_idle()
    assert anim.animation.animation_id == "GOLDEN_IDLE"
    assert anim.validation_report.is_valid is True
    assert anim.verify_readback()["readback_passed"] is True


def test_golden_walk():
    anim = UniversalAnimationFabricator.build_golden_walk()
    assert anim.animation.animation_id == "GOLDEN_WALK"
    assert anim.validation_report.is_valid is True
    assert anim.verify_readback()["readback_passed"] is True


def test_golden_run():
    anim = UniversalAnimationFabricator.build_golden_run()
    assert anim.animation.animation_id == "GOLDEN_RUN"
    assert anim.validation_report.is_valid is True
    assert anim.verify_readback()["readback_passed"] is True


def test_golden_sprint():
    anim = UniversalAnimationFabricator.build_golden_sprint()
    assert anim.animation.animation_id == "GOLDEN_SPRINT"
    assert anim.animation.sample_rate == 60
    assert anim.validation_report.is_valid is True
    assert anim.verify_readback()["readback_passed"] is True


def test_golden_jump():
    anim = UniversalAnimationFabricator.build_golden_jump()
    assert anim.animation.animation_id == "GOLDEN_JUMP"
    assert anim.validation_report.is_valid is True
    assert anim.verify_readback()["readback_passed"] is True


def test_golden_fall():
    anim = UniversalAnimationFabricator.build_golden_fall()
    assert anim.animation.animation_id == "GOLDEN_FALL"
    assert anim.validation_report.is_valid is True
    assert anim.verify_readback()["readback_passed"] is True


def test_golden_land():
    anim = UniversalAnimationFabricator.build_golden_land()
    assert anim.animation.animation_id == "GOLDEN_LAND"
    assert len(anim.animation.events) >= 1
    assert anim.validation_report.is_valid is True
    assert anim.verify_readback()["readback_passed"] is True


def test_golden_turn():
    anim = UniversalAnimationFabricator.build_golden_turn()
    assert anim.animation.animation_id == "GOLDEN_TURN"
    assert anim.validation_report.is_valid is True
    assert anim.verify_readback()["readback_passed"] is True


def test_golden_strafe():
    anim = UniversalAnimationFabricator.build_golden_strafe()
    assert anim.animation.animation_id == "GOLDEN_STRAFE"
    assert anim.validation_report.is_valid is True
    assert anim.verify_readback()["readback_passed"] is True


def test_golden_attack():
    anim = UniversalAnimationFabricator.build_golden_attack()
    assert anim.animation.animation_id == "GOLDEN_ATTACK"
    assert len(anim.montages) >= 1
    assert anim.validation_report.is_valid is True
    assert anim.verify_readback()["readback_passed"] is True


def test_golden_aim():
    anim = UniversalAnimationFabricator.build_golden_aim()
    assert anim.animation.animation_id == "GOLDEN_AIM"
    assert anim.validation_report.is_valid is True
    assert anim.verify_readback()["readback_passed"] is True


def test_golden_crouch():
    anim = UniversalAnimationFabricator.build_golden_crouch()
    assert anim.animation.animation_id == "GOLDEN_CROUCH"
    assert anim.validation_report.is_valid is True
    assert anim.verify_readback()["readback_passed"] is True


def test_golden_facial():
    anim = UniversalAnimationFabricator.build_golden_facial()
    assert anim.animation.animation_id == "GOLDEN_FACIAL"
    assert len(anim.facial_tracks) >= 3
    assert anim.validation_report.is_valid is True
    assert anim.verify_readback()["readback_passed"] is True


def test_golden_root_motion():
    anim = UniversalAnimationFabricator.build_golden_root_motion()
    assert anim.animation.animation_id == "GOLDEN_ROOT_MOTION"
    assert anim.animation.root_motion_enabled is True
    assert anim.warping is not None
    assert anim.validation_report.is_valid is True
    assert anim.verify_readback()["readback_passed"] is True


def test_golden_retarget():
    anim = UniversalAnimationFabricator.build_golden_retarget()
    assert anim.animation.animation_id == "GOLDEN_RETARGET"
    assert anim.retarget is not None
    assert anim.validation_report.is_valid is True
    assert anim.verify_readback()["readback_passed"] is True


# --- 1 END_TO_END TEST (Section 162) ---

def test_end_to_end_animation_pipeline():
    """
    Executes full pipeline:
    CHARACTER -> SKELETON -> RIG -> SOURCE ANIMATION -> IMPORT -> NORMALIZATION ->
    RETARGET -> IK RETARGET -> POSE VALIDATION -> BLENDING -> LOCOMOTION ->
    ROOT MOTION -> FOOT IK -> FACIAL ANIMATION -> COMPRESSION -> ANIMATION LOD ->
    RUNTIME VALIDATION -> UNREAL EXPORT -> READBACK -> FINAL VALIDATION.
    """
    # 1. CHARACTER, SKELETON, RIG (UAF-81.54)
    char = UniversalCharacterFabricator.build_golden_human_male()
    assert char.validation_report.is_valid is True

    # 2. SOURCE ANIMATION & IMPORT & NORMALIZATION
    walk_anim = UniversalAnimationFabricator.generate_procedural_walk(char.skeleton.bone_names, duration=1.2, sample_rate=30)
    assert walk_anim.is_valid is True

    # 3. RETARGET & IK RETARGET
    retarget = RetargetProfile55(
        profile_id="RP_E2E",
        source_skeleton=char.skeleton.skeleton_id,
        target_skeleton="SKEL_Target_UE5",
        bone_mapping={b: b for b in char.skeleton.bone_names},
        ik_goals=["IK_Foot_L", "IK_Foot_R"],
    )

    # 4. BLENDING & LOCOMOTION STATE MACHINE
    sm = UniversalAnimationFabricator.build_locomotion_state_machine()
    bs = UniversalAnimationFabricator.build_blend_space_1d("BS_E2E")

    # 5. MONTAGES & ROOT MOTION
    montage = UniversalAnimationFabricator.build_montage(walk_anim.animation_id, "MONT_E2E")

    # 6. FACIAL ANIMATION
    facial_tracks = [FacialAnimationTrack55("Morph_Smile", [(0.0, 0.0), (0.6, 0.7), (1.2, 0.0)])]

    # 7. COMPRESSION & ANIMATION LOD
    comp = AnimationCompressionProfile55(max_error_cm=0.04, budget_kb=256.0, compressed_size_kb=80.0)
    lod = AnimationLODProfile55()

    # 8. FABRICATE & UNREAL EXPORT
    package = UniversalAnimationFabricator.fabricate(
        character=char,
        animation=walk_anim,
        retarget=retarget,
        blend_space=bs,
        montages=[montage],
        state_machine=sm,
        facial_tracks=facial_tracks,
        compression=comp,
        lod_profile=lod,
        export_path="/Game/Animations/Anim_E2E_Walk.uasset",
    )

    # 9. READBACK
    readback = package.verify_readback()
    assert readback["readback_passed"] is True
    assert readback["animation_id"] == walk_anim.animation_id
    assert readback["retarget_valid"] is True
    assert readback["state_machine_valid"] is True

    # 10. FINAL VALIDATION
    assert package.validation_report.is_valid is True
    assert package.validation_report.review_status == "PASSED"
    assert package.validation_report.quality_score.aggregate_score == 1.0
    assert len(package.canonical_hash) == 64
