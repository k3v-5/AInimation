from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .prompt_types import (
    IntentType, AssetClassType, ProvenanceType,
    RequirementHardness, ConflictSeverity, CompilationStatus
)

@dataclass
class ExtractedComponent:
    component_name: str
    count: int = 1
    is_forbidden: bool = False
    provenance: ProvenanceType = ProvenanceType.USER_EXPLICIT

@dataclass
class RequirementConflict:
    conflict_id: str
    requirement_a: str
    requirement_b: str
    severity: ConflictSeverity = ConflictSeverity.CRITICAL
    reason: str = ""

@dataclass
class AmbiguityRecord:
    term: str
    interpretation_options: List[str] = field(default_factory=list)
    impact: str = "LOW"
    is_resolved: bool = True

@dataclass
class ClarificationRequest:
    request_id: str
    question: str
    impact_category: str = "GAMEPLAY"
    suggested_options: List[str] = field(default_factory=list)

@dataclass
class CompiledSpecification:
    specification_id: str
    version: str = "1.0.0"
    source_text: str = ""
    intent: IntentType = IntentType.CREATE
    asset_class: str = "PROP.BARREL"
    style: List[str] = field(default_factory=list)
    components: Dict[str, int] = field(default_factory=dict)
    dimensions: Dict[str, float] = field(default_factory=dict)
    materials: Dict[str, str] = field(default_factory=dict)
    gameplay_flags: Dict[str, bool] = field(default_factory=dict)
    derived_requirements: List[str] = field(default_factory=list)
    forbidden_features: List[str] = field(default_factory=list)
    provenance_map: Dict[str, ProvenanceType] = field(default_factory=dict)
    confidence: float = 0.95

@dataclass
class ConversationContext:
    active_asset_id: Optional[str] = None
    active_asset_class: Optional[str] = None
    previous_parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CompilationResult:
    status: CompilationStatus
    specification: Optional[CompiledSpecification] = None
    conflicts: List[RequirementConflict] = field(default_factory=list)
    clarifications: List[ClarificationRequest] = field(default_factory=list)
    confidence: float = 0.95
    error_message: Optional[str] = None
