from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

class CriticStatus(str, Enum):
    PASS = "PASS"
    NEEDS_REVISION = "NEEDS_REVISION"
    FAIL = "FAIL"
    UNCERTAIN = "UNCERTAIN"

class IssueSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

@dataclass
class CriticIssue:
    issue_id: str
    category: str # PROPORTION, SILHOUETTE, MATERIAL, COMPONENT, STYLE
    severity: IssueSeverity
    component: str # blade, guard, grip, pommel
    property_name: str # blade_width, blade_length, metallic
    current_value: Any
    expected_value: Any
    direction: str # INCREASE, DECREASE, SET
    magnitude: float # suggested delta or absolute multiplier
    confidence: float
    evidence: str

@dataclass
class CriticReport:
    status: CriticStatus
    overall_visual_score: float
    confidence: float
    issues: List[CriticIssue] = field(default_factory=list)
    summary: str = ""
