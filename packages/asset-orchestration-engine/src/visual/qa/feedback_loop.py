from typing import Dict, Any, List, Optional
from ..capture.camera_manager import ViewOrientation
from ..capture.camera_normalizer import CameraNormalizer
from ..capture.render_capture import RenderCapture
from ..reference.reference_metadata import VisualReference
from ..comparison.silhouette_comparator import SilhouetteComparator
from ..comparison.dimension_comparator import DimensionComparator
from ..perception.feature_analyzer import FeatureAnalyzer
from ..diagnosis.difference_detector import DifferenceDetector
from ..diagnosis.correction_mapper import CorrectionMapper, CorrectionProposal
from .quality_gate import QualityGate, QualityStatus
from .threshold_manager import ThresholdManager, QualityProfile
from .report_generator import ReportGenerator
from ...geometry.core.geometry_engine import GeometryEngine

class VisualFeedbackLoop:
    def __init__(self, geometry_engine: GeometryEngine, profile: Optional[QualityProfile] = None):
        self.geo_engine = geometry_engine
        self.profile = profile or ThresholdManager.get_profile("GAME_ASSET")

    def run_qa_cycle(
        self,
        asset_id: str,
        reference: VisualReference,
        auto_correct: bool = False,
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """
        Ejecuta el ciclo de Visual QA con corrección paramétrica automática y protección anti-loop.
        """
        history_proposals: List[List[Dict[str, Any]]] = []
        iteration_scores: List[float] = []

        for iteration in range(1, max_iterations + 1):
            # 1. Obtener componentes del GeometryEngine
            comps = self.geo_engine.registry.list_components(asset_id)
            if not comps:
                return {"success": False, "error_code": "ASSET_NOT_FOUND", "message": f"Asset '{asset_id}' has no components in GeometryEngine."}

            comp_geos = {c.component_id: c.geometry for c in comps if c.geometry}
            act_dims = {c.component_id: {"width": c.geometry.dimensions[0], "depth": c.geometry.dimensions[1], "height": c.geometry.dimensions[2]} for c in comps if c.geometry}
            act_comp_ids = [c.component_id for c in comps]

            # 2. Capturar Vistas Ortográficas Normalizadas
            # Calcular bounds globales
            total_w = sum(c.geometry.dimensions[0] for c in comps if c.geometry)
            total_h = sum(c.geometry.dimensions[2] for c in comps if c.geometry)
            cam = CameraNormalizer.get_normalized_camera(ViewOrientation.FRONT, (total_w, 0.5, total_h))
            captured_view = RenderCapture.capture_projected_view(comp_geos, cam)

            # 3. Comparar Silueta, Dimensiones y Estructura
            ref_front = reference.views.get(ViewOrientation.FRONT)
            if ref_front and ref_front.grid_occupancy:
                sil_score = SilhouetteComparator.calculate_iou(captured_view.occupancy_grid, ref_front.grid_occupancy)
            else:
                sil_score = 1.0 # Si no hay grid específico en spec, default 1.0

            dim_deltas = DimensionComparator.compare_component_dimensions(act_dims, reference.expected_dimensions, self.profile.dimension_tolerance)
            dim_score = 1.0 if not dim_deltas else max(0.0, 1.0 - (len(dim_deltas) * 0.15))

            struct_features = FeatureAnalyzer.analyze_structural_features(act_comp_ids, reference.expected_structure)
            struct_score = struct_features["structural_completeness"]

            # 4. Evaluar Quality Gate
            status, quality_score = QualityGate.evaluate(
                silhouette_score=sil_score,
                dimension_score=dim_score,
                structural_score=struct_score,
                weights=self.profile.weights,
                pass_threshold=self.profile.pass_threshold
            )
            iteration_scores.append(quality_score)

            # 5. Detectar Diferencias y Mapear Correcciones
            differences = DifferenceDetector.detect_differences(dim_deltas, struct_features, sil_score, self.profile.silhouette_threshold)
            corrections = CorrectionMapper.map_differences_to_corrections(differences)

            # Si ya cumple o no hay auto-corrección -> Retornar reporte
            if status == QualityStatus.PASS or not auto_correct or not corrections:
                unaffected = [c.component_id for c in comps if c.component_id not in [d.target_component for d in differences]]
                report = ReportGenerator.generate_json_report(
                    asset_id, status, quality_score, sil_score, dim_score, struct_score, differences, corrections, unaffected
                )
                report["iterations"] = iteration
                return report

            # 6. Detección Anti-Loop
            current_prop_dicts = [{"target": c.target_component, "param": c.parameter, "val": c.value} for c in corrections]
            if current_prop_dicts in history_proposals:
                # Detectado bucle de corrección repetitivo
                unaffected = [c.component_id for c in comps if c.component_id not in [d.target_component for d in differences]]
                report = ReportGenerator.generate_json_report(
                    asset_id, QualityStatus.FAIL, quality_score, sil_score, dim_score, struct_score, differences, corrections, unaffected
                )
                report["error_code"] = "CORRECTION_LOOP"
                report["message"] = "Correction loop detected: proposed changes oscillate between previous states."
                report["iterations"] = iteration
                return report

            history_proposals.append(current_prop_dicts)

            # 7. Aplicar Propuesta Paramétrica Quirúrgica (Sin Reconstruir Asset Completo)
            for prop in corrections:
                self.geo_engine.modify_component(
                    component_id=prop.target_component,
                    parameter_or_changes=prop.parameter,
                    operation=prop.operation,
                    value=prop.value
                )

            # 8. Comprobar que no haya degradado el score respecto a la iteración previa
            if len(iteration_scores) > 1 and quality_score < iteration_scores[-2]:
                # Degradación detectada -> Rollback y parada
                report = ReportGenerator.generate_json_report(
                    asset_id, QualityStatus.FAIL, quality_score, sil_score, dim_score, struct_score, differences, corrections, []
                )
                report["error_code"] = "ROLLBACK"
                report["message"] = "Proposed correction degraded visual quality score; rolling back."
                report["iterations"] = iteration
                return report

        # Finalización por límite de iteraciones
        unaffected = [c.component_id for c in comps if c.component_id not in [d.target_component for d in differences]]
        report = ReportGenerator.generate_json_report(
            asset_id, status, quality_score, sil_score, dim_score, struct_score, differences, corrections, unaffected
        )
        report["iterations"] = max_iterations
        return report
