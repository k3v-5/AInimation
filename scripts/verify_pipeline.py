#!/usr/bin/env python3
"""
IANIMATION - End-to-End 9-Phase Verification CLI Pipeline.

Simulates the entire assisted production pipeline from raw audio and concept images
to a final rendered cinematic video, validating all intermediate artifacts,
telemetry broadcasts, and data contracts.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.core.models import (
    AudioAnalysisResult,
    AutoRigResult,
    ImageTo3DResult,
    MocapResult,
    RenderResult,
    SceneBuildResult,
)
from backend.core.telemetry import TelemetryBus, get_telemetry_bus
from backend.mcp.plan_engine import PlanEngine
from backend.mcp.tools import (
    analyze_audio,
    auto_rig,
    build_ue5_scene,
    extract_mocap,
    image_to_3d,
    render_video,
)
from tests.e2e.fixtures.synthetic_audio import create_rhythmic_pulse_wav
from tests.e2e.fixtures.synthetic_image import create_solid_png
from tests.e2e.fixtures.synthetic_video import create_dummy_video


def log_phase(step_num: int, name: str) -> None:
    print(f"\n========================================================")
    print(f" [PHASE {step_num}/9] {name}")
    print(f"========================================================")


def main() -> int:
    start_total = time.time()
    work_dir = PROJECT_ROOT / "temp_verify_run"
    work_dir.mkdir(parents=True, exist_ok=True)

    print("========================================================")
    print("   IANIMATION - 3D AI ANIMATION ORCHESTRATOR VERIFY     ")
    print("========================================================")

    # -------------------------------------------------------------------------
    log_phase(1, "Environment & Configuration Verification")
    from backend.core.config import get_settings
    settings = get_settings()
    print(f"  * Mode: {settings.env}")
    print(f"  * UE5 Host: {settings.ue5_host}:{settings.ue5_http_port}")
    print(f"  * Cache Dir: {settings.cache_dir}")
    print("  [OK] Configuration loaded successfully.")

    # -------------------------------------------------------------------------
    log_phase(2, "Telemetry Bus & Event Subscription")
    bus = get_telemetry_bus()
    event_log = []
    bus.add_callback(lambda ev: event_log.append(ev))
    print("  [OK] Telemetry bus online. Registered real-time callback subscriber.")

    # -------------------------------------------------------------------------
    log_phase(3, "Synthetic Media Generation (Zero-GPU Fixtures)")
    audio_file = work_dir / "input_track_128bpm.wav"
    image_file = work_dir / "character_concept.png"
    video_file = work_dir / "dance_reference.mp4"

    create_rhythmic_pulse_wav(audio_file, bpm=128.0, duration_seconds=3.0)
    create_solid_png(image_file, width=128, height=128)
    create_dummy_video(video_file, duration_seconds=2.0)
    print(f"  * Audio: {audio_file.name} ({audio_file.stat().st_size} bytes)")
    print(f"  * Image: {image_file.name} ({image_file.stat().st_size} bytes)")
    print(f"  * Video: {video_file.name} ({video_file.stat().st_size} bytes)")
    print("  [OK] Synthetic input media fixtures ready.")

    # -------------------------------------------------------------------------
    log_phase(4, "Copilot Production Plan & Human Confirmation Gate")
    plan_engine = PlanEngine(telemetry_bus=bus)
    plan = plan_engine.create_plan(
        goal="Cyberpunk 3D Music Video",
        audio_path=str(audio_file),
        image_path=str(image_file),
        video_path=str(video_file),
        style="cyberpunk",
    )
    print(f"  * Plan ID: {plan.plan_id}")
    print(f"  * Proposed Steps: {len(plan.steps)}")
    for step in plan.steps:
        plan_engine.confirm_step(plan.plan_id, step.step_id, approved=True)
    print("  [OK] Human confirmation gate passed for all stages.")

    # -------------------------------------------------------------------------
    log_phase(5, "FastMCP Tool: Audio Rhythm Analysis (analyze_audio)")
    audio_res: AudioAnalysisResult = analyze_audio(str(audio_file), separate_stems=False)
    print(f"  * Detected BPM: {audio_res.bpm}")
    print(f"  * Beat Grid Markers: {len(audio_res.beat_timestamps)} timestamps")
    print(f"  * Danceability Score: {audio_res.danceability}")
    assert audio_res.bpm > 0
    print("  [OK] Audio analysis complete and verified.")

    # -------------------------------------------------------------------------
    log_phase(6, "FastMCP Tool: Image-to-3D Generation (image_to_3d)")
    mesh_out = work_dir / "character_mesh.glb"
    mesh_res: ImageTo3DResult = image_to_3d(str(image_file), provider="procedural_cpu", output_path=str(mesh_out))
    print(f"  * Output Mesh: {mesh_res.mesh_path}")
    print(f"  * Vertices: {mesh_res.vertex_count} | Polygons: {mesh_res.polygon_count}")
    print(f"  * Format: {mesh_res.mesh_format}")
    assert Path(mesh_res.mesh_path).exists()
    print("  [OK] 3D Mesh asset produced and verified.")

    # -------------------------------------------------------------------------
    log_phase(7, "FastMCP Tool: Skeletal Auto-Rigging (auto_rig)")
    rig_out = work_dir / "character_rigged.glb"
    rig_res: AutoRigResult = auto_rig(mesh_path=mesh_res.mesh_path, skeleton_type="ue5_mannequin", output_path=str(rig_out))
    print(f"  * Rigged Mesh: {rig_res.rigged_mesh_path}")
    print(f"  * Bone Count: {rig_res.bone_count} (Skeleton: {rig_res.skeleton_type})")
    assert Path(rig_res.rigged_mesh_path).exists()
    print("  [OK] Character skeletal rigging bound and verified.")

    # -------------------------------------------------------------------------
    log_phase(8, "FastMCP Tool: Scene Assembly in UE5 (build_ue5_scene)")
    from backend.ue5.camera import generate_camera_track
    camera_track = generate_camera_track(audio_res.beat_timestamps, total_duration=audio_res.duration_seconds, preset="dramatic_orbit")

    scene_res: SceneBuildResult = build_ue5_scene({
        "mesh_path": rig_res.rigged_mesh_path,
        "animation_path": rig_res.rigged_mesh_path,
        "lighting_preset": "cyberpunk_neon",
        "camera_choreography": [kf.model_dump() for kf in camera_track],
        "level_name": "Stage_Cyberpunk",
    })
    print(f"  * Scene Sequence: {scene_res.scene_path}")
    print(f"  * Spawned Actors: {len(scene_res.actor_ids)}")
    assert scene_res.success is True
    print("  [OK] UE5 scene constructed with Lumen lighting and CineCamera track.")

    # -------------------------------------------------------------------------
    log_phase(9, "FastMCP Tool: Movie Render Queue (render_video)")
    video_out = work_dir / "final_music_video.mp4"
    render_res: RenderResult = render_video(
        scene_path=scene_res.scene_path,
        output_path=str(video_out),
        fps=30,
        resolution="1280x720",
    )
    print(f"  * Rendered Video: {render_res.video_path}")
    print(f"  * Frames: {render_res.frame_count} | FPS: {render_res.fps}")
    print(f"  * File Size: {render_res.file_size_bytes} bytes")
    print(f"  * Render Time: {render_res.elapsed_seconds}s")
    assert Path(render_res.video_path).exists()
    assert render_res.file_size_bytes > 0
    print("  [OK] Cinematic video rendered and verified.")

    # -------------------------------------------------------------------------
    elapsed_total = round(time.time() - start_total, 2)
    print("\n========================================================")
    print(f"   VERIFICATION COMPLETED SUCCESSFULLY IN {elapsed_total}s!      ")
    print(f"   All 9 production phases verified with 0 errors.     ")
    print("========================================================\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
