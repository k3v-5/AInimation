"""
UAF-81.97: Procedural Cinematics & CineCamera Director Core Contracts.
Pydantic v2 domain models for optical lenses, camera transforms, framing rules,
keyframes, shots, and UE5 LevelSequence manifests.
"""

from enum import Enum
import math
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class CinematicShotType(str, Enum):
    ESTABLISHING_SHOT = "ESTABLISHING_SHOT"
    OVER_THE_SHOULDER = "OVER_THE_SHOULDER"
    SHOT_REVERSE_SHOT = "SHOT_REVERSE_SHOT"
    CLOSE_UP = "CLOSE_UP"
    WIDE_ACTION = "WIDE_ACTION"
    DUTCH_ANGLE = "DUTCH_ANGLE"
    ORBIT_BOSS_REVEAL = "ORBIT_BOSS_REVEAL"
    FIRST_PERSON_POV = "FIRST_PERSON_POV"


class FramingRule(str, Enum):
    RULE_OF_THIRDS = "RULE_OF_THIRDS"
    GOLDEN_RATIO = "GOLDEN_RATIO"
    CENTER_SYMMETRY = "CENTER_SYMMETRY"
    LOW_ANGLE_HERO = "LOW_ANGLE_HERO"
    HIGH_ANGLE_VULNERABLE = "HIGH_ANGLE_VULNERABLE"


class CameraDampingMode(str, Enum):
    SMOOTH_SPRING = "SMOOTH_SPRING"
    CATMULL_ROM_SPLINE = "CATMULL_ROM_SPLINE"
    LINEAR = "LINEAR"


class Vector3D(BaseModel):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def to_ue5_cm(self) -> "Vector3D":
        return Vector3D(x=self.x * 100.0, y=self.y * 100.0, z=self.z * 100.0)

    @classmethod
    def from_ue5_cm(cls, x_cm: float, y_cm: float, z_cm: float) -> "Vector3D":
        return cls(x=x_cm * 0.01, y=y_cm * 0.01, z=z_cm * 0.01)

    def distance_to(self, other: "Vector3D") -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2)

    def normalized(self) -> "Vector3D":
        mag = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
        if mag == 0:
            return Vector3D(x=0.0, y=0.0, z=1.0)
        return Vector3D(x=self.x / mag, y=self.y / mag, z=self.z / mag)

    def cross(self, other: "Vector3D") -> "Vector3D":
        return Vector3D(
            x=self.y * other.z - self.z * other.y,
            y=self.z * other.x - self.x * other.z,
            z=self.x * other.y - self.y * other.x,
        )

    def dot(self, other: "Vector3D") -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __add__(self, other: "Vector3D") -> "Vector3D":
        return Vector3D(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)

    def __sub__(self, other: "Vector3D") -> "Vector3D":
        return Vector3D(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)

    def __mul__(self, scalar: float) -> "Vector3D":
        return Vector3D(x=self.x * scalar, y=self.y * scalar, z=self.z * scalar)

    __rmul__ = __mul__


class Rotator3D(BaseModel):
    pitch: float = 0.0  # Rotation around Y axis in degrees
    yaw: float = 0.0    # Rotation around Z axis in degrees
    roll: float = 0.0   # Rotation around X axis in degrees


class Transform3D(BaseModel):
    position: Vector3D = Field(default_factory=Vector3D)
    rotation: Rotator3D = Field(default_factory=Rotator3D)


class CinematicSubject(BaseModel):
    actor_id: str
    world_pos: Vector3D
    eye_level_pos: Vector3D = Field(default_factory=Vector3D)
    bounding_radius: float = 0.5
    visual_weight: float = 1.0


class LensSettings(BaseModel):
    focal_length_mm: float = 35.0
    current_aperture_fstop: float = 2.8
    min_fstop: float = 1.4
    max_fstop: float = 22.0
    sensor_width_mm: float = 36.0
    sensor_height_mm: float = 24.0

    def compute_horizontal_fov_rad(self) -> float:
        return 2.0 * math.atan((self.sensor_width_mm * 0.5) / self.focal_length_mm)

    def compute_horizontal_fov_deg(self) -> float:
        return math.degrees(self.compute_horizontal_fov_rad())


class FocusSettings(BaseModel):
    manual_focus_distance_m: float = 5.0
    auto_focus_enabled: bool = True
    tracking_actor_id: Optional[str] = None
    circle_of_confusion_mm: float = 0.03


class CameraKeyframe(BaseModel):
    time_seconds: float
    transform: Transform3D
    focal_length_mm: float = 35.0
    aperture_fstop: float = 2.8
    focus_distance_m: float = 5.0


class CinematicShot(BaseModel):
    shot_id: str
    shot_type: CinematicShotType
    framing_rule: FramingRule = FramingRule.RULE_OF_THIRDS
    duration_s: float = 3.0
    primary_subject_id: str
    secondary_subject_id: Optional[str] = None
    lens: LensSettings = Field(default_factory=LensSettings)
    focus: FocusSettings = Field(default_factory=FocusSettings)
    keyframes: List[CameraKeyframe] = Field(default_factory=list)


class CinematicSequenceSpec(BaseModel):
    sequence_id: str
    sequence_name: str = ""
    frame_rate: float = 30.0
    total_duration_s: float = 10.0
    shots: List[CinematicShot] = Field(default_factory=list)
    audio_cue_track: Optional[str] = None


class UE5LevelSequenceManifest(BaseModel):
    asset_name: str
    total_frames: int
    frame_rate: float = 30.0
    camera_actor_name: str = "CineCameraActor_Auto"
    tracks: List[Dict[str, Any]] = Field(default_factory=list)
    python_script_helper: str = ""
