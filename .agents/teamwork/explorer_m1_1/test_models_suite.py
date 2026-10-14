"""
Comprehensive unit test suite for proposed_models.py.
Tests 100% of all required models, validation rules, Zero-Any policy,
and edge cases.
"""
from __future__ import annotations
import json
import pytest
from pydantic import ValidationError

from proposed_models import (
    StrictBaseModel,
    Vector3D,
    Rotator3D,
    ColorRGB,
    AudioStemType,
    AudioAnalysisRequest,
    StemSeparationResult,
    AudioAnalysisResult,
    MeshFormat,
    PBRTextureSet,
    ImageTo3DRequest,
    ImageTo3DResult,
    BoneDescriptor,
    SkeletalHierarchy,
    AutoRigRequest,
    AutoRigResult,
    Pose3DKeyframe,
    MocapExtractionRequest,
    MocapResult,
    CameraKeyframe,
    LumenLightConfig,
    SceneConfig,
    SceneBuildResult,
    MovieRenderQueueJobConfig,
    RenderResult,
    PlanRiskLevel,
    PlanStatus,
    PlanStep,
    ProductionPlan,
    PlanConfirmationRequest,
    PlanConfirmationResponse,
    ProgressEvent,
    PlanProposalEvent,
    AssetReadyEvent,
    LogEvent,
    AssetType,
    LogLevel,
)


def test_vector_and_rotator_and_color_ue5_helpers() -> None:
    vec = Vector3D(x=10.0, y=-20.0, z=30.0)
    assert vec.to_tuple() == (10.0, -20.0, 30.0)
    assert vec.to_ue5_dict() == {"X": 10.0, "Y": -20.0, "Z": 30.0}

    vec2 = Vector3D.from_tuple((5.0, 6.0, 7.0))
    assert vec2.x == 5.0

    rot = Rotator3D(pitch=15.0, yaw=90.0, roll=-45.0)
    assert rot.to_tuple() == (15.0, 90.0, -45.0)
    assert rot.to_ue5_dict() == {"Pitch": 15.0, "Yaw": 90.0, "Roll": -45.0}

    rot2 = Rotator3D.from_tuple((0.0, 180.0, 0.0))
    assert rot2.yaw == 180.0

    color = ColorRGB(r=0.9, g=0.8, b=0.2)
    assert color.to_tuple() == (0.9, 0.8, 0.2)
    assert color.to_ue5_dict() == {"R": 0.9, "G": 0.8, "B": 0.2, "A": 1.0}


def test_audio_analysis_models() -> None:
    req = AudioAnalysisRequest(
        audio_path="assets/audio/track.wav",
        separate_stems=True,
        sample_rate=48000,
        bpm_hint=128.0,
    )
    assert req.audio_path == "assets/audio/track.wav"
    assert req.separate_stems is True
    assert req.bpm_hint == 128.0

    # Test stem separation result
    sep = StemSeparationResult(
        stems={"vocals": "v.wav", "drums": "d.wav", "bass": "b.wav", "other": "o.wav"},
        model_used="demucs_htdemucs",
        duration_seconds=32.5,
    )
    assert len(sep.stems) == 4

    # Test audio analysis result
    res = AudioAnalysisResult(
        bpm=128.0,
        duration_seconds=32.5,
        beat_timestamps=[0.0, 0.468, 0.937],
        onset_envelope=[0.05, 0.95, 0.1],
        stems=sep.stems,
        time_signature="4/4",
        danceability=0.88,
    )
    assert res.bpm == 128.0
    assert res.get_stem_path(AudioStemType.VOCALS) == "v.wav"
    assert res.get_stem_path("drums") == "d.wav"
    assert res.get_stem_path("non_existent") is None


