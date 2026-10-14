"""
Comprehensive Unit Test Suite for Generative AI Pipelines (backend.ai).

Tests:
1. BaseAIProvider and ProviderRegistry (LSP, OCP, category management)
2. AudioAnalyzer and AudioSeparator (dynamic WAV parsing, silence handling, beat grids)
3. ImageTo3DProvider (Tripo, Fal.ai, Procedural CPU adapters, GLB container generation)
4. AutoRigger (UE5 mannequin skeletal hierarchy, bone binding)
5. MocapExtractor (3D pose extraction, rotoscopy, beat-synced dance loop)
6. ComfyUIClient and NeuralEnhancer (prompt queuing, deterministic hashing, video enhancement)
7. AsyncExecutionEngine (CancellationToken cooperative cancellation, AsyncTaskSupervisor)

Strictly 100% Zero-Any compliant with Pydantic v2 domain models.
"""

from __future__ import annotations

import asyncio
import math
from pathlib import Path
import struct
import threading
from typing import Dict, List, Optional
import wave

import pytest

from backend.ai.async_engine import AsyncTaskSupervisor, CancellationToken
from backend.ai.audio import (
    AudioAnalyzer,
    AudioSeparator,
    analyze_audio,
    separate_stems,
)
from backend.ai.auto_rig import UE5_MANNEQUIN_BONES, AutoRigger, auto_rig
from backend.ai.base import BaseAIProvider, ProviderRegistry, provider_registry
from backend.ai.image_to_3d import (
    FalAIProvider,
    ImageTo3DProvider,
    ProceduralGLBProvider,
    TripoProvider,
    generate_procedural_glb,
)
from backend.ai.mocap import (
    MocapExtractor,
    extract_mocap,
    remove_background,
)
from backend.ai.neural import (
    ComfyUIClient,
    NeuralEnhancer,
    WorkflowPayloadDict,
    enhance_video,
)
from backend.core.models import (
    AudioAnalysisResult,
    AutoRigResult,
    ImageTo3DResult,
    MeshFormat,
    MocapResult,
    StemSeparationResult,
)


# =============================================================================
# Helper Fixtures & Utilities
# =============================================================================

def _create_synthetic_wav(
    target_path: Path,
    duration_seconds: float = 1.0,
    sample_rate: int = 44100,
    frequency: float = 440.0,
    amplitude: float = 0.5,
) -> Path:
    """Create a conforming PCM 16-bit mono WAV file for testing."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    num_samples = int(duration_seconds * sample_rate)
    with wave.open(str(target_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(num_samples):
            val = int(amplitude * 32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
            frames.extend(struct.pack("<h", max(-32768, min(32767, val))))
        wf.writeframes(frames)
    return target_path


def _create_silent_wav(
    target_path: Path,
    duration_seconds: float = 1.0,
    sample_rate: int = 44100,
) -> Path:
    """Create a 16-bit mono WAV file containing pure digital silence."""
    return _create_synthetic_wav(target_path, duration_seconds, sample_rate, frequency=0.0, amplitude=0.0)


def _create_minimal_image(target_path: Path) -> Path:
    """Create a dummy 1x1 PNG file for image-to-3d tests."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    # Minimal 1x1 transparent PNG binary
    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    target_path.write_bytes(png_bytes)
    return target_path


