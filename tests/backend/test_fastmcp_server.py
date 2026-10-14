"""
Comprehensive Unit Test Suite for FastMCP Protocol Server (backend.mcp.server).

Tests:
1. FastMCPServer instantiation, naming, and tool registration
2. Default tool registry (all 6 atomic tools: analyze_audio, image_to_3d, auto_rig, extract_mocap, build_ue5_scene, render_video)
3. Dual-invocation parity via call_tool with strict typing
4. Parameter schema reflection, type validation, and error boundaries
5. Global singleton instance verification

Strictly 100% Zero-Any compliant with Pydantic v2 domain models.
"""

from __future__ import annotations

import inspect
import math
from pathlib import Path
import struct
from typing import Dict, List, Optional
import wave

import pytest

from backend.core.models import (
    AudioAnalysisResult,
    AutoRigResult,
    ImageTo3DResult,
    MocapResult,
    RenderResult,
    SceneBuildResult,
    SceneConfig,
    StrictBaseModel,
)
from backend.mcp.server import (
    FastMCPServer,
    MCPToolCallable,
    mcp_server,
)
from backend.mcp.tools import (
    SceneConfigDict,
    analyze_audio,
    auto_rig,
    build_ue5_scene,
    extract_mocap,
    image_to_3d,
    render_video,
)


# =============================================================================
# Helper Utilities & Test Fixtures
# =============================================================================

class DummyCustomResult(StrictBaseModel):
    """Custom model for testing dynamic tool registration."""
    status: str
    code: int


def _create_synthetic_wav(target_path: Path, duration_seconds: float = 1.0) -> Path:
    """Create a conforming PCM 16-bit mono WAV file."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 44100
    num_samples = int(duration_seconds * sample_rate)
    with wave.open(str(target_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(num_samples):
            val = int(0.5 * 32767.0 * math.sin(2.0 * math.pi * 440.0 * i / sample_rate))
            frames.extend(struct.pack("<h", max(-32768, min(32767, val))))
        wf.writeframes(frames)
    return target_path


def _create_minimal_image(target_path: Path) -> Path:
    """Create a 1x1 PNG file."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    target_path.write_bytes(png_bytes)
    return target_path


def _create_minimal_video(target_path: Path) -> Path:
    """Create a dummy MP4 video file."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(b"\x00\x00\x00 ftypmp42\x00\x00\x00\x00mp42isom\x00\x00\x00\x08mdat")
    return target_path


def _create_minimal_glb(target_path: Path) -> Path:
    """Create a dummy GLB mesh file."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(b"glTF\x02\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00JSON\x00\x00\x00\x00BIN\x00")
    return target_path


# =============================================================================
# 1. Server Instantiation & Configuration Tests
# =============================================================================

def test_fastmcp_server_default_init() -> None:
    server = FastMCPServer()
    assert server.server_name == "ianimation-orchestrator"
    assert len(server.tools) == 6


def test_fastmcp_server_custom_name() -> None:
    server = FastMCPServer(server_name="custom-ianimation-server")
    assert server.server_name == "custom-ianimation-server"


def test_fastmcp_server_default_tool_inventory() -> None:
    server = FastMCPServer()
    tools = server.list_tools()
    expected_tools = {
        "analyze_audio",
        "image_to_3d",
        "auto_rig",
        "extract_mocap",
        "build_ue5_scene",
        "render_video",
    }
    assert set(tools) == expected_tools


# =============================================================================
# 2. Custom Tool Registration & Introspection Tests
# =============================================================================

def test_fastmcp_register_custom_tool() -> None:
    server = FastMCPServer(server_name="test-server")

    def custom_ping(tag: str = "ok") -> DummyCustomResult:
        return DummyCustomResult(status=tag, code=200)

    server.register_tool("custom_ping", custom_ping)
    assert "custom_ping" in server.list_tools()

    result = server.call_tool("custom_ping", tag="pong")
    assert isinstance(result, DummyCustomResult)
    assert result.status == "pong"
    assert result.code == 200


def test_fastmcp_overwrite_existing_tool() -> None:
    server = FastMCPServer()

    def mock_audio(audio_path: str) -> DummyCustomResult:
        return DummyCustomResult(status="mocked", code=1)

    server.register_tool("analyze_audio", mock_audio)
    res = server.call_tool("analyze_audio", audio_path="test.wav")
    assert isinstance(res, DummyCustomResult)
    assert res.status == "mocked"


# =============================================================================
# 3. Dual-Invocation Parity Tests for all 6 Core Tools
# =============================================================================

def test_call_tool_unregistered_tool_raises_keyerror() -> None:
    server = FastMCPServer()
    with pytest.raises(KeyError, match="Tool 'unknown_tool' is not registered"):
        server.call_tool("unknown_tool")


def test_call_tool_analyze_audio(tmp_path: Path) -> None:
    server = FastMCPServer()
    wav_file = tmp_path / "test_track.wav"
    _create_synthetic_wav(wav_file, duration_seconds=1.5)

    result = server.call_tool("analyze_audio", audio_path=str(wav_file))
    assert isinstance(result, AudioAnalysisResult)
    assert result.duration_seconds == 1.5
    assert 40.0 <= result.bpm <= 300.0
    assert len(result.beat_timestamps) > 0


