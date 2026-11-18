import time
from typing import Dict, Any, List, Optional
from ..core.qa_types import (
    GeometricDefectCategory, DefectSeverity, ValidationStatus,
    ValidationProfileType, CorrectionSafetyLevel, MeshWatertightMode,
    NgonPolicy
)
from ..core.qa_schema import (
    GeometricDefect, GeometricCorrectionHint, MeshInventory,
    TopologyStatistics, UnrealReadinessReport, GeometryValidationConfiguration,
    GeometricValidationResult, QAValidationResult
)
from ..rules.rule_registry import GeometryValidationRegistry
from ..engine.mesh_inventory_scanner import MeshInventoryScanner
from ..engine.cross_correlation_engine import CrossCorrelationEngine
from ..engine.qa_hasher import QAHasher

class GeometricValidationEngine:
    """
    Geometric Validation & Topology QA Engine (AOE v62)
    
    Regla Fundamental:
    VALIDA ESTRUCTURALMENTE LA MALLA (MANIFOLD, NORMALES, TOPOLOGÍA, ESCALA, PRESUPUESTO, UCX)
    EN MODO READ-ONLY SIN MODIFICAR LA GEOMETRÍA, DESACOPLANDO LA VERDAD ESTRUCTURAL
    DE LA EVALUACIÓN VISUAL DE F61 Y PREPARANDO LA EVIDENCIA PARA F63 Y F64.
    """
    def __init__(self, engine_version: str = "1.0.0"):
        self.engine_version = engine_version
        self.registry = GeometryValidationRegistry()

    def validate(
        self,
        geometry: Any, # GeneratedGeometryResult from F58
        context: Optional[Dict[str, Any]] = None, # VisualEvaluationResult (F61), VAS (F56), Surface (F59)
        configuration: Optional[GeometryValidationConfiguration] = None
    ) -> GeometricValidationResult:
        ctx = context or {}
        config = configuration or GeometryValidationConfiguration()

        sem_id = getattr(geometry, "semantic_id", "asset.root")
        geom_id = getattr(geometry, "generation_id", "GEN_DEFAULT")

        # 1. Escaneo Read-Only de Inventario y Topología
        inventory, topo_stats = MeshInventoryScanner.scan_inventory(geometry)

        # 2. Evaluación de Reglas
        rule_scores, defects = self.registry.evaluate_all(geometry, ctx, config)

        # 3. Correlación Cruzada con F61 (si existe)
        visual_eval = ctx.get("visual_evaluation")
        correlations = CrossCorrelationEngine.correlate_with_visual_evaluation(visual_eval, defects)

        # 4. Cálculo de Scores por Dimensión
        top_score = rule_scores.get("RULE_TOPOLOGY_MANIFOLD_DEGENERACY", 1.0)
        tf_score = rule_scores.get("RULE_TRANSFORM_SCALE_DIMENSIONS", 1.0)
        norm_score = rule_scores.get("RULE_NORMALS_CONSISTENCY", 1.0)
        dens_score = rule_scores.get("RULE_DENSITY_POLYGON_BUDGET", 1.0)
        col_score = rule_scores.get("RULE_COLLISION_AND_LOD_QA", 1.0)

        overall_score = round((top_score * 0.30 + tf_score * 0.25 + norm_score * 0.20 + dens_score * 0.15 + col_score * 0.10), 4)

        quality_scores = {
            "topology_score": top_score,
            "transform_score": tf_score,
            "normal_score": norm_score,
            "density_score": dens_score,
            "collision_score": col_score,
            "geometry_score": round((top_score + tf_score) / 2.0, 4),
            "uv_score": 1.0,
            "overall_geometry_score": overall_score
        }

        # 5. Determinación de Estado
        if any(d.severity == DefectSeverity.CRITICAL for d in defects) or overall_score < 0.60:
            status = ValidationStatus.FAIL
        elif len(defects) > 0 or overall_score < 0.85:
            status = ValidationStatus.PASS_WITH_WARNINGS
        else:
            status = ValidationStatus.PASS

        # 6. Reporte de Unreal Readiness
        has_col = (getattr(geometry, "collision_geometry", None) is not None) or (getattr(geometry, "collision_mesh", None) is not None)
        unreal_rep = UnrealReadinessReport(
            geometry_ready=(top_score >= 0.85),
            collision_ready=has_col,
            lod_ready=True,
            uv_ready=True,
            transform_ready=(tf_score >= 0.90),
            semantic_ready=True,
            is_export_ready=(status in [ValidationStatus.PASS, ValidationStatus.PASS_WITH_WARNINGS] and has_col)
        )

        # 7. Hints de Corrección
        hints = [d.correction_hint for d in defects if d.correction_hint is not None]

        # 8. Hash Determinista
        val_hash = QAHasher.compute_validation_hash(
            geometry_id=geom_id,
            inventory_dict=inventory.__dict__,
            scores_dict=quality_scores,
            defects=defects,
            status=status.value
        )

        trace = [
            {"step": "SCAN_INVENTORY", "vertices": inventory.vertex_count, "triangles": inventory.triangle_count, "status": "SUCCESS"},
            {"step": "EVALUATE_RULES", "rules_count": len(rule_scores), "defects_count": len(defects), "status": "SUCCESS"},
            {"step": "CORRELATE_F61", "correlations_count": len(correlations), "status": "SUCCESS"}
        ]

        result = GeometricValidationResult(
            validation_id=f"GEOVAL_{geom_id.replace('GEN_', '')}",
            semantic_id=sem_id,
            asset_id=sem_id,
            geometry_id=geom_id,
            mesh_inventory=inventory,
            topology_statistics=topo_stats,
            unreal_readiness=unreal_rep,
            quality_scores=quality_scores,
            defects=defects,
            warnings=[],
            validation_status=status,
            confidence=0.98,
            correction_hints=hints,
            validation_hash=val_hash,
            execution_trace=trace,
            generation_metadata={"engine_version": self.engine_version, "correlations": correlations}
        )

        return result

    def validate_component(
        self,
        component_id: str,
        geometry: Any,
        context: Optional[Dict] = None
    ) -> GeometricValidationResult:
        return self.validate(geometry, context)

    def validate_result(self, result: GeometricValidationResult) -> QAValidationResult:
        errors = []
        warnings = []

        if not result.validation_id:
            errors.append("MISSING_VALIDATION_ID: Validation ID is mandatory.")
        if result.quality_scores.get("overall_geometry_score", 0.0) < 0.0 or result.quality_scores.get("overall_geometry_score", 0.0) > 1.0:
            errors.append("INVALID_SCORE: Overall score out of bounds [0.0, 1.0].")

        for d in result.defects:
            if d.severity == DefectSeverity.CRITICAL:
                warnings.append(f"CRITICAL_DEFECT_DETECTED: {d.defect_id} ({d.category.value})")

        return QAValidationResult(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)

    def compute_hash(self, result: GeometricValidationResult) -> str:
        return QAHasher.compute_validation_hash(
            geometry_id=result.geometry_id,
            inventory_dict=result.mesh_inventory.__dict__,
            scores_dict=result.quality_scores,
            defects=result.defects,
            status=result.validation_status.value
        )
