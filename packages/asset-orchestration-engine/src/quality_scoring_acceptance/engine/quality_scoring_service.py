import time
from typing import Dict, Any, List, Optional
from ..core.scoring_types import (
    AcceptanceStatus, QualityLevel, MetricCategory,
    ConstraintSeverity, DirectionType, MetricStatus
)
from ..core.scoring_schema import (
    QualityMetric, QualityConstraint, QualityDefect, QualityProfile,
    AcceptanceExplanation, QualityResult, QualityReport, ScoringValidationResult
)
from .metric_normalizer import MetricNormalizer
from .constraint_evaluator import ConstraintEvaluator
from .quality_scorer import QualityScorer
from .acceptance_policy import AcceptancePolicy
from .quality_report_generator import QualityReportGenerator
from .quality_hasher import QualityHasher

class QualityScoringService:
    """
    Quality Scoring & Acceptance Service (AOE v66)
    
    Regla Fundamental:
    CALCULA EL SCORE OBJETIVO 0-100 PONDERADO Y DETERMINA INEQUÍVOCAMENTE EL ESTADO DE ACEPTACIÓN
    (ACCEPTED, CONDITIONAL, REJECTED) APLICANDO GATES DUROS DONDE NINGÚN SCORE ELEVADO
    PUEDA OCULTAR UNA RESTRICCIÓN CRÍTICA O TOPOLÓGICA INCUMPLIDA.
    """
    def __init__(self, scoring_version: str = "1.0.0"):
        self.scoring_version = scoring_version

    def evaluate_quality(
        self,
        asset_id: str,
        semantic_id: str,
        visual_eval_result: Any,   # F61 VisualEvaluationResult
        geometry_qa_result: Any,   # F62 GeometricValidationResult
        profile: Optional[QualityProfile] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> QualityResult:
        ctx = context or {}
        prof = profile or QualityProfile()

        # 1. Chequeo de Datos Obsoletos / Stale Data Protection
        expected_hash = ctx.get("expected_state_hash", "")
        actual_hash = getattr(geometry_qa_result, "state_hash", "") or getattr(visual_eval_result, "state_hash", "")
        if expected_hash and actual_hash and expected_hash != actual_hash:
            return QualityResult(
                asset_id=asset_id,
                semantic_id=semantic_id,
                overall_score=0.0,
                quality_level=QualityLevel.INVALID,
                acceptance_status=AcceptanceStatus.INVALID,
                blocking_reasons=["STALE_DATA_DETECTED: Evaluated state hash does not match current state hash."]
            )

        # 2. Recopilación de Métricas
        metrics: List[QualityMetric] = []
        defects: List[QualityDefect] = []

        # Métricas Visuales F61
        v_score = getattr(visual_eval_result, "global_score", 1.0)
        metrics.append(QualityMetric(
            metric_id="METRIC_VISUAL_OVERALL",
            name="Visual Fidelity",
            category=MetricCategory.VISUAL,
            raw_value=v_score,
            normalized_value=MetricNormalizer.normalize(v_score, DirectionType.HIGHER_IS_BETTER),
            weight=prof.weights.get(MetricCategory.VISUAL, 0.30)
        ))

        # Defectos Visuales
        for d in getattr(visual_eval_result, "defects", []):
            defects.append(QualityDefect(
                defect_id=d.defect_id,
                category=MetricCategory.VISUAL,
                severity=ConstraintSeverity.HIGH if d.error_pct > 25.0 else ConstraintSeverity.MEDIUM,
                description=f"Visual defect in {d.region}: {d.defect_type.value} ({d.error_pct:.1f}%)",
                location=d.region
            ))

        # Métricas Geométricas F62
        g_scores = getattr(geometry_qa_result, "quality_scores", {})
        g_geom = g_scores.get("overall_geometry_score", 1.0)
        metrics.append(QualityMetric(
            metric_id="METRIC_GEOM_OVERALL",
            name="Geometry Quality",
            category=MetricCategory.GEOMETRY,
            raw_value=g_geom,
            normalized_value=MetricNormalizer.normalize(g_geom, DirectionType.HIGHER_IS_BETTER),
            weight=prof.weights.get(MetricCategory.GEOMETRY, 0.20)
        ))

        g_top = g_scores.get("topology_score", 1.0)
        metrics.append(QualityMetric(
            metric_id="METRIC_TOPOLOGY",
            name="Topology Score",
            category=MetricCategory.TOPOLOGY,
            raw_value=g_top,
            normalized_value=MetricNormalizer.normalize(g_top, DirectionType.HIGHER_IS_BETTER),
            weight=prof.weights.get(MetricCategory.TOPOLOGY, 0.15)
        ))

        # Defectos Geométricos F62
        for d in getattr(geometry_qa_result, "defects", []):
            sev = ConstraintSeverity.CRITICAL if getattr(d, "severity", "") == "CRITICAL" else ConstraintSeverity.MEDIUM
            defects.append(QualityDefect(
                defect_id=getattr(d, "defect_id", "DEF_G"),
                category=MetricCategory.TOPOLOGY if "MANIFOLD" in str(getattr(d, "category", "")) else MetricCategory.GEOMETRY,
                severity=sev,
                description=getattr(d, "description", "Geometry QA Defect"),
                location=getattr(d, "location", "mesh"),
                blocking=(sev == ConstraintSeverity.CRITICAL)
            ))

        # Métricas Unreal Readiness
        u_rep = getattr(geometry_qa_result, "unreal_readiness", None)
        u_ready = getattr(u_rep, "is_export_ready", True) if u_rep else True
        metrics.append(QualityMetric(
            metric_id="METRIC_UNREAL_READY",
            name="Unreal Engine Readiness",
            category=MetricCategory.UNREAL_READINESS,
            raw_value=u_ready,
            normalized_value=MetricNormalizer.normalize(u_ready, DirectionType.BOOLEAN),
            weight=prof.weights.get(MetricCategory.UNREAL_READINESS, 0.15)
        ))
        if not u_ready:
            defects.append(QualityDefect(
                defect_id="DEF_UNREAL_NOT_READY",
                category=MetricCategory.UNREAL_READINESS,
                severity=ConstraintSeverity.CRITICAL,
                description="Asset failed Unreal Engine export readiness gates (collision/scale/topology).",
                location="root",
                blocking=True
            ))

        # 3. Evaluación de Restricciones Duras (Hard Constraints)
        has_passed_hard_gates, blocking_reasons, warnings = ConstraintEvaluator.evaluate_constraints(defects)

        # 4. Cálculo de Scores Ponderados
        category_scores = QualityScorer.calculate_scores(metrics, prof)
        overall_score = category_scores.get("OVERALL", 100.0)

        # 5. Determinación de Estado de Aceptación y Nivel de Calidad
        status, q_level = AcceptancePolicy.evaluate_acceptance(
            overall_score, category_scores, has_passed_hard_gates, blocking_reasons, warnings, prof
        )

        # 6. Hash Determinista
        q_hash = QualityHasher.compute_quality_hash(
            asset_id, overall_score, status.value, q_level.value, prof.profile_id
        )

        return QualityResult(
            asset_id=asset_id,
            semantic_id=semantic_id,
            evaluation_id=f"Q_EVAL_{asset_id}_{int(time.time()*1000)%100000}",
            overall_score=overall_score,
            category_scores=category_scores,
            quality_level=q_level,
            acceptance_status=status,
            blocking_reasons=blocking_reasons,
            quality_hash=q_hash,
            evaluated_at=time.time(),
            scoring_version=self.scoring_version
        )

    def generate_report(
        self,
        quality_result: QualityResult,
        profile_id: str = "DEFAULT_GAME_PROP"
    ) -> QualityReport:
        explanation = AcceptanceExplanation(
            decision=quality_result.acceptance_status,
            summary=f"Quality Evaluation finished with status: {quality_result.acceptance_status.value} ({quality_result.quality_level.value})",
            blocking_reasons=quality_result.blocking_reasons,
            warnings=[]
        )
        return QualityReportGenerator.generate_report(
            report_id=f"Q_REP_{quality_result.asset_id}",
            asset_id=quality_result.asset_id,
            semantic_id=quality_result.semantic_id,
            result=quality_result,
            explanation=explanation,
            metrics=[],
            defects=[],
            profile_id=profile_id
        )

    def validate_result(self, result: QualityResult) -> ScoringValidationResult:
        errors = []
        warnings = []
        if not result.asset_id:
            errors.append("MISSING_ASSET_ID: Asset ID is mandatory.")
        if result.overall_score < 0.0 or result.overall_score > 100.0:
            errors.append(f"OUT_OF_BOUNDS_SCORE: Overall score {result.overall_score} outside 0.0-100.0.")
        return ScoringValidationResult(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)
