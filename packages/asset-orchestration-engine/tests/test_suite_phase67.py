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
from src.quality_scoring_acceptance import QualityScoringAPI
from src.asset_optimization_engine import (
    AssetOptimizationAPI, OptimizationProfile, OptimizationCandidate,
    AssetCost, TargetPlatform, StrategyType, CandidateManager
)

class TestAssetOptimizationPhase67(unittest.TestCase):
    def setUp(self):
        self.vas_api = VisualSpecificationAPI()
        self.msp_api = ProceduralModelingStrategyAPI()
        self.geom_api = GeometryGenerationAPI()
        self.surf_api = MaterialSurfaceAPI()
        self.pres_api = PresentationMatchingAPI()
        self.eval_api = AutomatedVisualEvaluationAPI()
        self.qa_api = GeometricValidationAPI()
        self.scoring_api = QualityScoringAPI()
        self.opt_api = AssetOptimizationAPI()

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
        q_res = self.scoring_api.evaluate_asset_quality("barrel_01", "barrel_01.root", v_eval, g_qa)
        return geom, surf, q_res

    def test_01_case_a_valid_optimization_execution(self):
        """Case A: Optimización válida reduce coste preservando calidad (status ACCEPTED)."""
        geom, surf, q_res = self._get_pipeline_data()
        res = self.opt_api.optimize_game_asset("barrel_01", "barrel_01.root", geom, surf, q_res)
        self.assertEqual(res.optimization_status, "ACCEPTED")
        self.assertLess(res.optimized_cost.total_cost_index, res.baseline_cost.total_cost_index)

    def test_02_case_b_excessive_visual_loss_rejection(self):
        """Case B: Candidato con pérdida visual superior al límite es rechazado."""
        prof = OptimizationProfile(visual_degradation_limit=0.02) # max 2%
        cand = OptimizationCandidate(
            candidate_id="CAND_BAD", parent_state_hash="H1", state_hash="H2",
            strategy_type=StrategyType.MESH_SIMPLIFICATION,
            visual_delta=-0.10, performance_delta=0.50 # 10% de pérdida visual
        )
        accepted = CandidateManager.evaluate_candidate(cand, prof)
        self.assertFalse(accepted)
        self.assertIn("EXCESSIVE_VISUAL_LOSS", cand.rejection_reason)

    def test_03_case_c_zero_gain_rejection(self):
        """Case C: Candidato que degrada calidad sin ganancia de rendimiento es rechazado."""
        prof = OptimizationProfile()
        cand = OptimizationCandidate(
            candidate_id="CAND_ZERO", parent_state_hash="H1", state_hash="H2",
            strategy_type=StrategyType.MESH_SIMPLIFICATION,
            visual_delta=-0.01, performance_delta=0.0, memory_delta=0.0
        )
        accepted = CandidateManager.evaluate_candidate(cand, prof)
        self.assertFalse(accepted)
        self.assertIn("ZERO_GAIN_REJECTION", cand.rejection_reason)

    def test_04_case_d_immutable_baseline_preservation(self):
        """Case D: El baseline permanece inmutable antes y después de optimizar."""
        geom, surf, q_res = self._get_pipeline_data()
        res = self.opt_api.optimize_game_asset("barrel_01", "barrel_01.root", geom, surf, q_res)
        self.assertGreater(res.baseline_cost.triangle_count, 0)
        self.assertGreaterEqual(res.baseline_cost.total_cost_index, res.optimized_cost.total_cost_index)

    def test_05_case_e_mesh_simplification_strategy(self):
        """Case E: Estrategia de simplificación de malla reduce polígonos."""
        from src.asset_optimization_engine.strategies.mesh_simplification_strategy import MeshSimplificationStrategy
        strat = MeshSimplificationStrategy()
        cost = AssetCost(triangle_count=1000, vertex_count=600, total_cost_index=500.0)
        cand = strat.execute_optimization(None, cost, {})
        self.assertLess(cand.cost_after.triangle_count, cost.triangle_count)

    def test_06_case_f_material_optimization_strategy(self):
        """Case F: Estrategia de materiales consolida slots redundantes."""
        from src.asset_optimization_engine.strategies.material_optimization_strategy import MaterialOptimizationStrategy
        strat = MaterialOptimizationStrategy()
        cost = AssetCost(material_count=4, estimated_draw_calls=4, total_cost_index=100.0)
        cand = strat.execute_optimization(None, cost, {})
        self.assertLess(cand.cost_after.material_count, cost.material_count)

    def test_07_case_g_texture_optimization_strategy(self):
        """Case G: Estrategia de texturas reduce consumo de memoria VRAM."""
        from src.asset_optimization_engine.strategies.texture_optimization_strategy import TextureOptimizationStrategy
        strat = TextureOptimizationStrategy()
        cost = AssetCost(texture_memory_mb=32.0, total_cost_index=100.0)
        cand = strat.execute_optimization(None, cost, {})
        self.assertLess(cand.cost_after.texture_memory_mb, cost.texture_memory_mb)

    def test_08_case_h_lod_generation_strategy(self):
        """Case H: Estrategia de LOD genera jerarquía de LOD0 a LOD3."""
        from src.asset_optimization_engine.strategies.lod_generation_strategy import LODGenerationStrategy
        strat = LODGenerationStrategy()
        cost = AssetCost(triangle_count=1000)
        cand = strat.execute_optimization(None, cost, {})
        self.assertIn("LOD0", cand.parameters["lods"])
        self.assertIn("LOD3", cand.parameters["lods"])

    def test_09_case_i_pareto_candidate_selection(self):
        """Case I: Selección del mejor candidato Pareto-óptimo."""
        c1 = OptimizationCandidate("C1", "H", "H", StrategyType.MESH_SIMPLIFICATION, performance_delta=0.10, visual_delta=0.0)
        c2 = OptimizationCandidate("C2", "H", "H", StrategyType.LOD_GENERATION, performance_delta=0.30, visual_delta=0.0)
        best = CandidateManager.select_best_candidate([c1, c2])
        self.assertEqual(best.candidate_id, "C2")

    def test_10_case_j_deterministic_optimization_hash(self):
        """Case J: Dos optimizaciones idénticas producen el mismo hash (SHA-256)."""
        geom, surf, q_res = self._get_pipeline_data()
        res1 = self.opt_api.optimize_game_asset("barrel_01", "barrel_01.root", geom, surf, q_res)
        res2 = self.opt_api.optimize_game_asset("barrel_01", "barrel_01.root", geom, surf, q_res)
        self.assertEqual(res1.optimization_hash, res2.optimization_hash)

    def test_11_cost_model_calculation(self):
        """Test 11: Cálculo correcto del modelo de costes multidimensional."""
        geom, surf, q_res = self._get_pipeline_data()
        res = self.opt_api.optimize_game_asset("barrel_01", "barrel_01.root", geom, surf, q_res)
        self.assertGreater(res.baseline_cost.total_cost_index, 0.0)
        self.assertGreater(res.optimized_cost.total_cost_index, 0.0)

    def test_12_validation_clean_result(self):
        """Test 12: Validación de resultado limpio retorna is_valid = True."""
        geom, surf, q_res = self._get_pipeline_data()
        res = self.opt_api.optimize_game_asset("barrel_01", "barrel_01.root", geom, surf, q_res)
        val = self.opt_api.validate_optimization_result(res)
        self.assertTrue(val.is_valid)

    def test_13_strategy_registry_listing(self):
        """Test 13: Registry contiene estrategias fundamentales."""
        from src.asset_optimization_engine.strategies.strategy_registry import OptimizationStrategyRegistry
        reg = OptimizationStrategyRegistry()
        strats = reg.list_strategies()
        self.assertIn(StrategyType.MESH_SIMPLIFICATION, strats)
        self.assertIn(StrategyType.MATERIAL_OPTIMIZATION, strats)
        self.assertIn(StrategyType.TEXTURE_OPTIMIZATION, strats)
        self.assertIn(StrategyType.LOD_GENERATION, strats)

    def test_14_preservation_of_ids(self):
        """Test 14: Preservación de asset_id y semantic_id."""
        geom, surf, q_res = self._get_pipeline_data()
        res = self.opt_api.optimize_game_asset("barrel_01", "barrel_01.root", geom, surf, q_res)
        self.assertEqual(res.asset_id, "barrel_01")
        self.assertEqual(res.semantic_id, "barrel_01.root")

    def test_15_target_platform_profiles(self):
        """Test 15: Configuración de perfiles de plataforma (MOBILE vs PC)."""
        prof_mobile = OptimizationProfile(target_platform=TargetPlatform.MOBILE, polygon_budget=2000)
        self.assertEqual(prof_mobile.target_platform, TargetPlatform.MOBILE)
        self.assertEqual(prof_mobile.polygon_budget, 2000)

    def test_16_performance_delta_positive(self):
        """Test 16: Delta de rendimiento es positivo tras optimizar."""
        geom, surf, q_res = self._get_pipeline_data()
        res = self.opt_api.optimize_game_asset("barrel_01", "barrel_01.root", geom, surf, q_res)
        self.assertGreaterEqual(res.performance_delta, 0.0)

    def test_17_lod_summary_structure(self):
        """Test 17: Estructura de resumen de LOD generada."""
        geom, surf, q_res = self._get_pipeline_data()
        res = self.opt_api.optimize_game_asset("barrel_01", "barrel_01.root", geom, surf, q_res)
        self.assertIsNotNone(res.lod_summary)

    def test_18_production_candidate_flag(self):
        """Test 18: Flag production_candidate emitido como True."""
        geom, surf, q_res = self._get_pipeline_data()
        res = self.opt_api.optimize_game_asset("barrel_01", "barrel_01.root", geom, surf, q_res)
        self.assertTrue(res.production_candidate)

    def test_19_fallback_to_baseline_when_no_candidate_accepted(self):
        """Test 19: Fallback seguro a baseline si ningún candidato es aceptado."""
        geom, surf, q_res = self._get_pipeline_data()
        # Perfil con límite de degradación 0.0 para forzar rechazo
        prof = OptimizationProfile(visual_degradation_limit=0.0, enabled_strategies=[])
        res = self.opt_api.optimize_game_asset("barrel_01", "barrel_01.root", geom, surf, q_res, profile=prof)
        self.assertEqual(res.selected_candidate_id, "NONE_BASELINE")

    def test_20_end_to_end_optimization_contract_for_f68(self):
        """Test 20: Flujo E2E Completo: Prompt -> F56 -> F57 -> F58 -> F59 -> F60 -> F61 -> F62 -> F63 -> F64 -> F65 -> F66 -> F67 -> Listo para F68."""
        geom, surf, q_res = self._get_pipeline_data()
        res = self.opt_api.optimize_game_asset("barrel_01", "barrel_01.root", geom, surf, q_res)
        val = self.opt_api.validate_optimization_result(res)
        self.assertTrue(val.is_valid)
        self.assertEqual(res.optimization_status, "ACCEPTED")
        self.assertGreater(len(res.optimized_state_hash), 0)
        self.assertGreater(len(res.optimization_hash), 0)

if __name__ == "__main__":
    unittest.main()