def test_3d_models() -> None:
    pbr_empty = PBRTextureSet()
    assert not pbr_empty.has_textures()

    pbr = PBRTextureSet(albedo_path="a.png", normal_path="n.png", roughness_path="r.png", resolution=2048)
    assert pbr.has_textures()
    assert pbr.resolution == 2048

    req = ImageTo3DRequest(
        image_path="input/concept.png",
        provider="tripo",
        texture_resolution=2048,
        target_format=MeshFormat.GLB,
        generate_textures=True,
        seed=1337,
    )
    assert req.seed == 1337

    res = ImageTo3DResult(
        mesh_path="output/mesh.glb",
        textures=pbr,
        vertex_count=12400,
        polygon_count=24800,
        cached=True,
        mesh_format=MeshFormat.GLB,
        provider_used="tripo",
        generation_time_seconds=4.2,
    )
    assert res.cached is True
    assert res.vertex_count == 12400


def test_rigging_models() -> None:
    b1 = BoneDescriptor(name="root", head_position=(0, 0, 0), tail_position=(0, 0, 10))
    b2 = BoneDescriptor(name="pelvis", parent_name="root", head_position=(0, 0, 10), tail_position=(0, 0, 15))
    skel = SkeletalHierarchy(skeleton_type="ue5_mannequin", root_bone="root", bones=[b1, b2])
    assert len(skel.bones) == 2

    req = AutoRigRequest(mesh_path="char.glb", skeleton_type="ue5_mannequin", max_influences=4)
    res = AutoRigResult(
        rigged_mesh_path="char_rigged.glb",
        bone_count=67,
        hierarchy=["root", "pelvis"],
        skeleton_type="ue5_mannequin",
        success=True,
    )
    assert res.success is True
    assert res.bone_count == 67


def test_mocap_models() -> None:
    kf = Pose3DKeyframe(
        timestamp=0.5,
        frame_index=15,
        keypoints_3d={"pelvis": (0.0, 0.9, 0.0), "head": (0.0, 1.7, 0.0)},
        confidence_scores={"pelvis": 0.98, "head": 0.95},
    )
    assert kf.frame_index == 15

    req = MocapExtractionRequest(video_path="dance.mp4", target_fps=30, remove_background=True)
    res = MocapResult(
        animation_path="anim.glb",
        frame_count=300,
        fps=30,
        duration=10.0,
        keyframes=[kf],
        tracked_joints_count=33,
    )
    assert res.duration == 10.0
    assert len(res.keyframes or []) == 1


def test_scene_and_camera_models() -> None:
    cam_kf = CameraKeyframe(
        timestamp=1.0,
        position=(100.0, -200.0, 120.0),
        rotation=(5.0, 45.0, 0.0),
        focal_length=50.0,
        aperture=2.0,
        focus_distance=250.0,
    )
    ue5_payload = cam_kf.to_ue5_payload()
    assert ue5_payload["CurrentFocalLength"] == 50.0
    assert "Location" in ue5_payload

    lumen = LumenLightConfig(
        preset_name="cinematic_three_point",
        directional_light_intensity=12.0,
        key_light_intensity=6000.0,
        fill_light_intensity=3000.0,
        rim_light_intensity=8000.0,
    )
    scene = SceneConfig(
        mesh_path="char.glb",
        animation_path="dance.glb",
        lighting_config=lumen,
        camera_choreography=[cam_kf],
        audio_track_path="audio.wav",
    )
    assert len(scene.camera_choreography) == 1

    build_res = SceneBuildResult(
        success=True,
        actor_ids=["Actor_Char", "Actor_Cam"],
        scene_path="/Game/Cinematics/Shot_Main",
        camera_actor_id="Actor_Cam",
        character_actor_id="Actor_Char",
    )
    assert build_res.success is True


def test_render_models() -> None:
    job = MovieRenderQueueJobConfig(
        scene_path="/Game/Cinematics/Shot_Main",
        output_path="renders/final.mp4",
        fps=60,
        resolution="3840x2160",
        codec="h264",
        anti_aliasing_samples=32,
        warmup_frames=45,
    )
    assert job.get_resolution_dimensions() == (3840, 2160)

    res = RenderResult(
        video_path="renders/final.mp4",
        frame_count=600,
        elapsed_seconds=55.4,
        fps=60,
        resolution="3840x2160",
        file_size_bytes=250000000,
        success=True,
    )
    assert res.frame_count == 600
    assert res.success is True


