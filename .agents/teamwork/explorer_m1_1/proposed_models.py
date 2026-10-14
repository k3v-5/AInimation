"""
Domain Models and Data Contracts for IANIMATION Backend & FastMCP Server.

This module defines the central Pydantic v2 domain schemas used across all system
boundaries: FastMCP tools, AI provider adapters, Unreal Engine 5 Remote Control bridge,
and the Tauri React frontend.

Adheres strictly to the Zero-Any Policy (100% strict typing) and SOLID design principles.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Dict, List, Literal, Optional, Tuple, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# -----------------------------------------------------------------------------
# Base Configuration
# -----------------------------------------------------------------------------

class StrictBaseModel(BaseModel):
    """
    Base model configuration enforcing strict typing, assignment validation,
    and forbidding unmapped extra attributes to prevent silent schema drift.
    """
    model_config = ConfigDict(
        strict=False,
        validate_assignment=True,
        populate_by_name=True,
        extra="forbid",
        arbitrary_types_allowed=False,
    )


# -----------------------------------------------------------------------------
# 1. Primitives & Math Data Types
# -----------------------------------------------------------------------------

class Vector3D(StrictBaseModel):
    """
    3D Cartesian Vector representation (X, Y, Z).
    Can represent translation coordinates or spatial offsets.
    """
    x: float = Field(default=0.0, description="X coordinate (in centimeters for UE5, meters for glTF)")
    y: float = Field(default=0.0, description="Y coordinate (in centimeters for UE5, meters for glTF)")
    z: float = Field(default=0.0, description="Z coordinate (in centimeters for UE5, meters for glTF)")

    def to_tuple(self) -> Tuple[float, float, float]:
        """Convert vector coordinates to a 3-tuple (X, Y, Z)."""
        return (self.x, self.y, self.z)

    @classmethod
    def from_tuple(cls, val: Tuple[float, float, float]) -> Vector3D:
        """Create Vector3D from a 3-tuple."""
        return cls(x=val[0], y=val[1], z=val[2])

    def to_ue5_dict(self) -> Dict[str, float]:
        """Format as Unreal Engine Remote Control vector parameter."""
        return {"X": self.x, "Y": self.y, "Z": self.z}


class Rotator3D(StrictBaseModel):
    """
    3D Euler Rotation representation in degrees (Pitch, Yaw, Roll).
    Adheres to Unreal Engine rotation conventions.
    """
    pitch: float = Field(default=0.0, description="Rotation around Y axis in degrees")
    yaw: float = Field(default=0.0, description="Rotation around Z axis in degrees")
    roll: float = Field(default=0.0, description="Rotation around X axis in degrees")

    def to_tuple(self) -> Tuple[float, float, float]:
        """Convert rotation angles to a 3-tuple (Pitch, Yaw, Roll)."""
        return (self.pitch, self.yaw, self.roll)

    @classmethod
    def from_tuple(cls, val: Tuple[float, float, float]) -> Rotator3D:
        """Create Rotator3D from a 3-tuple."""
        return cls(pitch=val[0], yaw=val[1], roll=val[2])

    def to_ue5_dict(self) -> Dict[str, float]:
        """Format as Unreal Engine Remote Control rotator parameter."""
        return {"Pitch": self.pitch, "Yaw": self.yaw, "Roll": self.roll}


class ColorRGB(StrictBaseModel):
    """Normalized linear RGB color representation (values typically 0.0 to 1.0)."""
    r: float = Field(default=1.0, ge=0.0, le=1.0, description="Red color component (0.0 to 1.0)")
    g: float = Field(default=1.0, ge=0.0, le=1.0, description="Green color component (0.0 to 1.0)")
    b: float = Field(default=1.0, ge=0.0, le=1.0, description="Blue color component (0.0 to 1.0)")

    def to_tuple(self) -> Tuple[float, float, float]:
        """Convert to (R, G, B) tuple."""
        return (self.r, self.g, self.b)

    def to_ue5_dict(self) -> Dict[str, float]:
        """Format as Unreal Engine Remote Control LinearColor parameter."""
        return {"R": self.r, "G": self.g, "B": self.b, "A": 1.0}


# -----------------------------------------------------------------------------
# 2. Audio Domain Models
# -----------------------------------------------------------------------------

class AudioStemType(StrEnum):
    """Standard audio stem channel classification."""
    VOCALS = "vocals"
    DRUMS = "drums"
    BASS = "bass"
    OTHER = "other"
    GUITAR = "guitar"
    PIANO = "piano"


class AudioAnalysisRequest(StrictBaseModel):
    """
    Input parameters for audio tempo, beat tracking, and stem separation.
    """
    audio_path: str = Field(
        ...,
        min_length=1,
        description="Absolute or relative path to the input audio file (.wav, .mp3, .ogg, .flac)",
    )
    separate_stems: bool = Field(
        default=True,
        description="Whether to run Demucs/filterbank stem separation (vocals, drums, bass, other)",
    )
    sample_rate: int = Field(
        default=44100,
        ge=8000,
        le=192000,
        description="Target sampling rate in Hz for audio analysis",
    )
    bpm_hint: Optional[float] = Field(
        default=None,
        ge=30.0,
        le=300.0,
        description="Optional prior estimate to guide and constrain tempo detection",
    )


class StemSeparationResult(StrictBaseModel):
    """
    Output payload of the audio stem separation step.
    """
    stems: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapping from stem name ('vocals', 'drums', 'bass', 'other') to output audio file path",
    )
    model_used: str = Field(
        default="demucs",
        description="Name of the stem separation model or fallback filterbank algorithm used",
    )
    sample_rate: int = Field(
        default=44100,
        ge=8000,
        description="Sampling rate in Hz of the separated stem files",
    )
    duration_seconds: float = Field(
        ...,
        ge=0.0,
        description="Total duration of the separated stems in seconds",
    )


class AudioAnalysisResult(StrictBaseModel):
    """
    Comprehensive audio feature extraction result conforming to the FastMCP tool contract.
    """
    bpm: float = Field(
        ...,
        ge=0.0,
        description="Detected music tempo in Beats Per Minute",
    )
    duration_seconds: float = Field(
        ...,
        ge=0.0,
        description="Total duration of the analyzed audio track in seconds",
    )
    beat_timestamps: List[float] = Field(
        default_factory=list,
        description="Chronological list of beat onset timestamps in seconds",
    )
    onset_envelope: List[float] = Field(
        default_factory=list,
        description="Normalized audio energy / onset strength envelope over time",
    )
    stems: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional dictionary mapping stem categories to separated file paths",
    )
    time_signature: str = Field(
        default="4/4",
        description="Estimated musical meter or time signature (e.g. '4/4', '3/4')",
    )
    danceability: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Normalized danceability score (0.0 = static/ambient, 1.0 = highly rhythmic)",
    )

    def get_stem_path(self, stem_type: Union[AudioStemType, str]) -> Optional[str]:
        """Retrieve path for a specific stem if present."""
        if not self.stems:
            return None
        key = stem_type.value if isinstance(stem_type, AudioStemType) else str(stem_type)
        return self.stems.get(key)


# -----------------------------------------------------------------------------
# 3. 3D Mesh & Texture Models
# -----------------------------------------------------------------------------

class MeshFormat(StrEnum):
    """Supported 3D asset container formats."""
    GLB = "glb"
    GLTF = "gltf"
    FBX = "fbx"
    OBJ = "obj"
    USD = "usd"


class PBRTextureSet(StrictBaseModel):
    """
    Set of Physically Based Rendering (PBR) texture map file paths.
    Standardized according to the metallic-roughness workflow.
    """
    albedo_path: Optional[str] = Field(default=None, description="Path to base color / diffuse texture map")
    normal_path: Optional[str] = Field(default=None, description="Path to tangent-space normal map")
    roughness_path: Optional[str] = Field(default=None, description="Path to scalar roughness texture map")
    metallic_path: Optional[str] = Field(default=None, description="Path to scalar metallic texture map")
    ambient_occlusion_path: Optional[str] = Field(default=None, description="Path to ambient occlusion texture map")
    emissive_path: Optional[str] = Field(default=None, description="Path to emissive color texture map")
    height_path: Optional[str] = Field(default=None, description="Path to displacement / height texture map")
    resolution: int = Field(default=1024, ge=128, le=8192, description="Texture resolution dimension (width/height in pixels)")

    def has_textures(self) -> bool:
        """Check whether at least one texture map path is populated."""
        return any([
            self.albedo_path,
            self.normal_path,
            self.roughness_path,
            self.metallic_path,
            self.ambient_occlusion_path,
            self.emissive_path,
            self.height_path,
        ])


class ImageTo3DRequest(StrictBaseModel):
    """
    Input payload for generating a 3D textured mesh from a 2D reference image.
    """
    image_path: str = Field(
        ...,
        min_length=1,
        description="Path to input 2D image file (.png, .jpg, .jpeg, .webp)",
    )
    provider: str = Field(
        default="auto",
        description="Inference provider identifier ('auto', 'fal', 'tripo', 'replicate', 'procedural_stub')",
    )
    texture_resolution: int = Field(
        default=1024,
        ge=256,
        le=4096,
        description="Target resolution for generated PBR texture maps",
    )
    target_format: MeshFormat = Field(
        default=MeshFormat.GLB,
        description="Desired 3D file format container",
    )
    generate_textures: bool = Field(
        default=True,
        description="Whether to generate and bake full PBR textures or output geometric proxy",
    )
    seed: Optional[int] = Field(
        default=None,
        description="Optional random seed for deterministic generation across runs",
    )


class ImageTo3DResult(StrictBaseModel):
    """
    Output payload of 3D asset generation conforming to FastMCP tool contract.
    """
    mesh_path: str = Field(
        ...,
        min_length=1,
        description="Absolute file path to the generated 3D mesh (.glb/.fbx)",
    )
    textures: PBRTextureSet = Field(
        default_factory=PBRTextureSet,
        description="Associated PBR texture maps generated for the mesh",
    )
    vertex_count: int = Field(
        ...,
        ge=0,
        description="Total vertex count of the generated 3D mesh",
    )
    polygon_count: int = Field(
        default=0,
        ge=0,
        description="Total triangle or polygon count in the mesh",
    )
    cached: bool = Field(
        default=False,
        description="Flag indicating whether this result was retrieved from CAS cache",
    )
    mesh_format: MeshFormat = Field(
        default=MeshFormat.GLB,
        description="Format of the output 3D mesh file",
    )
    provider_used: str = Field(
        default="procedural_stub",
        description="Identifier of the provider or algorithm that produced the mesh",
    )
    generation_time_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Elapsed time for generation in seconds",
    )


# -----------------------------------------------------------------------------
# 4. Rigging Domain Models
# -----------------------------------------------------------------------------

class BoneDescriptor(StrictBaseModel):
    """
    Anatomical bone definition within a skeletal armature.
    """
    name: str = Field(
        ...,
        min_length=1,
        description="Unique bone identifier matching skeleton hierarchy standard (e.g. 'pelvis', 'spine_01')",
    )
    parent_name: Optional[str] = Field(
        default=None,
        description="Name of the parent bone in the hierarchy (None for root joint)",
    )
    head_position: Tuple[float, float, float] = Field(
        ...,
        description="3D position coordinates (X, Y, Z) of the bone head / joint origin",
    )
    tail_position: Tuple[float, float, float] = Field(
        ...,
        description="3D position coordinates (X, Y, Z) of the bone tail / terminal tip",
    )
    roll: float = Field(
        default=0.0,
        description="Bone axial roll rotation angle in degrees",
    )


class SkeletalHierarchy(StrictBaseModel):
    """
    Complete skeletal hierarchy representing an anatomical standard (e.g. UE5 Mannequin).
    """
    skeleton_type: str = Field(
        default="ue5_mannequin",
        description="Skeleton archetype template standard ('ue5_mannequin', 'mixamo')",
    )
    root_bone: str = Field(
        default="root",
        description="Name of the root bone at the base of the hierarchy",
    )
    bones: List[BoneDescriptor] = Field(
        default_factory=list,
        description="List of all bones comprising the skeletal armature",
    )
    is_biped: bool = Field(
        default=True,
        description="Whether the skeleton conforms to a humanoid biped topology",
    )


class AutoRigRequest(StrictBaseModel):
    """
    Input payload for automated character rigging and skin weight computation.
    """
    mesh_path: str = Field(
        ...,
        min_length=1,
        description="Path to the static 3D mesh file (.glb or .fbx) to rig",
    )
    skeleton_type: str = Field(
        default="ue5_mannequin",
        description="Target skeleton standard archetype ('ue5_mannequin', 'mixamo')",
    )
    max_influences: int = Field(
        default=4,
        ge=1,
        le=8,
        description="Maximum number of bone weights assigned per vertex",
    )
    symmetry: bool = Field(
        default=True,
        description="Whether to enforce bilateral anatomical symmetry in bone positions and weights",
    )


class AutoRigResult(StrictBaseModel):
    """
    Output payload of character auto-rigging conforming to FastMCP tool contract.
    """
    rigged_mesh_path: str = Field(
        ...,
        min_length=1,
        description="File path to the output rigged skeletal mesh (.glb or .fbx)",
    )
    bone_count: int = Field(
        ...,
        ge=1,
        description="Total number of bones bound to the character armature",
    )
    hierarchy: List[str] = Field(
        default_factory=list,
        description="Topologically ordered list of bone names from root to extremities",
    )
    skeleton_type: str = Field(
        default="ue5_mannequin",
        description="Skeleton standard template used for the armature",
    )
    success: bool = Field(
        default=True,
        description="Flag indicating whether skin weight binding completed successfully",
    )


# -----------------------------------------------------------------------------
# 5. Mocap & Motion Tracking Models
# -----------------------------------------------------------------------------

class Pose3DKeyframe(StrictBaseModel):
    """
    Single frame 3D skeletal pose keyframe extracted from video tracking.
    """
    timestamp: float = Field(
        ...,
        ge=0.0,
        description="Keyframe timestamp in seconds from animation start",
    )
    frame_index: int = Field(
        ...,
        ge=0,
        description="Zero-based video or animation frame number",
    )
    keypoints_3d: Dict[str, Tuple[float, float, float]] = Field(
        ...,
        description="Dictionary mapping joint names to 3D Cartesian coordinates (X, Y, Z)",
    )
    confidence_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Mapping of joint names to tracking confidence scores (0.0 to 1.0)",
    )


class MocapExtractionRequest(StrictBaseModel):
    """
    Input payload for extracting 3D motion capture animation from reference video.
    """
    video_path: str = Field(
        ...,
        min_length=1,
        description="Path to reference dance / motion video file (.mp4, .mov, .webm)",
    )
    target_fps: int = Field(
        default=30,
        ge=1,
        le=120,
        description="Target animation sampling rate in frames per second",
    )
    extract_hands: bool = Field(
        default=False,
        description="Whether to extract detailed finger articulation tracking",
    )
    extract_face: bool = Field(
        default=False,
        description="Whether to extract facial expressions and head rotation blendshapes",
    )
    remove_background: bool = Field(
        default=True,
        description="Whether to execute alpha rotoscopy/background removal before pose tracking",
    )
    smoothing_window: int = Field(
        default=5,
        ge=1,
        le=30,
        description="Temporal filter window size in frames for jitter suppression",
    )


class MocapResult(StrictBaseModel):
    """
    Output payload of 3D motion capture extraction conforming to FastMCP tool contract.
    """
    animation_path: str = Field(
        ...,
        min_length=1,
        description="Path to the exported skeletal animation track (.glb or .fbx)",
    )
    frame_count: int = Field(
        ...,
        ge=0,
        description="Total number of animation frames generated",
    )
    fps: int = Field(
        default=30,
        ge=1,
        le=120,
        description="Animation playback frame rate",
    )
    duration: float = Field(
        ...,
        ge=0.0,
        description="Total duration of the extracted motion in seconds",
    )
    keyframes: Optional[List[Pose3DKeyframe]] = Field(
        default=None,
        description="Optional raw 3D pose keyframe data list",
    )
    tracked_joints_count: int = Field(
        default=33,
        ge=1,
        description="Count of anatomical body joints tracked across frames",
    )


# -----------------------------------------------------------------------------
# 6. Scene & Cinematic Camera Models
# -----------------------------------------------------------------------------

class CameraKeyframe(StrictBaseModel):
    """
    Choreographed CineCameraActor keyframe synchronized to audio or sequence timeline.
    """
    timestamp: float = Field(
        ...,
        ge=0.0,
        description="Timeline timestamp in seconds",
    )
    position: Tuple[float, float, float] = Field(
        ...,
        description="Camera position (X, Y, Z) in Unreal Engine world space (centimeters)",
    )
    rotation: Tuple[float, float, float] = Field(
        default=(0.0, 0.0, 0.0),
        description="Camera rotation Euler angles (Pitch, Yaw, Roll) in degrees",
    )
    focal_length: float = Field(
        default=35.0,
        ge=10.0,
        le=300.0,
        description="Camera lens focal length in millimeters (e.g. 24, 35, 50, 85)",
    )
    aperture: float = Field(
        default=2.8,
        ge=0.7,
        le=22.0,
        description="Lens aperture f-number for depth-of-field control",
    )
    focus_distance: float = Field(
        default=1000.0,
        ge=1.0,
        description="Manual focus plane distance from camera in centimeters",
    )

    def to_ue5_payload(self) -> Dict[str, Union[Dict[str, float], float]]:
        """Format as Unreal Engine Remote Control transform payload."""
        return {
            "Location": {"X": self.position[0], "Y": self.position[1], "Z": self.position[2]},
            "Rotation": {"Pitch": self.rotation[0], "Yaw": self.rotation[1], "Roll": self.rotation[2]},
            "CurrentFocalLength": self.focal_length,
            "CurrentAperture": self.aperture,
            "FocusDistance": self.focus_distance,
        }


class LumenLightConfig(StrictBaseModel):
    """
    Unreal Engine 5 Lumen dynamic lighting configuration and rig settings.
    """
    preset_name: str = Field(
        default="cinematic_three_point",
        description="Identifier of lighting preset rig",
    )
    directional_light_intensity: float = Field(
        default=10.0,
        ge=0.0,
        description="Directional sunlight intensity in lux",
    )
    directional_light_color: Tuple[float, float, float] = Field(
        default=(1.0, 0.95, 0.9),
        description="Directional sunlight RGB tint (0.0 to 1.0)",
    )
    sky_light_intensity: float = Field(
        default=1.0,
        ge=0.0,
        description="SkyLight ambient capture intensity",
    )
    sky_light_color: Tuple[float, float, float] = Field(
        default=(0.8, 0.88, 1.0),
        description="SkyLight ambient sky tint (0.0 to 1.0)",
    )
    key_light_intensity: float = Field(
        default=5000.0,
        ge=0.0,
        description="Character key light intensity in lumens",
    )
    fill_light_intensity: float = Field(
        default=2500.0,
        ge=0.0,
        description="Character fill light intensity in lumens",
    )
    rim_light_intensity: float = Field(
        default=7500.0,
        ge=0.0,
        description="Character rim / backlight intensity in lumens",
    )
    use_lumen_gi: bool = Field(
        default=True,
        description="Enable Lumen Global Illumination in post-process settings",
    )
    use_lumen_reflections: bool = Field(
        default=True,
        description="Enable Lumen Raytraced Reflections in post-process settings",
    )


class SceneConfig(StrictBaseModel):
    """
    Specification for programmatically building an Unreal Engine 5 cinematic scene.
    """
    mesh_path: str = Field(
        ...,
        min_length=1,
        description="File path to the character or object 3D mesh (.glb/.fbx)",
    )
    animation_path: str = Field(
        ...,
        min_length=1,
        description="File path to the skeletal animation asset (.glb/.fbx)",
    )
    lighting_preset: str = Field(
        default="cinematic_three_point",
        description="Preset lighting rig to instantiate",
    )
    lighting_config: Optional[LumenLightConfig] = Field(
        default=None,
        description="Optional custom Lumen lighting parameter overrides",
    )
    camera_choreography: List[CameraKeyframe] = Field(
        default_factory=list,
        description="Array of choreographed camera keyframes synchronized with timeline",
    )
    audio_track_path: Optional[str] = Field(
        default=None,
        description="Optional path to master audio track to embed in Level Sequence",
    )
    level_name: str = Field(
        default="Stage_Main",
        description="Target Unreal Engine map or level sequence package path",
    )


class SceneBuildResult(StrictBaseModel):
    """
    Output payload of UE5 scene construction conforming to FastMCP tool contract.
    """
    success: bool = Field(
        ...,
        description="Flag indicating whether scene construction completed without error",
    )
    actor_ids: List[str] = Field(
        default_factory=list,
        description="List of spawned Unreal Engine actor IDs or object paths",
    )
    scene_path: str = Field(
        ...,
        min_length=1,
        description="Unreal Engine package path of the instantiated Level Sequence",
    )
    camera_actor_id: Optional[str] = Field(
        default=None,
        description="Actor path of the instantiated CineCameraActor",
    )
    character_actor_id: Optional[str] = Field(
        default=None,
        description="Actor path of the instantiated SkeletalMeshActor",
    )
    message: str = Field(
        default="Scene constructed successfully",
        description="Informational status message or error description",
    )


# -----------------------------------------------------------------------------
# 7. Render Domain Models
# -----------------------------------------------------------------------------

class MovieRenderQueueJobConfig(StrictBaseModel):
    """
    Configuration payload for executing high-fidelity Movie Render Queue (MRQ) exports.
    """
    scene_path: str = Field(
        ...,
        min_length=1,
        description="Path to the Unreal Engine Level Sequence to render",
    )
    output_path: str = Field(
        ...,
        min_length=1,
        description="Target destination file path for the rendered video (.mp4)",
    )
    fps: int = Field(
        default=60,
        ge=1,
        le=240,
        description="Video output frame rate",
    )
    resolution: str = Field(
        default="1920x1080",
        pattern=r"^\d+x\d+$",
        description="Render resolution string in format 'WIDTHxHEIGHT' (e.g. '1920x1080', '3840x2160')",
    )
    codec: str = Field(
        default="h264",
        description="Output video codec: 'h264', 'apple_prores', 'png_sequence'",
    )
    anti_aliasing_samples: int = Field(
        default=16,
        ge=1,
        le=64,
        description="Spatial and temporal anti-aliasing sample count",
    )
    warmup_frames: int = Field(
        default=30,
        ge=0,
        description="Number of engine warmup frames to simulate prior to frame capture",
    )
    render_passes: List[str] = Field(
        default_factory=lambda: ["FinalImage"],
        description="Render passes to export (e.g. 'FinalImage', 'Depth', 'WorldNormal')",
    )

    def get_resolution_dimensions(self) -> Tuple[int, int]:
        """Parse resolution string into (width, height) integers."""
        parts = self.resolution.split("x")
        return (int(parts[0]), int(parts[1]))


class RenderResult(StrictBaseModel):
    """
    Output payload of cinematic video rendering conforming to FastMCP tool contract.
    """
    video_path: str = Field(
        ...,
        min_length=1,
        description="Absolute path to the final rendered video file (.mp4)",
    )
    frame_count: int = Field(
        ...,
        ge=0,
        description="Total number of frames rendered",
    )
    elapsed_seconds: float = Field(
        ...,
        ge=0.0,
        description="Total render execution time in seconds",
    )
    fps: int = Field(
        default=60,
        ge=1,
        description="Frame rate of the rendered video",
    )
    resolution: str = Field(
        default="1920x1080",
        description="Resolution of the rendered video",
    )
    file_size_bytes: int = Field(
        default=0,
        ge=0,
        description="Final video file size in bytes",
    )
    success: bool = Field(
        default=True,
        description="Flag indicating whether video rendering completed successfully",
    )


# -----------------------------------------------------------------------------
# 8. Copilot & Production Plan Models (Human-in-the-Loop)
# -----------------------------------------------------------------------------

class PlanRiskLevel(StrEnum):
    """Risk classification for production steps to trigger confirmation gates."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PlanStatus(StrEnum):
    """Lifecycle status states for production plans and steps."""
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


