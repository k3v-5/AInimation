from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .presentation_types import (
    ProjectionType, CompositionAlignment, LightType,
    BackgroundType, ViewTransformType, PresentationViewAngle,
    InferenceConfidenceLevel, PresentationValidationSeverity
)

@dataclass
class CameraConfiguration:
    projection: ProjectionType = ProjectionType.PERSPECTIVE
    focal_length: float = 50.0 # mm
    sensor_width: float = 36.0 # mm
    sensor_height: float = 24.0 # mm
    field_of_view: float = 39.6 # degrees
    distance: float = 3.0 # meters
    position: Tuple[float, float, float] = (2.12, -2.12, 1.5)
    rotation: Tuple[float, float, float] = (65.0, 0.0, 45.0) # pitch, roll, yaw
    orthographic_scale: float = 2.0
    target_position: Tuple[float, float, float] = (0.0, 0.0, 0.5)
    confidence: float = 0.95
    inference_level: InferenceConfidenceLevel = InferenceConfidenceLevel.KNOWN

@dataclass
class FramingSpecification:
    alignment: CompositionAlignment = CompositionAlignment.CENTER
    subject_bbox: Tuple[float, float, float, float] = (0.1, 0.1, 0.9, 0.9) # min_x, min_y, max_x, max_y
    subject_center: Tuple[float, float] = (0.5, 0.5)
    horizontal_margin: float = 0.10
    vertical_margin: float = 0.10
    occupancy_ratio: float = 0.78
    safe_frame_padding: float = 0.05

@dataclass
class LightSourceSpec:
    light_id: str
    light_type: LightType = LightType.AREA
    position: Tuple[float, float, float] = (3.0, -2.0, 4.0)
    rotation: Tuple[float, float, float] = (45.0, 0.0, -30.0)
    intensity: float = 500.0 # Watts / Lumens
    color: Tuple[float, float, float] = (1.0, 0.98, 0.95)
    size: float = 1.0
    temperature: float = 5500.0 # Kelvin
    cast_shadow: bool = True
    softness: float = 0.5

@dataclass
class LightingConfiguration:
    key_light: LightSourceSpec = field(default_factory=lambda: LightSourceSpec("LIGHT_KEY", LightType.AREA, (2.5, -2.5, 3.5), (45,0,-45), 650.0, (1.0, 0.98, 0.95), 1.2, 5600.0, True, 0.4))
    fill_light: Optional[LightSourceSpec] = field(default_factory=lambda: LightSourceSpec("LIGHT_FILL", LightType.AREA, (-3.0, -2.0, 2.0), (30,0,45), 250.0, (0.92, 0.95, 1.0), 2.0, 6500.0, False, 0.8))
    rim_light: Optional[LightSourceSpec] = field(default_factory=lambda: LightSourceSpec("LIGHT_RIM", LightType.SPOT, (0.0, 3.0, 3.0), (-45,0,180), 400.0, (1.0, 1.0, 1.0), 0.5, 6000.0, True, 0.2))
    environment_intensity: float = 0.25
    ground_plane_enabled: bool = True
    ground_color: Tuple[float, float, float] = (0.2, 0.2, 0.2)
    ground_roughness: float = 0.85

@dataclass
class EnvironmentSpec:
    world_type: str = "WORLD_COLOR"
    hdri_name: str = "studio_neutral_01"
    intensity: float = 1.0
    rotation: float = 0.0

@dataclass
class BackgroundSpec:
    background_type: BackgroundType = BackgroundType.SOLID
    color: Tuple[float, float, float, float] = (0.12, 0.12, 0.13, 1.0)
    brightness: float = 1.0
    gradient_stop_color: Tuple[float, float, float, float] = (0.05, 0.05, 0.06, 1.0)

@dataclass
class ColorManagementSpec:
    view_transform: ViewTransformType = ViewTransformType.FILMIC
    exposure: float = 0.0
    gamma: float = 1.0
    white_balance_temp: float = 6500.0
    contrast: str = "Medium High Contrast"

@dataclass
class RenderSettingsSpec:
    resolution_x: int = 1920
    resolution_y: int = 1080
    aspect_ratio: float = 1.7778 # 16:9
    samples: int = 128
    enable_shadows: bool = True
    enable_ao: bool = True
    enable_dof: bool = False
    focus_distance: float = 3.0
    f_stop: float = 5.6

@dataclass
class PresentationQualityMetrics:
    framing_score: float = 0.95
    orientation_score: float = 0.95
    projection_score: float = 0.98
    lighting_score: float = 0.92
    shadow_score: float = 0.90
    exposure_score: float = 0.96
    overall_presentation_score: float = 0.94

@dataclass
class PresentationPreset:
    preset_id: str = "PRESET_THREE_QUARTER"
    view_angle: PresentationViewAngle = PresentationViewAngle.THREE_QUARTER
    camera: CameraConfiguration = field(default_factory=CameraConfiguration)
    lighting: LightingConfiguration = field(default_factory=LightingConfiguration)
    background: BackgroundSpec = field(default_factory=BackgroundSpec)
    color_management: ColorManagementSpec = field(default_factory=ColorManagementSpec)
    render_settings: RenderSettingsSpec = field(default_factory=RenderSettingsSpec)

@dataclass
class VisualPresentationContext:
    presentation_id: str = "VPC_DEFAULT"
    semantic_id: str = "asset.root"
    geometry_generation_id: str = "GEN_DEFAULT"
    surface_generation_id: str = "SURF_DEFAULT"
    reference_id: str = "REF_DEFAULT"
    view_angle: PresentationViewAngle = PresentationViewAngle.THREE_QUARTER
    camera: CameraConfiguration = field(default_factory=CameraConfiguration)
    framing: FramingSpecification = field(default_factory=FramingSpecification)
    lighting: LightingConfiguration = field(default_factory=LightingConfiguration)
    environment: EnvironmentSpec = field(default_factory=EnvironmentSpec)
    background: BackgroundSpec = field(default_factory=BackgroundSpec)
    color_management: ColorManagementSpec = field(default_factory=ColorManagementSpec)
    render_settings: RenderSettingsSpec = field(default_factory=RenderSettingsSpec)
    quality_metrics: PresentationQualityMetrics = field(default_factory=PresentationQualityMetrics)
    subject_bounds: Dict[str, Any] = field(default_factory=dict)
    presentation_hash: str = ""
    warnings: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    generation_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PresentationValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
