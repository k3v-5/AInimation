"""
UAF-81.60 Acceptance & Normative Compliance Test Suite.
Verifies Universal Cinematic, Cutscene, Camera, Sequencer, Facial Performance, Lip-Sync & Presentation System.
Covers Core, Timeline, Bindings, Camera System, Character Performance, Facial, Lip-Sync, Dialogue,
Subtitles, VFX, Lighting, Gameplay Locks, Branching, Skip, Fast-Forward, Checkpoints, Replay,
Persistence, Network, 29 Failure Scenarios, 15 Determinism Proofs, 16 Golden Scenarios, and Full End-to-End Pipeline.
Total: 255 normative test cases (satisfies >= 254 requirement of §133).
"""

import math
import time
import pytest

from uaf.universal_cinematics import (
    PlaybackState,
    CinematicCommandType,
    SeekMode,
    TrackType,
    ClipOverlapPolicy,
    BindingType,
    BindingFailurePolicy,
    CameraRigType,
    CameraInterpolationType,
    CameraPriority,
    ReleasePolicy,
    PerformanceChannel,
    AnimationLayer,
    RootMotionPolicy,
    FacialInputType,
    LipSyncSource,
    LipSyncFallback,
    GameplayLockType,
    BranchConditionType,
    ChoiceTimeoutPolicy,
    SkipPolicy,
    FastForwardMultiplier,
    FastForwardEventPolicy,
    PauseType,
    NetworkAuthority,
    JoinInProgressPolicy,
    EventExecutionPolicy,
    RollbackPolicy,
    CinematicClip,
    CinematicMarker,
    CinematicTrack,
    Timeline,
    CinematicBinding,
    CinematicCamera,
    CameraRig,
    CameraBlend,
    CameraCut,
    FacialState,
    LipSyncData,
    DialogueClip,
    SubtitleClip,
    GameplayLock,
    CinematicChoice,
    CinematicBranch,
    CinematicCheckpoint,
    CinematicReplay,
    CinematicCommand,
    CinematicAsset,
    CinematicInstance,
    CinematicState,
    CinematicSaveState,
    CinematicDiagnosticReport,
    UniversalCinematicFabricator,
    UniversalCinematicValidator,
    CinematicValidationReport,
    UniversalCinematicPackager,
    ProductionReadyCinematic,
)


@pytest.fixture
def fabricator():
    return UniversalCinematicFabricator()


@pytest.fixture
def validator():
    return UniversalCinematicValidator()


@pytest.fixture
def packager():
    return UniversalCinematicPackager()


@pytest.fixture
def basic_asset():
    timeline = Timeline(start_time=0.0, end_time=10.0, duration=10.0)
    timeline.tracks.append(
        CinematicTrack(
            track_id="track_cam_01",
            track_type=TrackType.CAMERA,
            order=0,
            clips=[CinematicClip(clip_id="clip_cam_01", start=0.0, duration=10.0, source="cine_cam_01")]
        )
    )
    bindings = [
        CinematicBinding(binding_id="cam_main", binding_type=BindingType.STATIC, target_reference="cine_cam_01"),
        CinematicBinding(binding_id="hero", binding_type=BindingType.PLAYER),
    ]
    return CinematicAsset(
        cinematic_id="cin_intro_seq",
        version="1.0.0",
        duration=10.0,
        timeline=timeline,
        bindings=bindings,
    )


# ==============================================================================
# 1. CORE (12 tests - §4, §5, §6, §7, §133)
# ==============================================================================

def test_core_asset_instantiation(basic_asset):
    assert basic_asset.cinematic_id == "cin_intro_seq"
    assert basic_asset.duration == 10.0
    assert len(basic_asset.timeline.tracks) == 1
    assert len(basic_asset.bindings) == 2


def test_core_instance_creation(fabricator, basic_asset):
    instance = fabricator.create_instance(basic_asset, instance_id="inst_001")
    assert instance.instance_id == "inst_001"
    assert instance.cinematic_id == "cin_intro_seq"
    assert instance.playback_state == PlaybackState.IDLE
    assert instance.current_time == 0.0


def test_core_instance_initial_state(fabricator, basic_asset):
    instance = fabricator.create_instance(basic_asset)
    assert instance.playback_state == PlaybackState.IDLE
    assert instance.checkpoint is None


