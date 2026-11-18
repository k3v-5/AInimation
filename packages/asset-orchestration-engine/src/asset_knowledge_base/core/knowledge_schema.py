from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
from .knowledge_types import (
    ArchetypeCategory, ComponentNecessity, DependencyType,
    DesignRuleSeverity, StyleEra, DefectPatternType,
    ValidationProfileType, QualityProfileType, AssetLifecycleState,
    KnowledgeStatus, ConflictPriority
)

@dataclass
class ComponentSlot:
    name: str
    necessity: ComponentNecessity
    generator_type: str
    parent_component: Optional[str] = None
    children: List[str] = field(default_factory=list)
    min_count: int = 1
    max_count: int = 1
    allowed_types: List[str] = field(default_factory=list)
    attachment_target: Optional[str] = None
    dependency_type: DependencyType = DependencyType.REQUIRED

@dataclass
class ParameterDefinitionKB:
    name: str
    param_type: str = "FLOAT"
    unit: str = "METERS"
    default: Any = 0.0
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    expression: Optional[str] = None # e.g. "roof_width = house_width + 0.4"
    description: str = ""

@dataclass
class DesignRule:
    rule_id: str
    name: str
    severity: DesignRuleSeverity
    description: str
    condition_code: str = ""

@dataclass
class GeneratorDefinitionKB:
    generator_id: str
    version: str = "1.0.0"
    capabilities: List[str] = field(default_factory=list)
    cost: str = "LOW" # LOW, MEDIUM, HIGH
    reliability_score: float = 0.98
    fallback_generator_id: Optional[str] = None
    compatible_archetypes: List[str] = field(default_factory=list)

@dataclass
class FailureKnowledge:
    failure_id: str
    category: str
    symptoms: List[str] = field(default_factory=list)
    causes: List[str] = field(default_factory=list)
    candidate_corrections: List[str] = field(default_factory=list)
    severity: DesignRuleSeverity = DesignRuleSeverity.WARNING

@dataclass
class CorrectionPattern:
    defect_type: DefectPatternType
    candidate_parameter: str
    recommended_factor: float
    success_rate: float = 0.95
    description: str = ""

@dataclass
class ObservationRecord:
    observation_id: str
    rule_signature: str
    success_count: int = 1
    fail_count: int = 0
    confidence: float = 0.90
    status: KnowledgeStatus = KnowledgeStatus.PROPOSED
    evidence: str = ""

@dataclass
class ArchetypeDefinition:
    archetype_id: str
    name: str
    category: ArchetypeCategory
    style_era: StyleEra
    component_slots: Dict[str, ComponentSlot] = field(default_factory=dict)
    default_parameters: Dict[str, Any] = field(default_factory=dict)
    parameter_expressions: Dict[str, str] = field(default_factory=dict) # derived parameters
    design_rules: List[DesignRule] = field(default_factory=list)
    primary_generators: Dict[str, str] = field(default_factory=dict) # component -> generator_id

@dataclass
class DesignTemplate:
    template_id: str
    parent_template: Optional[str] = None
    archetype_id: str = "MEDIEVAL_HOUSE"
    style_era: StyleEra = StyleEra.MEDIEVAL
    parameter_overrides: Dict[str, Any] = field(default_factory=dict)
    materials: Dict[str, str] = field(default_factory=dict)

@dataclass
class RuleValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

@dataclass
class KnowledgeContextSummary:
    archetype_id: str
    relevant_components: List[str] = field(default_factory=list)
    active_parameters: Dict[str, Any] = field(default_factory=dict)
    recommended_generators: Dict[str, str] = field(default_factory=dict)
    known_failures: List[str] = field(default_factory=list)
    estimated_context_tokens: int = 250
