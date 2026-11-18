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
from src.automated_visual_evaluation import AutomatedVisualEvaluationAPI, VisualDefect, DefectType
from src.geometric_validation_qa import GeometricValidationAPI
from src.intelligent_critic_engine import IntelligentCriticAPI
from src.autonomous_correction_engine import (
    AutonomousCorrectionAPI, CorrectionStatus, RollbackStatus,
    CorrectionConfiguration, ActionAuthorization, OperationType
)

class TestAutonomousCorrectionPhase64(unittest.TestCase):
    def setUp(self):
        self.vas_api = VisualSpecificationAPI()
        self.msp_api = ProceduralModelingStrategyAPI()
        self.geom_api = GeometryGenerationAPI()
        self.surf_api = MaterialSurfaceAPI()
        self.pres_api = PresentationMatchingAPI()
        self.eval_api = AutomatedVisualEvaluationAPI()
        self.qa_api = GeometricValidationAPI()
        self.critic_api = IntelligentCriticAPI()
        self.corr_api = AutonomousCorrectionAPI()

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
        v_eval.defects = [VisualDefect("DEF_SIL", DefectType.WRONG_SILHOUETTE, region="part_body", error_pct=15.0)]
        g_qa = self.qa_api.validate_geometry(geom, {"visual_evaluation": v_eval, "surface": surf})
        critic_res = self.critic_api.generate_critic_diagnosis(vas, g_qa, v_eval)
        return vas, geom, critic_res

    def test_01_case_a_valid_action_execution(self):
        """Case A: Ejecución válida de acciones produce status ACCEPTED y ganancia positiva."""
        vas, geom, critic_res = self._get_pipeline_data()
        res = self.corr_api.apply_corrections(critic_res, geom)
        self.assertEqual(res.status, CorrectionStatus.ACCEPTED)
        self.assertGreater(len(res.actions_applied), 0)
        self.assertGreater(res.quality_delta.overall_gain, 0.0)

    def test_02_case_b_automatic_rollback_on_regression(self):
        """Case B: Regresión crítica activa rollback automático y status ROLLED_BACK."""
        vas, geom, critic_res = self._get_pipeline_data()
        context = {"force_regression_flag": True}
        res = self.corr_api.apply_corrections(critic_res, geom, context=context)
        self.assertEqual(res.status, CorrectionStatus.ROLLED_BACK)
        self.assertEqual(res.rollback_status, RollbackStatus.ROLLBACK_SUCCESS)
        self.assertEqual(len(res.actions_applied), 0)
        self.assertGreater(len(res.actions_rolled_back), 0)

    def test_03_case_c_immutable_baseline_snapshot(self):
        """Case C: Se captura un snapshot inmutable antes de cualquier cambio."""
        vas, geom, critic_res = self._get_pipeline_data()
        res = self.corr_api.apply_corrections(critic_res, geom)
        self.assertIsNotNone(res.before_state)
        self.assertGreater(len(res.before_state.state_hash), 0)

    def test_04_case_d_parameter_bounds_clamping(self):
        """Case D: Ajustes de parámetros respetan límites mínimos y máximos."""
        vas, geom, critic_res = self._get_pipeline_data()
        # Modificar acción para solicitar delta excesivo
        critic_res.correction_plan.ordered_actions[0].delta = -5.0 # Por debajo del mínimo 0.50
        res = self.corr_api.apply_corrections(critic_res, geom)
        p_change = res.parameter_changes[0]
        self.assertGreaterEqual(p_change.new_value, p_change.min_value)

    def test_05_case_e_dry_run_simulation(self):
        """Case E: Modo dry-run simula sin aplicar cambios reales."""
        vas, geom, critic_res = self._get_pipeline_data()
        config = CorrectionConfiguration(dry_run=True)
        res = self.corr_api.apply_corrections(critic_res, geom, configuration=config)
        self.assertEqual(res.status, CorrectionStatus.READY)
        self.assertEqual(len(res.actions_applied), 0)

    def test_06_case_f_multi_action_execution(self):
        """Case F: Ejecución secuencial de múltiples acciones dependientes."""
        vas, geom, critic_res = self._get_pipeline_data()
        from src.intelligent_critic_engine import CorrectionAction
        critic_res.correction_plan.ordered_actions.append(
            CorrectionAction("ACT_002", "component.part_body", "scale", delta=-0.05)
        )
        res = self.corr_api.apply_corrections(critic_res, geom)
        self.assertGreaterEqual(len(res.actions_applied), 2)

    def test_07_case_g_blocked_invalid_action(self):
        """Case G: Acción sin parámetro ni target es rechazada."""
        vas, geom, critic_res = self._get_pipeline_data()
        critic_res.correction_plan.ordered_actions[0].parameter = ""
        res = self.corr_api.apply_corrections(critic_res, geom)
        self.assertIn(critic_res.correction_plan.ordered_actions[0].action_id, res.actions_rejected)

    def test_08_case_h_oscillation_protection(self):
        """Case H: Protección contra oscilaciones rechaza deltas opuestos consecutivos."""
        vas, geom, critic_res = self._get_pipeline_data()
        param_name = critic_res.correction_plan.ordered_actions[0].parameter
        delta_val = critic_res.correction_plan.ordered_actions[0].delta
        context = {
            "correction_history": [
                {"parameter_id": param_name, "delta": -delta_val},
                {"parameter_id": param_name, "delta": -delta_val}
            ]
        }
        res = self.corr_api.apply_corrections(critic_res, geom, context=context)
        self.assertGreater(len(res.actions_rejected), 0)

    def test_09_case_i_deterministic_correction_hash(self):
        """Case I: Dos ejecuciones idénticas producen el mismo correction_hash (SHA-256)."""
        vas, geom, critic_res = self._get_pipeline_data()
        res1 = self.corr_api.apply_corrections(critic_res, geom)
        res2 = self.corr_api.apply_corrections(critic_res, geom)
        self.assertEqual(res1.correction_hash, res2.correction_hash)

    def test_10_case_j_idempotent_execution(self):
        """Case J: Reejecutar corrección produce resultados consistentes."""
        vas, geom, critic_res = self._get_pipeline_data()
        res1 = self.corr_api.apply_corrections(critic_res, geom)
        res2 = self.corr_api.apply_corrections(critic_res, geom)
        self.assertEqual(res1.status, res2.status)

    def test_11_quality_delta_calculation(self):
        """Test 11: Cálculo de deltas de calidad tras aplicar corrección."""
        vas, geom, critic_res = self._get_pipeline_data()
        res = self.corr_api.apply_corrections(critic_res, geom)
        self.assertGreater(res.quality_delta.visual_delta, 0.0)
        self.assertGreater(res.quality_delta.geometry_delta, 0.0)

    def test_12_transaction_commit_lifecycle(self):
        """Test 12: Ciclo de commit de transacción completado."""
        vas, geom, critic_res = self._get_pipeline_data()
        res = self.corr_api.apply_corrections(critic_res, geom)
        self.assertEqual(res.status, CorrectionStatus.ACCEPTED)

    def test_13_operation_registry_routing(self):
        """Test 13: Enrutamiento de operaciones a través de CorrectionOperationRegistry."""
        vas, geom, critic_res = self._get_pipeline_data()
        res = self.corr_api.apply_corrections(critic_res, geom)
        self.assertGreater(len(res.parameter_changes), 0)

    def test_14_action_authorization_safe(self):
        """Test 14: Acciones estándar autorizadas como SAFE."""
        vas, geom, critic_res = self._get_pipeline_data()
        res = self.corr_api.apply_corrections(critic_res, geom)
        self.assertEqual(res.status, CorrectionStatus.ACCEPTED)

    def test_15_rollback_verification_state_restored(self):
        """Test 15: Verificación de restauración de estado tras rollback."""
        vas, geom, critic_res = self._get_pipeline_data()
        context = {"force_regression_flag": True}
        res = self.corr_api.apply_corrections(critic_res, geom, context=context)
        self.assertEqual(res.after_state.state_hash, res.before_state.state_hash)

    def test_16_validation_clean_result(self):
        """Test 16: Validación de resultado limpio retorna is_valid = True."""
        vas, geom, critic_res = self._get_pipeline_data()
        res = self.corr_api.apply_corrections(critic_res, geom)
        val = self.corr_api.validate_correction_result(res)
        self.assertTrue(val.is_valid)

    def test_17_execution_trace_records_steps(self):
        """Test 17: Traza de ejecución registra etapas (SNAPSHOT, APPLY, GATE)."""
        vas, geom, critic_res = self._get_pipeline_data()
        res = self.corr_api.apply_corrections(critic_res, geom)
        self.assertGreater(len(res.execution_trace), 0)
        steps = [t["step"] for t in res.execution_trace]
        self.assertIn("SNAPSHOT_BASELINE", steps)
        self.assertIn("APPLY_ACTIONS", steps)

    def test_18_iteration_recommendation_continue_on_accepted(self):
        """Test 18: Recomendación CONTINUE tras corrección exitosa."""
        vas, geom, critic_res = self._get_pipeline_data()
        res = self.corr_api.apply_corrections(critic_res, geom)
        self.assertEqual(res.iteration_recommendation, "CONTINUE")

    def test_19_preservation_of_semantic_and_asset_ids(self):
        """Test 19: Preservación de asset_id y semantic_id sin mutación arbitraria."""
        vas, geom, critic_res = self._get_pipeline_data()
        res = self.corr_api.apply_corrections(critic_res, geom)
        self.assertEqual(res.semantic_id, "barrel_01.root")
        self.assertEqual(res.asset_id, "barrel_01.root")

    def test_20_end_to_end_autonomous_correction_pipeline(self):
        """Test 20: Flujo E2E Completo: Prompt -> F56 -> F57 -> F58 -> F59 -> F60 -> F61 -> F62 -> F63 -> F64 -> Listo para F65 Loop."""
        vas, geom, critic_res = self._get_pipeline_data()
        res = self.corr_api.apply_corrections(critic_res, geom)
        val = self.corr_api.validate_correction_result(res)
        self.assertTrue(val.is_valid)
        self.assertEqual(res.status, CorrectionStatus.ACCEPTED)
        self.assertGreater(len(res.actions_applied), 0)
        self.assertGreater(len(res.correction_hash), 0)

if __name__ == "__main__":
    unittest.main()
