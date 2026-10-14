"""
Unit tests for Generative AI Pipelines (audio, image_to_3d, auto_rig, mocap, neural, async_engine).
Conforms 100% to Zero-Any strict typing and SOLID architecture.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import pytest
import wave

from backend.ai.audio import AudioAnalyzer, analyze_audio, separate_stems
from backend.ai.image_to_3d import (
    ImageTo3DProvider,
    ProceduralGLBProvider,
    TripoProvider,
    FalAIProvider,
    generate_procedural_glb,
)
from backend.ai.auto_rig import AutoRigger, auto_rig, UE5_MANNEQUIN_BONES
from backend.ai.mocap import MocapExtractor, extract_mocap, remove_background, generate_dance_loop
from backend.ai.neural import ComfyUIClient, enhance_video
from backend.ai.async_engine import CancellationToken, AsyncTaskSupervisor
from backend.ai.base import provider_registry
from backend.core.models import MeshFormat, AudioAnalysisResult, ImageTo3DResult, AutoRigResult, MocapResult
from backend.ue5.client import _validate_glb_container


def _create_simple_wav(file_path: Path, duration_sec: float = 1.0, sample_rate: int = 44100) -> Path:
    """Helper to synthesize standard PCM mono WAV audio."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    n_frames = int(duration_sec * sample_rate)
    with wave.open(str(file_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        # Synthesize simple alternating square wave
        raw = b"\x7f\x00\x80\xff" * (n_frames // 2)
        wf.writeframes(raw[: n_frames * 2])
    return file_path


def _create_dummy_image(file_path: Path) -> Path:
    """Helper to write minimal PNG header."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
        b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return file_path


class TestAudioPipeline:
    def test_audio_analysis_basic(self, tmp_path: Path) -> None:
        wav_file = _create_simple_wav(tmp_path / "test.wav", duration_sec=1.5)
        res = analyze_audio(str(wav_file), separate_stems=False)
        assert isinstance(res, AudioAnalysisResult)
        assert res.duration_seconds > 0.0
        assert res.bpm >= 40.0
        assert len(res.onset_envelope) > 0
        assert res.stems is None

    def test_audio_analysis_with_stems(self, tmp_path: Path) -> None:
        wav_file = _create_simple_wav(tmp_path / "song.wav", duration_sec=1.0)
        res = analyze_audio(str(wav_file), separate_stems=True)
        assert res.stems is not None
        assert "vocals" in res.stems
        assert "drums" in res.stems
        assert "bass" in res.stems
        assert "other" in res.stems


class TestImageTo3DPipeline:
    def test_generate_procedural_glb(self, tmp_path: Path) -> None:
        img = _create_dummy_image(tmp_path / "character.png")
        out_glb = tmp_path / "character.glb"
        res = generate_procedural_glb(str(img), str(out_glb), provider_name="procedural_cpu")
        assert isinstance(res, ImageTo3DResult)
        assert res.mesh_format == MeshFormat.GLB
        assert out_glb.exists()
        assert _validate_glb_container(out_glb) is None
        assert res.vertex_count > 0
        assert res.polygon_count > 0

    def test_cloud_providers_registered(self) -> None:
        p_cpu = provider_registry.get_provider("image_to_3d", "procedural_cpu")
        p_tripo = provider_registry.get_provider("image_to_3d", "tripo_ai")
        p_fal = provider_registry.get_provider("image_to_3d", "fal_ai")
        assert p_cpu is not None
        assert p_tripo is not None
        assert p_fal is not None
        assert p_tripo.health_check() is True
        assert p_fal.health_check() is True


class TestAutoRigPipeline:
    def test_auto_rig_generation(self, tmp_path: Path) -> None:
        img = _create_dummy_image(tmp_path / "char.png")
        out_glb = tmp_path / "char.glb"
        generate_procedural_glb(str(img), str(out_glb))

        rig_res = auto_rig(str(out_glb), skeleton_type="ue5_mannequin")
        assert isinstance(rig_res, AutoRigResult)
        assert rig_res.success is True
        assert rig_res.bone_count == len(UE5_MANNEQUIN_BONES)
        assert "root" in rig_res.hierarchy
        assert "pelvis" in rig_res.hierarchy
        assert Path(rig_res.rigged_mesh_path).exists()


class TestMocapPipeline:
    def test_mocap_dance_loop(self, tmp_path: Path) -> None:
        out_glb = tmp_path / "dance.glb"
        loop_path = generate_dance_loop(bpm=128.0, duration=2.0, output_path=str(out_glb))
        assert Path(loop_path).exists()
        assert _validate_glb_container(Path(loop_path)) is None

    def test_mocap_rotoscope(self, tmp_path: Path) -> None:
        dummy_vid = tmp_path / "clip.mp4"
        dummy_vid.write_bytes(b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00isomiso2mp41\x00\x00\x00\x08mdat")
        roto = remove_background(str(dummy_vid))
        assert Path(roto).exists()


class TestNeuralPipeline:
    def test_comfyui_health_check(self) -> None:
        client = ComfyUIClient()
        assert client.health_check() is True

    def test_comfyui_queue_prompt_dynamic_id(self) -> None:
        client = ComfyUIClient()
        pid1 = client.queue_prompt({"test": 1})
        pid2 = client.queue_prompt({"test": 2})
        assert pid1.startswith("prompt_")
        assert pid2.startswith("prompt_")
        assert pid1 != pid2  # Dynamic SHA-256 / UUID entropy


class TestAsyncEngine:
    def test_cancellation_token(self) -> None:
        token = CancellationToken()
        assert token.is_cancelled is False
        token.cancel()
        assert token.is_cancelled is True
        with pytest.raises(asyncio.CancelledError):
            token.check()
        token.reset()
        assert token.is_cancelled is False

    def test_async_task_supervisor(self) -> None:
        supervisor = AsyncTaskSupervisor()
        tok = supervisor.create_token("job_42")
        assert tok.is_cancelled is False
        assert supervisor.cancel_job("job_42") is True
        assert tok.is_cancelled is True
        supervisor.cleanup("job_42")
        assert supervisor.cancel_job("job_42") is False
