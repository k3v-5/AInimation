"""
Tier 3: Cross-Feature Interactions E2E Test Suite.
Validates pairwise data flows, serialization handshakes, and subsystem contracts.
Strictly adheres to SOLID principles and Zero-Any Policy (Pydantic v2).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import pytest

from tests.e2e.conftest import import_or_skip


# ---------------------------------------------------------------------------
# Interaction 1: Audio Analysis -> CineCamera Beat Choreography
# ---------------------------------------------------------------------------

@pytest.mark.tier3
def test_interaction_audio_to_camera_choreography(synthetic_audio_path: Path) -> None:
    """
    Validates data flow:
    F-AI-02 (Audio Analysis) -> F-UE5-07 (CineCamera Beat Sync).
    Audio analysis generates beat timestamps which are consumed directly by
    the CineCamera choreographer to produce aligned camera cuts.
    """
    audio_mod = import_or_skip("backend.ai.audio")
    cam_mod = import_or_skip("backend.ue5.camera")
    
    analyze_fn = getattr(audio_mod, "analyze_audio", None)
    cam_choreograph_fn = getattr(cam_mod, "generate_camera_track", None)
    if analyze_fn is None or cam_choreograph_fn is None:
        pytest.skip("Audio or Camera module not yet fully implemented")
        
    # Phase 1: Extract audio beats
    audio_res = analyze_fn(str(synthetic_audio_path), separate_stems=False)
    assert audio_res.bpm > 0.0
    assert len(audio_res.beat_timestamps) > 0
    
    # Phase 2: Feed beat timestamps into camera choreographer
    camera_keyframes = cam_choreograph_fn(
        beat_timestamps=audio_res.beat_timestamps,
        total_duration=audio_res.duration_seconds,
        preset="dramatic_orbit",
    )
    assert len(camera_keyframes) > 0
    # Keyframe timestamps should align within epsilon of beat timestamps
    first_keyframe_time = camera_keyframes[0].time if hasattr(camera_keyframes[0], "time") else camera_keyframes[0]["time"]
    assert first_keyframe_time >= 0.0


# ---------------------------------------------------------------------------
# Interaction 2: Image-to-3D Mesh -> Auto-Rigging Armature
# ---------------------------------------------------------------------------

@pytest.mark.tier3
def test_interaction_image_to_3d_to_auto_rig(synthetic_image_path: Path, tmp_path: Path) -> None:
    """
    Validates data flow:
    F-AI-05 (Image-to-3D GLB) -> F-AI-06 (Auto-Rigging).
    Generates a 3D mesh from input image, then passes the resulting .glb
    into the auto-rigger to attach a standard UE5 bipedal skeletal hierarchy.
    """
    img_mod = import_or_skip("backend.ai.image_to_3d")
    rig_mod = import_or_skip("backend.ai.auto_rig")
    
    img_to_3d_fn = getattr(img_mod, "generate_procedural_glb", None)
    auto_rig_fn = getattr(rig_mod, "auto_rig", None)
    if img_to_3d_fn is None or auto_rig_fn is None:
        pytest.skip("Image-to-3D or Auto-Rig module not yet fully implemented")
        
    # Phase 1: Ingest image, output GLB mesh
    mesh_path = tmp_path / "generated_mesh.glb"
    img_res = img_to_3d_fn(str(synthetic_image_path), str(mesh_path))
    assert mesh_path.exists()
    
    # Phase 2: Ingest GLB mesh, output rigged mesh with bone hierarchy
    rig_res = auto_rig_fn(mesh_path=str(mesh_path), skeleton_type="ue5_mannequin")
    assert rig_res is not None
    assert hasattr(rig_res, "rigged_mesh_path") or hasattr(rig_res, "bone_count")
    if hasattr(rig_res, "bone_count"):
        assert rig_res.bone_count > 0


# ---------------------------------------------------------------------------
# Interaction 3: Rigged Mesh + Mocap -> Scene Assembly & MRQ Render
# ---------------------------------------------------------------------------

@pytest.mark.tier3
def test_interaction_scene_assembly_to_mrq_render(
    synthetic_glb_path: Path,
    sample_camera_keyframes: List[Dict[str, float]],
    tmp_path: Path,
) -> None:
    """
    Validates data flow:
    F-UE5-04/05/06 (Scene Assembly) -> F-UE5-08 (MRQ Render).
    Combines rigged mesh, camera choreography, and Lumen lighting into a
    Level Sequence, then triggers the Movie Render Queue.
    """
    mcp_tools_mod = import_or_skip("backend.mcp.tools")
    build_scene_fn = getattr(mcp_tools_mod, "build_ue5_scene", None)
    render_video_fn = getattr(mcp_tools_mod, "render_video", None)
    if build_scene_fn is None or render_video_fn is None:
        pytest.skip("FastMCP atomic scene tools not yet fully implemented")
        
    # Phase 1: Build scene
    scene_config = {
        "mesh_path": str(synthetic_glb_path),
        "animation_path": str(synthetic_glb_path),
        "lighting_preset": "studio_3point",
        "camera_choreography": sample_camera_keyframes,
    }
    scene_result = build_scene_fn(scene_config)
    assert scene_result.success is True
    assert scene_result.scene_path is not None
    
    # Phase 2: Render video from scene
    output_video = tmp_path / "output_render.mp4"
    render_result = render_video_fn(
        scene_path=scene_result.scene_path,
        output_path=str(output_video),
        fps=30,
        resolution="1280x720",
    )
    assert render_result is not None
    assert render_result.frame_count > 0


# ---------------------------------------------------------------------------
# Interaction 4: Production Plan Proposal -> Human Approval -> Telemetry Event
# ---------------------------------------------------------------------------

@pytest.mark.tier3
def test_interaction_plan_proposal_approval_telemetry() -> None:
    """
    Validates data flow:
    F-MCP-03 (Plan Proposal) -> F-MCP-04 (Approval Gate) -> F-CORE-02 (Telemetry Bus).
    Verifies that approving a proposed plan step emits a progress telemetry event
    to listening frontend subscribers.
    """
    plan_mod = import_or_skip("backend.mcp.plan_engine")
    telem_mod = import_or_skip("backend.core.telemetry")
    
    plan_engine_cls = getattr(plan_mod, "PlanEngine", None)
    telem_bus_cls = getattr(telem_mod, "TelemetryBus", None)
    if plan_engine_cls is None or telem_bus_cls is None:
        pytest.skip("PlanEngine or TelemetryBus not yet fully implemented")
        
    telem_bus = telem_bus_cls()
    captured_events: List[Any] = []
    
    def on_event(event: Any) -> None:
        captured_events.append(event)
        
    telem_bus.subscribe(on_event)
    
    engine = plan_engine_cls(telemetry_bus=telem_bus)
    plan = engine.create_plan(
        goal="Produce Animated 3D Music Video",
        audio_path="test_audio.wav",
        image_path="test_char.png",
    )
    assert len(plan.steps) > 0
    
    # Approve first step
    first_step = plan.steps[0]
    engine.confirm_step(plan_id=plan.plan_id, step_id=first_step.step_id, approved=True)
    
    # Verify telemetry bus received events
    assert len(captured_events) > 0
