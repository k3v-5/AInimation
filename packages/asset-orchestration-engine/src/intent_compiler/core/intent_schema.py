import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .intent_status import (
    ActionType, RequirementPriority, RequirementStatus, AmbiguitySeverity, SpecStatus
)

@dataclass
class RequestContext:
    scene_id: Optional[str] = None
    current_asset_id: Optional[str] = None
    current_selection: List[str] = field(default_factory=list)
    available_entities: Dict[str, str] = field(default_factory=dict) # entity_id -> type (e.g. tower_001 -> tower)
    previous_request: Optional[str] = None
    previous_specification: Optional[Any] = None

@dataclass
class NaturalLanguageRequest:
    request_id: str
    text: str
    context: RequestContext = field(default_factory=RequestContext)
    reference_image_uri: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

@dataclass
class Requirement:
    requirement_id: str
    category: str # DIMENSION, STYLE, MATERIAL, COUNT, SPATIAL
    name: str # length, width, style, count
    value: Any
    unit: str = "m"
    priority: RequirementPriority = RequirementPriority.HIGH
    status: RequirementStatus = RequirementStatus.RESOLVED
    source: str = "USER_EXPLICIT" # USER_EXPLICIT, REFERENCE, INFERRED, DEFAULT
    source_text: str = ""

@dataclass
class IntentConstraint:
    constraint_id: str
    subject: str # e.g. tower_001
    relation: str # NORTH_OF, EXACT, MIN, MAX
    object_target: Optional[str] = None
    value: Any = None
    priority: RequirementPriority = RequirementPriority.CRITICAL

@dataclass
class BuildSpecification:
    spec_id: str
    action: ActionType
    target_type: str # SWORD, HOUSE, TOWER, VILLAGE
    target_id: Optional[str]
    requirements: Dict[str, Requirement] = field(default_factory=dict)
    constraints: List[IntentConstraint] = field(default_factory=list)
    status: SpecStatus = SpecStatus.DRAFT
    blocking_reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

@dataclass
class BuildAuthorization:
    authorized: bool
    status: SpecStatus
    spec_id: str
    reasons: List[str] = field(default_factory=list)