def test_call_tool_image_to_3d(tmp_path: Path) -> None:
    server = FastMCPServer()
    img_file = tmp_path / "avatar.png"
    _create_minimal_image(img_file)
    out_glb = tmp_path / "avatar_out.glb"

    result = server.call_tool("image_to_3d", image_path=str(img_file), output_path=str(out_glb))
    assert isinstance(result, ImageTo3DResult)
    assert Path(result.mesh_path).exists()
    assert result.vertex_count > 0


def test_call_tool_auto_rig(tmp_path: Path) -> None:
    server = FastMCPServer()
    mesh_file = tmp_path / "character.glb"
    _create_minimal_glb(mesh_file)
    out_rig = tmp_path / "character_rigged.glb"

    result = server.call_tool("auto_rig", mesh_path=str(mesh_file), output_path=str(out_rig))
    assert isinstance(result, AutoRigResult)
    assert result.success is True
    assert result.bone_count == 21
    assert Path(result.rigged_mesh_path).exists()


def test_call_tool_extract_mocap(tmp_path: Path) -> None:
    server = FastMCPServer()
    vid_file = tmp_path / "dance.mp4"
    _create_minimal_video(vid_file)
    out_mocap = tmp_path / "dance_mocap.glb"

    result = server.call_tool("extract_mocap", video_path=str(vid_file), target_fps=30, output_path=str(out_mocap))
    assert isinstance(result, MocapResult)
    assert result.fps == 30
    assert result.duration > 0
    assert Path(result.animation_path).exists()


def test_call_tool_build_ue5_scene_with_model(tmp_path: Path) -> None:
    server = FastMCPServer()
    mesh_file = tmp_path / "stage_char.glb"
    _create_minimal_glb(mesh_file)

    config = SceneConfig(
        mesh_path=str(mesh_file),
        level_name="TestMcpStage",
        lighting_preset="cyberpunk_neon",
    )
    result = server.call_tool("build_ue5_scene", scene_config=config)
    assert isinstance(result, SceneBuildResult)
    assert result.success is True
    assert len(result.actor_ids) > 0
    assert "LS_TestMcpStage" in result.scene_path


def test_call_tool_build_ue5_scene_with_dict(tmp_path: Path) -> None:
    server = FastMCPServer()
    mesh_file = tmp_path / "dict_char.glb"
    _create_minimal_glb(mesh_file)

    config_dict: SceneConfigDict = {
        "mesh_path": str(mesh_file),
        "level_name": "DictStage",
        "lighting_preset": "studio_3point",
    }
    result = server.call_tool("build_ue5_scene", scene_config=config_dict)
    assert isinstance(result, SceneBuildResult)
    assert result.success is True
    assert "LS_DictStage" in result.scene_path


def test_call_tool_render_video(tmp_path: Path) -> None:
    server = FastMCPServer()
    out_mp4 = tmp_path / "rendered_clip.mp4"

    result = server.call_tool(
        "render_video",
        scene_path="/Game/Sequences/LS_TestStage",
        output_path=str(out_mp4),
        fps=30,
        resolution="1280x720",
    )
    assert isinstance(result, RenderResult)
    assert result.success is True
    assert Path(result.video_path).exists()
    assert result.fps == 30


# =============================================================================
# 4. Error Boundaries & Parameter Validation Tests
# =============================================================================

def test_call_tool_empty_string_argument_raises_typeerror() -> None:
    server = FastMCPServer()
    with pytest.raises(TypeError, match="must be a non-empty string"):
        server.call_tool("analyze_audio", audio_path="")

    with pytest.raises(TypeError, match="must be a non-empty string"):
        server.call_tool("image_to_3d", image_path="   ")

    with pytest.raises(TypeError, match="must be a non-empty string"):
        server.call_tool("auto_rig", mesh_path="")

    with pytest.raises(TypeError, match="must be a non-empty string"):
        server.call_tool("extract_mocap", video_path="")

    with pytest.raises(TypeError, match="must be a non-empty string"):
        server.call_tool("render_video", scene_path="", output_path="out.mp4")

    with pytest.raises(TypeError, match="must be a non-empty string"):
        server.call_tool("render_video", scene_path="/Game/Seq", output_path="")


def test_call_tool_missing_required_arguments_raises() -> None:
    server = FastMCPServer()
    with pytest.raises(TypeError):
        server.call_tool("analyze_audio")  # missing audio_path

    with pytest.raises(TypeError):
        server.call_tool("image_to_3d")  # missing image_path


# =============================================================================
# 5. Schema Reflection & Global Singleton Tests
# =============================================================================

def test_tool_signatures_and_docstrings() -> None:
    server = FastMCPServer()
    for tool_name, tool_func in server.tools.items():
        sig = inspect.signature(tool_func)
        assert len(sig.parameters) >= 1, f"Tool '{tool_name}' must have parameters"
        assert tool_func.__doc__ is not None, f"Tool '{tool_name}' must have a docstring"
        assert len(tool_func.__doc__.strip()) > 10


def test_global_singleton_mcp_server() -> None:
    assert isinstance(mcp_server, FastMCPServer)
    assert len(mcp_server.tools) == 6
    assert "analyze_audio" in mcp_server.tools
    assert "render_video" in mcp_server.tools
