from typing import Dict, Any, List, Set, Optional
from ..core.knowledge_types import (
    ArchetypeCategory, ComponentNecessity, DependencyType,
    DesignRuleSeverity, StyleEra, DefectPatternType,
    ValidationProfileType, QualityProfileType, AssetLifecycleState,
    KnowledgeStatus, ConflictPriority
)
from ..core.knowledge_schema import (
    ComponentSlot, DesignRule, ArchetypeDefinition, DesignTemplate,
    GeneratorDefinitionKB, FailureKnowledge, CorrectionPattern,
    ObservationRecord, RuleValidationResult, KnowledgeContextSummary
)
from ..registry.archetype_registry import ArchetypeRegistry, DesignTemplateLibrary
from ..rules.design_rule_engine import DesignRuleEngine, CorrectionPatternEngine
from ..engine.generator_selector import GeneratorSelector
from ..engine.conflict_resolver import ConflictResolver
from ..engine.knowledge_query_engine import KnowledgeQueryEngine, KnowledgeContextBuilder
from ..engine.knowledge_learning_pipeline import KnowledgeLearningPipeline

class AssetKnowledgeAPI:
    """
    Asset Knowledge Base & Procedural Design Library API (AOE v44)
    
    Regla Fundamental:
    LA IA NO INVENTA ESTRUCTURAS, REGLAS NI GENERADORES DESDE CERO.
    CONSULTA LA BASE DE CONOCIMIENTO PARA OBTENER ARQUETIPOS FORMALES, SLOTS OBLIGATORIOS,
    RESTRICCIONES FÍSICAS, PLANTILLAS PARAMÉTRICAS, SELECCIÓN DE GENERADORES Y PATRONES DE CORRECCIÓN HISTÓRICOS.
    """
    def __init__(self):
        self.archetype_registry = ArchetypeRegistry()
        self.template_library = DesignTemplateLibrary()
        self.generator_selector = GeneratorSelector(self.archetype_registry)
        self.query_engine = KnowledgeQueryEngine(self.archetype_registry)
        self.learning_pipeline = KnowledgeLearningPipeline()

    def get_archetype(self, archetype_id: str) -> ArchetypeDefinition:
        return self.archetype_registry.get_archetype(archetype_id)

    def get_template(self, template_id: str) -> DesignTemplate:
        return self.template_library.get_resolved_template(template_id)

    def query_archetypes_by_style(self, style: StyleEra) -> List[ArchetypeDefinition]:
        return self.archetype_registry.query_by_style(style)

    def hybrid_search_archetypes(self, query: str) -> List[ArchetypeDefinition]:
        return self.query_engine.hybrid_search(query)

    def build_knowledge_context(self, archetype_id: str, target_component: Optional[str] = None) -> KnowledgeContextSummary:
        archetype = self.get_archetype(archetype_id)
        return KnowledgeContextBuilder.build_focused_context(archetype, target_component)

    def validate_design(
        self,
        archetype_id: str,
        parameters: Dict[str, Any],
        active_components: Set[str]
    ) -> RuleValidationResult:
        archetype = self.archetype_registry.get_archetype(archetype_id)
        return DesignRuleEngine.validate_asset_design(archetype, parameters, active_components)

    def select_generator(self, archetype_id: str, component_name: str, simulate_failure: bool = False) -> GeneratorDefinitionKB:
        return self.generator_selector.select_generator_for_component(archetype_id, component_name, simulate_failure)

    def rank_generators(self, archetype_id: str) -> List[Dict[str, Any]]:
        return self.generator_selector.rank_generators_for_archetype(archetype_id)

    def lookup_correction_pattern(self, defect_type: DefectPatternType) -> Optional[CorrectionPattern]:
        return CorrectionPatternEngine.lookup_pattern(defect_type)

    def resolve_conflict(self, param_name: str, proposals: Dict[ConflictPriority, Any]) -> Dict[str, Any]:
        return ConflictResolver.resolve_parameter_conflict(param_name, proposals)

    def record_repair_observation(self, rule_sig: str, succeeded: bool, evidence: str = "") -> ObservationRecord:
        return self.learning_pipeline.record_repair_observation(rule_sig, succeeded, evidence)

    def promote_candidate_rule(self, rule_sig: str, has_formal_tests: bool = False) -> str:
        return self.learning_pipeline.promote_to_approved(rule_sig, has_formal_tests)
