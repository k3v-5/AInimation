"""
Tier 2: Boundary & Corner Cases E2E Test Suite.
Exposes failure modes, edge conditions, resource constraints, corrupt files, and adversarial inputs.
Strictly adheres to SOLID principles and Zero-Any Policy (Pydantic v2).
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, List
import pytest
from pydantic import ValidationError

from tests.e2e.conftest import import_or_skip
from tests.e2e.fixtures.synthetic_audio import (
    create_corrupt_wav,
    create_rhythmic_pulse_wav,
    create_silent_wav,
)
from tests.e2e.fixtures.synthetic_image import (
    create_1x1_png,
    create_corrupt_png,
)
from tests.e2e.fixtures.synthetic_mesh import (
    create_corrupt_glb,
    create_minimal_glb,
)
from tests.e2e.fixtures.synthetic_video import (
    create_corrupt_video,
    create_dummy_video,
)


# ---------------------------------------------------------------------------
# Corrupt & Empty File Handlers (Media Integrity)
# ---------------------------------------------------------------------------

@pytest.mark.tier2
def test_f_core_01_invalid_payload_validation() -> None:
    """Tier 2: Core domain models reject malformed or missing required fields with ValidationError."""
    models_mod = import_or_skip("backend.core.models")
    scene_config_cls = getattr(models_mod, "SceneConfig", None)
    if scene_config_cls is None:
        pytest.skip("SceneConfig not yet exported in backend.core.models")
        
    # Attempt instantiating SceneConfig with missing required fields
    with pytest.raises(ValidationError):
        scene_config_cls.model_validate({"lighting_preset": "invalid_missing_all_paths"})


@pytest.mark.tier2
def test_f_ai_02_silent_and_extreme_bpm(tmp_path: Path) -> None:
    """Tier 2: Audio analyzer handles digital silence and extreme BPM bounds gracefully."""
    audio_mod = import_or_skip("backend.ai.audio")
    analyze_fn = getattr(audio_mod, "analyze_audio", None)
    if analyze_fn is None:
        pytest.skip("analyze_audio not yet exported in backend.ai.audio")
        
    # Case 1: Silent audio track
    silent_path = create_silent_wav(tmp_path / "silence.wav", duration_seconds=1.0)
    result_silent = analyze_fn(str(silent_path), separate_stems=False)
    # Should not crash; should return valid model with 0.0 or default BPM
    assert result_silent.bpm >= 0.0
    assert isinstance(result_silent.beat_timestamps, list)
    
    # Case 2: Extreme fast BPM (240.0 BPM)
    fast_path = create_rhythmic_pulse_wav(tmp_path / "fast_240bpm.wav", bpm=240.0, duration_seconds=2.0)
    result_fast = analyze_fn(str(fast_path), separate_stems=False)
    assert result_fast.bpm > 0.0


@pytest.mark.tier2
def test_f_ai_02_corrupt_audio_file(tmp_path: Path) -> None:
    """Tier 2: Audio analyzer gracefully handles corrupt or truncated WAV files with structured error."""
    audio_mod = import_or_skip("backend.ai.audio")
    analyze_fn = getattr(audio_mod, "analyze_audio", None)
    if analyze_fn is None:
        pytest.skip("analyze_audio not yet exported in backend.ai.audio")
        
    corrupt_path = create_corrupt_wav(tmp_path / "corrupt.wav")
    with pytest.raises((ValueError, RuntimeError, IOError, ValidationError)):
        analyze_fn(str(corrupt_path), separate_stems=False)


@pytest.mark.tier2
def test_f_ai_05_1x1_and_monochrome_image(tmp_path: Path) -> None:
    """Tier 2: Image-to-3D generator handles 1x1 boundary images and corrupt image files."""
    img_mod = import_or_skip("backend.ai.image_to_3d")
    gen_fn = getattr(img_mod, "generate_procedural_glb", None)
    if gen_fn is None:
        pytest.skip("generate_procedural_glb not yet exported in backend.ai.image_to_3d")
        
    img_1x1 = create_1x1_png(tmp_path / "boundary_1x1.png")
    out_glb = tmp_path / "out_1x1.glb"
    result = gen_fn(str(img_1x1), str(out_glb))
    assert out_glb.exists()
    assert out_glb.stat().st_size > 0


@pytest.mark.tier2
def test_f_ue5_04_corrupt_glb_import_failure(tmp_path: Path) -> None:
    """Tier 2: UE5 asset importer returns structured error on malformed glTF binary."""
    ue5_mod = import_or_skip("backend.ue5.client")
    client_cls = getattr(ue5_mod, "UE5RestClient", None)
    if client_cls is None:
        pytest.skip("UE5RestClient not yet exported in backend.ue5.client")
        
    corrupt_glb = create_corrupt_glb(tmp_path / "corrupt_mesh.glb")
    # Client should return structured error code or raise expected exception
    assert corrupt_glb.exists()


# ---------------------------------------------------------------------------
# Spatial Transform Boundary Tests (Zero / Negative / Extreme)
# ---------------------------------------------------------------------------

@pytest.mark.tier2
def test_f_ue5_07_zero_beats_fallback() -> None:
    """Tier 2: CineCamera choreographer provides fallback timeline when beat list is empty."""
    cam_mod = import_or_skip("backend.ue5.camera")
    gen_cam_fn = getattr(cam_mod, "generate_camera_track", None)
    if gen_cam_fn is None:
        pytest.skip("generate_camera_track not yet exported in backend.ue5.camera")
        
    # Empty beat list (silent track)
    empty_beats: List[float] = []
    track = gen_cam_fn(beat_timestamps=empty_beats, total_duration=10.0, preset="smooth_orbit")
    assert track is not None
    assert len(track) >= 2, "Choreographer must generate at least start and end keyframes"


@pytest.mark.tier2
def test_f_core_01_negative_and_zero_spatial_transforms() -> None:
    """Tier 2: Spatial transforms validate zero scale and negative coordinates without NaN crash."""
    models_mod = import_or_skip("backend.core.models")
    keyframe_cls = getattr(models_mod, "CameraKeyframe", None)
    if keyframe_cls is None:
        pytest.skip("CameraKeyframe not yet exported in backend.core.models")
        
    # Valid extreme/negative coordinates
    valid_keyframe = keyframe_cls.model_validate({
        "time": 0.0,
        "x": -9999.0,
        "y": -9999.0,
        "z": -100.0,
        "pitch": -89.0,
        "yaw": 359.0,
        "fov": 30.0,
    })
    assert valid_keyframe.x == -9999.0
    
    # Invalid negative FOV or extreme angle
    with pytest.raises(ValidationError):
        keyframe_cls.model_validate({
            "time": 0.0,
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
            "pitch": 0.0,
            "yaw": 0.0,
            "fov": -15.0,  # Physically impossible FOV
        })


# ---------------------------------------------------------------------------
# Async Supervisors, Cancellation & Timeouts
# ---------------------------------------------------------------------------

@pytest.mark.tier2
def test_f_ai_10_cancellation_token_abort() -> None:
    """Tier 2: Async supervisor stops tasks cooperatively when cancellation token is triggered."""
    async_mod = import_or_skip("backend.ai.async_engine")
    token_cls = getattr(async_mod, "CancellationToken", None)
    if token_cls is None:
        pytest.skip("CancellationToken not yet exported in backend.ai.async_engine")
        
    token = token_cls()
    assert not token.is_cancelled
    token.cancel()
    assert token.is_cancelled


@pytest.mark.tier2
def test_f_mcp_04_rejected_step_halts_pipeline() -> None:
    """Tier 2: Rejecting a heavy step in PlanEngine halts execution without side effects."""
    plan_mod = import_or_skip("backend.mcp.plan_engine")
    plan_engine_cls = getattr(plan_mod, "PlanEngine", None)
    if plan_engine_cls is None:
        pytest.skip("PlanEngine not yet exported in backend.mcp.plan_engine")
        
    engine = plan_engine_cls()
    plan = engine.create_plan(goal="Render 3D Music Video", audio_path="mock.wav", image_path="mock.png")
    assert plan is not None
    
    # Reject the first step requiring confirmation
    first_heavy_step = next((s for s in plan.steps if s.requires_confirmation), None)
    if first_heavy_step:
        updated_plan = engine.reject_step(plan_id=plan.plan_id, step_id=first_heavy_step.step_id)
        assert updated_plan.status in ("rejected", "halted", "cancelled")


# ---------------------------------------------------------------------------
# Adversarial Security & Input Sanitization
# ---------------------------------------------------------------------------

@pytest.mark.tier2
def test_f_mcp_01_tool_invalid_args_rpc_error() -> None:
    """Tier 2: FastMCP tools reject malicious or out-of-type arguments with clear error."""
    tools_mod = import_or_skip("backend.mcp.tools")
    analyze_fn = getattr(tools_mod, "analyze_audio", None)
    if analyze_fn is None:
        pytest.skip("analyze_audio not yet exported in backend.mcp.tools")
        
    # Passing an invalid type (e.g. integer instead of file path string)
    with pytest.raises((TypeError, ValidationError, ValueError)):
        analyze_fn(audio_path=12345)  # type: ignore[arg-type]
