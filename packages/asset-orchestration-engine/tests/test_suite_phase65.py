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
from src.iterative_generation_loop import (
    IterativeGenerationLoopAPI, IterativeGenerationRequest, IterationLoopConfiguration,
    LoopState, StopReason, IterationTargets
)

class TestIterativeGenerationLoopPhase65(unittest.TestCase):
    def setUp(self):
        self.vas_api = VisualSpecificationAPI()
        self.msp_api = ProceduralModelingStrategyAPI()
        self.geom_api = GeometryGenerationAPI()
        self.surf_api = MaterialSurfaceAPI()
        self.pres_api = PresentationMatchingAPI()
        self.loop_api = IterativeGenerationLoopAPI()

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
        return ref_report, vas, geom, surf, vpc

    def test_01_case_a_clean_asset_convergence(self):
        """Case A: Asset limpio alcanza target en iteración 0 y finaliza como CONVERGED."""
        ref, vas, geom, surf, vpc = self._get_pipeline_data()
        req = IterativeGenerationRequest(
            job_id="JOB_01", asset_id="barrel_01", semantic_id="barrel_01.root",
            reference_report=ref, vas=vas,
            configuration=IterationLoopConfiguration(targets=IterationTargets(overall_target_score=0.90))
        )
        res = self.loop_api.execute_iterative_loop(req, geom, surf, vpc)
        self.assertEqual(res.status, LoopState.CONVERGED)
        self.assertEqual(res.stop_reason, StopReason.CONVERGENCE_REACHED)

    def test_02_case_b_stagnation_detection(self):
        """Case C: Detección de estancamiento tras ventana sin mejora."""
        ref, vas, geom, surf, vpc = self._get_pipeline_data()
        config = IterationLoopConfiguration(
            targets=IterationTargets(overall_target_score=0.999), # Inalcanzable para forzar estancamiento
            stagnation_window=2,
            minimum_improvement=0.50 # Mejora mínima imposible
        )
        req = IterativeGenerationRequest("JOB_02", "barrel_01", "barrel_01.root", ref, vas, config)
        res = self.loop_api.execute_iterative_loop(req, geom, surf, vpc)
        self.assertEqual(res.stop_reason, StopReason.STAGNATION_DETECTED)

    def test_03_case_c_budget_exhaustion(self):
        """Case E: Agotamiento de presupuesto al alcanzar max_iterations."""
        ref, vas, geom, surf, vpc = self._get_pipeline_data()
        config = IterationLoopConfiguration(
            max_iterations=1,
            targets=IterationTargets(overall_target_score=0.999),
            stagnation_window=10 # Deshabilitar estancamiento
        )
        req = IterativeGenerationRequest("JOB_03", "barrel_01", "barrel_01.root", ref, vas, config)
        res = self.loop_api.execute_iterative_loop(req, geom, surf, vpc)
        self.assertEqual(res.status, LoopState.BUDGET_EXHAUSTED)
        self.assertEqual(res.stop_reason, StopReason.MAX_ITERATIONS_REACHED)

    def test_04_case_d_checkpoint_and_resume(self):
        """Case H: Guardado de checkpoint y reanudación mediante resume_loop."""
        ref, vas, geom, surf, vpc = self._get_pipeline_data()
        req = IterativeGenerationRequest("JOB_04", "barrel_01", "barrel_01.root", ref, vas)
        res = self.loop_api.execute_iterative_loop(req, geom, surf, vpc)
        cp = self.loop_api.resume_loop(res.loop_id)
        self.assertIsNotNone(cp)
        self.assertEqual(cp["iteration_number"], res.accepted_iteration)

    def test_05_case_e_deterministic_loop_hash(self):
        """Case I: Dos ejecuciones idénticas producen el mismo loop_hash (SHA-256)."""
        ref, vas, geom, surf, vpc = self._get_pipeline_data()
        req = IterativeGenerationRequest("JOB_05", "barrel_01", "barrel_01.root", ref, vas)
        res1 = self.loop_api.execute_iterative_loop(req, geom, surf, vpc)
        res2 = self.loop_api.execute_iterative_loop(req, geom, surf, vpc)
        self.assertEqual(res1.loop_hash, res2.loop_hash)

    def test_06_case_f_best_state_tracking(self):
        """Case G: BestStateTracker preserva la iteración óptima."""
        ref, vas, geom, surf, vpc = self._get_pipeline_data()
        req = IterativeGenerationRequest("JOB_06", "barrel_01", "barrel_01.root", ref, vas)
        res = self.loop_api.execute_iterative_loop(req, geom, surf, vpc)
        self.assertGreaterEqual(res.best_iteration, 0)
        self.assertGreaterEqual(res.final_quality, res.initial_quality)

    def test_07_case_g_hard_constraints_priority(self):
        """Case F: Restricciones críticas de topología impiden convergencia."""
        ref, vas, geom, surf, vpc = self._get_pipeline_data()
        # Inyectar fallo no manifold
        geom.topology_summary.is_manifold = False
        config = IterationLoopConfiguration(
            max_iterations=1,
            targets=IterationTargets(overall_target_score=0.50) # Bajo score pero restricción crítica
        )
        req = IterativeGenerationRequest("JOB_07", "barrel_01", "barrel_01.root", ref, vas, config)
        res = self.loop_api.execute_iterative_loop(req, geom, surf, vpc)
        self.assertNotEqual(res.status, LoopState.CONVERGED)

    def test_08_case_h_non_destructive_loop(self):
        """Case J: El loop no muta la especificación de entrada VAS."""
        ref, vas, geom, surf, vpc = self._get_pipeline_data()
        spec_id_before = vas.specification_id
        req = IterativeGenerationRequest("JOB_08", "barrel_01", "barrel_01.root", ref, vas)
        _ = self.loop_api.execute_iterative_loop(req, geom, surf, vpc)
        self.assertEqual(vas.specification_id, spec_id_before)

    def test_09_iteration_history_tracking(self):
        """Test 09: Historial completo de iteraciones registrado."""
        ref, vas, geom, surf, vpc = self._get_pipeline_data()
        req = IterativeGenerationRequest("JOB_09", "barrel_01", "barrel_01.root", ref, vas)
        res = self.loop_api.execute_iterative_loop(req, geom, surf, vpc)
        self.assertGreater(len(res.iteration_history), 0)
        self.assertEqual(res.iteration_history[0].iteration_number, 0)

    def test_10_quality_delta_calculation(self):
        """Test 10: Cálculo del delta de calidad final vs inicial."""
        ref, vas, geom, surf, vpc = self._get_pipeline_data()
        req = IterativeGenerationRequest("JOB_10", "barrel_01", "barrel_01.root", ref, vas)
        res = self.loop_api.execute_iterative_loop(req, geom, surf, vpc)
        self.assertIsNotNone(res.quality_delta)

    def test_11_validation_clean_result(self):
        """Test 11: Validación de resultado limpio retorna is_valid = True."""
        ref, vas, geom, surf, vpc = self._get_pipeline_data()
        req = IterativeGenerationRequest("JOB_11", "barrel_01", "barrel_01.root", ref, vas)
        res = self.loop_api.execute_iterative_loop(req, geom, surf, vpc)
        val = self.loop_api.validate_loop_result(res)
        self.assertTrue(val.is_valid)

    def test_12_execution_trace_records_steps(self):
        """Test 12: Traza de ejecución registra etapas y decisiones."""
        ref, vas, geom, surf, vpc = self._get_pipeline_data()
        req = IterativeGenerationRequest("JOB_12", "barrel_01", "barrel_01.root", ref, vas)
        res = self.loop_api.execute_iterative_loop(req, geom, surf, vpc)
        self.assertGreater(len(res.execution_trace), 0)
        self.assertIn("overall_score", res.execution_trace[0])

    def test_13_target_thresholds_customization(self):
        """Test 13: Configuración personalizada de targets de iteración."""
        targets = IterationTargets(overall_target_score=0.95, minimum_visual_score=0.92)
        config = IterationLoopConfiguration(targets=targets)
        self.assertEqual(config.targets.overall_target_score, 0.95)

    def test_14_preservation_of_ids(self):
        """Test 14: Preservación de asset_id y semantic_id en el resultado."""
        ref, vas, geom, surf, vpc = self._get_pipeline_data()
        req = IterativeGenerationRequest("JOB_14", "barrel_01", "barrel_01.root", ref, vas)
        res = self.loop_api.execute_iterative_loop(req, geom, surf, vpc)
        self.assertEqual(res.asset_id, "barrel_01")
        self.assertEqual(res.semantic_id, "barrel_01.root")

    def test_15_f61_visual_evaluation_integrated(self):
        """Test 15: Integración verificada con F61 Visual Evaluation."""
        ref, vas, geom, surf, vpc = self._get_pipeline_data()
        req = IterativeGenerationRequest("JOB_15", "barrel_01", "barrel_01.root", ref, vas)
        res = self.loop_api.execute_iterative_loop(req, geom, surf, vpc)
        self.assertGreater(res.iteration_history[0].visual_score, 0.0)

    def test_16_f62_geometry_qa_integrated(self):
        """Test 16: Integración verificada con F62 Geometry Validation QA."""
        ref, vas, geom, surf, vpc = self._get_pipeline_data()
        req = IterativeGenerationRequest("JOB_16", "barrel_01", "barrel_01.root", ref, vas)
        res = self.loop_api.execute_iterative_loop(req, geom, surf, vpc)
        self.assertGreater(res.iteration_history[0].geometry_score, 0.0)

    def test_17_f63_critic_and_f64_correction_flow(self):
        """Test 17: Integración con F63 y F64 cuando se requiere corrección."""
        ref, vas, geom, surf, vpc = self._get_pipeline_data()
        # Modificar silueta de referencia para provocar ciclo correctivo
        ref.silhouette.aspect_ratio = 1.40
        config = IterationLoopConfiguration(
            max_iterations=2,
            targets=IterationTargets(overall_target_score=0.999),
            stagnation_window=5
        )
        req = IterativeGenerationRequest("JOB_17", "barrel_01", "barrel_01.root", ref, vas, config)
        res = self.loop_api.execute_iterative_loop(req, geom, surf, vpc)
        self.assertGreaterEqual(res.iterations_executed, 2)

    def test_18_iteration_numbering_uniqueness(self):
        """Test 18: Numeración secuencial y única de iteraciones."""
        ref, vas, geom, surf, vpc = self._get_pipeline_data()
        config = IterationLoopConfiguration(max_iterations=2, stagnation_window=10, targets=IterationTargets(overall_target_score=0.999))
        req = IterativeGenerationRequest("JOB_18", "barrel_01", "barrel_01.root", ref, vas, config)
        res = self.loop_api.execute_iterative_loop(req, geom, surf, vpc)
        nums = [h.iteration_number for h in res.iteration_history]
        self.assertEqual(nums, list(range(len(nums))))

    def test_19_stop_reason_types(self):
        """Test 19: Tipos válidos de StopReason."""
        self.assertEqual(StopReason.CONVERGENCE_REACHED.value, "CONVERGENCE_REACHED")
        self.assertEqual(StopReason.MAX_ITERATIONS_REACHED.value, "MAX_ITERATIONS_REACHED")

    def test_20_end_to_end_closed_loop_pipeline(self):
        """Test 20: Flujo E2E Completo: Prompt -> F56 -> F57 -> F58 -> F59 -> F60 -> F61 -> F62 -> F63 -> F64 -> F65 -> Listo para F66."""
        ref, vas, geom, surf, vpc = self._get_pipeline_data()
        req = IterativeGenerationRequest("JOB_20", "barrel_01", "barrel_01.root", ref, vas)
        res = self.loop_api.execute_iterative_loop(req, geom, surf, vpc)
        val = self.loop_api.validate_loop_result(res)
        self.assertTrue(val.is_valid)
        self.assertGreater(len(res.final_state_hash), 0)
        self.assertGreater(len(res.loop_hash), 0)
        self.assertEqual(res.status, LoopState.CONVERGED)

if __name__ == "__main__":
    unittest.main()