# Strictly typed JSON primitive value definition enforcing Zero-Any policy
PlanParamScalar = Union[str, int, float, bool]
PlanParamValue = Union[PlanParamScalar, List[str], Dict[str, str]]


class PlanStep(StrictBaseModel):
    """
    Individual atomic action in an AI-assisted production plan.
    """
    step_id: str = Field(
        ...,
        min_length=1,
        description="Unique identifier for the plan step (e.g. 'step_audio_01')",
    )
    index: int = Field(
        ...,
        ge=0,
        description="Ordinal execution index in the production sequence",
    )
    tool_name: str = Field(
        ...,
        min_length=1,
        description="Target FastMCP atomic tool name (e.g. 'analyze_audio', 'image_to_3d')",
    )
    description: str = Field(
        ...,
        description="Human-readable explanation of what this step will produce",
    )
    parameters: Dict[str, PlanParamValue] = Field(
        default_factory=dict,
        description="Strictly typed dictionary of parameters to supply to the tool",
    )
    risk_level: PlanRiskLevel = Field(
        default=PlanRiskLevel.LOW,
        description="Operational risk level of this step",
    )
    requires_confirmation: bool = Field(
        default=False,
        description="Whether this step requires explicit human approval before execution",
    )
    status: PlanStatus = Field(
        default=PlanStatus.PROPOSED,
        description="Current lifecycle execution status of this step",
    )
    output_preview: Optional[str] = Field(
        default=None,
        description="Path or URL to intermediate asset produced by this step for UI preview",
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Failure reason or error log if the step failed",
    )