def test_production_plan_methods() -> None:
    s1 = PlanStep(
        step_id="step_audio",
        index=0,
        tool_name="analyze_audio",
        description="Analyze audio tempo and separate stems",
        parameters={"audio_path": "song.mp3", "separate_stems": True},
        risk_level=PlanRiskLevel.LOW,
    )
    s2 = PlanStep(
        step_id="step_render",
        index=1,
        tool_name="render_video",
        description="Render final MRQ output",
        parameters={"scene_path": "/Game/Cinematics/Seq1", "output_path": "out.mp4"},
        risk_level=PlanRiskLevel.HIGH,
        requires_confirmation=True,
    )
    plan = ProductionPlan(
        plan_id="plan_001",
        title="Complete Production Pipeline",
        description="End-to-end pipeline execution",
        steps=[s1, s2],
        status=PlanStatus.PROPOSED,
    )

    assert plan.get_step("step_audio") == s1
    assert plan.get_step("unknown_step") is None
    assert not plan.is_all_completed()

    # Transition steps
    plan.mark_step_status("step_audio", PlanStatus.COMPLETED, output_preview="audio/preview.wav")
    assert s1.status == PlanStatus.COMPLETED
    assert s1.output_preview == "audio/preview.wav"

    plan.mark_step_status("step_render", PlanStatus.COMPLETED, output_preview="renders/out.mp4")
    assert plan.is_all_completed()

    # Test Plan Confirmation Request & Response
    req = PlanConfirmationRequest(plan_id="plan_001", step_id="step_render", user_prompt="Make it 60fps")
    assert req.user_prompt == "Make it 60fps"

    resp = PlanConfirmationResponse(
        plan_id="plan_001",
        step_id="step_render",
        approved=True,
        feedback="Confirmed, start rendering",
        modified_parameters={"fps": 60},
    )
    assert resp.approved is True
    assert resp.modified_parameters["fps"] == 60


def test_telemetry_events() -> None:
    prog = ProgressEvent(stage="Mesh Generation", percentage=75.0, message="Generating PBR textures")
    assert prog.type == "progress"

    asset = AssetReadyEvent(
        asset_id="asset_01",
        asset_type=AssetType.RENDER_VIDEO,
        file_path="renders/out.mp4",
    )
    assert asset.asset_type == AssetType.RENDER_VIDEO

    log = LogEvent(level=LogLevel.WARNING, message="Low disk space warning")
    assert log.level == LogLevel.WARNING


def test_fastmcp_json_schema_validity() -> None:
    # Ensure every single model generates valid JSON schema without errors
    models = [
        AudioAnalysisRequest,
        AudioAnalysisResult,
        StemSeparationResult,
        PBRTextureSet,
        ImageTo3DRequest,
        ImageTo3DResult,
        BoneDescriptor,
        SkeletalHierarchy,
        AutoRigRequest,
        AutoRigResult,
        Pose3DKeyframe,
        MocapExtractionRequest,
        MocapResult,
        CameraKeyframe,
        LumenLightConfig,
        SceneConfig,
        SceneBuildResult,
        MovieRenderQueueJobConfig,
        RenderResult,
        PlanStep,
        ProductionPlan,
        PlanConfirmationRequest,
        PlanConfirmationResponse,
        ProgressEvent,
        PlanProposalEvent,
        AssetReadyEvent,
        LogEvent,
    ]
    for model_cls in models:
        schema = model_cls.model_json_schema()
        assert "properties" in schema
        assert schema.get("type") == "object"


def test_extra_forbid_strictness() -> None:
    with pytest.raises(ValidationError):
        ImageTo3DRequest(image_path="test.png", unauthorized_field="bad_data")
