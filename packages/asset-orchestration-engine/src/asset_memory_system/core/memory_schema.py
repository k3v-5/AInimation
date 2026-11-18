import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .memory_status import AssetStatus, PatternStatus, PatternScope

@dataclass
class AssetRecord:
    asset_id: str
    name: str
    asset_type: str # SWORD, AXE, SHIELD
    template_id: str
    status: AssetStatus = AssetStatus.DRAFT
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)

@dataclass
class AssetVersionRecord:
    version_id: str
    asset_id: str
    version_number: str # e.g. 1.0.0
    parent_version_id: Optional[str] = None
    branch: str = "main"
    parameters: Dict[str, Any] = field(default_factory=dict)
    parameter_hash: str = ""
    template_version: str = "1.0.0"
    generation_seed: int = 42
    created_at: float = field(default_factory=time.time)

@dataclass
class PatternRecord:
    pattern_id: str
    template_id: str
    trigger_issue: str # e.g. blade_too_narrow
    recommended_action: str # e.g. SET blade_width = 0.075
    target_parameter: str # blade_width
    parameter_multiplier: float = 1.0
    status: PatternStatus = PatternStatus.CANDIDATE
    scope: PatternScope = PatternScope.TEMPLATE
    confidence: float = 0.50
    evidence_count: int = 1
    success_count: int = 1
    failure_count: int = 0
    success_rate: float = 1.0
    compatible_template_versions: str = ">=1.0.0 <2.0.0"
    created_at: float = field(default_factory=time.time)

@dataclass
class PatternEvidence:
    evidence_id: str
    pattern_id: str
    asset_id: str
    version_id: str
    before_score: float
    after_score: float
    result: str # SUCCESS, FAILURE
    timestamp: float = field(default_factory=time.time)

@dataclass
class EvaluationRecord:
    evaluation_id: str
    version_id: str
    technical_score: float
    visual_score: float
    status: str
    created_at: float = field(default_factory=time.time)

@dataclass
class FailureMemoryRecord:
    failure_id: str
    asset_id: str
    template_id: str
    problematic_parameters: Dict[str, Any]
    error_type: str # COLLISION, INVALID_TOPOLOGY, MANIFOLD_ERROR
    created_at: float = field(default_factory=time.time)

@dataclass
class AuditEvent:
    event_id: str
    entity_id: str
    entity_type: str # ASSET, VERSION, PATTERN
    event_type: str # CREATE, MODIFY, EVALUATE, PATCH, PROMOTE
    actor: str = "SYSTEM" # USER, AI, SYSTEM, AUTOMATION
    payload_hash: str = ""
    timestamp: float = field(default_factory=time.time)
