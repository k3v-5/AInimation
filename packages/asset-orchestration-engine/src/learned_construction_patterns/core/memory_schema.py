import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .memory_types import PatternState, MemorySource, ProblemSignature, TrustLevel, PatternScope

@dataclass
class MemoryEntry:
    id: str
    entry_type: str # ASSET, BUILD, CORRECTION, PATTERN, FAILURE, REFERENCE, PROJECT
    version: str = "v1.0.0"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    source: MemorySource = MemorySource.SUCCESSFUL_BUILD
    confidence: float = 0.90
    quality: float = 0.90
    tags: List[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""

@dataclass
class AssetMemoryRecord:
    asset_id: str
    asset_type: str
    family_id: str
    template_id: str
    definition_version: str
    builder_version: str
    creation_timestamp: float = field(default_factory=time.time)
    parameters: Dict[str, Any] = field(default_factory=dict)
    materials: List[str] = field(default_factory=list)
    seed: int = 42
    build_fingerprint: str = ""
    quality_score: float = 0.95

@dataclass
class BuildMemoryRecord:
    build_id: str
    asset_id: str
    input_specification: Dict[str, Any]
    resolved_parameters: Dict[str, Any]
    build_stages: List[str]
    execution_time_ms: float
    geometry_statistics: Dict[str, int]
    validation_results: List[str]
    visual_scores: Dict[str, float]
    final_status: str

@dataclass
class CorrectionMemoryRecord:
    correction_id: str
    asset_id: str
    parameter_name: str
    old_value: Any
    new_value: Any
    delta_percent: float
    reason: str
    detected_error: str
    before_score: float
    after_score: float
    success: bool = True

@dataclass
class PatternRecord:
    pattern_id: str
    name: str
    asset_family: str
    problem_signature: str # e.g. "ROOF_TOO_LOW"
    target_parameter: str # e.g. "roof_height"
    correction_delta: float # e.g. +0.18 (+18%) or relative float
    success_rate: float = 1.00
    confidence: float = 0.85
    quality: float = 0.90
    applications_count: int = 1
    success_count: int = 1
    failure_count: int = 0
    average_improvement: float = 0.15
    state: PatternState = PatternState.CANDIDATE
    scope: PatternScope = PatternScope.FAMILY
    trust_level: TrustLevel = TrustLevel.VALIDATED
    builder_version: str = "v1.0.0"
    definition_version: str = "v1.0.0"
    applicability_conditions: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

@dataclass
class FailureMemoryRecord:
    failure_id: str
    error_signature: str
    trigger_conditions: Dict[str, Any]
    affected_parameters: List[str]
    failed_templates: List[str]
    successful_fixes: List[str]
    consecutive_failures: int = 1
    do_not_retry: bool = False
    created_at: float = field(default_factory=time.time)

@dataclass
class ReferenceMemoryRecord:
    reference_profile_id: str
    reference_type: str
    landmarks: List[Dict[str, Any]]
    proportions: Dict[str, float]
    silhouette_features: Dict[str, Any]
    style_features: Dict[str, str]
    confidence: float = 0.95

@dataclass
class ProjectMemoryRecord:
    project_id: str
    style_lock: str = "medieval_stylized"
    aesthetic_preferences: Dict[str, Any] = field(default_factory=dict)
    trusted_families: List[str] = field(default_factory=list)
