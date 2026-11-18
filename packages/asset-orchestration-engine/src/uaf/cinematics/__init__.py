"""
UAF-81.97: Procedural Cinematics, CineCamera Director & UE5 Sequencer Package.
"""

from .core.contracts import (
    CinematicShotType,
    FramingRule,
    CameraDampingMode,
    Vector3D,
    Rotator3D,
    Transform3D,
    CinematicSubject,
    LensSettings,
    FocusSettings,
    CameraKeyframe,
    CinematicShot,
    CinematicSequenceSpec,
    UE5LevelSequenceManifest,
)
from .framing.framing_engine import CinematicFramingEngine
from .trajectory.spline_solver import CameraTrajectorySolver, BoundingBox3D
from .focus.depth_of_field import AutoFocusDepthOfField
from .exporter.ue5_sequencer_exporter import UE5SequencerExporter

__all__ = [
    "CinematicShotType",
    "FramingRule",
    "CameraDampingMode",
    "Vector3D",
    "Rotator3D",
    "Transform3D",
    "CinematicSubject",
    "LensSettings",
    "FocusSettings",
    "CameraKeyframe",
    "CinematicShot",
    "CinematicSequenceSpec",
    "UE5LevelSequenceManifest",
    "CinematicFramingEngine",
    "CameraTrajectorySolver",
    "BoundingBox3D",
    "AutoFocusDepthOfField",
    "UE5SequencerExporter",
]
