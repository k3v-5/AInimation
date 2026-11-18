from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .surface_types import (
    SurfaceTypeTag, ShaderModelType, ColorSpaceType,
    UVUnwrapMethod, BakeChannelType, AttributeSemanticName,
    InvalidationState, SurfaceValidationSeverity
)

@dataclass
class SurfaceRegion:
    surface_region_id: str
    semantic_id: str
    component_id: str
    material_id: str
    surface_type: SurfaceTypeTag = SurfaceTypeTag.WOOD
    importance: float = 1.0
    visual_weight: float = 1.0

@dataclass
class MaterialDefinition:
    material_id: str
    material_class: SurfaceTypeTag = SurfaceTypeTag.WOOD
    shader_model: ShaderModelType = ShaderModelType.DEFAULT_LIT
    base_color: Tuple[float, float, float, float] = (0.5, 0.3, 0.15, 1.0)
    metallic: float = 0.0
    roughness: float = 0.65
    specular: float = 0.5
    ior: float = 1.45
    normal: str = "NOT_REQUIRED"
    height: str = "NOT_REQUIRED"
    ao: str = "PROCEDURAL"
    emissive: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    opacity: float = 1.0
    is_instance: bool = False
    parent_material_id: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ShaderNodeSpec:
    node_id: str
    node_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ShaderGraphSpec:
    graph_id: str
    nodes: List[ShaderNodeSpec] = field(default_factory=list)
    connections: List[Dict[str, str]] = field(default_factory=list) # [{from_node, from_socket, to_node, to_socket}]
    parameters: Dict[str, Any] = field(default_factory=dict)
    output_node_id: str = "PBR_OUTPUT"

@dataclass
class MaterialAssignment:
    surface_region_id: str
    object_id: str
    material_id: str
    face_selection_mode: str = "MATERIAL_SLOT"
    priority: int = 1

@dataclass
class UVLayout:
    uv_channel: int = 0
    unwrap_method: UVUnwrapMethod = UVUnwrapMethod.SMART
    padding: float = 0.02
    resolution: int = 2048
    overlap_count: int = 0
    out_of_bounds_count: int = 0
    unused_space_pct: float = 15.0

@dataclass
class TexelDensityReport:
    current_texel_density: float = 10.24 # px/cm
    target_texel_density: float = 10.24
    density_error_pct: float = 0.0
    is_compliant: bool = True

@dataclass
class VertexAttributeSpec:
    attribute_name: str
    channel: str = "RGB"
    semantic_purpose: AttributeSemanticName = AttributeSemanticName.AO
    value_range: Tuple[float, float] = (0.0, 1.0)

@dataclass
class TextureRequirement:
    texture_id: str
    channel: str
    resolution: int = 2048
    format: str = "PNG"
    color_space: ColorSpaceType = ColorSpaceType.SRGB
    is_required: bool = True

@dataclass
class BakePlan:
    bake_id: str
    maps_to_bake: List[BakeChannelType] = field(default_factory=lambda: [BakeChannelType.NORMAL, BakeChannelType.AO, BakeChannelType.ORM])
    resolution: int = 2048
    format: str = "TGA"
    bit_depth: int = 16
    orm_channels: Dict[str, str] = field(default_factory=lambda: {"R": "AO", "G": "Roughness", "B": "Metallic"})

@dataclass
class UnrealMaterialInterface:
    material_name: str
    parent_shader: str = "/Engine/MasterMaterials/M_PBR_Master"
    parameters: Dict[str, Any] = field(default_factory=dict)
    textures: Dict[str, str] = field(default_factory=dict)
    uv_channels: int = 2
    blend_mode: str = "BLEND_Opaque"
    shading_model: str = "MSM_DefaultLit"
    nanite_compatible: bool = True

@dataclass
class GeneratedSurfaceResult:
    surface_generation_id: str = "SURF_DEFAULT"
    semantic_id: str = "asset.root"
    geometry_generation_id: str = "GEN_DEFAULT"
    surface_version: str = "1.0.0"
    surface_hash: str = ""
    material_definitions: Dict[str, MaterialDefinition] = field(default_factory=dict)
    material_assignments: List[MaterialAssignment] = field(default_factory=list)
    surface_regions: List[SurfaceRegion] = field(default_factory=list)
    uv_layouts: List[UVLayout] = field(default_factory=list)
    texel_density_report: TexelDensityReport = field(default_factory=TexelDensityReport)
    vertex_attributes: List[VertexAttributeSpec] = field(default_factory=list)
    masks: Dict[str, Any] = field(default_factory=dict)
    texture_requirements: List[TextureRequirement] = field(default_factory=list)
    procedural_parameters: Dict[str, Any] = field(default_factory=dict)
    variation_parameters: Dict[str, Any] = field(default_factory=dict)
    baking_plan: Optional[BakePlan] = None
    shader_graphs: Dict[str, ShaderGraphSpec] = field(default_factory=dict)
    unreal_material_interface: Dict[str, UnrealMaterialInterface] = field(default_factory=dict)
    invalidation_state: InvalidationState = InvalidationState.VALID
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    generation_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SurfaceValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