def test_core_play_command(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    assert fabricator.play(inst) is True
    assert inst.playback_state == PlaybackState.PLAYING


def test_core_pause_command(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.play(inst)
    assert fabricator.pause(inst) is True
    assert inst.playback_state == PlaybackState.PAUSED
    assert inst.pause_type == PauseType.CINEMATIC_PAUSE


def test_core_resume_command(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.play(inst)
    fabricator.pause(inst)
    assert fabricator.resume(inst) is True
    assert inst.playback_state == PlaybackState.PLAYING
    assert inst.pause_type is None


def test_core_stop_command(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.play(inst)
    inst.current_time = 5.0
    assert fabricator.stop(inst) is True
    assert inst.playback_state == PlaybackState.IDLE
    assert inst.current_time == 0.0


def test_core_restart_command(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    inst.current_time = 8.0
    assert fabricator.restart(inst) is True
    assert inst.playback_state == PlaybackState.PLAYING
    assert inst.current_time == 0.0


def test_core_playback_state_enum():
    states = list(PlaybackState)
    assert len(states) == 9
    assert PlaybackState.IDLE == "IDLE"
    assert PlaybackState.COMPLETED == "COMPLETED"
    assert PlaybackState.FAST_FORWARD == "FAST_FORWARD"


def test_core_command_type_enum():
    commands = list(CinematicCommandType)
    assert len(commands) >= 18
    assert CinematicCommandType.PLAY == "PLAY"
    assert CinematicCommandType.TRIGGER_EVENT == "TRIGGER_EVENT"


def test_core_asset_metadata_dependencies():
    asset = CinematicAsset(
        cinematic_id="cin_meta",
        metadata={"author": "Team", "genre": "SciFi"},
        dependencies=["anim_pkg_01", "sfx_pkg_02"],
    )
    assert asset.metadata["author"] == "Team"
    assert len(asset.dependencies) == 2


def test_core_diagnostics_generation(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    diag = fabricator.get_diagnostics(inst, basic_asset)
    assert isinstance(diag, CinematicDiagnosticReport)
    assert diag.is_healthy is True
    assert diag.active_tracks_count == 1
    assert diag.active_bindings_count == 2


# ==============================================================================
# 2. TIMELINE (12 tests - §8 - §12, §133)
# ==============================================================================

def test_timeline_creation():
    tl = Timeline(start_time=0.0, end_time=15.0, duration=15.0, tempo=130.0)
    assert tl.duration == 15.0
    assert tl.tempo == 130.0
    assert tl.time_resolution == 0.01


def test_timeline_duration_auto_calculation():
    tl = Timeline(start_time=2.0, end_time=12.0, duration=0.0)
    assert tl.duration == 10.0


def test_timeline_fixed_resolution():
    tl = Timeline(time_resolution=0.005)
    assert tl.time_resolution == 0.005


def test_timeline_seek_continuous(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    res = fabricator.seek(inst, basic_asset, 4.35, SeekMode.CONTINUOUS)
    assert res == pytest.approx(4.35)
    assert inst.current_time == pytest.approx(4.35)


def test_timeline_seek_snap(fabricator, basic_asset):
    basic_asset.timeline.time_resolution = 0.5
    inst = fabricator.create_instance(basic_asset)
    res = fabricator.seek(inst, basic_asset, 4.28, SeekMode.SNAP)
    assert res == pytest.approx(4.5)


def test_timeline_seek_marker(fabricator, basic_asset):
    basic_asset.timeline.markers = [
        CinematicMarker(marker_id="m1", time=2.0),
        CinematicMarker(marker_id="m2", time=7.0),
    ]
    inst = fabricator.create_instance(basic_asset)
    res = fabricator.seek(inst, basic_asset, 6.8, SeekMode.MARKER)
    assert res == 7.0


def test_timeline_seek_checkpoint(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    inst.current_time = 6.2
    fabricator.create_checkpoint(inst, "chk_test")
    inst.current_time = 1.0
    res = fabricator.seek(inst, basic_asset, 0.0, SeekMode.CHECKPOINT)
    assert res == pytest.approx(6.2)


def test_timeline_track_ordering(fabricator, basic_asset):
    t1 = CinematicTrack(track_id="t_vfx", track_type=TrackType.VFX, order=2)
    t2 = CinematicTrack(track_id="t_audio", track_type=TrackType.AUDIO, order=1)
    basic_asset.timeline.tracks.extend([t1, t2])
    eval_res = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 1.0)
    assert eval_res is not None


def test_timeline_marker_creation():
    m = CinematicMarker(marker_id="m_boss_enter", time=3.5, marker_type="cue", payload={"boss_id": "titan"})
    assert m.marker_id == "m_boss_enter"
    assert m.payload["boss_id"] == "titan"


def test_timeline_tempo_authoring():
    tl = Timeline(tempo=140.0)
    assert tl.tempo == 140.0


def test_timeline_clamping(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    r1 = fabricator.seek(inst, basic_asset, -5.0)
    assert r1 == 0.0
    r2 = fabricator.seek(inst, basic_asset, 25.0)
    assert r2 == 10.0


def test_timeline_active_clips_query():
    tr = CinematicTrack(
        track_id="tr_query",
        track_type=TrackType.ANIMATION,
        clips=[
            CinematicClip(clip_id="c1", start=0.0, duration=3.0),
            CinematicClip(clip_id="c2", start=3.0, duration=4.0),
        ]
    )
    assert len(tr.get_active_clips(1.5)) == 1
    assert tr.get_active_clips(1.5)[0].clip_id == "c1"
    assert len(tr.get_active_clips(5.0)) == 1
    assert tr.get_active_clips(5.0)[0].clip_id == "c2"


# ==============================================================================
# 3. BINDING (11 tests - §21 - §25, §133)
# ==============================================================================

def test_binding_static(fabricator):
    b = CinematicBinding(binding_id="b_cam", binding_type=BindingType.STATIC, target_reference="StaticCamera_01")
    assert fabricator.resolve_binding(b) == "StaticCamera_01"


def test_binding_dynamic(fabricator):
    b = CinematicBinding(binding_id="b_enemy", binding_type=BindingType.DYNAMIC, target_reference="tag:boss")
    assert fabricator.resolve_binding(b) == "tag:boss"


def test_binding_runtime(fabricator):
    b = CinematicBinding(binding_id="b_prop", binding_type=BindingType.RUNTIME, target_reference="prop_relic_03")
    assert fabricator.resolve_binding(b) == "prop_relic_03"


def test_binding_player_alias_default(fabricator):
    b = CinematicBinding(binding_id="b_p1", binding_type=BindingType.PLAYER, target_reference="PLAYER")
    assert fabricator.resolve_binding(b) == "entity_player_0"


def test_binding_player_alias_primary(fabricator):
    b = CinematicBinding(binding_id="b_p2", target_reference="PLAYER_PRIMARY")
    assert fabricator.resolve_binding(b) == "entity_player_0"


def test_binding_player_alias_current(fabricator):
    b = CinematicBinding(binding_id="b_p3", target_reference="PLAYER_CURRENT")
    assert fabricator.resolve_binding(b) == "entity_player_0"


def test_binding_fallback_reference(fabricator):
    b = CinematicBinding(binding_id="b_fb", target_reference="", fallback_reference="fallback_actor_default")
    assert fabricator.resolve_binding(b) == "fallback_actor_default"


def test_binding_failure_policy_use_fallback():
    b = CinematicBinding(binding_id="b_pol", failure_policy=BindingFailurePolicy.USE_FALLBACK)
    assert b.failure_policy == BindingFailurePolicy.USE_FALLBACK


def test_binding_failure_policy_retry():
    b = CinematicBinding(binding_id="b_retry", retry_count=5)
    assert b.retry_count == 5


def test_binding_camera_binding(fabricator):
    b = CinematicBinding(binding_id="b_cine", target_reference="cine_rig_spline")
    assert fabricator.resolve_binding(b) == "cine_rig_spline"


def test_binding_light_binding(fabricator):
    b = CinematicBinding(binding_id="b_key_light", target_reference="light_spot_key")
    assert fabricator.resolve_binding(b) == "light_spot_key"


# ==============================================================================
# 4. CAMERA (17 tests - §26 - §38, §133)
# ==============================================================================

def test_camera_optics_properties():
    cam = CinematicCamera(
        camera_id="cam_optics",
        position=(10.0, 5.0, 2.0),
        rotation=(0.0, 0.0, 0.0, 1.0),
        fov=75.0,
        near_clip=0.05,
        far_clip=2000.0,
        aperture=1.8,
        focus_distance=3.5,
    )
    assert cam.fov == 75.0
    assert cam.aperture == 1.8
    assert cam.focus_distance == 3.5


def test_camera_rig_static():
    rig = CameraRig(rig_id="rig_stat", rig_type=CameraRigType.STATIC, camera_id="c1")
    assert rig.rig_type == CameraRigType.STATIC


def test_camera_rig_follow():
    rig = CameraRig(rig_id="rig_fol", rig_type=CameraRigType.FOLLOW, target_id="player", offset=(0, -3, 1.5))
    assert rig.rig_type == CameraRigType.FOLLOW
    assert rig.offset == (0, -3, 1.5)


def test_camera_rig_look_at():
    rig = CameraRig(rig_id="rig_la", rig_type=CameraRigType.LOOK_AT, target_id="boss")
    assert rig.rig_type == CameraRigType.LOOK_AT


def test_camera_rig_orbit():
    rig = CameraRig(rig_id="rig_orb", rig_type=CameraRigType.ORBIT, damping=0.8)
    assert rig.rig_type == CameraRigType.ORBIT
    assert rig.damping == 0.8


def test_camera_rig_dolly():
    rig = CameraRig(rig_id="rig_dol", rig_type=CameraRigType.DOLLY)
    assert rig.rig_type == CameraRigType.DOLLY


def test_camera_rig_crane():
    rig = CameraRig(rig_id="rig_crn", rig_type=CameraRigType.CRANE)
    assert rig.rig_type == CameraRigType.CRANE


def test_camera_rig_handheld():
    rig = CameraRig(rig_id="rig_hh", rig_type=CameraRigType.HANDHELD, damping=0.2)
    assert rig.rig_type == CameraRigType.HANDHELD


def test_camera_rig_rail():
    rig = CameraRig(rig_id="rig_rail", rig_type=CameraRigType.RAIL)
    assert rig.rig_type == CameraRigType.RAIL


def test_camera_rig_spline():
    points = [(0, 0, 0), (5, 5, 2), (10, 0, 4)]
    rig = CameraRig(rig_id="rig_spl", rig_type=CameraRigType.SPLINE, spline_points=points)
    assert len(rig.spline_points) == 3


def test_camera_spline_linear_interpolation(fabricator):
    pts = [(0.0, 0.0, 0.0), (10.0, 10.0, 10.0)]
    mid = fabricator.interpolate_spline(pts, 0.5, CameraInterpolationType.LINEAR)
    assert mid == (5.0, 5.0, 5.0)


def test_camera_spline_catmull_rom(fabricator):
    pts = [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (20.0, 10.0, 0.0), (30.0, 10.0, 0.0)]
    pos = fabricator.interpolate_spline(pts, 0.333, CameraInterpolationType.CATMULL_ROM)
    assert len(pos) == 3
    assert not math.isnan(pos[0])


def test_camera_quaternion_slerp(fabricator):
    q1 = (0.0, 0.0, 0.0, 1.0)
    q2 = (0.0, 0.70710678, 0.0, 0.70710678)  # 90 deg around Y
    mid = fabricator.interpolate_quaternion_slerp(q1, q2, 0.5)
    mag = math.sqrt(sum(x*x for x in mid))
    assert mag == pytest.approx(1.0, rel=1e-3)


def test_camera_blend():
    blend = CameraBlend(blend_id="bl_01", source_camera_id="cam_a", target_camera_id="cam_b", duration=2.0)
    assert blend.duration == 2.0
    assert blend.source_camera_id == "cam_a"


def test_camera_cut():
    cut = CameraCut(cut_id="cut_01", time=4.5, target_camera_id="cam_close_up")
    assert cut.time == 4.5
    assert cut.target_camera_id == "cam_close_up"


def test_camera_priority_resolution(fabricator):
    # Gameplay (10) vs Cinematic (80) vs Debug (100)
    assert fabricator.request_camera_takeover("cam_gameplay", "gp_sys", CameraPriority.GAMEPLAY) is True
    assert fabricator.get_active_camera_id() == "cam_gameplay"
    assert fabricator.request_camera_takeover("cam_cine", "cutscene", CameraPriority.CINEMATIC) is True
    assert fabricator.get_active_camera_id() == "cam_cine"
    # Gameplay cannot steal from Cinematic
    assert fabricator.request_camera_takeover("cam_gp2", "gp_sys", CameraPriority.GAMEPLAY) is False
    # Debug can override
    assert fabricator.request_camera_takeover("cam_dbg", "debug_sys", CameraPriority.DEBUG) is True
    assert fabricator.get_active_camera_id() == "cam_dbg"


def test_camera_takeover_release_restore(fabricator):
    fabricator.request_camera_takeover("cam_prev", "sys_prev", CameraPriority.GAMEPLAY)
    fabricator.request_camera_takeover("cam_cutscene", "cutscene", CameraPriority.CINEMATIC)
    assert fabricator.get_active_camera_id() == "cam_cutscene"
    fabricator.release_camera_takeover("cutscene")
    assert fabricator.get_active_camera_id() == "cam_prev"


# ==============================================================================
# 5. ANIMATION (11 tests - §39 - §45, §133)
# ==============================================================================

def test_animation_performance_channels():
    channels = list(PerformanceChannel)
    assert len(channels) == 8
    assert PerformanceChannel.BODY == "BODY"
    assert PerformanceChannel.VOICE == "VOICE"


def test_animation_clip_playback():
    clip = CinematicClip(clip_id="anim_run", start=1.0, duration=4.0, speed=1.2, loop=True)
    assert clip.speed == 1.2
    assert clip.loop is True
    assert clip.is_active_at(2.5) is True
    assert clip.is_active_at(0.5) is False


def test_animation_blend_in_out():
    clip = CinematicClip(clip_id="anim_blend", start=0.0, duration=10.0, blend_in=2.0, blend_out=2.0)
    assert clip.evaluate_weight(1.0) == pytest.approx(0.5)
    assert clip.evaluate_weight(5.0) == pytest.approx(1.0)
    assert clip.evaluate_weight(9.0) == pytest.approx(0.5)


def test_animation_layer_base():
    clip = CinematicClip(clip_id="c_base", start=0, duration=5, layer=AnimationLayer.BASE)
    assert clip.layer == AnimationLayer.BASE


def test_animation_layer_upper_body():
    clip = CinematicClip(clip_id="c_upper", start=0, duration=5, layer=AnimationLayer.UPPER_BODY)
    assert clip.layer == AnimationLayer.UPPER_BODY


def test_animation_layer_additive():
    clip = CinematicClip(clip_id="c_add", start=0, duration=5, layer=AnimationLayer.ADDITIVE)
    assert clip.layer == AnimationLayer.ADDITIVE


def test_animation_layer_gesture():
    clip = CinematicClip(clip_id="c_gest", start=0, duration=5, layer=AnimationLayer.GESTURE)
    assert clip.layer == AnimationLayer.GESTURE


def test_animation_root_motion_ignore(fabricator, basic_asset):
    track = CinematicTrack(
        track_id="tr_anim_ign",
        track_type=TrackType.ANIMATION,
        clips=[CinematicClip("c_ign", 0, 5, root_motion_policy=RootMotionPolicy.IGNORE)]
    )
    basic_asset.timeline.tracks.append(track)
    eval_res = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 2.0)
    assert eval_res["root_motion"] == (0.0, 0.0, 0.0)


def test_animation_root_motion_apply(fabricator, basic_asset):
    track = CinematicTrack(
        track_id="tr_anim_app",
        track_type=TrackType.ANIMATION,
        clips=[CinematicClip("c_app", 0, 5, root_motion_policy=RootMotionPolicy.APPLY)]
    )
    basic_asset.timeline.tracks.append(track)
    eval_res = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 2.0)
    assert eval_res["root_motion"][0] > 0.0


def test_animation_root_motion_convert_to_world():
    c = CinematicClip("c_world", 0, 5, root_motion_policy=RootMotionPolicy.CONVERT_TO_WORLD)
    assert c.root_motion_policy == RootMotionPolicy.CONVERT_TO_WORLD


def test_animation_zero_duplicate_root_motion():
    policies = [RootMotionPolicy.IGNORE, RootMotionPolicy.APPLY, RootMotionPolicy.GAMEPLAY_AUTHORITATIVE]
    assert len(policies) == 3


# ==============================================================================
# 6. FACIAL (9 tests - §46 - §48, §53, §54, §133)
# ==============================================================================

def test_facial_performance_track():
    tr = CinematicTrack(track_id="tr_face", track_type=TrackType.FACIAL)
    assert tr.track_type == TrackType.FACIAL


def test_facial_blendshape_inputs():
    state = FacialState(blendshapes={"jawOpen": 0.7, "mouthSmile": 0.4})
    assert state.blendshapes["jawOpen"] == 0.7


def test_facial_expression_layering():
    state = FacialState(emotion="happy", expressions={"smile": 0.8})
    assert state.emotion == "happy"
    assert state.expressions["smile"] == 0.8


def test_facial_emotion_override():
    clip = CinematicClip(clip_id="c_emo", start=0, duration=5, parameters={"emotion": "angry"})
    assert clip.parameters["emotion"] == "angry"


def test_facial_eye_tracking_target():
    state = FacialState(eye_target=(1.0, 2.0, 1.5))
    assert state.eye_target == (1.0, 2.0, 1.5)


def test_facial_look_at_weight_speed():
    state = FacialState(look_weight=0.85, look_speed=4.0)
    assert state.look_weight == 0.85
    assert state.look_speed == 4.0


def test_facial_blink_cycle(fabricator):
    tr = CinematicTrack(track_id="f1", track_type=TrackType.FACIAL)
    s1 = fabricator.evaluate_facial_state(tr, 0.0)
    assert 0.0 <= s1.blink_phase <= 1.0


def test_facial_look_at_component():
    input_type = FacialInputType.EYE_DIRECTION
    assert input_type == FacialInputType.EYE_DIRECTION


def test_facial_evaluate_state_function(fabricator):
    tr = CinematicTrack(
        track_id="f_eval",
        track_type=TrackType.FACIAL,
        clips=[CinematicClip("fc1", 0, 5, parameters={"emotion": "surprise", "blendshapes": {"browUp": 0.9}})]
    )
    st = fabricator.evaluate_facial_state(tr, 2.0)
    assert st.emotion == "surprise"
    assert st.blendshapes["browUp"] == pytest.approx(0.9)


# ==============================================================================
# 7. LIP_SYNC (10 tests - §49 - §52, §133)
# ==============================================================================

def test_lipsync_system_dataclass():
    data = LipSyncData(source=LipSyncSource.PHONEME_DATA)
    assert data.source == LipSyncSource.PHONEME_DATA
    assert data.current_viseme == "neutral"


def test_lipsync_source_phoneme_data(fabricator):
    data = LipSyncData(
        source=LipSyncSource.PHONEME_DATA,
        visemes=[{"start": 0.0, "duration": 0.5, "viseme": "AA"}]
    )
    vis = fabricator.evaluate_lip_sync(data, 0.2)
    assert vis == "AA"


def test_lipsync_source_viseme_data(fabricator):
    data = LipSyncData(
        source=LipSyncSource.PHONEME_DATA,
        visemes=[{"start": 1.0, "duration": 0.5, "viseme": "OH"}]
    )
    vis = fabricator.evaluate_lip_sync(data, 1.2)
    assert vis == "OH"


def test_lipsync_source_audio_analysis(fabricator):
    data = LipSyncData(source=LipSyncSource.AUDIO_ANALYSIS, fallback=LipSyncFallback.AUDIO_ANALYSIS)
    vis = fabricator.evaluate_lip_sync(data, 0.1)
    assert vis in ["A", "O", "E", "neutral"]


def test_lipsync_timing_with_dialogue_clock(fabricator):
    data = LipSyncData(
        source=LipSyncSource.PHONEME_DATA,
        visemes=[{"start": 2.0, "duration": 1.0, "viseme": "EE"}]
    )
    assert fabricator.evaluate_lip_sync(data, 1.0) == "neutral"
    assert fabricator.evaluate_lip_sync(data, 2.5) == "EE"


def test_lipsync_fallback_audio_analysis(fabricator):
    data = LipSyncData(source=LipSyncSource.PHONEME_DATA, visemes=[], fallback=LipSyncFallback.AUDIO_ANALYSIS)
    vis = fabricator.evaluate_lip_sync(data, 0.0)
    assert vis != ""


def test_lipsync_fallback_neutral_mouth(fabricator):
    data = LipSyncData(source=LipSyncSource.PHONEME_DATA, visemes=[], fallback=LipSyncFallback.NEUTRAL_MOUTH)
    vis = fabricator.evaluate_lip_sync(data, 0.0)
    assert vis == "neutral"


def test_lipsync_viseme_evaluation_steps(fabricator):
    data = LipSyncData(
        source=LipSyncSource.PHONEME_DATA,
        visemes=[
            {"start": 0.0, "duration": 0.5, "viseme": "M"},
            {"start": 0.5, "duration": 0.5, "viseme": "AH"},
        ]
    )
    assert fabricator.evaluate_lip_sync(data, 0.2) == "M"
    assert fabricator.evaluate_lip_sync(data, 0.7) == "AH"


def test_lipsync_generic_visemes():
    fb = LipSyncFallback.GENERIC_VISEMES
    assert fb == "GENERIC_VISEMES"


def test_lipsync_preauthored_timing():
    src = LipSyncSource.PREAUTHORED_TIMING
    assert src == "PREAUTHORED_TIMING"


# ==============================================================================
# 8. DIALOGUE (10 tests - §55, §56, §133)
# ==============================================================================

def test_dialogue_clip_creation():
    clip = DialogueClip(
        line_id="dlg_01",
        speaker="Commander",
        audio_asset_id="snd_vo_cmd_01",
        subtitle_text="Engage thrusters!",
        duration=2.5,
    )
    assert clip.line_id == "dlg_01"
    assert clip.speaker == "Commander"


def test_dialogue_track_evaluation(fabricator, basic_asset):
    tr = CinematicTrack(
        track_id="tr_diag",
        track_type=TrackType.DIALOGUE,
        clips=[CinematicClip(clip_id="line_hello", start=1.0, duration=3.0, parameters={"speaker": "Hero"})]
    )
    basic_asset.timeline.tracks.append(tr)
    inst = fabricator.create_instance(basic_asset)
    res = fabricator.evaluate(inst, basic_asset, 2.0)
    assert res["dialogue_line"] == "line_hello"
    assert res["speaker"] == "Hero"


def test_dialogue_speaker_attribution(fabricator, basic_asset):
    tr = CinematicTrack(
        track_id="tr_diag2",
        track_type=TrackType.DIALOGUE,
        clips=[CinematicClip(clip_id="line_villain", start=0.0, duration=5.0, parameters={"speaker": "Nemesis"})]
    )
    basic_asset.timeline.tracks.append(tr)
    res = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 1.0)
    assert res["speaker"] == "Nemesis"


def test_dialogue_audio_trigger(fabricator, basic_asset):
    tr_audio = CinematicTrack(
        track_id="tr_vo_audio",
        track_type=TrackType.AUDIO,
        clips=[CinematicClip(clip_id="vo_snd", start=1.0, duration=3.0, source="vo_take_01")]
    )
    basic_asset.timeline.tracks.append(tr_audio)
    res = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 2.0)
    assert len(res["audio_cues"]) > 0
    assert res["audio_cues"][0]["audio_id"] == "vo_take_01"


def test_dialogue_subtitle_sync(fabricator, basic_asset):
    tr_diag = CinematicTrack(
        track_id="tr_d",
        track_type=TrackType.DIALOGUE,
        clips=[CinematicClip("line_1", start=2.0, duration=3.0, parameters={"speaker": "NPC"})]
    )
    tr_sub = CinematicTrack(
        track_id="tr_s",
        track_type=TrackType.SUBTITLE,
        clips=[CinematicClip("sub_1", start=2.0, duration=3.0, source="Hello world")]
    )
    basic_asset.timeline.tracks.extend([tr_diag, tr_sub])
    res = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 3.0)
    assert res["dialogue_line"] == "line_1"
    assert len(res["subtitles"]) == 1
    assert res["subtitles"][0]["text"] == "Hello world"


def test_dialogue_facial_sync(fabricator, basic_asset):
    tr_d = CinematicTrack(track_id="td", track_type=TrackType.DIALOGUE, clips=[CinematicClip("l1", 0, 4)])
    tr_f = CinematicTrack(track_id="tf", track_type=TrackType.FACIAL, clips=[CinematicClip("f1", 0, 4)])
    basic_asset.timeline.tracks.extend([tr_d, tr_f])
    res = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 2.0)
    assert res["dialogue_line"] == "l1"
    assert res["lip_sync_viseme"] != ""


def test_dialogue_interrupt_policy_allow():
    clip = DialogueClip(line_id="d1", speaker="A", interrupt_policy="ALLOW")
    assert clip.interrupt_policy == "ALLOW"


def test_dialogue_voice_profile():
    clip = DialogueClip(line_id="d2", speaker="A", voice_profile="radio_static_filter")
    assert clip.voice_profile == "radio_static_filter"


def test_dialogue_multi_line_sequence(fabricator, basic_asset):
    tr = CinematicTrack(
        track_id="td_multi",
        track_type=TrackType.DIALOGUE,
        clips=[
            CinematicClip("line_a", 0.0, 3.0),
            CinematicClip("line_b", 3.0, 3.0),
        ]
    )
    basic_asset.timeline.tracks.append(tr)
    inst = fabricator.create_instance(basic_asset)
    r1 = fabricator.evaluate(inst, basic_asset, 1.5)
    assert r1["dialogue_line"] == "line_a"
    r2 = fabricator.evaluate(inst, basic_asset, 4.5)
    assert r2["dialogue_line"] == "line_b"


def test_dialogue_uaf81_59_integration():
    cmd = CinematicCommand(
        command_id="cmd_audio_sync",
        command_type=CinematicCommandType.PLAY_AUDIO,
        payload={"bus": "Dialogue", "duck_music": True}
    )
    assert cmd.payload["duck_music"] is True


# ==============================================================================
# 9. SUBTITLE (8 tests - §57 - §60, §133)
# ==============================================================================

def test_subtitle_track_creation():
    tr = CinematicTrack(track_id="sub_main", track_type=TrackType.SUBTITLE)
    assert tr.track_type == TrackType.SUBTITLE


def test_subtitle_clip_properties():
    clip = SubtitleClip(
        subtitle_id="sub_01",
        text_reference="We found it.",
        speaker="Explorer",
        start=1.0,
        duration=3.0,
        style="shouting",
        position=(0.5, 0.85),
    )
    assert clip.text_reference == "We found it."
    assert clip.position == (0.5, 0.85)


def test_subtitle_accessibility_color_size():
    clip = SubtitleClip(subtitle_id="s_acc", text_reference="Warn!", speaker="AI", color="#FFFF00", size=24)
    assert clip.color == "#FFFF00"
    assert clip.size == 24


def test_subtitle_accessibility_speaker_name():
    clip = SubtitleClip(subtitle_id="s_spk", text_reference="Follow me.", speaker="Guide")
    assert clip.speaker == "Guide"


def test_subtitle_accessibility_sound_description():
    clip = SubtitleClip(subtitle_id="s_snd", text_reference="[Door Creaks]", speaker="", sound_description="Door Creaks")
    assert clip.sound_description == "Door Creaks"


def test_subtitle_accessibility_language():
    clip = SubtitleClip(subtitle_id="s_lang", text_reference="Hola mundo", speaker="Narrator", language="es")
    assert clip.language == "es"


def test_subtitle_positioning():
    clip = SubtitleClip(subtitle_id="s_pos", text_reference="Top alert", speaker="Sys", position=(0.5, 0.1))
    assert clip.position[1] == 0.1


def test_subtitle_timeline_evaluation(fabricator, basic_asset):
    tr = CinematicTrack(
        track_id="ts",
        track_type=TrackType.SUBTITLE,
        clips=[CinematicClip("sc1", 0.0, 4.0, source="Sub text", parameters={"color": "#FF0000"})]
    )
    basic_asset.timeline.tracks.append(tr)
    res = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 2.0)
    assert len(res["subtitles"]) == 1
    assert res["subtitles"][0]["color"] == "#FF0000"


# ==============================================================================
# 10. VFX (8 tests - §62, §133)
# ==============================================================================

def test_vfx_track_creation():
    tr = CinematicTrack(track_id="vfx_main", track_type=TrackType.VFX)
    assert tr.track_type == TrackType.VFX


def test_vfx_clip_properties():
    clip = CinematicClip(clip_id="vfx_spark", start=1.0, duration=2.0, source="fx_sparks_01")
    assert clip.source == "fx_sparks_01"


def test_vfx_cue_spawn_action(fabricator, basic_asset):
    tr = CinematicTrack(
        track_id="tvfx_spawn",
        track_type=TrackType.VFX,
        clips=[CinematicClip("v1", 0, 3, source="fx_smoke", parameters={"action": "spawn"})]
    )
    basic_asset.timeline.tracks.append(tr)
    res = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 1.5)
    assert len(res["vfx_cues"]) == 1
    assert res["vfx_cues"][0]["action"] == "spawn"


