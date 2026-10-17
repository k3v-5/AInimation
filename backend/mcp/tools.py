"""
Atomic FastMCP Tool Implementations for IANIMATION.

Exposes the 6 core production tools with 100% strict typing, JSON Schema contracts,
and dual invocation parity (usable directly via Python and through Model Context Protocol).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Union

from backend.ai.audio import analyze_audio as ai_analyze_audio
from backend.ai.image_to_3d import generate_procedural_glb
from backend.ai.auto_rig import auto_rig as ai_auto_rig
from backend.ai.mocap import extract_mocap as ai_extract_mocap
from backend.core.models import (
    AudioAnalysisResult,
    AutoRigResult,
    ImageTo3DResult,
    MocapResult,
    RenderResult,
    SceneBuildResult,
    SceneConfig,
    ProgressEvent,
    LogEvent,
)
from backend.core.telemetry import get_telemetry_bus
from backend.engines.base import get_engine_adapter
from backend.ue5.client import UE5RestClient
from backend.ue5.lighting import LightingRig
from backend.ue5.mrq import render_sequence


def analyze_audio(
    audio_path: str,
    separate_stems: bool = True,
    tempo_hint: Optional[float] = None,
) -> AudioAnalysisResult:
    """
    Extract musical BPM, rhythm onsets, and beat timestamps from an audio track.

    Args:
        audio_path: Path to the audio file (.wav, .mp3).
        separate_stems: Whether to perform 4-stem track separation.
        tempo_hint: Optional BPM prior hint.

    Returns:
        AudioAnalysisResult containing BPM and beat grid.
    """
    if not isinstance(audio_path, str) or not audio_path.strip():
        raise TypeError(f"audio_path must be a non-empty string, got {type(audio_path).__name__}")

    bus = get_telemetry_bus()
    bus.emit_threadsafe(
        ProgressEvent(
            stage="audio_analysis",
            percentage=20.0,
            message=f"Analyzing audio file '{audio_path}'",
        )
    )
    result = ai_analyze_audio(audio_path=audio_path, separate_stems=separate_stems, tempo_hint=tempo_hint)
    bus.emit_threadsafe(
        ProgressEvent(
            stage="audio_analysis",
            percentage=100.0,
            message=f"Audio analysis complete: {result.bpm} BPM",
        )
    )
    return result


def image_to_3d(
    image_path: str,
    provider: str = "auto",
    texture_resolution: int = 1024,
    output_path: Optional[str] = None,
) -> ImageTo3DResult:
    """
    Generate a 3D textured mesh with PBR maps from a 2D reference image.

    Args:
        image_path: Path to the concept image file.
        provider: Provider identifier ('auto', 'tripo', 'fal', 'procedural_cpu').
        texture_resolution: Resolution for generated PBR textures.
        output_path: Optional destination path for the output .glb mesh.

    Returns:
        ImageTo3DResult with mesh path and vertex statistics.
    """
    if not isinstance(image_path, str) or not image_path.strip():
        raise TypeError(f"image_path must be a non-empty string, got {type(image_path).__name__}")

    dest = output_path or str(Path(image_path).with_suffix(".glb"))
    return generate_procedural_glb(
        image_path=image_path,
        output_path=dest,
        provider_name=provider,
        texture_resolution=texture_resolution,
    )


def auto_rig(
    mesh_path: str,
    skeleton_type: str = "ue5_mannequin",
    output_path: Optional[str] = None,
    engine: str = "auto",
) -> AutoRigResult:
    """
    Bind an anatomical skeletal hierarchy (UE5 humanoid, Avian, Canine) to a static 3D mesh.

    Args:
        mesh_path: Path to input 3D mesh (.glb/.obj/.fbx).
        skeleton_type: Hierarchy standard ('ue5_mannequin', 'avian', 'canine', 'mixamo').
        output_path: Optional destination for the rigged character asset.
        engine: Target rigging engine ('auto', 'ue5', or 'blender').

    Returns:
        AutoRigResult with bone hierarchy and binding status.
    """
    if not isinstance(mesh_path, str) or not mesh_path.strip():
        raise TypeError(f"mesh_path must be a non-empty string, got {type(mesh_path).__name__}")

    return ai_auto_rig(mesh_path=mesh_path, skeleton_type=skeleton_type, output_path=output_path, engine=engine)


def extract_mocap(
    video_path: str,
    target_fps: int = 30,
    output_path: Optional[str] = None,
) -> MocapResult:
    """
    Extract 3D skeletal motion capture animation from reference video.

    Args:
        video_path: Path to dance or motion video.
        target_fps: Target frame rate for animation keys.
        output_path: Optional output path for the animation track (.glb).

    Returns:
        MocapResult with animation path and frame count.
    """
    if not isinstance(video_path, str) or not video_path.strip():
        raise TypeError(f"video_path must be a non-empty string, got {type(video_path).__name__}")

    return ai_extract_mocap(video_path=video_path, target_fps=target_fps, output_path=output_path)


SceneConfigValue = Union[str, int, float, bool, None, List[Dict[str, float]], Dict[str, Union[str, float, bool]]]
SceneConfigDict = Dict[str, SceneConfigValue]


def build_scene(
    scene_config: Union[SceneConfig, SceneConfigDict],
    engine: str = "ue5",
) -> SceneBuildResult:
    """
    Assemble a 3D scene (Unreal Engine Level Sequence or Blender .blend) with lighting and camera.

    Args:
        scene_config: Specification of mesh, animation, lighting, and camera keyframes.
        engine: Target engine adapter ('ue5' or 'blender'). Defaults to 'ue5' for retrocompatibility.

    Returns:
        SceneBuildResult with instantiated sequence/scene path and actor IDs.
    """
    if isinstance(scene_config, dict):
        config_obj = SceneConfig.model_validate(scene_config)
    else:
        config_obj = scene_config

    adapter = get_engine_adapter(engine)
    return adapter.build_scene(config_obj)


def build_ue5_scene(scene_config: Union[SceneConfig, SceneConfigDict]) -> SceneBuildResult:
    """
    Assemble an Unreal Engine 5 cinematic scene (Level Sequence) with lighting and camera.
    Maintained as a high-fidelity alias for build_scene(scene_config, engine='ue5').
    """
    return build_scene(scene_config, engine="ue5")


def render_video(
    scene_path: str,
    output_path: str,
    fps: int = 60,
    resolution: str = "1920x1080",
    warmup_frames: int = 15,
    anti_aliasing_samples: int = 8,
    engine: str = "auto",
) -> RenderResult:
    """
    Render final cinematic video or still from Level Sequence (UE5 MRQ) or Blender scene.

    Args:
        scene_path: Path to Level Sequence package or Blender scene file.
        output_path: Destination path for final .mp4 video or image.
        fps: Video frame rate.
        resolution: Output resolution string (e.g. '1280x720', '1920x1080').
        warmup_frames: Simulation warmup frames.
        anti_aliasing_samples: Spatial/temporal AA samples.
        engine: Target engine ('auto', 'ue5', or 'blender').

    Returns:
        RenderResult with final video file statistics.
    """
    if not isinstance(scene_path, str) or not scene_path.strip():
        raise TypeError(f"scene_path must be a non-empty string, got {type(scene_path).__name__}")
    if not isinstance(output_path, str) or not output_path.strip():
        raise TypeError(f"output_path must be a non-empty string, got {type(output_path).__name__}")

    eng = engine.lower().strip()
    if eng == "auto":
        if scene_path.endswith((".blend", ".obj", ".glb", ".gltf")) or output_path.endswith((".png", ".jpg")):
            eng = "blender"
        else:
            eng = "ue5"

    adapter = get_engine_adapter(eng)
    return adapter.render_video(
        scene_path=scene_path,
        output_path=output_path,
        fps=fps,
        resolution=resolution,
        warmup_frames=warmup_frames,
        anti_aliasing_samples=anti_aliasing_samples,
    )
