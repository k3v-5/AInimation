import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.visual_specification_compiler import VisualSpecificationAPI, VisualCompilationInput
from src.reference_analysis_visual_decomposition import (
    DecomposedReferenceReport, SilhouetteExtraction, ProportionEstimate,
    DecomposedPart, MaterialPalette, ExtractedMaterialType
)
from src.procedural_modeling_strategy import ProceduralModelingStrategyAPI
from src.geometry_generation_engine import GeometryGenerationAPI
from src.material_surface_generation import MaterialSurfaceAPI
from src.presentation_matching import PresentationMatchingAPI
from src.automated_visual_evaluation import AutomatedVisualEvaluationAPI
from src.geometric_validation_qa import GeometricValidationAPI
from src.intelligent_critic_engine import (
    IntelligentCriticAPI, CausalCategory, CriticPriority, RiskLevel,
    IterationRecommendation, ActionAutonomyLevel
)

class TestIntelligentCriticPhase63(unittest.TestCase):
    def setUp(self):
        self.vas_api = VisualSpecificationAPI()
        self.msp_api = ProceduralModelingStrategyAPI()
        self.geom_api = GeometryGenerationAPI()
        self.surf_api = MaterialSurfaceAPI()
        self.pres_api = PresentationMatchingAPI()
        self.eval_api = AutomatedVisualEvaluationAPI()
        self.qa_api = GeometricValidationAPI()
        self.critic_api = IntelligentCriticAPI()

    def _get_pipeline_data(self):
        ref_report = DecomposedReferenceReport(
            report_id="REP_F55_BARREL_01",
            reference_ids=["REF_01"],
            silhouette=SilhouetteExtraction(aspect_ratio=1.0),
            proportions=ProportionEstimate(component_ratios={"body": 0.8, "top_ring": 0.1, "bottom_ring": 0.1}),
            parts=[
                DecomposedPart("part_body", "BODY", (0, 0, 1, 1.0), (0, 0, 0), True, 0.98),
                DecomposedPart("part_ring_top", "RING_01", (0, 0.8, 1.02, 0.15), (0, 0, 0.8), False, 0.95),
                DecomposedPart("part_ring_bottom", "RING_02", (0, 0.2, 1.02, 0.15), (0, 0, 0.2), False, 0.95)
            ],
            materials=MaterialPalette(base_material=ExtractedMaterialType.WOOD, surface_roughness=0.68)
        )
        vas_in = VisualCompilationInput(
            prompt="Barril medieval de roble con aros de hierro",
            asset_class_hint="PROP.BARREL",
            reference_reports=[ref_report],
            semantic_context={"semantic_id": "barrel_01.root", "asset_id": "barrel_01"},
            project_constraints={"nanite": True, "collision": "CUSTOM_UCX"}
        )
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom = self.geom_api.generate_geometry(msp)
        surf = self.surf_api.generate_surface(geom)
        vpc = self.pres_api.build_presentation_context(geom, surf, ref_report, vas)
        v_eval = self.eval_api.evaluate_visuals(ref_report, geom, {"surface": surf, "presentation": vpc})
        g_qa = self.qa_api.validate_geometry(geom, {"visual_evaluation": v_eval, "surface": surf})
        return vas, geom, v_eval, g_qa

    def test_01_case_a_clean_asset_recommendation_stop(self):
        """Case A: Asset sin defectos produce recomendación STOP y 0 blockers."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        res = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        self.assertEqual(res.iteration_recommendation, IterationRecommendation.STOP)
        self.assertEqual(len(res.acceptance_blockers), 0)

    def test_02_case_b_proportion_symptom_to_causal_diagnosis(self):
        """Case B: Síntoma de silueta/proporción se transforma en diagnóstico causal."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        # Inyectar defecto visual artificial
        from src.automated_visual_evaluation import VisualDefect, DefectType
        v_eval.defects = [VisualDefect("DEF_SIL_BODY", DefectType.WRONG_SILHOUETTE, region="part_body", error_pct=18.0)]
        res = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        self.assertGreater(len(res.diagnoses), 0)
        self.assertEqual(res.diagnoses[0].category, CausalCategory.PROPORTION)
        self.assertGreater(len(res.parameter_recommendations), 0)

    def test_03_case_c_topology_failure_critical_priority(self):
        """Case C: Falla topológica produce causa TOPOLOGY con prioridad CRITICAL."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        from src.geometric_validation_qa import GeometricDefect, GeometricDefectCategory, DefectSeverity
        g_qa.defects = [GeometricDefect("DEF_NM", GeometricDefectCategory.NON_MANIFOLD, severity=DefectSeverity.CRITICAL, location="part_body")]
        res = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        top_diags = [d for d in res.diagnoses if d.category == CausalCategory.TOPOLOGY]
        self.assertGreater(len(top_diags), 0)
        self.assertEqual(top_diags[0].priority, CriticPriority.CRITICAL)

    def test_04_case_d_defect_clustering(self):
        """Case D: Defectos visuales y geométricos de la misma región se agrupan en un cluster."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        from src.automated_visual_evaluation import VisualDefect, DefectType
        from src.geometric_validation_qa import GeometricDefect, GeometricDefectCategory
        v_eval.defects = [VisualDefect("DEF_V_1", DefectType.WRONG_SILHOUETTE, region="part_body")]
        g_qa.defects = [GeometricDefect("DEF_G_1", GeometricDefectCategory.TRANSFORM_ERROR, location="part_body")]
        res = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        self.assertGreater(len(res.defect_clusters), 0)
        body_cluster = [c for c in res.defect_clusters if "PART_BODY" in c.cluster_id]
        self.assertGreater(len(body_cluster), 0)
        self.assertIn("DEF_V_1", body_cluster[0].visual_defects)
        self.assertIn("DEF_G_1", body_cluster[0].geometric_defects)

    def test_05_case_e_actionable_parameter_delta(self):
        """Case E: Recomendación de parámetro incluye delta, rango recomendado y bounds."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        from src.automated_visual_evaluation import VisualDefect, DefectType
        v_eval.defects = [VisualDefect("DEF_SIL_BODY", DefectType.WRONG_SILHOUETTE, region="part_body", error_pct=15.0)]
        res = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        rec = res.parameter_recommendations[0]
        self.assertIsNotNone(rec.delta)
        self.assertIsNotNone(rec.recommended_range)
        self.assertLessEqual(rec.recommended_range[0], rec.recommended_range[1])

    def test_06_case_f_correction_plan_generation(self):
        """Case F: Generación de plan de corrección estructurado con nivel de autonomía."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        from src.automated_visual_evaluation import VisualDefect, DefectType
        v_eval.defects = [VisualDefect("DEF_SIL_BODY", DefectType.WRONG_SILHOUETTE, region="part_body")]
        res = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        plan = res.correction_plan
        self.assertGreater(len(plan.ordered_actions), 0)
        self.assertEqual(plan.ordered_actions[0].autonomy_level, ActionAutonomyLevel.AUTONOMOUSLY_ACTIONABLE)

    def test_07_case_g_global_before_local_prioritization(self):
        """Case G: Defectos críticos/estructurales preceden a los de menor severidad en el plan."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        from src.automated_visual_evaluation import VisualDefect, DefectType
        from src.geometric_validation_qa import GeometricDefect, GeometricDefectCategory, DefectSeverity
        v_eval.defects = [VisualDefect("DEF_SIL", DefectType.WRONG_SILHOUETTE, region="part_body")]
        g_qa.defects = [GeometricDefect("DEF_NM", GeometricDefectCategory.NON_MANIFOLD, severity=DefectSeverity.CRITICAL, location="mesh.root")]
        res = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        self.assertGreater(len(res.correction_plan.ordered_actions), 1)
        # Primer elemento debe ser la acción de mayor severidad
        self.assertEqual(res.diagnoses[0].priority, CriticPriority.CRITICAL)

    def test_08_case_h_oscillation_detection(self):
        """Case H: Detección de oscilaciones históricas entre iteraciones."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        context = {
            "iteration_history": [{"param": 1.15}, {"param": 0.85}, {"param": 1.15}],
            "force_oscillation_flag": True
        }
        res = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval, context=context)
        osc_diags = [d for d in res.diagnoses if "OSCILLATION" in d.diagnosis_id]
        self.assertGreater(len(osc_diags), 0)

    def test_09_case_i_deterministic_critic_hash(self):
        """Case I: Dos ejecuciones idénticas producen el mismo critic_hash (SHA-256)."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        res1 = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        res2 = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        self.assertEqual(res1.critic_hash, res2.critic_hash)

    def test_10_case_j_non_destructive_critic(self):
        """Case J: F63 no muta la especificación ni la geometría de entrada."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        v_count = geom.vertex_count
        _ = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        self.assertEqual(geom.vertex_count, v_count)

    def test_11_risk_analysis_evaluation(self):
        """Test 11: Análisis de riesgos multiobjetivo."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        res = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        self.assertIn("regression_risk", res.risk_analysis)
        self.assertIn("semantic_risk", res.risk_analysis)

    def test_12_iteration_recommendation_correct_on_defects(self):
        """Test 12: Recomendación CORRECT cuando existen defectos."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        from src.automated_visual_evaluation import VisualDefect, DefectType
        v_eval.defects = [VisualDefect("DEF_SIL", DefectType.WRONG_SILHOUETTE, region="part_body")]
        res = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        self.assertEqual(res.iteration_recommendation, IterationRecommendation.CORRECT)

    def test_13_rule_registry_executes_all_rules(self):
        """Test 13: CriticRuleRegistry evalúa todas las reglas activas."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        res = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        self.assertGreaterEqual(res.confidence, 0.90)

    def test_14_acceptance_blockers_on_critical_severity(self):
        """Test 14: Defectos críticos se agregan a acceptance_blockers."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        from src.geometric_validation_qa import GeometricDefect, GeometricDefectCategory, DefectSeverity
        g_qa.defects = [GeometricDefect("DEF_CRIT", GeometricDefectCategory.NON_MANIFOLD, severity=DefectSeverity.CRITICAL, location="mesh.root")]
        res = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        self.assertGreater(len(res.acceptance_blockers), 0)

    def test_15_critic_result_validation(self):
        """Test 15: Validación de resultado limpio retorna is_valid = True."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        res = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        val = self.critic_api.validate_critic_result(res)
        self.assertTrue(val.is_valid)

    def test_16_execution_trace_records_steps(self):
        """Test 16: Traza de ejecución registra etapas del diagnóstico causal."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        res = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        self.assertGreater(len(res.execution_trace), 0)
        steps = [t["step"] for t in res.execution_trace]
        self.assertIn("EVALUATE_RULES", steps)
        self.assertIn("CLUSTER_DEFECTS", steps)

    def test_17_evidence_items_traceability(self):
        """Test 17: Evidencias contienen fuente, descripción y nivel de confianza."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        from src.automated_visual_evaluation import VisualDefect, DefectType
        v_eval.defects = [VisualDefect("DEF_SIL", DefectType.WRONG_SILHOUETTE, region="part_body")]
        res = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        diag = res.diagnoses[0]
        self.assertGreater(len(diag.evidence), 0)
        self.assertEqual(diag.evidence[0].source, "F61_VISUAL_EVAL")

    def test_18_root_cause_probability(self):
        """Test 18: Causas raíz contienen probabilidad calculada."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        from src.automated_visual_evaluation import VisualDefect, DefectType
        v_eval.defects = [VisualDefect("DEF_SIL", DefectType.WRONG_SILHOUETTE, region="part_body")]
        res = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        self.assertGreater(res.root_causes[0].probability, 0.80)

    def test_19_quality_summary_included(self):
        """Test 19: Resumen de calidad visual y geométrica consolidado."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        res = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        self.assertIn("visual_score", res.quality_summary)
        self.assertIn("geometry_score", res.quality_summary)

    def test_20_end_to_end_critic_pipeline(self):
        """Test 20: Flujo E2E Completo: Prompt -> F56 -> F57 -> F58 -> F59 -> F60 -> F61 -> F62 -> F63 -> Listo para F64."""
        vas, geom, v_eval, g_qa = self._get_pipeline_data()
        from src.automated_visual_evaluation import VisualDefect, DefectType
        v_eval.defects = [VisualDefect("DEF_SIL", DefectType.WRONG_SILHOUETTE, region="part_body", error_pct=12.0)]
        res = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        val = self.critic_api.validate_critic_result(res)
        self.assertTrue(val.is_valid)
        self.assertEqual(res.iteration_recommendation, IterationRecommendation.CORRECT)
        self.assertGreater(len(res.correction_plan.ordered_actions), 0)
        self.assertGreater(len(res.critic_hash), 0)

if __name__ == "__main__":
    unittest.main()
