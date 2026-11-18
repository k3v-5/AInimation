from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .reference_types import (
    ReferenceModality, CameraPerspective, ExtractedMaterialType,
    StyleArchetype, ConfidenceTier, VisualFeatureImportance
)

@dataclass
class ImageReferenceInput:
    reference_id: str
    file_path_or_uri: str
    modality: ReferenceModality = ReferenceModality.CONCEPT_ART
    role: str = "PRIMARY" # PRIMARY, MATERIAL, SILHOUETTE, DETAIL
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SilhouetteExtraction:
    aspect_ratio: float = 1.42
    bounding_box: Tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.42) # x, y, w, h
    contour_complexity: float = 0.35 # 0.0 = circle/box, 1.0 = highly jagged
    symmetry_axis: str = "VERTICAL_Z"
    silhouette_confidence: float = 0.94

@dataclass
class ProportionEstimate:
    height_to_width_ratio: float = 1.42
    component_ratios: Dict[str, float] = field(default_factory=lambda: {"body": 0.80, "top_ring": 0.10, "bottom_ring": 0.10})
    estimated_curvature: float = 0.25 # Grosor / abombamiento del perfil
    tolerance: float = 0.05

@dataclass
class DecomposedPart:
    part_id: str
    semantic_type: str
    bounding_box: Tuple[float, float, float, float]
    relative_position: Tuple[float, float, float] # x, y, z normalizado
    is_primary: bool = True
    confidence: float = 0.95

@dataclass
class MaterialPalette:
    base_material: ExtractedMaterialType = ExtractedMaterialType.WOOD
    secondary_materials: List[ExtractedMaterialType] = field(default_factory=lambda: [ExtractedMaterialType.IRON])
    surface_roughness: float = 0.70
    metallic_ratio: float = 0.30

@dataclass
class ColorPalette:
    dominant_colors: List[str] = field(default_factory=lambda: ["#4A2E18", "#2C1D11"]) # Tonos madera oscura
    accent_colors: List[str] = field(default_factory=lambda: ["#3A3A3C"]) # Tono hierro
    brightness_profile: str = "MEDIUM_DARK"
    saturation_profile: str = "MUTED"

@dataclass
class CameraEstimation:
    estimated_view: CameraPerspective = CameraPerspective.ISOMETRIC_THREE_QUARTERS
    elevation_deg: float = 25.0
    azimuth_deg: float = 45.0
    field_of_view: float = 50.0

@dataclass
class VisualRequirementItem:
    requirement_id: str
    category: str # SILHOUETTE, PROPORTION, COMPONENT, MATERIAL, COLOR
    description: str
    target_value: Any
    importance: VisualFeatureImportance = VisualFeatureImportance.HIGH
    confidence: float = 0.95

@dataclass
class DecomposedReferenceReport:
    report_id: str
    reference_ids: List[str]
    asset_class_hint: str = "PROP.BARREL"
    style_archetype: StyleArchetype = StyleArchetype.STYLIZED
    silhouette: SilhouetteExtraction = field(default_factory=SilhouetteExtraction)
    proportions: ProportionEstimate = field(default_factory=ProportionEstimate)
    parts: List[DecomposedPart] = field(default_factory=list)
    materials: MaterialPalette = field(default_factory=MaterialPalette)
    colors: ColorPalette = field(default_factory=ColorPalette)
    camera: CameraEstimation = field(default_factory=CameraEstimation)
    visual_requirements: List[VisualRequirementItem] = field(default_factory=list)
    overall_confidence: float = 0.92
    warnings: List[str] = field(default_factory=list)