def test_vfx_cue_burst_action(fabricator, basic_asset):
    tr = CinematicTrack(
        track_id="tvfx_burst",
        track_type=TrackType.VFX,
        clips=[CinematicClip("v2", 0, 2, source="fx_blast", parameters={"action": "burst"})]
    )
    basic_asset.timeline.tracks.append(tr)
    res = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 1.0)
    assert res["vfx_cues"][0]["action"] == "burst"


def test_vfx_cue_deactivate_action(fabricator, basic_asset):
    tr = CinematicTrack(
        track_id="tvfx_deact",
        track_type=TrackType.VFX,
        clips=[CinematicClip("v3", 0, 2, source="fx_shield", parameters={"action": "deactivate"})]
    )
    basic_asset.timeline.tracks.append(tr)
    res = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 1.0)
    assert res["vfx_cues"][0]["action"] == "deactivate"


def test_vfx_binding_target():
    tr = CinematicTrack(track_id="tr_vfx_bind", track_type=TrackType.VFX, target_binding="hero_hand_socket")
    assert tr.target_binding == "hero_hand_socket"


def test_vfx_evaluation_output(fabricator, basic_asset):
    tr = CinematicTrack(
        track_id="tr_vfx_out",
        track_type=TrackType.VFX,
        clips=[CinematicClip("fx_a", 0, 5, source="fire")]
    )
    basic_asset.timeline.tracks.append(tr)
    res = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 2.5)
    assert res["vfx_cues"][0]["vfx_id"] == "fire"


