"""
Pytest configuration and shared fixtures for IANIMATION E2E test suites.
Adheres strictly to SOLID and Zero-Any principles (Pydantic v2 validation).
"""
from __future__ import annotations

import importlib
from pathlib import Path
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple, Type
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.e2e.fixtures.synthetic_audio import (
    create_corrupt_wav,
    create_rhythmic_pulse_wav,
    create_silent_wav,
    create_sine_wave_wav,
)
from tests.e2e.fixtures.synthetic_image import (
    create_1x1_png,
    create_corrupt_png,
    create_solid_png,
)
from tests.e2e.fixtures.synthetic_mesh import (
    create_corrupt_glb,
    create_minimal_glb,
)
from tests.e2e.fixtures.synthetic_video import (
    create_corrupt_video,
    create_dummy_video,
    create_synthetic_pose_sequence,
)


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers for 4-tier E2E testing methodology."""
    config.addinivalue_line("markers", "tier1: Tier 1 Feature Coverage tests")
    config.addinivalue_line("markers", "tier2: Tier 2 Boundary and Corner Case tests")
    config.addinivalue_line("markers", "tier3: Tier 3 Cross-Feature Interaction tests")
    config.addinivalue_line("markers", "tier4: Tier 4 Real-World Scenario tests")


@pytest.fixture
def synthetic_audio_path(tmp_path: Path) -> Path:
    """Provide a valid 120.0 BPM rhythmic WAV fixture."""
    file_path = tmp_path / "synthetic_beat_120bpm.wav"
    return create_rhythmic_pulse_wav(file_path, bpm=120.0, duration_seconds=3.0)


@pytest.fixture
def synthetic_sine_audio_path(tmp_path: Path) -> Path:
    """Provide a clean 440 Hz sine wave WAV fixture."""
    file_path = tmp_path / "synthetic_sine_440hz.wav"
    return create_sine_wave_wav(file_path, duration_seconds=2.0)


@pytest.fixture
def synthetic_silent_audio_path(tmp_path: Path) -> Path:
    """Provide a digital silence WAV fixture."""
    file_path = tmp_path / "synthetic_silence.wav"
    return create_silent_wav(file_path, duration_seconds=1.0)


@pytest.fixture
def synthetic_corrupt_audio_path(tmp_path: Path) -> Path:
    """Provide a corrupt WAV file fixture."""
    file_path = tmp_path / "corrupt_audio.wav"
    return create_corrupt_wav(file_path)


@pytest.fixture
def synthetic_image_path(tmp_path: Path) -> Path:
    """Provide a solid 64x64 RGBA PNG fixture."""
    file_path = tmp_path / "concept_character.png"
    return create_solid_png(file_path, width=64, height=64)


@pytest.fixture
def synthetic_1x1_image_path(tmp_path: Path) -> Path:
    """Provide a 1x1 PNG fixture for boundary testing."""
    file_path = tmp_path / "boundary_1x1.png"
    return create_1x1_png(file_path)


@pytest.fixture
def synthetic_corrupt_image_path(tmp_path: Path) -> Path:
    """Provide a corrupt PNG file fixture."""
    file_path = tmp_path / "corrupt_image.png"
    return create_corrupt_png(file_path)


@pytest.fixture
def synthetic_glb_path(tmp_path: Path) -> Path:
    """Provide a conforming glTF 2.0 binary mesh fixture."""
    file_path = tmp_path / "character_biped.glb"
    return create_minimal_glb(file_path, mesh_name="CharacterModel")


@pytest.fixture
def synthetic_corrupt_glb_path(tmp_path: Path) -> Path:
    """Provide a corrupt GLB mesh fixture."""
    file_path = tmp_path / "corrupt_mesh.glb"
    return create_corrupt_glb(file_path)


@pytest.fixture
def synthetic_video_path(tmp_path: Path) -> Path:
    """Provide a synthetic MP4 video container fixture."""
    file_path = tmp_path / "dance_motion.mp4"
    return create_dummy_video(file_path, duration_seconds=1.0, fps=30)


@pytest.fixture
def synthetic_corrupt_video_path(tmp_path: Path) -> Path:
    """Provide a corrupt MP4 video container fixture."""
    file_path = tmp_path / "corrupt_video.mp4"
    return create_corrupt_video(file_path)


@pytest.fixture
def sample_camera_keyframes() -> List[Dict[str, float]]:
    """Provide standard CineCamera keyframe specifications."""
    return [
        {"time": 0.0, "x": 0.0, "y": -400.0, "z": 120.0, "pitch": -5.0, "yaw": 0.0, "fov": 45.0},
        {"time": 1.0, "x": 100.0, "y": -350.0, "z": 130.0, "pitch": -4.0, "yaw": 15.0, "fov": 45.0},
        {"time": 2.0, "x": 200.0, "y": -300.0, "z": 140.0, "pitch": -3.0, "yaw": 30.0, "fov": 50.0},
    ]


@pytest.fixture
def sample_scene_config(
    synthetic_glb_path: Path,
    sample_camera_keyframes: List[Dict[str, float]],
) -> Dict[str, Any]:
    """Provide standard SceneConfig payload conforming to PROJECT.md §1."""
    return {
        "mesh_path": str(synthetic_glb_path),
        "animation_path": str(synthetic_glb_path),
        "lighting_preset": "studio_3point",
        "camera_choreography": sample_camera_keyframes,
        "environment": "dark_stage",
        "lumen_enabled": True,
    }


def import_or_skip(module_name: str, symbol_name: Optional[str] = None) -> Any:
    """
    Safely import a backend module or symbol.
    If the milestone implementation has not landed yet, gracefully skips the test
    with an informative message rather than crashing with an unhandled ModuleNotFoundError.
    This enables progressive testability as workers implement milestones.
    """
    try:
        mod = importlib.import_module(module_name)
        if symbol_name:
            if not hasattr(mod, symbol_name):
                pytest.skip(f"Symbol '{symbol_name}' not yet exported in '{module_name}'")
            return getattr(mod, symbol_name)
        return mod
    except (ImportError, ModuleNotFoundError) as err:
        pytest.skip(f"Module '{module_name}' pending milestone implementation: {err}")
