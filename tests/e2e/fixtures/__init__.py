"""
IANIMATION E2E Test Suite - Synthetic Fixtures Package.
Provides pure-Python generators for synthetic audio, image, 3D mesh, and video artifacts.
"""
from __future__ import annotations

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

__all__ = [
    "create_sine_wave_wav",
    "create_rhythmic_pulse_wav",
    "create_silent_wav",
    "create_corrupt_wav",
    "create_solid_png",
    "create_1x1_png",
    "create_corrupt_png",
    "create_minimal_glb",
    "create_corrupt_glb",
    "create_dummy_video",
    "create_synthetic_pose_sequence",
    "create_corrupt_video",
]
