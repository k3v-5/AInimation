"""
Tests for Character Classification, Animation Clips, State Machines, and Animation LOD.
UAF-81.9 Sections 5, 6, 60, 112, 125, 128.
"""

from uaf.animation.models.classification import CharacterClassification, RigProfile
from uaf.animation.models.clip import (
    Keyframe,
    AnimationTrack,
    AnimationEventType,
    AnimationEvent,
    AnimationClip,
)
from uaf.animation.models.state_machine import (
    AnimState,
    AnimTransition,
    AnimStateMachine,
    MontageDefinition,
    AnimationBlueprintContract,
)
from uaf.animation.models.lod import AnimationLODLevel, AnimationLODProfile


def test_character_classification_and_rig_profile():
    profile = RigProfile("Prof_Biped_Hero", CharacterClassification.HUMANOID, max_bones=64)
    assert profile.classification == CharacterClassification.HUMANOID
    assert profile.supports_ik is True
    assert profile.max_bones == 64
    data = profile.to_dict()
    assert data["classification"] == "HUMANOID"


def test_animation_clip_tracks_and_events():
    clip = AnimationClip.create_walk_clip("A_Hero_Walk_01")
    assert clip.clip_id == "A_Hero_Walk_01"
    assert clip.duration_seconds == 1.0
    assert len(clip.events) == 2
    assert clip.events[0].event_type == AnimationEventType.FOOTSTEP
    assert len(clip.clip_hash) == 64


def test_animation_blueprint_contract_and_state_machine():
    abp = AnimationBlueprintContract.create_standard_locomotion_contract("ABP_Hero_Locomotion")
    assert abp.blueprint_id == "ABP_Hero_Locomotion"
    assert abp.ik_enabled is True
    assert "Speed" in abp.parameters
    assert "IDLE" in abp.state_machine.states
    assert len(abp.state_machine.transitions) == 4
    assert len(abp.montages) == 1
    assert len(abp.blueprint_hash) == 64


def test_animation_lod_profile_distance_scaling():
    lod = AnimationLODProfile.create_standard_profile("AnimLOD_Hero")
    assert len(lod.lods) == 3
    assert lod.lods[0].distance_meters == 0.0
    assert lod.lods[0].skip_ik is False
    assert lod.lods[1].skip_ik is True
    assert lod.lods[2].skip_facial is True
    assert lod.lods[2].update_rate_divisor == 2
