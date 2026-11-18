import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .parametric_types import AssetType, ParameterType, ParameterCategory, BuildStage, BuildState

@dataclass
class ParameterDefinition:
    parameter_id: str
    name: str
    param_type: ParameterType
    category: ParameterCategory
    default_value: Any
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    unit: str = "m"
    description: str = ""
    is_derived: bool = False
    formula: Optional[str] = None
    editable: bool = True

@dataclass
class ParametricAssetDefinition:
    asset_type: AssetType
    version: str = "v1.0.0"
    parameters: Dict[str, ParameterDefinition] = field(default_factory=dict)
    components: List[str] = field(default_factory=list) # e.g. ["foundation", "walls", "roof", "windows"]
    default_materials: Dict[str, str] = field(default_factory=dict)

@dataclass
class ParameterChange:
    parameter_name: str
    old_value: Any
    new_value: Any
    operation: str = "SET" # SET, INCREASE_PERCENT, DECREASE_PERCENT
    source: str = "AI_INTENT"

@dataclass
class BuildResult:
    asset_id: str
    asset_type: AssetType
    parameters: Dict[str, Any]
    created_components: List[str] = field(default_factory=list)
    modified_components: List[str] = field(default_factory=list)
    dimensions: Dict[str, float] = field(default_factory=dict)
    geometry_stats: Dict[str, int] = field(default_factory=dict) # vertex_count, face_count
    build_fingerprint: str = ""
    stage_reached: BuildStage = BuildStage.COMPLETED
    is_cache_hit: bool = False
    build_time_ms: float = 0.0
    status: BuildState = BuildState.COMPLETED
    errors: List[str] = field(default_factory=list)