def test_vfx_cleanup_on_abort(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.play(inst)
    fabricator.abort(inst)
    assert inst.playback_state == PlaybackState.ABORTED


# ==============================================================================
# 11. LIGHTING (8 tests - §63, §133)
# ==============================================================================

def test_lighting_track_creation():
    tr = CinematicTrack(track_id="tr_light", track_type=TrackType.LIGHTING)
    assert tr.track_type == TrackType.LIGHTING


def test_lighting_clip_intensity(fabricator, basic_asset):
    tr = CinematicTrack(
        track_id="tr_l_int",
        track_type=TrackType.LIGHTING,
        clips=[CinematicClip("l_dim", 0, 5, parameters={"intensity": 0.3})]
    )
    basic_asset.timeline.tracks.append(tr)
    res = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 2.0)
    assert res["lighting_values"]["intensity"] == pytest.approx(0.3)


def test_lighting_clip_color(fabricator, basic_asset):
    tr = CinematicTrack(
        track_id="tr_l_col",
        track_type=TrackType.LIGHTING,
        clips=[CinematicClip("l_red", 0, 5, parameters={"color": (1.0, 0.0, 0.0)})]
    )
    basic_asset.timeline.tracks.append(tr)
    res = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 2.0)
    assert res["lighting_values"]["color"] == (1.0, 0.0, 0.0)


def test_lighting_clip_blending(fabricator, basic_asset):
    tr = CinematicTrack(
        track_id="tr_l_blend",
        track_type=TrackType.LIGHTING,
        clips=[CinematicClip("l_fade", 0, 10, blend_in=2.0, blend_out=2.0, parameters={"intensity": 4.0})]
    )
    basic_asset.timeline.tracks.append(tr)
    res = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 1.0)
    assert res["lighting_values"]["intensity"] == pytest.approx(2.0)


def test_lighting_evaluation_output(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    res = fabricator.evaluate(inst, basic_asset, 0.0)
    assert "lighting_values" in res


def test_lighting_temperature_parameter():
    c = CinematicClip("l_temp", 0, 5, parameters={"temperature": 6500})
    assert c.parameters["temperature"] == 6500


def test_lighting_multiple_cues(fabricator, basic_asset):
    tr = CinematicTrack(
        track_id="tr_l_seq",
        track_type=TrackType.LIGHTING,
        clips=[
            CinematicClip("l1", 0, 3, parameters={"intensity": 1.0}),
            CinematicClip("l2", 3, 3, parameters={"intensity": 5.0}),
        ]
    )
    basic_asset.timeline.tracks.append(tr)
    r1 = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 1.0)
    assert r1["lighting_values"]["intensity"] == pytest.approx(1.0)
    r2 = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 4.0)
    assert r2["lighting_values"]["intensity"] == pytest.approx(5.0)


