from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .readiness_types import (
    ReadinessStatus, EngineTarget, ValidationSeverity,
    PivotMode, CoordinateSystem, NaniteReadinessState
)

@dataclass
class EngineProfile:
    profile_id: str = "UNREAL_ENGINE_5_DEFAULT"
    version: str = "1.0.0"
    target_engine: EngineTarget = EngineTarget.UNREAL_ENGINE_5
    coordinate_system: CoordinateSystem = CoordinateSystem.Z_UP_LEFT_HANDED
    unit_scale_cm: float = 1.0 # 1 Blender unit = 100 cm in Unreal
    require_ucx_collision: bool = True
    require_lightmap_uv: bool = True
    max_triangle_count: int = 50000
    max_material_slots: int = 4
    nanite_state: NaniteReadinessState = NaniteReadinessState.NANITE_READY

@dataclass
class ExportProfile:
    profile_id: str = "EXPORT_UNREAL_FBX_V2020"
    format: str = "FBX"
    unit_scale: float = 100.0
    forward_axis: str = "-Z"
    up_axis: str = "Y"
    embed_textures: bool = False

@dataclass
class EngineValidationResult:
    validator_id: str
    passed: bool
    severity: ValidationSeverity
    message: str
    target: str = "root"
    remediation: Optional[str] = None

@dataclass
class EngineReadinessScore:
    geometry: float = 100.0
    materials: float = 100.0
    textures: float = 100.0
    uv: float = 100.0
    transforms: float = 100.0
    collision: float = 100.0
    lod: float = 100.0
    total: float = 100.0

@dataclass
class EnginePreparationOperation:
    operation_id: str
    operation_type: str
    target: str
    result: str = "SUCCESS"
    before_hash: str = ""
    after_hash: str = ""

@dataclass
class EngineReadinessManifest:
    manifest_id: str
    asset_id: str
    semantic_id: str
    readiness_status: ReadinessStatus
    readiness_score: EngineReadinessScore
    validation_results: List[EngineValidationResult] = field(default_factory=list)
    preparation_operations: List[EnginePreparationOperation] = field(default_factory=list)
    engine_profile_id: str = "UNREAL_ENGINE_5_DEFAULT"
    export_profile_id: str = "EXPORT_UNREAL_FBX_V2020"

@dataclass
class GameEngineReadyAsset:
    asset_id: str
    semantic_id: str
    source_state_hash: str
    prepared_state_hash: str
    engine_profile_id: str
    export_profile_id: str
    readiness_status: ReadinessStatus
    readiness_score: float
    manifest: EngineReadinessManifest
    readiness_hash: str = ""
    generation_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReadinessValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