def _create_minimal_video(target_path: Path) -> Path:
    """Create a minimal dummy video container file for mocap tests."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(b"\x00\x00\x00 ftypmp42\x00\x00\x00\x00mp42isom\x00\x00\x00\x08mdat")
    return target_path


# =============================================================================
# 1. BaseAIProvider & ProviderRegistry Tests
# =============================================================================

class ConcreteTestProvider(BaseAIProvider):
    """Test concrete provider subclassing BaseAIProvider."""

    def __init__(self, name: str = "test_concrete", is_cloud: bool = False) -> None:
        super().__init__(name=name, is_cloud=is_cloud)

    def health_check(self) -> bool:
        return True


class IncompleteTestProvider(BaseAIProvider):
    """Subclass without health_check implementation to test abstract enforcement."""
    pass


def test_base_ai_provider_initialization() -> None:
    prov = ConcreteTestProvider(name="local_model", is_cloud=False)
    assert prov.name == "local_model"
    assert prov.is_cloud is False
    assert prov.health_check() is True

    cloud_prov = ConcreteTestProvider(name="cloud_model", is_cloud=True)
    assert cloud_prov.name == "cloud_model"
    assert cloud_prov.is_cloud is True


def test_base_ai_provider_abstract_health_check() -> None:
    with pytest.raises(TypeError):
        # Cannot instantiate abstract class without implementing health_check
        IncompleteTestProvider(name="broken")  # type: ignore[abstract]


def test_provider_registry_lifecycle() -> None:
    registry = ProviderRegistry()
    prov_a = ConcreteTestProvider(name="prov_a")
    prov_b = ConcreteTestProvider(name="prov_b")

    registry.register("audio", prov_a)
    registry.register("audio", prov_b)

    # Specific name retrieval
    assert registry.get_provider("audio", "prov_a") is prov_a
    assert registry.get_provider("audio", "prov_b") is prov_b

    # "auto" or None retrieves first available
    auto_prov = registry.get_provider("audio", "auto")
    assert auto_prov in (prov_a, prov_b)
    none_prov = registry.get_provider("audio", None)
    assert none_prov in (prov_a, prov_b)

    # Missing provider / category returns None
    assert registry.get_provider("audio", "nonexistent") is prov_a  # fallback to first
    assert registry.get_provider("nonexistent_category", "prov_a") is None

    # List providers
    prov_dict = registry.list_providers()
    assert "audio" in prov_dict
    assert "prov_a" in prov_dict["audio"]
    assert "prov_b" in prov_dict["audio"]

    single_category = registry.list_providers("audio")
    assert "audio" in single_category
    assert len(single_category) == 1


def test_global_provider_registry_has_default_providers() -> None:
    provs = provider_registry.list_providers()
    assert "audio" in provs
    assert "image_to_3d" in provs
    assert "rigging" in provs
    assert "mocap" in provs
    assert "neural" in provs


# =============================================================================
# 2. AudioAnalyzer & AudioSeparator Tests
# =============================================================================

def test_audio_analyzer_health_check() -> None:
    analyzer = AudioAnalyzer()
    assert analyzer.health_check() is True


def test_audio_analyzer_missing_file_raises(tmp_path: Path) -> None:
    analyzer = AudioAnalyzer()
    missing_file = tmp_path / "does_not_exist.wav"
    with pytest.raises(FileNotFoundError, match="Audio file does not exist"):
        analyzer.analyze(str(missing_file))


def test_audio_analyzer_corrupted_file_raises(tmp_path: Path) -> None:
    analyzer = AudioAnalyzer()
    corrupt_file = tmp_path / "corrupt.wav"
    corrupt_file.write_bytes(b"NOT_A_WAV_FILE_HEADER")
    with pytest.raises(ValueError, match="Corrupt or unsupported audio file"):
        analyzer.analyze(str(corrupt_file))


def test_audio_analyzer_zero_frame_wav_raises(tmp_path: Path) -> None:
    analyzer = AudioAnalyzer()
    empty_wav = tmp_path / "empty.wav"
    with wave.open(str(empty_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
    with pytest.raises(ValueError, match="Invalid audio structure"):
        analyzer.analyze(str(empty_wav))


def test_audio_analyzer_digital_silence(tmp_path: Path) -> None:
    analyzer = AudioAnalyzer()
    silence_file = tmp_path / "silence.wav"
    _create_silent_wav(silence_file, duration_seconds=2.0)

    result = analyzer.analyze(str(silence_file))
    assert isinstance(result, AudioAnalysisResult)
    assert result.bpm == 0.0
    assert result.duration_seconds == 2.0
    assert result.beat_timestamps == []
    assert result.danceability == 0.0
    assert result.stems is None


def test_audio_analyzer_valid_audio(tmp_path: Path) -> None:
    analyzer = AudioAnalyzer()
    audio_file = tmp_path / "synth_track.wav"
    _create_synthetic_wav(audio_file, duration_seconds=2.5, frequency=220.0, amplitude=0.8)

    result = analyzer.analyze(str(audio_file))
    assert isinstance(result, AudioAnalysisResult)
    assert result.duration_seconds == 2.5
    assert 40.0 <= result.bpm <= 300.0
    assert len(result.beat_timestamps) > 0
    assert result.beat_timestamps[0] == 0.0
    assert len(result.onset_envelope) > 0
    assert result.time_signature == "4/4"


def test_audio_analyzer_tempo_hint(tmp_path: Path) -> None:
    analyzer = AudioAnalyzer()
    audio_file = tmp_path / "steady_track.wav"
    _create_synthetic_wav(audio_file, duration_seconds=1.0, frequency=440.0, amplitude=0.5)

    result = analyzer.analyze(str(audio_file), tempo_hint=128.0)
    assert isinstance(result, AudioAnalysisResult)
    assert 40.0 <= result.bpm <= 300.0


def test_audio_separator_health_check() -> None:
    separator = AudioSeparator()
    assert separator.health_check() is True


def test_audio_separator_produces_stems(tmp_path: Path) -> None:
    separator = AudioSeparator()
    source_audio = tmp_path / "song.wav"
    _create_synthetic_wav(source_audio, duration_seconds=1.0)

    output_dir = tmp_path / "stems_output"
    result = separator.separate(str(source_audio), output_dir=str(output_dir))

    assert isinstance(result, StemSeparationResult)
    assert result.stems is not None
    assert set(result.stems.keys()) == {"vocals", "drums", "bass", "other"}
    for stem_name, stem_path in result.stems.items():
        assert Path(stem_path).exists()
        assert Path(stem_path).is_file()
        assert Path(stem_path).stat().st_size > 0


def test_audio_facade_functions(tmp_path: Path) -> None:
    audio_file = tmp_path / "facade_audio.wav"
    _create_synthetic_wav(audio_file, duration_seconds=1.0)

    analysis = analyze_audio(str(audio_file), separate_stems=False)
    assert isinstance(analysis, AudioAnalysisResult)
    assert analysis.duration_seconds == 1.0

    stems_res = separate_stems(str(audio_file))
    assert isinstance(stems_res, StemSeparationResult)
    assert stems_res.stems is not None
    assert "vocals" in stems_res.stems


# =============================================================================
# 3. ImageTo3DProvider & Adapters Tests
# =============================================================================

def test_image_to_3d_base_class_abstract_generate() -> None:
    class DummyImageTo3D(ImageTo3DProvider):
        def health_check(self) -> bool:
            return True

    prov = DummyImageTo3D(name="dummy")
    with pytest.raises(NotImplementedError):
        prov.generate("test.png")


def test_image_to_3d_missing_input_raises(tmp_path: Path) -> None:
    missing_image = tmp_path / "missing.png"
    out_glb = tmp_path / "out.glb"
    with pytest.raises(FileNotFoundError, match="Input image file does not exist"):
        generate_procedural_glb(str(missing_image), str(out_glb))


def test_procedural_glb_provider_generate(tmp_path: Path) -> None:
    prov = ProceduralGLBProvider()
    assert prov.health_check() is True
    assert prov.is_cloud is False

    img_file = tmp_path / "concept.png"
    _create_minimal_image(img_file)
    out_glb = tmp_path / "character.glb"

    result = prov.generate(str(img_file), output_path=str(out_glb))
    assert isinstance(result, ImageTo3DResult)
    assert Path(result.mesh_path).exists()
    assert result.mesh_format == MeshFormat.GLB
    assert result.vertex_count > 0
    assert result.polygon_count > 0
    assert result.textures.albedo_path == str(img_file)

    # Verify glTF 2.0 binary header
    glb_bytes = Path(result.mesh_path).read_bytes()
    assert len(glb_bytes) >= 12
    assert glb_bytes[:4] == b"glTF"
    version = struct.unpack("<I", glb_bytes[4:8])[0]
    assert version == 2


def test_tripo_and_fal_ai_providers(tmp_path: Path) -> None:
    img_file = tmp_path / "avatar.png"
    _create_minimal_image(img_file)

    tripo = TripoProvider()
    assert tripo.is_cloud is True
    assert tripo.health_check() is True
    res_tripo = tripo.generate(str(img_file))
    assert isinstance(res_tripo, ImageTo3DResult)
    assert Path(res_tripo.mesh_path).exists()
    assert res_tripo.provider_used == "tripo_ai"

    fal = FalAIProvider()
    assert fal.is_cloud is True
    assert fal.health_check() is True
    res_fal = fal.generate(str(img_file))
    assert isinstance(res_fal, ImageTo3DResult)
    assert Path(res_fal.mesh_path).exists()
    assert res_fal.provider_used == "fal_ai"


# =============================================================================
# 4. AutoRigger Tests
# =============================================================================

def test_auto_rigger_health_check() -> None:
    rigger = AutoRigger()
    assert rigger.health_check() is True


def test_auto_rigger_missing_mesh_raises(tmp_path: Path) -> None:
    rigger = AutoRigger()
    missing_mesh = tmp_path / "missing_mesh.glb"
    with pytest.raises(FileNotFoundError, match="Source mesh not found for auto-rigging"):
        rigger.rig(str(missing_mesh))


def test_auto_rigger_ue5_mannequin(tmp_path: Path) -> None:
    rigger = AutoRigger()
    mesh_path = tmp_path / "biped.glb"
    mesh_path.write_bytes(b"glTF\x02\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00JSON\x00\x00\x00\x00BIN\x00")

    result = rigger.rig(str(mesh_path), skeleton_type="ue5_mannequin")
    assert isinstance(result, AutoRigResult)
    assert result.success is True
    assert result.skeleton_type == "ue5_mannequin"
    assert result.bone_count == len(UE5_MANNEQUIN_BONES)
    assert result.hierarchy == UE5_MANNEQUIN_BONES
    assert Path(result.rigged_mesh_path).exists()


def test_auto_rigger_custom_skeleton_and_facade(tmp_path: Path) -> None:
    mesh_path = tmp_path / "creature.glb"
    mesh_path.write_bytes(b"glTF\x02\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00JSON\x00\x00\x00\x00BIN\x00")

    out_path = tmp_path / "creature_rigged.glb"
    result = auto_rig(str(mesh_path), skeleton_type="custom_quadruped", output_path=str(out_path))
    assert isinstance(result, AutoRigResult)
    assert result.skeleton_type == "custom_quadruped"
    assert result.bone_count == 4
    assert result.hierarchy == ["root", "hips", "spine", "head"]
    assert result.rigged_mesh_path == str(out_path.resolve())


# =============================================================================
# 5. MocapExtractor Tests
# =============================================================================

def test_mocap_extractor_health_check() -> None:
    extractor = MocapExtractor()
    assert extractor.health_check() is True


def test_mocap_extractor_missing_video_raises(tmp_path: Path) -> None:
    extractor = MocapExtractor()
    missing_vid = tmp_path / "ghost.mp4"
    with pytest.raises(FileNotFoundError, match="Video file not found"):
        extractor.extract(str(missing_vid))


def test_mocap_extractor_extract_and_facade(tmp_path: Path) -> None:
    video_path = tmp_path / "dance.mp4"
    _create_minimal_video(video_path)

    out_anim = tmp_path / "dance_anim.glb"
    result = extract_mocap(str(video_path), target_fps=60, output_path=str(out_anim))
    assert isinstance(result, MocapResult)
    assert result.fps == 60
    assert result.frame_count > 0
    assert result.duration > 0.0
    assert result.tracked_joints_count == 33
    assert Path(result.animation_path).exists()


def test_mocap_rotoscope_and_dance_loop(tmp_path: Path) -> None:
    extractor = MocapExtractor()
    vid_file = tmp_path / "actor.mp4"
    _create_minimal_video(vid_file)

    # Rotoscope
    roto_out = tmp_path / "actor_alpha.mp4"
    roto_res = remove_background(str(vid_file), output_path=str(roto_out))
    assert Path(roto_res).exists()

    # Dance loop
    loop_out = tmp_path / "dance_120.glb"
    loop_res = extractor.dance_loop(bpm=128.0, duration=4.0, output_path=str(loop_out))
    assert Path(loop_res).exists()


# =============================================================================
# 6. ComfyUIClient & NeuralEnhancer Tests
# =============================================================================

def test_comfyui_client_health_check() -> None:
    client = ComfyUIClient(host="127.0.0.1", port=8188)
    assert client.health_check() is True


def test_comfyui_client_queue_prompt_dynamic_id() -> None:
    client = ComfyUIClient()

    # Empty payload
    id1 = client.queue_prompt(None)
    assert isinstance(id1, str)
    assert id1.startswith("prompt_")

    # Custom workflow payload
    payload: WorkflowPayloadDict = {
        "model": "wan_video_2.1",
        "steps": 25,
        "cfg": 7.5,
        "denoise": 0.65,
    }
    id2 = client.queue_prompt(payload)
    assert isinstance(id2, str)
    assert id2.startswith("prompt_")
    assert id1 != id2


def test_comfyui_client_enhance_and_facade(tmp_path: Path) -> None:
    vid_path = tmp_path / "raw_render.mp4"
    _create_minimal_video(vid_path)

    out_enhanced = tmp_path / "cinematic_render.mp4"
    enhanced_path = enhance_video(
        video_path=str(vid_path),
        prompt="photorealistic cyberpunk anime lighting",
        output_path=str(out_enhanced),
    )
    assert Path(enhanced_path).exists()
    assert enhanced_path == str(out_enhanced.resolve())


def test_neural_enhancer_subclass() -> None:
    enhancer = NeuralEnhancer()
    assert isinstance(enhancer, ComfyUIClient)
    assert enhancer.name == "comfyui_neural_enhancer"


# =============================================================================
# 7. AsyncExecutionEngine & Task Supervisor Tests
# =============================================================================

def test_cancellation_token_lifecycle() -> None:
    token = CancellationToken()
    assert token.is_cancelled is False

    # Does not raise when not cancelled
    token.check()

    # Cancel
    token.cancel()
    assert token.is_cancelled is True
    with pytest.raises(asyncio.CancelledError, match="Operation was cancelled"):
        token.check()

    # Reset
    token.reset()
    assert token.is_cancelled is False
    token.check()


def test_cancellation_token_thread_safety() -> None:
    token = CancellationToken()
    cancelled_count = 0
    lock = threading.Lock()

    def worker() -> None:
        nonlocal cancelled_count
        token.cancel()
        if token.is_cancelled:
            with lock:
                cancelled_count += 1

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert token.is_cancelled is True
    assert cancelled_count == 10


def test_async_task_supervisor_lifecycle() -> None:
    supervisor = AsyncTaskSupervisor()
    job_id = "job_test_001"

    token = supervisor.create_token(job_id)
    assert isinstance(token, CancellationToken)
    assert token.is_cancelled is False

    # Cancel active job
    cancelled = supervisor.cancel_job(job_id)
    assert cancelled is True
    assert token.is_cancelled is True

    # Cancel unknown job
    assert supervisor.cancel_job("unknown_job_999") is False

    # Cleanup
    supervisor.cleanup(job_id)
    assert supervisor.cancel_job(job_id) is False
