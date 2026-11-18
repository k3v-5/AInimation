"""Camera bridge supporting Editor, Game, Cinematic, and Multi-Camera synchronization."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class CameraRole(str, Enum):
    CINEMATIC = "CINEMATIC"
    GAME = "GAME"
    EDITOR = "EDITOR"
    DEBUG = "DEBUG"
    CAPTURE = "CAPTURE"

    # UE-style aliases
    CINEMATIC_CAMERA = "CINEMATIC"
    GAME_CAMERA = "GAME"
    EDITOR_CAMERA = "EDITOR"
    DEBUG_CAMERA = "DEBUG"
    CAPTURE_CAMERA = "CAPTURE"


@dataclass
class CameraBridgePayload:
    camera_id: str
    camera_role: CameraRole = CameraRole.GAME
    location: List[float] = field(default_factory=lambda: [0.0, 0.0, 100.0])
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    fov: float = 90.0
    aspect_ratio: float = 1.777778
    near_clip_plane: float = 10.0
    far_clip_plane: float = 100000.0
    focal_length_mm: float = 35.0
    aperture_fstop: float = 2.8
    post_process_settings: Dict[str, Any] = field(default_factory=dict)
    role: Optional[CameraRole] = None
    fov_degrees: Optional[float] = None

    def __post_init__(self) -> None:
        if self.role is not None:
            self.camera_role = self.role
        else:
            self.role = self.camera_role

        if self.fov_degrees is not None:
            self.fov = self.fov_degrees
        else:
            self.fov_degrees = self.fov

    def to_dict(self) -> Dict[str, Any]:
        return {
            "camera_id": self.camera_id,
            "role": self.camera_role.value,
            "camera_role": self.camera_role.value,
            "location": self.location,
            "rotation": self.rotation,
            "fov": self.fov,
            "fov_degrees": self.fov,
            "aspect_ratio": self.aspect_ratio,
            "near_clip_plane": self.near_clip_plane,
            "far_clip_plane": self.far_clip_plane,
            "focal_length_mm": self.focal_length_mm,
            "aperture_fstop": self.aperture_fstop,
            "post_process_settings": self.post_process_settings,
        }