class ProductionPlan(StrictBaseModel):
    """
    Multi-stage end-to-end production plan generated by the Copilot agent.
    """
    plan_id: str = Field(
        ...,
        min_length=1,
        description="Unique identifier for this production plan",
    )
    title: str = Field(
        ...,
        description="Human-readable title summarizing the production goal",
    )
    description: str = Field(
        ...,
        description="Detailed description of the steps, assets, and styling to be produced",
    )
    steps: List[PlanStep] = Field(
        default_factory=list,
        description="Ordered sequence of atomic production steps",
    )
    status: PlanStatus = Field(
        default=PlanStatus.PROPOSED,
        description="Overall lifecycle execution status of the plan",
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 creation timestamp",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp of last state transition",
    )
    total_estimated_duration_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Copilot estimate of total processing time in seconds",
    )

    def get_step(self, step_id: str) -> Optional[PlanStep]:
        """Find a step by its unique step_id."""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None

    def mark_step_status(
        self,
        step_id: str,
        status: PlanStatus,
        output_preview: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        """Update the status and output of a specific step."""
        step = self.get_step(step_id)
        if not step:
            return False
        step.status = status
        if output_preview is not None:
            step.output_preview = output_preview
        if error_message is not None:
            step.error_message = error_message
        self.updated_at = datetime.now(timezone.utc).isoformat()
        return True

    def is_all_completed(self) -> bool:
        """Check whether every step in the plan has completed successfully."""
        return len(self.steps) > 0 and all(step.status == PlanStatus.COMPLETED for step in self.steps)


class PlanConfirmationRequest(StrictBaseModel):
    """
    Request payload asking the user or copilot client to confirm execution of a plan or step.
    """
    plan_id: str = Field(
        ...,
        min_length=1,
        description="Unique identifier of the target production plan",
    )
    step_id: Optional[str] = Field(
        default=None,
        description="Specific step ID being confirmed (if None, applies to entire plan)",
    )
    auto_proceed: bool = Field(
        default=False,
        description="Flag allowing non-interactive automatic execution in automated/batch mode",
    )
    user_prompt: Optional[str] = Field(
        default=None,
        description="Original user instruction that prompted this plan proposal",
    )


class PlanConfirmationResponse(StrictBaseModel):
    """
    User or client response granting or denying permission to execute a plan or step.
    """
    plan_id: str = Field(
        ...,
        min_length=1,
        description="Identifier of the production plan",
    )
    step_id: Optional[str] = Field(
        default=None,
        description="Step ID confirmed or rejected (None if whole plan)",
    )
    approved: bool = Field(
        ...,
        description="Whether permission to execute is granted (True) or denied (False)",
    )
    feedback: Optional[str] = Field(
        default=None,
        description="Optional feedback, reason for rejection, or adjustment instructions",
    )
    modified_parameters: Optional[Dict[str, PlanParamValue]] = Field(
        default=None,
        description="Optional parameter modifications requested by the user",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp of user response",
    )


# -----------------------------------------------------------------------------
# 9. Telemetry & Progress Event Models (Cross-Boundary SSE/WebSocket)
# -----------------------------------------------------------------------------

class AssetType(StrEnum):
    """Classification of generated intermediate or final pipeline assets."""
    AUDIO_STEMS = "audio_stems"
    MESH_3D = "mesh_3d"
    RIGGED_MESH = "rigged_mesh"
    MOCAP = "mocap"
    RENDER_VIDEO = "render_video"


class LogLevel(StrEnum):
    """Log level severity classification."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ProgressEvent(StrictBaseModel):
    """
    Event emitted to report percentage progress and status of ongoing background tasks.
    Conforms to frontend TelemetryEventSchema.
    """
    type: Literal["progress"] = "progress"
    stage: str = Field(..., min_length=1, description="Current execution stage name")
    percentage: float = Field(..., ge=0.0, le=100.0, description="Completion percentage (0.0 to 100.0)")
    message: str = Field(..., description="Human-readable progress description")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="ISO 8601 timestamp")


class PlanProposalEvent(StrictBaseModel):
    """
    Event emitted when a new production plan has been formulated by Copilot.
    Conforms to frontend TelemetryEventSchema.
    """
    type: Literal["plan_proposal"] = "plan_proposal"
    plan_id: str = Field(..., min_length=1, description="Unique production plan identifier")
    steps: List[PlanStep] = Field(default_factory=list, description="List of proposed production steps")
    status: PlanStatus = Field(default=PlanStatus.PROPOSED, description="Current status of the proposed plan")


class AssetReadyEvent(StrictBaseModel):
    """
    Event emitted when a pipeline asset is finalized and ready for consumption.
    Conforms to frontend TelemetryEventSchema.
    """
    type: Literal["asset_ready"] = "asset_ready"
    asset_id: str = Field(..., min_length=1, description="Unique asset identifier")
    asset_type: AssetType = Field(..., description="Asset type classification")
    file_path: str = Field(..., min_length=1, description="Absolute file path to the completed asset")


class LogEvent(StrictBaseModel):
    """
    Event emitted for structured real-time logging streamed to the UI console.
    Conforms to frontend TelemetryEventSchema.
    """
    type: Literal["log"] = "log"
    level: LogLevel = Field(default=LogLevel.INFO, description="Log severity level")
    message: str = Field(..., description="Log message text")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="ISO 8601 timestamp")


TelemetryEvent = Union[ProgressEvent, PlanProposalEvent, AssetReadyEvent, LogEvent]
