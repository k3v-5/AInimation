"""
Unit test suite for backend.core.models.

Tests comprehensive domain model instantiation, serialization, validation,
edge cases, and Zero-Any compliance.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.core.models import (
    AssetReadyEvent,
    AssetType,
    AudioAnalysisRequest,
    AudioAnalysisResult,
    AudioStemType,
    AutoRigRequest,
    AutoRigResult,
    BoneDescriptor,
    CameraKeyframe,
    ColorRGB,
    ImageTo3DRequest,
    ImageTo3DResult,
    LogEvent,
    LogLevel,
    LumenLightConfig,
    MeshFormat,
    MocapExtractionRequest,
    MocapResult,
    MovieRenderQueueJobConfig,
    PBRTextureSet,
    PlanConfirmationRequest,
    PlanConfirmationResponse,
    PlanProposalEvent,
    PlanRiskLevel,
    PlanStatus,
    PlanStep,
    Pose3DKeyframe,
    ProductionPlan,
    ProgressEvent,
    RenderResult,
    Rotator3D,
    SceneBuildResult,
    SceneConfig,
    SkeletalHierarchy,
    StemSeparationResult,
    TelemetryEvent,
    Vector3D,
)


# -----------------------------------------------------------------------------
# 1. Primitives & Math
# -----------------------------------------------------------------------------

def test_vector_3d_operations() -> None:
    vec = Vector3D(x=10.0, y=20.5, z=-30.0)
    assert vec.x == 10.0
    assert vec.to_tuple() == (10.0, 20.5, -30.0)
    assert Vector3D.from_tuple((1.0, 2.0, 3.0)).to_tuple() == (1.0, 2.0, 3.0)
    ue5_dict = vec.to_ue5_dict()
    assert ue5_dict == {"X": 10.0, "Y": 20.5, "Z": -30.0}


def test_rotator_3d_operations() -> None:
    rot = Rotator3D(pitch=15.0, yaw=90.0, roll=-45.0)
    assert rot.to_tuple() == (15.0, 90.0, -45.0)
    assert Rotator3D.from_tuple((0.0, 180.0, 0.0)).yaw == 180.0
    assert rot.to_ue5_dict() == {"Pitch": 15.0, "Yaw": 90.0, "Roll": -45.0}


def test_color_rgb_validation() -> None:
    col = ColorRGB(r=0.5, g=1.0, b=0.0)
    assert col.to_tuple() == (0.5, 1.0, 0.0)
    assert col.to_ue5_dict()["A"] == 1.0

    with pytest.raises(ValidationError):
        ColorRGB(r=1.5, g=0.0, b=0.0)


# -----------------------------------------------------------------------------
# 2. Audio Models
# -----------------------------------------------------------------------------

def test_audio_analysis_models() -> None:
    req = AudioAnalysisRequest(audio_path="track.wav", separate_stems=True, sample_rate=48000)
    assert req.audio_path == "track.wav"
    assert req.sample_rate == 48000

    res = AudioAnalysisResult(
        bpm=128.0,
        duration_seconds=180.5,
        beat_timestamps=[0.5, 1.0, 1.5, 2.0],
        onset_envelope=[0.1, 0.9, 0.2],
        stems={"vocals": "vocal.wav", "drums": "drums.wav"},
    )
    assert res.bpm == 128.0
    assert res.get_stem_path(AudioStemType.VOCALS) == "vocal.wav"
    assert res.get_stem_path("drums") == "drums.wav"
    assert res.get_stem_path("bass") is None


def test_stem_separation_result() -> None:
    stem_res = StemSeparationResult(
        stems={"vocals": "v.wav", "drums": "d.wav"},
        model_used="htdemucs",
        sample_rate=44100,
        duration_seconds=12.5,
    )
    assert stem_res.model_used == "htdemucs"
    assert len(stem_res.stems) == 2


# -----------------------------------------------------------------------------
# 3. 3D Mesh & Textures
# -----------------------------------------------------------------------------

def test_pbr_texture_set() -> None:
    empty_pbr = PBRTextureSet()
    assert not empty_pbr.has_textures()

    pbr = PBRTextureSet(albedo_path="albedo.png", resolution=2048)
    assert pbr.has_textures()
    assert pbr.resolution == 2048


def test_image_to_3d_models() -> None:
    req = ImageTo3DRequest(image_path="char.png", provider="tripo", texture_resolution=1024)
    assert req.provider == "tripo"

    res = ImageTo3DResult(
        mesh_path="out.glb",
        vertex_count=5000,
        polygon_count=9800,
        cached=True,
        mesh_format=MeshFormat.GLB,
        provider_used="tripo",
        generation_time_seconds=1.25,
    )
    assert res.cached is True
    assert res.vertex_count == 5000


# -----------------------------------------------------------------------------
# 4. Rigging & Mocap
# -----------------------------------------------------------------------------

def test_rigging_models() -> None:
    bone = BoneDescriptor(
        name="root",
        parent_name=None,
        head_position=(0.0, 0.0, 0.0),
        tail_position=(0.0, 0.0, 10.0),
    )
    hierarchy = SkeletalHierarchy(skeleton_type="ue5_mannequin", root_bone="root", bones=[bone])
    assert hierarchy.bones[0].name == "root"

    rig_res = AutoRigResult(
        rigged_mesh_path="rigged.glb",
        bone_count=64,
        hierarchy=["root", "pelvis", "spine_01"],
        skeleton_type="ue5_mannequin",
        success=True,
    )
    assert rig_res.bone_count == 64
    assert rig_res.success is True


def test_mocap_models() -> None:
    keyframe = Pose3DKeyframe(
        timestamp=0.033,
        frame_index=1,
        keypoints_3d={"nose": (0.0, 1.7, 0.0), "left_eye": (-0.05, 1.75, 0.0)},
        confidence_scores={"nose": 0.99},
    )
    assert keyframe.frame_index == 1

    mocap_res = MocapResult(
        animation_path="dance.glb",
        frame_count=90,
        fps=30,
        duration=3.0,
        keyframes=[keyframe],
    )
    assert mocap_res.duration == 3.0
    assert mocap_res.fps == 30


# -----------------------------------------------------------------------------
# 5. Scene & Camera Keyframes
# -----------------------------------------------------------------------------

def test_camera_keyframe_normalization() -> None:
    # Flat representation
    kf1 = CameraKeyframe.model_validate({
        "time": 1.5,
        "x": 100.0,
        "y": -200.0,
        "z": 150.0,
        "pitch": -10.0,
        "yaw": 45.0,
        "fov": 35.0,
    })
    assert kf1.time == 1.5
    assert kf1.timestamp == 1.5
    assert kf1.x == 100.0
    assert kf1.position == (100.0, -200.0, 150.0)
    assert kf1.rotation == (-10.0, 45.0, 0.0)

    # Tuple representation
    kf2 = CameraKeyframe.model_validate({
        "timestamp": 2.0,
        "position": [50.0, -100.0, 80.0],
        "rotation": [5.0, 30.0, 0.0],
        "fov": 50.0,
    })
    assert kf2.time == 2.0
    assert kf2.x == 50.0
    assert kf2.position == (50.0, -100.0, 80.0)
    assert kf2.pitch == 5.0

    payload = kf1.to_ue5_payload()
    assert "Location" in payload
    assert "Rotation" in payload


def test_camera_keyframe_validation_bounds() -> None:
    with pytest.raises(ValidationError):
        CameraKeyframe.model_validate({"fov": -10.0})

    with pytest.raises(ValidationError):
        CameraKeyframe.model_validate({"fov": 200.0})


def test_scene_config_and_build_result() -> None:
    cfg = SceneConfig(
        mesh_path="char.glb",
        animation_path="anim.glb",
        lighting_preset="cinematic_three_point",
        lighting_config=LumenLightConfig(),
    )
    assert cfg.mesh_path == "char.glb"

    res = SceneBuildResult(
        success=True,
        actor_ids=["CineCameraActor_1", "SkeletalMeshActor_1"],
        scene_path="/Game/Cinematics/Seq_Main",
    )
    assert res.success is True
    assert len(res.actor_ids) == 2


# -----------------------------------------------------------------------------
# 6. Render Models
# -----------------------------------------------------------------------------

def test_mrq_job_config() -> None:
    job = MovieRenderQueueJobConfig(
        scene_path="/Game/Seq",
        output_path="render.mp4",
        resolution="3840x2160",
    )
    assert job.get_resolution_dimensions() == (3840, 2160)

    res = RenderResult(
        video_path="render.mp4",
        frame_count=1800,
        elapsed_seconds=45.2,
        fps=60,
        resolution="3840x2160",
    )
    assert res.frame_count == 1800


# -----------------------------------------------------------------------------
# 7. Production Plan & Copilot
# -----------------------------------------------------------------------------

def test_production_plan_lifecycle() -> None:
    step = PlanStep(
        step_id="step_audio",
        index=0,
        tool_name="analyze_audio",
        description="Analyze audio BPM and beats",
        parameters={"audio_path": "song.mp3"},
        requires_confirmation=False,
    )
    plan = ProductionPlan(
        plan_id="plan_01",
        title="Music Video Production",
        description="End-to-end production pipeline",
        steps=[step],
    )
    assert plan.get_step("step_audio") is not None
    assert not plan.is_all_completed()

    updated = plan.mark_step_status("step_audio", PlanStatus.COMPLETED, output_preview="audio_preview.json")
    assert updated is True
    assert plan.steps[0].status == PlanStatus.COMPLETED
    assert plan.steps[0].output_preview == "audio_preview.json"
    assert plan.is_all_completed()


def test_plan_confirmation() -> None:
    req = PlanConfirmationRequest(plan_id="plan_01", step_id="step_render")
    assert req.plan_id == "plan_01"

    resp = PlanConfirmationResponse(plan_id="plan_01", step_id="step_render", approved=True)
    assert resp.approved is True


# -----------------------------------------------------------------------------
# 8. Telemetry Events Polymorphism
# -----------------------------------------------------------------------------

def test_telemetry_event_polymorphism() -> None:
    # Progress event
    pe_raw = {
        "type": "progress",
        "stage": "audio",
        "percentage": 50.0,
        "message": "Separating stems",
    }
    pe = TelemetryEvent.model_validate(pe_raw)
    assert isinstance(pe, ProgressEvent)
    assert pe.stage == "audio"
    assert pe.percentage == 50.0

    # Plan proposal event
    ppe_raw = {
        "type": "plan_proposal",
        "plan_id": "p123",
        "steps": [],
        "status": "proposed",
    }
    ppe = TelemetryEvent.model_validate(ppe_raw)
    assert isinstance(ppe, PlanProposalEvent)
    assert ppe.plan_id == "p123"

    # Asset ready event
    are_raw = {
        "type": "asset_ready",
        "asset_id": "mesh_01",
        "asset_type": "mesh_3d",
        "file_path": "/path/mesh.glb",
    }
    are = TelemetryEvent.model_validate(are_raw)
    assert isinstance(are, AssetReadyEvent)
    assert are.asset_type == AssetType.MESH_3D

    # Log event
    le_raw = {
        "type": "log",
        "level": "info",
        "message": "System initialized",
    }
    le = TelemetryEvent.model_validate(le_raw)
    assert isinstance(le, LogEvent)
    assert le.level == LogLevel.INFO
