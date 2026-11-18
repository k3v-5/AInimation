import time
from typing import Dict, Any, List, Optional
from ..core.evaluation_types import (
    EvaluationCategory, DefectType, DefectSeverity,
    DefectCauseCategory, AcceptanceStatus, EvaluationLevel,
    RegressionStatus
)
from ..core.evaluation_schema import (
    VisualDefect, CorrectionHint, CategoryEvaluation,
    RegionEvaluation, RequirementEvaluationResult, EvaluationDelta,
    EvaluationConfiguration, VisualEvaluationResult, EvaluationValidationResult
)
from ..metrics.metric_registry import MetricRegistry
from ..engine.defect_detector import DefectDetector
from ..engine.temporal_comparator import TemporalComparator
from ..engine.evaluation_hasher import EvaluationHasher

class AutomatedVisualEvaluationEngine:
    """
    Automated Visual Evaluation Engine (AVEE v61)
    
    Regla Fundamental:
    COMPARA OBJETIVAMENTE EL RENDER Y LA ESPECIFICACIÓN VISUAL,
    GENERANDO MÉTRICAS MULTINIVEL, DEFECTOS LOCALIZADOS, CAUSAS MULTI-HIPÓTESIS
    Y HINTS DE CORRECCIÓN PARA F63 Y F64 SIN DEPENDER DIRECTAMENTE DE BPY NI MCP.
    """
    def __init__(self, engine_version: str = "1.0.0"):
        self.engine_version = engine_version
        self.registry = MetricRegistry()

    def evaluate(
        self,
        reference: Optional[Any] = None, # DecomposedReferenceReport from F55
        generated: Optional[Any] = None, # GeneratedGeometryResult from F58
        context: Optional[Dict[str, Any]] = None, # surface (F59), presentation (F60), vas (F56)
        configuration: Optional[EvaluationConfiguration] = None
    ) -> VisualEvaluationResult:
        ctx = context or {}
        config = configuration or EvaluationConfiguration()

        sem_id = getattr(generated, "semantic_id", "asset.root") if generated else "asset.root"
        geom_id = getattr(generated, "generation_id", "GEN_DEFAULT") if generated else "GEN_DEFAULT"
        ref_id = getattr(reference, "report_id", "REF_DEFAULT") if reference else "REF_DEFAULT"
        surf_res = ctx.get("surface")
        surf_id = getattr(surf_res, "surface_generation_id", "SURF_DEFAULT") if surf_res else "SURF_DEFAULT"
        vpc = ctx.get("presentation")
        pres_id = getattr(vpc, "presentation_id", "VPC_DEFAULT") if vpc else "VPC_DEFAULT"

        # 1. Ejecutar métricas por categoría
        cat_evals = self.registry.evaluate_all(reference, generated, ctx, config)

        # 2. Calcular Score Global Ponderado
        total_w = sum(c.weight * c.confidence for c in cat_evals.values())
        if total_w > 0:
            global_score = round(sum(c.score * c.weight * c.confidence for c in cat_evals.values()) / total_w, 4)
        else:
            global_score = 1.0

        # 3. Detección y Localización de Defectos
        defects = DefectDetector.detect_defects(cat_evals, reference, generated, ctx)

        # 4. Hints de Corrección
        correction_hints = [d.correction_hint for d in defects if d.correction_hint is not None]

        # 5. Determinación de Acceptance Status Preliminar
        if any(d.severity == DefectSeverity.CRITICAL for d in defects) or global_score < config.thresholds.get("warn_global", 0.70):
            status = AcceptanceStatus.FAIL
        elif len(defects) > 0 or global_score < config.thresholds.get("pass_global", 0.85):
            status = AcceptanceStatus.PASS_WITH_WARNINGS
        else:
            status = AcceptanceStatus.PASS

        # 6. Hash Determinista
        eval_hash = EvaluationHasher.compute_evaluation_hash(
            global_score=global_score,
            category_scores=cat_evals,
            defects=defects,
            acceptance_status=status.value
        )

        trace = [
            {"step": "EXECUTE_METRICS", "categories_evaluated": len(cat_evals), "status": "SUCCESS"},
            {"step": "DETECT_DEFECTS", "defects_count": len(defects), "status": "SUCCESS"},
            {"step": "COMPUTE_GLOBAL_SCORE", "global_score": global_score, "status": "SUCCESS"}
        ]

        result = VisualEvaluationResult(
            evaluation_id=f"EVAL_{geom_id.replace('GEN_', '')}",
            semantic_id=sem_id,
            reference_id=ref_id,
            geometry_generation_id=geom_id,
            surface_generation_id=surf_id,
            presentation_id=pres_id,
            global_score=global_score,
            category_scores=cat_evals,
            region_scores={},
            defects=defects,
            difference_maps={"silhouette_diff": "MAP_SIL_DIFF_CLEAN", "heatmap": "MAP_HEATMAP_NORMALIZED"},
            confidence=0.95,
            requirement_results=[],
            correction_hints=correction_hints,
            acceptance_status=status,
            evaluation_hash=eval_hash,
            execution_trace=trace,
            generation_metadata={"engine_version": self.engine_version}
        )

        return result

    def evaluate_category(
        self,
        category: EvaluationCategory,
        reference: Any,
        generated: Any,
        context: Dict[str, Any]
    ) -> CategoryEvaluation:
        config = EvaluationConfiguration(enabled_categories=[category])
        res = self.registry.evaluate_all(reference, generated, context, config)
        return res.get(category.value, CategoryEvaluation(category=category, score=1.0))

    def detect_defects(self, evaluation_context: Dict[str, Any]) -> List[VisualDefect]:
        cat_evals = evaluation_context.get("category_scores", {})
        return DefectDetector.detect_defects(cat_evals, None, None, evaluation_context)

    def compare_iterations(
        self,
        previous: VisualEvaluationResult,
        current: VisualEvaluationResult
    ) -> EvaluationDelta:
        return TemporalComparator.compare_evaluations(previous, current)

    def validate(self, result: VisualEvaluationResult) -> EvaluationValidationResult:
        errors = []
        warnings = []

        if not result.evaluation_id:
            errors.append("MISSING_EVALUATION_ID: Evaluation ID is mandatory.")
        if result.global_score < 0.0 or result.global_score > 1.0:
            errors.append(f"INVALID_SCORE: Global score {result.global_score} is out of bounds [0.0, 1.0].")
        if not result.category_scores:
            errors.append("EMPTY_CATEGORIES: At least one category score must be present.")

        for d in result.defects:
            if d.severity == DefectSeverity.CRITICAL:
                warnings.append(f"CRITICAL_DEFECT_PRESENT: {d.defect_id} ({d.defect_type.value})")

        return EvaluationValidationResult(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)

    def compute_hash(self, result: VisualEvaluationResult) -> str:
        return EvaluationHasher.compute_evaluation_hash(
            global_score=result.global_score,
            category_scores=result.category_scores,
            defects=result.defects,
            acceptance_status=result.acceptance_status.value
        )
