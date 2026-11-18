import time
from typing import Dict, Any, List, Optional
from ..core.strategy_types import (
    GenerationStrategyType, AssetComplexityLevel, FailureCategory, StageType
)
from ..core.strategy_schema import (
    GenerationStrategy, CandidateStrategy, GenerationPlan, GenerationStage,
    StrategyDecisionRecord, AssetComplexityReport, ReuseAnalysisReport
)
from ..registry.strategy_registry import GenerationStrategyRegistry
from ..analyzers.complexity_analyzer import AssetComplexityAnalyzer
from ..analyzers.reuse_analyzer import ReuseAnalyzer

class StrategySelector:
    def __init__(self):
        self.registry = GenerationStrategyRegistry()
        self.blacklist: Dict[str, List[GenerationStrategyType]] = {}
        self.failure_counts: Dict[str, int] = {}

    def select_strategy(
        self,
        asset_class: str,
        components_count: int,
        batch_size: int = 1,
        existing_library: Optional[Dict[str, Dict[str, Any]]] = None,
        intent_type: str = "CREATE",
        force_strategy: Optional[GenerationStrategyType] = None,
        expected_frequent_revisions: bool = True
    ) -> Tuple_StrategyDecision:
        existing_library = existing_library or {}
        complexity_rep = AssetComplexityAnalyzer.analyze(asset_class, components_count, batch_size)
        reuse_rep = ReuseAnalyzer.analyze_reuse(asset_class, existing_library, intent_type)

        candidate_scores: Dict[str, float] = {}

        # 1. Human Override
        if force_strategy:
            return GenerationStrategyType(force_strategy), {force_strategy.value: 1.0}, True, "Human override requested and honored."

        # 2. Reutilización de Asset Existente
        if reuse_rep.has_match and reuse_rep.recommended_action == "EXISTING_ASSET_MODIFICATION":
            return GenerationStrategyType.EXISTING_ASSET_MODIFICATION, {"EXISTING_ASSET_MODIFICATION": 1.0}, False, f"Reusing approved asset '{reuse_rep.matched_asset_id}' with similarity {reuse_rep.similarity_score:.2f}."

        # 3. Lote / Batch -> Procedural
        if complexity_rep.is_batch:
            return GenerationStrategyType.PROCEDURAL_GENERATION, {"PROCEDURAL_GENERATION": 0.98}, False, f"Batch generation of {batch_size} assets requires Procedural Generation."

        # 4. Arquitectura / Modular -> Component Assembly
        if "BUILDING" in asset_class.upper():
            return GenerationStrategyType.COMPONENT_ASSEMBLY, {"COMPONENT_ASSEMBLY": 0.95}, False, "Modular architecture requires Component Assembly."

        # 5. Props Estándar Parametrizados (Barriles, Espadas, Cajas)
        # Evaluamos Scripted vs Primitive Composition con penalización de rework
        strat_scripted = self.registry.get_strategy(GenerationStrategyType.SCRIPTED_MODELING)
        strat_primitive = self.registry.get_strategy(GenerationStrategyType.PRIMITIVE_COMPOSITION)

        # Cálculo de Coste Total = BaseCost + (1.0 - Editability)*ReworkPenalty
        rework_penalty = 2.0 if expected_frequent_revisions else 0.5
        
        cost_scripted = strat_scripted.base_cost + (1.0 - strat_scripted.editability_score) * rework_penalty
        cost_primitive = strat_primitive.base_cost + (1.0 - strat_primitive.editability_score) * rework_penalty

        score_scripted = strat_scripted.quality_score * strat_scripted.reliability_score / cost_scripted
        score_primitive = strat_primitive.quality_score * strat_primitive.reliability_score / cost_primitive

        candidate_scores[GenerationStrategyType.SCRIPTED_MODELING.value] = round(score_scripted, 3)
        candidate_scores[GenerationStrategyType.PRIMITIVE_COMPOSITION.value] = round(score_primitive, 3)

        # Verificamos si Scripted está en blacklist por fallos repetidos
        if GenerationStrategyType.SCRIPTED_MODELING in self.blacklist.get(asset_class, []):
            return GenerationStrategyType.GEOMETRY_NODES, candidate_scores, False, "Scripted modeling blacklisted due to repeated topology errors; falling back to Geometry Nodes."

        selected = GenerationStrategyType.SCRIPTED_MODELING if score_scripted >= score_primitive else GenerationStrategyType.PRIMITIVE_COMPOSITION
        reason = f"Selected {selected.value} due to superior editability ({strat_scripted.editability_score:.2f}) and lower expected rework cost."

        return selected, candidate_scores, False, reason

    def record_strategy_failure(self, asset_class: str, strategy: GenerationStrategyType, category: FailureCategory):
        key = f"{asset_class}_{strategy.value}"
        self.failure_counts[key] = self.failure_counts.get(key, 0) + 1
        if self.failure_counts[key] >= 2 and category == FailureCategory.TOPOLOGY_ERROR:
            if asset_class not in self.blacklist:
                self.blacklist[asset_class] = []
            self.blacklist[asset_class].append(strategy)

    def build_generation_plan(
        self,
        specification_id: str,
        selected_strategy: GenerationStrategyType,
        parameters: Dict[str, Any],
        seed: int = 1337
    ) -> GenerationPlan:
        stages = [
            GenerationStage("STG_1_BLOCKOUT", StageType.BLOCKOUT, 1, "Generate primary bounding volume and silhouette", {"silhouette": 0.80}),
            GenerationStage("STG_2_PRIMARY", StageType.PRIMARY_GEOMETRY, 2, "Model base structural geometry", {"proportions": 0.85}),
            GenerationStage("STG_3_SECONDARY", StageType.SECONDARY_COMPONENTS, 3, "Assemble secondary details/rings", {"components": 1.0}),
            GenerationStage("STG_4_MATERIALS", StageType.MATERIALS, 4, "Assign PBR shaders and texture maps", {"material_match": 0.90}),
            GenerationStage("STG_5_TECHNICAL", StageType.TECHNICAL_SETUP, 5, "Configure collision, pivots, and LODs", {"collision": 1.0}),
            GenerationStage("STG_6_VALIDATION", StageType.VALIDATION, 6, "Final quality gate verification", {"overall": 0.85})
        ]

        fallback = GenerationStrategyType.GEOMETRY_NODES if selected_strategy == GenerationStrategyType.SCRIPTED_MODELING else GenerationStrategyType.SCRIPTED_MODELING

        return GenerationPlan(
            plan_id=f"PLAN_{int(time.time()*1000)}",
            specification_id=specification_id,
            selected_strategy=selected_strategy,
            stages=stages,
            parameters=parameters,
            seed=seed,
            fallback_strategy=fallback,
            is_deterministic=True
        )

# Helper tuple alias
Tuple_StrategyDecision = Any
