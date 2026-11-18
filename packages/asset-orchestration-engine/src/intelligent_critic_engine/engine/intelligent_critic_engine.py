from typing import Dict, Any, List, Optional
from ..core.critic_types import (
    CausalCategory, CriticPriority, RiskLevel, IterationRecommendation,
    ActionAutonomyLevel
)
from ..core.critic_schema import (
    CriticDiagnosis, RootCause, DefectCluster, ParameterRecommendation,
    CorrectionPlan, CriticConflict, DiagnosticGraph, CriticConfiguration,
    IntelligentCriticResult, CriticValidationResult
)
from ..rules.rule_registry import CriticRuleRegistry
from ..engine.defect_clusterer import DefectClusterer
from ..engine.root_cause_analyzer import RootCauseAnalyzer
from ..engine.correction_planner import CorrectionPlanner
from ..engine.diagnostic_graph_builder import DiagnosticGraphBuilder
from ..engine.critic_hasher import CriticHasher

class IntelligentCriticEngine:
    """
    Intelligent Critic Engine (AOE v63)
    
    Regla Fundamental:
    TRANSFORMA OBSERVACIONES Y DEFECTOS AISLADOS (F61 PERCEPCIÓN + F62 QA GEOMÉTRICO)
    EN UN DIAGNÓSTICO CAUSAL ESTRUCTURADO, IDENTIFICANDO CAUSAS RAÍZ, AGRUPANDO CLUSTERS,
    ESTABLECIENDO PRIORIDADES Y RECOMENDANDO UN PLAN DE CORRECCIÓN PARA F64.
    """
    def __init__(self, engine_version: str = "1.0.0"):
        self.engine_version = engine_version
        self.registry = CriticRuleRegistry()

    def critique(
        self,
        visual_specification: Optional[Any] = None, # VAS (F56)
        geometry_qa: Optional[Any] = None, # GeometricValidationResult (F62)
        visual_eval: Optional[Any] = None, # VisualEvaluationResult (F61)
        context: Optional[Dict[str, Any]] = None,
        configuration: Optional[CriticConfiguration] = None
    ) -> IntelligentCriticResult:
        ctx = context or {}
        ctx["visual_specification"] = visual_specification
        ctx["geometry_validation"] = geometry_qa
        ctx["visual_evaluation"] = visual_eval
        config = configuration or CriticConfiguration()

        sem_id = getattr(visual_specification, "semantic_id", "asset.root") if visual_specification else "asset.root"
        if geometry_qa and hasattr(geometry_qa, "semantic_id"):
            sem_id = geometry_qa.semantic_id

        # 1. Ejecutar Reglas de Diagnóstico Causal
        diagnoses = self.registry.evaluate_all(ctx, config)
        priority_order_map = {
            CriticPriority.CRITICAL: 0,
            CriticPriority.HIGH: 1,
            CriticPriority.MEDIUM: 2,
            CriticPriority.LOW: 3,
            CriticPriority.INFO: 4
        }
        diagnoses = sorted(diagnoses, key=lambda d: priority_order_map.get(d.priority, 5))

        # 2. Agrupar Síntomas en Clusters
        v_defs = getattr(visual_eval, "defects", []) if visual_eval else []
        g_defs = getattr(geometry_qa, "defects", []) if geometry_qa else []
        clusters = DefectClusterer.cluster_defects(v_defs, g_defs)

        # 3. Análisis de Causa Raíz y Recomendación de Parámetros
        root_causes, param_recs = RootCauseAnalyzer.analyze_causes_and_parameters(diagnoses, ctx)

        # 4. Planificador de Correcciones
        plan = CorrectionPlanner.build_plan(diagnoses, param_recs, ctx)

        # 5. Orden de Prioridad
        priority_order = [d.diagnosis_id for d in diagnoses]

        # 6. Recomendación de Iteración
        if any(d.severity == "CRITICAL" for d in diagnoses):
            rec = IterationRecommendation.CORRECT
        elif len(diagnoses) > 0:
            rec = IterationRecommendation.CORRECT
        else:
            rec = IterationRecommendation.STOP

        # 7. Hash Determinista
        critic_hash = CriticHasher.compute_critic_hash(
            semantic_id=sem_id,
            diagnoses=diagnoses,
            root_causes=root_causes,
            plan_id=plan.plan_id,
            recommendation=rec.value
        )

        trace = [
            {"step": "EVALUATE_RULES", "diagnoses_count": len(diagnoses), "status": "SUCCESS"},
            {"step": "CLUSTER_DEFECTS", "clusters_count": len(clusters), "status": "SUCCESS"},
            {"step": "ANALYZE_ROOT_CAUSES", "causes_count": len(root_causes), "status": "SUCCESS"},
            {"step": "BUILD_PLAN", "actions_count": len(plan.ordered_actions), "status": "SUCCESS"}
        ]

        result = IntelligentCriticResult(
            critic_id=f"CRITIC_{sem_id.replace('.', '_')}",
            semantic_id=sem_id,
            asset_id=sem_id,
            iteration_index=ctx.get("iteration_index", 1),
            diagnoses=diagnoses,
            root_causes=root_causes,
            defect_clusters=clusters,
            priority_order=priority_order,
            correction_plan=plan,
            parameter_recommendations=param_recs,
            conflicts=[],
            uncertainties=[],
            confidence=0.97,
            risk_analysis={
                "regression_risk": RiskLevel.LOW,
                "semantic_risk": RiskLevel.LOW,
                "topology_risk": RiskLevel.LOW
            },
            iteration_recommendation=rec,
            acceptance_blockers=[d.diagnosis_id for d in diagnoses if d.severity == "CRITICAL"],
            quality_summary={
                "visual_score": getattr(visual_eval, "global_score", 1.0) if visual_eval else 1.0,
                "geometry_score": getattr(geometry_qa, "quality_scores", {}).get("overall_geometry_score", 1.0) if geometry_qa else 1.0
            },
            critic_hash=critic_hash,
            execution_trace=trace,
            generation_metadata={"engine_version": self.engine_version}
        )

        return result

    def validate_result(self, result: IntelligentCriticResult) -> CriticValidationResult:
        errors = []
        warnings = []
        if not result.critic_id:
            errors.append("MISSING_CRITIC_ID: Critic ID is mandatory.")
        if result.confidence < 0.0 or result.confidence > 1.0:
            errors.append("INVALID_CONFIDENCE: Confidence out of bounds [0.0, 1.0].")
        return CriticValidationResult(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)

    def compute_hash(self, result: IntelligentCriticResult) -> str:
        return CriticHasher.compute_critic_hash(
            semantic_id=result.semantic_id,
            diagnoses=result.diagnoses,
            root_causes=result.root_causes,
            plan_id=result.correction_plan.plan_id,
            recommendation=result.iteration_recommendation.value
        )