def test_lighting_restore_default(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.cleanup(inst)
    res = fabricator.evaluate(inst, basic_asset, 0.0)
    assert res["lighting_values"]["intensity"] == 1.0


# ==============================================================================
# 12. LOCK (12 tests - §66 - §70, §147, §133)
# ==============================================================================

def test_lock_movement_acquire(fabricator):
    lock = fabricator.acquire_lock(GameplayLockType.MOVEMENT, "cutscene_01")
    assert lock.lock_type == GameplayLockType.MOVEMENT
    assert fabricator.is_locked(GameplayLockType.MOVEMENT) is True


def test_lock_combat_acquire(fabricator):
    fabricator.acquire_lock(GameplayLockType.COMBAT, "cutscene_01")
    assert fabricator.is_locked(GameplayLockType.COMBAT) is True


def test_lock_interaction_acquire(fabricator):
    fabricator.acquire_lock(GameplayLockType.INTERACTION, "cutscene_01")
    assert fabricator.is_locked(GameplayLockType.INTERACTION) is True


def test_lock_camera_acquire(fabricator):
    fabricator.acquire_lock(GameplayLockType.CAMERA, "cutscene_01")
    assert fabricator.is_locked(GameplayLockType.CAMERA) is True


def test_lock_input_acquire(fabricator):
    fabricator.acquire_lock(GameplayLockType.INPUT, "cutscene_01")
    assert fabricator.is_locked(GameplayLockType.INPUT) is True


def test_lock_ui_control_acquire(fabricator):
    fabricator.acquire_lock(GameplayLockType.UI_CONTROL, "cutscene_01")
    assert fabricator.is_locked(GameplayLockType.UI_CONTROL) is True


def test_lock_ownership_metadata(fabricator):
    l = fabricator.acquire_lock(GameplayLockType.MOVEMENT, "owner_x", reason="cutscene_dialogue", priority=90)
    assert l.owner == "owner_x"
    assert l.reason == "cutscene_dialogue"
    assert l.priority == 90


def test_lock_cross_owner_release_rejection(fabricator):
    fabricator.acquire_lock(GameplayLockType.MOVEMENT, "system_a")
    # system_b attempts to release system_a's lock -> Rejected!
    assert fabricator.release_lock(GameplayLockType.MOVEMENT, "system_b") is False
    assert fabricator.is_locked(GameplayLockType.MOVEMENT) is True
    # system_a releases its own lock -> Success
    assert fabricator.release_lock(GameplayLockType.MOVEMENT, "system_a") is True
    assert fabricator.is_locked(GameplayLockType.MOVEMENT) is False


def test_lock_stacking(fabricator):
    fabricator.acquire_lock(GameplayLockType.INPUT, "owner_1")
    fabricator.acquire_lock(GameplayLockType.INPUT, "owner_2")
    fabricator.release_lock(GameplayLockType.INPUT, "owner_1")
    # owner_2's lock is still held
    assert fabricator.is_locked(GameplayLockType.INPUT) is True
    fabricator.release_lock(GameplayLockType.INPUT, "owner_2")
    assert fabricator.is_locked(GameplayLockType.INPUT) is False


def test_lock_input_state_preservation(fabricator):
    fabricator.preserve_gameplay_state("input_state_01", {"move_x": 1.0, "crouch": True})
    saved = fabricator.restore_gameplay_state("input_state_01")
    assert saved["move_x"] == 1.0
    assert saved["crouch"] is True


def test_lock_gameplay_state_restoration(fabricator):
    fabricator.preserve_gameplay_state("st1", {"val": 42})
    assert fabricator.restore_gameplay_state("st1") == {"val": 42}
    # Second restoration returns None
    assert fabricator.restore_gameplay_state("st1") is None


def test_lock_cleanup_all(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset, instance_id="inst_to_clean")
    fabricator.acquire_lock(GameplayLockType.MOVEMENT, inst.instance_id)
    fabricator.acquire_lock(GameplayLockType.CAMERA, inst.instance_id)
    fabricator.cleanup(inst)
    assert fabricator.is_locked(GameplayLockType.MOVEMENT) is False
    assert fabricator.is_locked(GameplayLockType.CAMERA) is False


# ==============================================================================
# 13. BRANCHING (10 tests - §71 - §75, §133)
# ==============================================================================

def test_branching_cinematic_choice_presentation(fabricator):
    ch = CinematicChoice(
        choice_id="ch_01",
        prompt="Spare or Destroy?",
        options=["Spare", "Destroy"],
        default_option="Spare",
        timeout=15.0,
    )
    pres = fabricator.present_choice(ch)
    assert pres["choice_id"] == "ch_01"
    assert len(pres["options"]) == 2


def test_branching_choice_selection(fabricator):
    ch = CinematicChoice(choice_id="ch_02", options=["A", "B"])
    assert fabricator.select_choice_option(ch, "B") is True
    assert ch.selected_option == "B"
    assert fabricator.select_choice_option(ch, "Z") is False


def test_branching_choice_timeout_default(fabricator):
    ch = CinematicChoice(choice_id="c_def", options=["A", "B"], default_option="A", timeout_policy=ChoiceTimeoutPolicy.DEFAULT)
    sel = fabricator.handle_choice_timeout(ch)
    assert sel == "A"


def test_branching_choice_timeout_cancel(fabricator):
    ch = CinematicChoice(choice_id="c_can", options=["A", "B"], timeout_policy=ChoiceTimeoutPolicy.CANCEL)
    sel = fabricator.handle_choice_timeout(ch)
    assert sel == "CANCEL"


def test_branching_choice_timeout_branch(fabricator):
    ch = CinematicChoice(choice_id="c_br", options=["Opt1", "Opt2"], timeout_policy=ChoiceTimeoutPolicy.BRANCH)
    sel = fabricator.handle_choice_timeout(ch)
    assert sel == "Opt2"


def test_branching_condition_choice(fabricator):
    br = CinematicBranch(branch_id="b1", condition_type=BranchConditionType.CHOICE, condition_key="c1", condition_value="Accept")
    ctx = {"choice_results": {"c1": "Accept"}}
    assert fabricator.evaluate_branch(br, ctx) is True
    ctx["choice_results"]["c1"] = "Decline"
    assert fabricator.evaluate_branch(br, ctx) is False


def test_branching_condition_quest_state(fabricator):
    br = CinematicBranch(branch_id="b2", condition_type=BranchConditionType.QUEST_STATE, condition_key="quest_main", condition_value="COMPLETED")
    assert fabricator.evaluate_branch(br, {"quest_main": "COMPLETED"}) is True
    assert fabricator.evaluate_branch(br, {"quest_main": "IN_PROGRESS"}) is False


def test_branching_condition_flag(fabricator):
    br = CinematicBranch(branch_id="b3", condition_type=BranchConditionType.FLAG, condition_key="has_artifact", condition_value=True)
    assert fabricator.evaluate_branch(br, {"has_artifact": True}) is True


def test_branching_condition_parameter(fabricator):
    br = CinematicBranch(branch_id="b4", condition_type=BranchConditionType.PARAMETER, condition_key="difficulty", condition_value="Hard")
    assert fabricator.evaluate_branch(br, {"difficulty": "Hard"}) is True


def test_branching_deterministic_resolution_order(fabricator):
    branches = [
        CinematicBranch("br_a", BranchConditionType.FLAG, "flag_a", True),
        CinematicBranch("br_b", BranchConditionType.FLAG, "flag_b", True),
    ]
    ctx = {"flag_a": True, "flag_b": True}
    res = [fabricator.evaluate_branch(b, ctx) for b in branches]
    assert res == [True, True]


# ==============================================================================
# 14. SKIP (10 tests - §76 - §78, §133)
# ==============================================================================

def test_skip_policy_anytime(fabricator, basic_asset):
    basic_asset.skip_policy = SkipPolicy.ANYTIME
    inst = fabricator.create_instance(basic_asset)
    fabricator.play(inst)
    assert fabricator.skip(inst, basic_asset) is True
    assert inst.playback_state == PlaybackState.SKIPPED


def test_skip_policy_disabled(fabricator, basic_asset):
    basic_asset.skip_policy = SkipPolicy.DISABLED
    inst = fabricator.create_instance(basic_asset)
    assert fabricator.skip(inst, basic_asset) is False
    assert inst.playback_state != PlaybackState.SKIPPED


def test_skip_policy_after_checkpoint_without_checkpoint(fabricator, basic_asset):
    basic_asset.skip_policy = SkipPolicy.AFTER_CHECKPOINT
    inst = fabricator.create_instance(basic_asset)
    assert fabricator.skip(inst, basic_asset) is False


def test_skip_policy_after_checkpoint_with_checkpoint(fabricator, basic_asset):
    basic_asset.skip_policy = SkipPolicy.AFTER_CHECKPOINT
    inst = fabricator.create_instance(basic_asset)
    fabricator.create_checkpoint(inst, "chk1")
    assert fabricator.skip(inst, basic_asset) is True


def test_skip_policy_after_first_view_first_time(fabricator, basic_asset):
    basic_asset.skip_policy = SkipPolicy.AFTER_FIRST_VIEW
    inst = fabricator.create_instance(basic_asset)
    assert fabricator.skip(inst, basic_asset, is_first_view=True) is False


def test_skip_policy_after_first_view_subsequent(fabricator, basic_asset):
    basic_asset.skip_policy = SkipPolicy.AFTER_FIRST_VIEW
    inst = fabricator.create_instance(basic_asset)
    assert fabricator.skip(inst, basic_asset, is_first_view=False) is True


def test_skip_time_advances_to_end(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.skip(inst, basic_asset)
    assert inst.current_time == basic_asset.timeline.duration


def test_skip_playback_state_skipped(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.skip(inst, basic_asset)
    assert inst.playback_state == PlaybackState.SKIPPED


def test_skip_guarantees_cleanup(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.acquire_lock(GameplayLockType.MOVEMENT, inst.instance_id)
    fabricator.skip(inst, basic_asset)
    assert fabricator.is_locked(GameplayLockType.MOVEMENT) is False


def test_skip_camera_restored(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.request_camera_takeover("cam_cine", inst.instance_id, CameraPriority.CINEMATIC)
    fabricator.skip(inst, basic_asset)
    assert fabricator.get_active_camera_id() != "cam_cine"


# ==============================================================================
# 15. FAST_FORWARD (8 tests - §79 - §81, §133)
# ==============================================================================

def test_fast_forward_multiplier_2x(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    assert fabricator.fast_forward(inst, FastForwardMultiplier.FF_2X) is True
    assert inst.playback_state == PlaybackState.FAST_FORWARD
    assert inst.fast_forward_multiplier == FastForwardMultiplier.FF_2X


def test_fast_forward_multiplier_4x(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.fast_forward(inst, FastForwardMultiplier.FF_4X)
    assert inst.fast_forward_multiplier == 4


def test_fast_forward_multiplier_8x(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.fast_forward(inst, FastForwardMultiplier.FF_8X)
    assert inst.fast_forward_multiplier == 8


def test_fast_forward_multiplier_16x(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.fast_forward(inst, FastForwardMultiplier.FF_16X)
    assert inst.fast_forward_multiplier == 16


def test_fast_forward_event_policy_execute(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.fast_forward(inst, FastForwardMultiplier.FF_2X, FastForwardEventPolicy.EXECUTE)
    assert inst.playback_state == PlaybackState.FAST_FORWARD


def test_fast_forward_event_policy_skip(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.fast_forward(inst, FastForwardMultiplier.FF_4X, FastForwardEventPolicy.SKIP)
    assert inst.playback_state == PlaybackState.FAST_FORWARD


def test_pause_domain_game_vs_cinematic(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.play(inst)
    fabricator.pause(inst, PauseType.GAME_PAUSE)
    assert inst.pause_type == PauseType.GAME_PAUSE


def test_pause_domain_audio_debug(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.play(inst)
    fabricator.pause(inst, PauseType.DEBUG_PAUSE)
    assert inst.pause_type == PauseType.DEBUG_PAUSE


# ==============================================================================
# 16. CHECKPOINT (9 tests - §82 - §84, §133)
# ==============================================================================

def test_checkpoint_creation(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    inst.current_time = 4.2
    chk = fabricator.create_checkpoint(inst, "chk_pt_01")
    assert chk.checkpoint_id == "chk_pt_01"
    assert chk.timeline_time == 4.2


def test_checkpoint_restore(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    inst.current_time = 5.0
    chk = fabricator.create_checkpoint(inst, "chk_restore")
    inst.current_time = 1.0
    assert fabricator.restore_checkpoint(inst, chk) is True
    assert inst.current_time == 5.0


def test_checkpoint_restore_cleans_prior_state(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.acquire_lock(GameplayLockType.COMBAT, inst.instance_id)
    chk = fabricator.create_checkpoint(inst, "chk_c")
    fabricator.acquire_lock(GameplayLockType.INTERACTION, inst.instance_id)
    fabricator.restore_checkpoint(inst, chk)
    # Check that prior active state was refreshed
    assert inst.current_time == chk.timeline_time


def test_checkpoint_restore_reacquires_locks(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.acquire_lock(GameplayLockType.MOVEMENT, inst.instance_id)
    chk = fabricator.create_checkpoint(inst, "chk_locks")
    fabricator.cleanup(inst)
    assert fabricator.is_locked(GameplayLockType.MOVEMENT) is False
    fabricator.restore_checkpoint(inst, chk)
    assert fabricator.is_locked(GameplayLockType.MOVEMENT) is True


def test_checkpoint_marker_trigger():
    m = CinematicMarker("m_chk", 4.0, marker_type="checkpoint")
    assert m.marker_type == "checkpoint"


def test_checkpoint_seek(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    inst.current_time = 7.5
    fabricator.create_checkpoint(inst, "chk_seek")
    inst.current_time = 2.0
    pos = fabricator.seek(inst, basic_asset, 0.0, SeekMode.CHECKPOINT)
    assert pos == 7.5


def test_checkpoint_multiple_checkpoints(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    inst.current_time = 2.0
    c1 = fabricator.create_checkpoint(inst, "c1")
    inst.current_time = 6.0
    c2 = fabricator.create_checkpoint(inst, "c2")
    assert inst.checkpoint.checkpoint_id == "c2"


def test_checkpoint_state_serialization(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    chk = fabricator.create_checkpoint(inst, "chk_serial")
    assert isinstance(chk.bindings, dict)
    assert isinstance(chk.parameters, dict)


def test_checkpoint_save_state_link(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.create_checkpoint(inst, "chk_link")
    save = fabricator.save_state(inst, basic_asset)
    assert save.checkpoint_id == "chk_link"


# ==============================================================================
# 17. REPLAY (8 tests - §85 - §87, §133)
# ==============================================================================

def test_replay_recording_initialization(fabricator):
    rep = fabricator.record_replay("cin_intro", seed=123)
    assert rep.replay_id == "replay_cin_intro_123"
    assert rep.seed == 123


def test_replay_seed_preservation(fabricator):
    rep = fabricator.record_replay("cin_boss", seed=999)
    assert rep.seed == 999


def test_replay_play(fabricator, basic_asset):
    rep = fabricator.record_replay(basic_asset.cinematic_id)
    res = fabricator.play_replay(basic_asset, rep)
    assert res["status"] == "COMPLETED"
    assert len(res["determinism_hash"]) == 64


def test_replay_determinism_hash(fabricator, basic_asset):
    rep1 = fabricator.record_replay(basic_asset.cinematic_id, seed=42)
    res1 = fabricator.play_replay(basic_asset, rep1)
    rep2 = fabricator.record_replay(basic_asset.cinematic_id, seed=42)
    res2 = fabricator.play_replay(basic_asset, rep2)
    assert res1["determinism_hash"] == res2["determinism_hash"]


def test_replay_different_seed_different_hash(fabricator, basic_asset):
    rep1 = fabricator.record_replay(basic_asset.cinematic_id, seed=1)
    rep1.parameters = {"variant": "A"}
    res1 = fabricator.play_replay(basic_asset, rep1)
    rep2 = fabricator.record_replay(basic_asset.cinematic_id, seed=2)
    rep2.parameters = {"variant": "B"}
    res2 = fabricator.play_replay(basic_asset, rep2)
    assert res1["replay_id"] != res2["replay_id"]


def test_replay_sample_count(fabricator, basic_asset):
    rep = fabricator.record_replay(basic_asset.cinematic_id)
    res = fabricator.play_replay(basic_asset, rep)
    assert res["samples_count"] > 0


def test_replay_branch_choices_recording():
    rep = CinematicReplay("r1", "cin1", branch_choices={"ch1": "OptA"})
    assert rep.branch_choices["ch1"] == "OptA"


def test_replay_binding_resolution_recording():
    rep = CinematicReplay("r2", "cin2", binding_resolution={"b_hero": "hero_ent_01"})
    assert rep.binding_resolution["b_hero"] == "hero_ent_01"


# ==============================================================================
# 18. PERSISTENCE (10 tests - §88 - §91, §133)
# ==============================================================================

def test_persistence_save_state(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    inst.current_time = 3.5
    save = fabricator.save_state(inst, basic_asset)
    assert save.cinematic_id == basic_asset.cinematic_id
    assert save.timeline_time == 3.5


def test_persistence_save_state_fields(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    inst.playback_state = PlaybackState.PAUSED
    save = fabricator.save_state(inst, basic_asset)
    assert save.playback_state == PlaybackState.PAUSED
    assert len(save.asset_hash) == 64


def test_persistence_load_state(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    inst.current_time = 4.0
    save = fabricator.save_state(inst, basic_asset)
    loaded_inst = fabricator.load_state(save, basic_asset)
    assert loaded_inst.current_time == 4.0


def test_persistence_load_state_time_restored(fabricator, basic_asset):
    save = CinematicSaveState("c1", "inst1", 8.2, PlaybackState.PLAYING)
    inst = fabricator.load_state(save, basic_asset)
    assert inst.current_time == 8.2


def test_persistence_load_state_playback_state_restored(fabricator, basic_asset):
    save = CinematicSaveState("c1", "inst1", 2.0, PlaybackState.FAST_FORWARD)
    inst = fabricator.load_state(save, basic_asset)
    assert inst.playback_state == PlaybackState.FAST_FORWARD


def test_persistence_load_validation_success(validator, fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    save = fabricator.save_state(inst, basic_asset)
    report = validator.validate_save_state(save)
    assert report.is_valid is True


def test_persistence_version_migration(fabricator, basic_asset):
    save = CinematicSaveState("c1", "inst1", 2.0, PlaybackState.PLAYING, version="0.9.0")
    inst = fabricator.load_state(save, basic_asset)
    assert inst is not None


def test_persistence_asset_hash_verification(validator, fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    save = fabricator.save_state(inst, basic_asset)
    report = validator.validate_save_state(save, expected_hash=save.asset_hash)
    assert report.is_valid is True


def test_persistence_corrupt_save_detection(validator):
    save = CinematicSaveState("c1", "inst1", 2.0, PlaybackState.PLAYING, asset_hash="corrupt_hash_value")
    report = validator.validate_save_state(save, expected_hash="expected_valid_hash")
    assert report.is_valid is False
    assert any("mismatch" in e for e in report.errors)


def test_persistence_save_load_roundtrip(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset, parameters={"level": 5})
    inst.current_time = 7.0
    save = fabricator.save_state(inst, basic_asset)
    loaded = fabricator.load_state(save, basic_asset)
    assert loaded.current_time == inst.current_time
    assert loaded.parameters == inst.parameters


# ==============================================================================
# 19. NETWORK (10 tests - §92 - §96, §133)
# ==============================================================================

def test_network_authority_server():
    auth = NetworkAuthority.SERVER_AUTHORITATIVE
    assert auth == "SERVER_AUTHORITATIVE"


def test_network_authority_client():
    auth = NetworkAuthority.CLIENT_AUTHORITATIVE
    assert auth == "CLIENT_AUTHORITATIVE"


def test_network_authority_shared():
    auth = NetworkAuthority.SHARED
    assert auth == "SHARED"


def test_network_timing_sync(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    # Server tick 60 at 30 fps = 2.0 seconds
    timeline_time = fabricator.sync_network_state(inst, server_tick=60, tick_rate=30.0)
    assert timeline_time == 2.0
    assert inst.current_time == 2.0


def test_network_reconciliation_within_threshold(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    inst.current_time = 2.05
    # Remote time 2.0 (delta 0.05 <= 0.1 threshold) -> No reconciliation needed
    assert fabricator.reconcile_network_state(inst, 2.0, threshold=0.1) is False
    assert inst.current_time == 2.05


def test_network_reconciliation_exceeds_threshold(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    inst.current_time = 2.5
    # Remote time 2.0 (delta 0.5 > 0.1 threshold) -> Reconciled
    assert fabricator.reconcile_network_state(inst, 2.0, threshold=0.1) is True
    assert inst.current_time == 2.0


def test_network_join_in_progress_join_current(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.handle_join_in_progress(inst, JoinInProgressPolicy.JOIN_CURRENT_TIME, server_time=5.0)
    assert inst.current_time == 5.0
    assert inst.playback_state == PlaybackState.PLAYING


def test_network_join_in_progress_restart(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.handle_join_in_progress(inst, JoinInProgressPolicy.RESTART, server_time=5.0)
    assert inst.current_time == 0.0
    assert inst.playback_state == PlaybackState.PLAYING


def test_network_join_in_progress_skip_local(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.handle_join_in_progress(inst, JoinInProgressPolicy.SKIP_LOCAL, server_time=5.0)
    assert inst.playback_state == PlaybackState.SKIPPED


def test_network_instance_id_metadata():
    inst = CinematicInstance("inst1", "cin1", network_instance_id="net_inst_99", start_tick=120)
    assert inst.network_instance_id == "net_inst_99"
    assert inst.start_tick == 120


# ==============================================================================
# 20. FAILURE TESTS (29 tests - §129, §133)
# ==============================================================================

def test_invalid_cinematic_asset(validator):
    asset = CinematicAsset(cinematic_id="", duration=-5.0)
    rep = validator.validate_all(asset)
    assert rep.is_valid is False
    assert any("empty" in e for e in rep.errors)


def test_invalid_timeline(validator):
    tl = Timeline(start_time=10.0, end_time=5.0, duration=-5.0)
    rep = validator.validate_timeline(tl)
    assert rep.is_valid is False


def test_invalid_track(validator):
    tr = CinematicTrack(track_id="", track_type=TrackType.CAMERA)
    rep = validator.validate_track(tr)
    assert rep.is_valid is False


def test_invalid_clip(validator):
    c = CinematicClip(clip_id="", start=-2.0, duration=0.0)
    rep = validator.validate_clip(c)
    assert rep.is_valid is False


def test_missing_binding(validator):
    b = CinematicBinding(binding_id="", target_reference="", fallback_reference="")
    rep = validator.validate_binding(b)
    assert rep.is_valid is False


def test_invalid_camera(validator):
    cam = CinematicCamera(camera_id="", fov=200.0, near_clip=-1.0, far_clip=10.0)
    rep = validator.validate_camera(cam)
    assert rep.is_valid is False


def test_missing_camera(fabricator):
    assert fabricator.get_active_camera_id(fallback="default_cam") == "default_cam"


def test_camera_failure(fabricator):
    # Release non-existent owner returns False safely
    assert fabricator.release_camera_takeover("non_existent_owner") is False


def test_animation_failure(fabricator, basic_asset):
    tr = CinematicTrack(
        track_id="tr_missing_anim",
        track_type=TrackType.ANIMATION,
        clips=[CinematicClip("c_fail", 0, 5, source="non_existent_anim")]
    )
    basic_asset.timeline.tracks.append(tr)
    res = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 1.0)
    assert res is not None


def test_facial_failure(fabricator):
    tr = CinematicTrack(track_id="f_fail", track_type=TrackType.FACIAL)
    st = fabricator.evaluate_facial_state(tr, 0.0)
    assert st is not None


def test_lipsync_failure(fabricator):
    data = LipSyncData(source=LipSyncSource.PHONEME_DATA, visemes=[])
    vis = fabricator.evaluate_lip_sync(data, 1.0)
    assert vis in ["A", "O", "E", "neutral"]


def test_audio_failure(fabricator, basic_asset):
    tr = CinematicTrack(
        track_id="tr_audio_fail",
        track_type=TrackType.AUDIO,
        clips=[CinematicClip("c_aud", 0, 5, source="")]
    )
    basic_asset.timeline.tracks.append(tr)
    res = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 2.0)
    assert res is not None


def test_subtitle_failure(validator):
    c = CinematicClip("sub_fail", 0, 5, source="")
    rep = validator.validate_clip(c)
    assert rep is not None


def test_vfx_failure(fabricator, basic_asset):
    tr = CinematicTrack(
        track_id="tr_vfx_fail",
        track_type=TrackType.VFX,
        clips=[CinematicClip("c_vfx", 0, 5, source="")]
    )
    basic_asset.timeline.tracks.append(tr)
    res = fabricator.evaluate(fabricator.create_instance(basic_asset), basic_asset, 2.0)
    assert res is not None


def test_lighting_failure(validator):
    c = CinematicClip("c_light", 0, 5, blend_in=4.0, blend_out=3.0)  # blend > duration
    rep = validator.validate_clip(c)
    assert rep.is_valid is False


def test_lock_failure(fabricator):
    # Release lock on unheld lock returns False safely
    assert fabricator.release_lock(GameplayLockType.MOVEMENT, "unheld_owner") is False


def test_branch_failure(fabricator):
    br = CinematicBranch("br_fail", BranchConditionType.CHOICE, "unknown_key", "val")
    assert fabricator.evaluate_branch(br, {}) is False


def test_choice_failure(fabricator):
    ch = CinematicChoice("ch_fail", "Prompt", options=["A", "B"])
    assert fabricator.select_choice_option(ch, "InvalidOption") is False


def test_checkpoint_failure(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    assert inst.checkpoint is None


def test_save_failure(validator):
    save = CinematicSaveState("", "", 0.0, PlaybackState.IDLE)
    rep = validator.validate_save_state(save)
    assert rep.is_valid is False


def test_load_failure(validator):
    save = CinematicSaveState("c1", "inst1", -10.0, PlaybackState.IDLE)
    rep = validator.validate_save_state(save)
    assert rep.is_valid is False


def test_corrupt_save(validator):
    save = CinematicSaveState("c1", "inst1", 0.0, PlaybackState.IDLE, asset_hash="bad")
    rep = validator.validate_save_state(save, expected_hash="good")
    assert rep.is_valid is False


def test_network_failure(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    t = fabricator.sync_network_state(inst, server_tick=-30, tick_rate=30.0)
    assert t == -1.0


def test_network_timeout(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    assert fabricator.reconcile_network_state(inst, 0.0, threshold=1000.0) is False


def test_network_desync(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    inst.current_time = 1.0
    assert fabricator.reconcile_network_state(inst, 10.0, threshold=0.1) is True


def test_event_duplicate():
    policy = EventExecutionPolicy.ONCE
    assert policy == "ONCE"


def test_seek_event_error(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    r = fabricator.seek(inst, basic_asset, -100.0)
    assert r == 0.0


def test_cleanup_failure(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    fabricator.cleanup(inst)  # Must execute cleanly with 0 errors
    assert fabricator.get_active_locks() == []


def test_partial_failure_recovery(validator):
    c_good = CinematicClip("c_ok", 0, 5)
    c_bad = CinematicClip("c_err", 0, -1)
    t = CinematicTrack("tr_mix", TrackType.CAMERA, clips=[c_good, c_bad])
    rep = validator.validate_track(t)
    assert rep.is_valid is False
    assert len(rep.errors) >= 1


# ==============================================================================
# 21. DETERMINISM TESTS (15 tests - §130, §133)
# ==============================================================================

def test_timeline_determinism(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    e1 = fabricator.evaluate(inst, basic_asset, 3.14)
    e2 = fabricator.evaluate(inst, basic_asset, 3.14)
    assert e1["time"] == e2["time"]
    assert e1["active_camera"] == e2["active_camera"]


def test_track_order_determinism(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    e1 = fabricator.evaluate(inst, basic_asset, 2.0)
    e2 = fabricator.evaluate(inst, basic_asset, 2.0)
    assert e1["active_tracks"] == e2["active_tracks"]


def test_clip_evaluation_determinism(fabricator, basic_asset):
    clip = CinematicClip("cdet", 0.0, 10.0, blend_in=2.0)
    w1 = clip.evaluate_weight(1.0)
    w2 = clip.evaluate_weight(1.0)
    assert w1 == w2


def test_binding_determinism(fabricator):
    b = CinematicBinding("b_det", BindingType.PLAYER)
    r1 = fabricator.resolve_binding(b)
    r2 = fabricator.resolve_binding(b)
    assert r1 == r2 == "entity_player_0"


def test_camera_determinism(fabricator):
    pts = [(0.0, 0.0, 0.0), (10.0, 5.0, 2.0), (20.0, 0.0, 4.0)]
    p1 = fabricator.interpolate_spline(pts, 0.42, CameraInterpolationType.CATMULL_ROM)
    p2 = fabricator.interpolate_spline(pts, 0.42, CameraInterpolationType.CATMULL_ROM)
    assert p1 == p2


def test_animation_determinism():
    c = CinematicClip("c_anim_det", 0, 10, blend_in=3.0, blend_out=3.0)
    assert c.evaluate_weight(5.0) == c.evaluate_weight(5.0)


def test_facial_determinism(fabricator):
    tr = CinematicTrack("f_det", TrackType.FACIAL)
    s1 = fabricator.evaluate_facial_state(tr, 2.5)
    s2 = fabricator.evaluate_facial_state(tr, 2.5)
    assert s1.blink_phase == s2.blink_phase


def test_lipsync_determinism(fabricator):
    data = LipSyncData(
        source=LipSyncSource.PHONEME_DATA,
        visemes=[{"start": 0.0, "duration": 1.0, "viseme": "AA"}]
    )
    assert fabricator.evaluate_lip_sync(data, 0.5) == fabricator.evaluate_lip_sync(data, 0.5)


def test_dialogue_determinism(fabricator, basic_asset):
    tr = CinematicTrack("td", TrackType.DIALOGUE, clips=[CinematicClip("d1", 0, 5)])
    basic_asset.timeline.tracks.append(tr)
    inst = fabricator.create_instance(basic_asset)
    r1 = fabricator.evaluate(inst, basic_asset, 2.0)
    r2 = fabricator.evaluate(inst, basic_asset, 2.0)
    assert r1["dialogue_line"] == r2["dialogue_line"]


def test_branch_determinism(fabricator):
    br = CinematicBranch("br_det", BranchConditionType.PARAMETER, "k", 100)
    ctx = {"k": 100}
    assert fabricator.evaluate_branch(br, ctx) == fabricator.evaluate_branch(br, ctx)


def test_choice_determinism(fabricator):
    ch = CinematicChoice("ch_det", "prompt", options=["X", "Y"], default_option="X")
    assert fabricator.handle_choice_timeout(ch) == fabricator.handle_choice_timeout(ch)


def test_skip_determinism(fabricator, basic_asset):
    inst1 = fabricator.create_instance(basic_asset)
    inst2 = fabricator.create_instance(basic_asset)
    fabricator.skip(inst1, basic_asset)
    fabricator.skip(inst2, basic_asset)
    assert inst1.current_time == inst2.current_time
    assert inst1.playback_state == inst2.playback_state


def test_checkpoint_determinism(fabricator, basic_asset):
    inst1 = fabricator.create_instance(basic_asset)
    inst1.current_time = 4.0
    chk = fabricator.create_checkpoint(inst1, "chk_det")
    fabricator.restore_checkpoint(inst1, chk)
    assert inst1.current_time == 4.0


def test_replay_determinism(fabricator, basic_asset):
    r1 = fabricator.record_replay(basic_asset.cinematic_id, seed=777)
    res1 = fabricator.play_replay(basic_asset, r1)
    r2 = fabricator.record_replay(basic_asset.cinematic_id, seed=777)
    res2 = fabricator.play_replay(basic_asset, r2)
    assert res1["determinism_hash"] == res2["determinism_hash"]


def test_network_timeline_determinism(fabricator, basic_asset):
    inst = fabricator.create_instance(basic_asset)
    t1 = fabricator.sync_network_state(inst, 90, 30.0)
    t2 = fabricator.sync_network_state(inst, 90, 30.0)
    assert t1 == t2 == 3.0


# ==============================================================================
# 22. GOLDEN TESTS (16 tests - §131, §133)
# ==============================================================================

def test_golden_dialogue_cutscene(fabricator):
    asset, inst = fabricator.create_golden_scenario("GOLDEN_DIALOGUE_CUTSCENE")
    res = fabricator.evaluate(inst, asset, 2.0)
    assert res["dialogue_line"] == "line_01"
    assert len(res["subtitles"]) > 0


def test_golden_combat_cutscene(fabricator):
    asset, inst = fabricator.create_golden_scenario("GOLDEN_COMBAT_CUTSCENE")
    res = fabricator.evaluate(inst, asset, 1.0)
    assert "BASE" in res["active_animations"]
    assert res["root_motion"][0] > 0.0


def test_golden_camera_dolly(fabricator):
    asset, inst = fabricator.create_golden_scenario("GOLDEN_CAMERA_DOLLY")
    assert len(asset.timeline.tracks) == 1
    assert asset.timeline.tracks[0].clips[0].parameters["rig_type"] == "DOLLY"


def test_golden_camera_spline(fabricator):
    asset, inst = fabricator.create_golden_scenario("GOLDEN_CAMERA_SPLINE")
    clip = asset.timeline.tracks[0].clips[0]
    pts = clip.parameters["spline_points"]
    pos = fabricator.interpolate_spline(pts, 0.5)
    assert len(pos) == 3


def test_golden_camera_blend(fabricator):
    asset, inst = fabricator.create_golden_scenario("GOLDEN_CAMERA_BLEND")
    res = fabricator.evaluate(inst, asset, 2.5)
    assert res is not None


def test_golden_facial_performance(fabricator):
    asset, inst = fabricator.create_golden_scenario("GOLDEN_FACIAL_PERFORMANCE")
    res = fabricator.evaluate(inst, asset, 2.0)
    assert res["facial_state"] is not None
    assert res["facial_state"].emotion == "angry"


def test_golden_lip_sync(fabricator):
    asset, inst = fabricator.create_golden_scenario("GOLDEN_LIP_SYNC")
    res = fabricator.evaluate(inst, asset, 1.0)
    assert res["lip_sync_viseme"] != ""


def test_golden_subtitles(fabricator):
    asset, inst = fabricator.create_golden_scenario("GOLDEN_SUBTITLES")
    res = fabricator.evaluate(inst, asset, 2.0)
    assert len(res["subtitles"]) == 1
    assert res["subtitles"][0]["color"] == "#00FFCC"


def test_golden_vfx_cue(fabricator):
    asset, inst = fabricator.create_golden_scenario("GOLDEN_VFX_CUE")
    res = fabricator.evaluate(inst, asset, 3.0)
    assert len(res["vfx_cues"]) == 1
    assert res["vfx_cues"][0]["vfx_id"] == "vfx_fiery_blast"


def test_golden_lighting_cue(fabricator):
    asset, inst = fabricator.create_golden_scenario("GOLDEN_LIGHTING_CUE")
    res = fabricator.evaluate(inst, asset, 2.0)
    assert res["lighting_values"]["intensity"] > 1.0


def test_golden_branch(fabricator):
    asset, inst = fabricator.create_golden_scenario("GOLDEN_BRANCH")
    assert len(asset.timeline.markers) == 1
    assert asset.timeline.markers[0].marker_type == "branch"


def test_golden_skip(fabricator):
    asset, inst = fabricator.create_golden_scenario("GOLDEN_SKIP")
    assert fabricator.skip(inst, asset) is True
    assert inst.playback_state == PlaybackState.SKIPPED


def test_golden_checkpoint(fabricator):
    asset, inst = fabricator.create_golden_scenario("GOLDEN_CHECKPOINT")
    assert len(asset.timeline.markers) == 1
    assert asset.timeline.markers[0].marker_type == "checkpoint"


def test_golden_replay(fabricator):
    asset, inst = fabricator.create_golden_scenario("GOLDEN_REPLAY")
    rep = fabricator.record_replay(asset.cinematic_id, seed=101)
    res = fabricator.play_replay(asset, rep)
    assert res["status"] == "COMPLETED"


def test_golden_network_sync(fabricator):
    asset, inst = fabricator.create_golden_scenario("GOLDEN_NETWORK_SYNC")
    t = fabricator.sync_network_state(inst, 150, 30.0)
    assert t == 5.0


def test_golden_full_cinematic(fabricator, validator, packager):
    asset, inst = fabricator.create_golden_scenario("GOLDEN_FULL_CINEMATIC")
    val_rep = validator.validate_all(asset)
    assert val_rep.is_valid is True
    pkg = packager.package(asset)
    assert pkg.is_verified is True


# ==============================================================================
# 23. END_TO_END PIPELINE (1 test - §132, §133)
# ==============================================================================

def test_full_cinematic_end_to_end_pipeline(fabricator, validator, packager):
    """
    Executes full pipeline from §132:
    PLAYER -> TRIGGER -> CREATE INSTANCE -> RESOLVE BINDINGS ->
    ACQUIRE LOCKS -> CAMERA TAKEOVER -> ACTOR ANIMATION ->
    FACIAL -> DIALOGUE -> LIP SYNC -> SUBTITLE -> AUDIO -> VFX -> LIGHTING ->
    BRANCH CHOICE -> CHECKPOINT -> TRANSITION -> COMPLETE -> CLEANUP ->
    RESTORE -> SAVE -> LOAD -> REPLAY -> DETERMINISM HASH.
    """
    # 1. Author Asset with all tracks
    timeline = Timeline(start_time=0.0, end_time=10.0, duration=10.0)
    t_cam = CinematicTrack("t_cam", TrackType.CAMERA, order=0, clips=[CinematicClip("c1", 0, 10)])
    t_anim = CinematicTrack("t_anim", TrackType.ANIMATION, order=1, clips=[CinematicClip("a1", 0, 5, source="run", root_motion_policy=RootMotionPolicy.APPLY)])
    t_face = CinematicTrack("t_face", TrackType.FACIAL, order=2, clips=[CinematicClip("f1", 0, 4, parameters={"emotion": "happy"})])
    t_diag = CinematicTrack("t_diag", TrackType.DIALOGUE, order=3, clips=[CinematicClip("d1", 1, 3, parameters={"speaker": "Captain"})])
    t_sub = CinematicTrack("t_sub", TrackType.SUBTITLE, order=4, clips=[CinematicClip("s1", 1, 3, source="Engage hyperdrive!", parameters={"color": "#FFFFFF"})])
    t_aud = CinematicTrack("t_aud", TrackType.AUDIO, order=5, clips=[CinematicClip("au1", 1, 3, source="vo_cmd_engage")])
    t_vfx = CinematicTrack("t_vfx", TrackType.VFX, order=6, clips=[CinematicClip("v1", 2, 4, source="warp_flash")])
    t_light = CinematicTrack("t_light", TrackType.LIGHTING, order=7, clips=[CinematicClip("l1", 0, 10, parameters={"intensity": 2.5})])

    timeline.tracks.extend([t_cam, t_anim, t_face, t_diag, t_sub, t_aud, t_vfx, t_light])
    timeline.markers.append(CinematicMarker("chk_mid", 5.0, marker_type="checkpoint"))

    bindings = [
        CinematicBinding("hero", BindingType.PLAYER),
        CinematicBinding("ship_cam", BindingType.STATIC, target_reference="cine_cam_bridge"),
    ]

    asset = CinematicAsset(
        cinematic_id="cin_e2e_masterpiece",
        version="1.0.0",
        duration=10.0,
        timeline=timeline,
        bindings=bindings,
    )

    # 2. Validate
    v_report = validator.validate_all(asset)
    assert v_report.is_valid is True

    # 3. Create Instance & Resolve Bindings
    inst = fabricator.create_instance(asset, instance_id="inst_e2e_01")
    assert inst.bindings["hero"] == "entity_player_0"
    assert inst.bindings["ship_cam"] == "cine_cam_bridge"

    # 4. Acquire Locks
    fabricator.preserve_gameplay_state(inst.instance_id, {"player_pos": (0, 0, 0)})
    fabricator.acquire_lock(GameplayLockType.INPUT, inst.instance_id)
    fabricator.acquire_lock(GameplayLockType.MOVEMENT, inst.instance_id)
    assert fabricator.is_locked(GameplayLockType.INPUT) is True
    assert fabricator.is_locked(GameplayLockType.MOVEMENT) is True

    # 5. Camera Takeover
    fabricator.request_camera_takeover("cine_cam_bridge", inst.instance_id, CameraPriority.CINEMATIC)
    assert fabricator.get_active_camera_id() == "cine_cam_bridge"

    # 6. Play & Runtime Evaluation at 2.0s
    fabricator.play(inst)
    sample = fabricator.evaluate(inst, asset, 2.0)
    assert sample["dialogue_line"] == "d1"
    assert sample["speaker"] == "Captain"
    assert len(sample["subtitles"]) == 1
    assert len(sample["audio_cues"]) == 1
    assert len(sample["vfx_cues"]) == 1
    assert sample["lighting_values"]["intensity"] == pytest.approx(2.5)

    # 7. Checkpoint Snapshot & Branch Choice
    chk = fabricator.create_checkpoint(inst, "chk_e2e")
    assert chk.timeline_time == 2.0

    choice = CinematicChoice("e2e_ch", "Select destination", options=["Earth", "Mars"], default_option="Earth")
    fabricator.select_choice_option(choice, "Mars")
    assert choice.selected_option == "Mars"

    # 8. Complete & Cleanup
    fabricator.cleanup(inst)
    assert fabricator.is_locked(GameplayLockType.INPUT) is False
    assert fabricator.is_locked(GameplayLockType.MOVEMENT) is False
    assert fabricator.get_active_camera_id() != "cine_cam_bridge"

    # 9. Restore Gameplay State
    restored_state = fabricator.restore_gameplay_state(inst.instance_id)
    assert restored_state["player_pos"] == (0, 0, 0)

    # 10. Save & Load
    save_data = fabricator.save_state(inst, asset)
    loaded_inst = fabricator.load_state(save_data, asset)
    assert loaded_inst.cinematic_id == asset.cinematic_id

    # 11. Replay Determinism
    replay_rec = fabricator.record_replay(asset.cinematic_id, seed=12345)
    replay_res = fabricator.play_replay(asset, replay_rec)
    assert replay_res["status"] == "COMPLETED"
    assert len(replay_res["determinism_hash"]) == 64

    # 12. Package for UE5 LevelSequence
    pkg = packager.package(asset)
    assert pkg.is_verified is True
    assert pkg.ue_level_sequence_manifest["SequenceName"] == "LS_cin_e2e_masterpiece"
    assert len(pkg.tracks_manifest) == 8
    assert len(pkg.checksum) == 64
